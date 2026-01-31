"""
Agent with Pipecat and Daily.co - Self-Hosted Avatar Agent

This example demonstrates how to integrate the BitHuman avatar runtime with
Pipecat Cloud through Daily.co for WebRTC-based real-time communication.

Features:
- Pipecat Pipeline architecture for frame processing
- Daily.co WebRTC transport for audio/video streaming
- BitHuman AsyncBithuman runtime for avatar rendering with lip-sync
- OpenAI GPT-4o-mini for fast, real-time LLM conversation
- Deepgram STT for real-time speech-to-text (supports streaming audio)
- OpenAI TTS for text-to-speech
- Custom FrameProcessor for BitHuman video/audio generation

Architecture:
    User Audio (Daily) → Deepgram STT → GPT-4o-mini → OpenAI TTS → BitHuman Runtime
                                                                        ↓
    User Display ← Video/Audio Frames ← BitHuman Avatar Generation ←────┘

Performance Note:
- Avatar worker model connection and loading typically takes approximately 20 seconds
  on first initialization.

Requirements:
- Python 3.10+
- BitHuman model file (.imx format)
- Daily.co API key and room URL
- OpenAI API key (for LLM and TTS)
- Deepgram API key (for STT - get from https://console.deepgram.com)

Usage:
    # Set environment variables
    export BITHUMAN_MODEL_PATH="path/to/model.imx"
    export BITHUMAN_API_SECRET="your_bithuman_api_secret"
    export DAILY_API_KEY="your_daily_api_key"
    export OPENAI_API_KEY="your_openai_api_key"
    export DEEPGRAM_API_KEY="your_deepgram_api_key"

    # Run the agent
    python agent_pipecat_daily.py --room-url https://your-domain.daily.co/your-room
"""

import argparse
import asyncio
import logging
import os
from typing import Optional

import aiohttp
import cv2
import numpy as np
from dotenv import load_dotenv

# Pipecat imports
from pipecat.frames.frames import (
    AudioRawFrame,
    CancelFrame,
    EndFrame,
    Frame,
    InterruptionFrame,
    OutputAudioRawFrame,
    OutputImageRawFrame,
    StartFrame,
    StartInterruptionFrame,
    SystemFrame,
    TextFrame,
    TranscriptionFrame,
    TTSAudioRawFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.openai import OpenAILLMService, OpenAITTSService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from scipy import signal

# BitHuman imports
from bithuman import AsyncBithuman

# Configure logging
logger = logging.getLogger("bithuman-pipecat-daily-agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)

# Load environment variables
load_dotenv()


class BitHumanAvatarProcessor(FrameProcessor):
    """
    Pipecat FrameProcessor that integrates BitHuman avatar rendering.

    This processor receives TTS audio frames, passes them to the BitHuman runtime,
    and outputs synchronized video and audio frames for the avatar.
    """

    def __init__(
        self,
        model_path: str,
        api_secret: str,
        video_fps: int = 25,
        flush_delay: float = 0.5,
        **kwargs,
    ):
        """
        Initialize the BitHuman Avatar Processor.

        Args:
            model_path: Path to the BitHuman model file (.imx format)
            api_secret: BitHuman API secret for authentication
            video_fps: Target video frame rate (default: 25)
            flush_delay: Delay in seconds before flushing runtime after TTSStoppedFrame (default: 0.5)
                         This ensures all TTS audio frames arrive before signaling end_of_speech.
                         Increase this value if you experience premature lip-sync ending.
        """
        super().__init__(**kwargs)
        self._model_path = model_path
        self._api_secret = api_secret
        self._video_fps = video_fps
        self._runtime: Optional[AsyncBithuman] = None
        self._render_task: Optional[asyncio.Task] = None
        self._running = False
        self._frame_size: tuple[int, int] = (512, 512)  # Default, updated on start
        self._sample_rate: int = 16000
        self._last_tts_stop_time: Optional[float] = None
        self._flush_task: Optional[asyncio.Task] = None
        self._tts_active: bool = False  # Track if TTS is currently active
        self._last_audio_frame_time: Optional[float] = (
            None  # Track last TTS audio frame time
        )
        self._flush_delay: float = (
            flush_delay  # Fallback delay if duration-based detection fails
        )

        # Audio duration tracking for precise completion detection
        self._input_audio_duration: float = (
            0.0  # Total duration of TTS audio pushed to runtime
        )
        self._output_audio_duration: float = (
            0.0  # Total duration of audio output from runtime
        )
        self._tts_segment_start_time: Optional[float] = (
            None  # When current TTS segment started
        )

    async def _initialize_runtime(self):
        """Initialize the BitHuman runtime (can be called from start() or lazily)."""
        if self._runtime:
            logger.info("✅ BitHuman runtime already initialized")
            return

        logger.info(
            f"🚀 Initializing BitHuman Avatar Processor with model: {self._model_path}"
        )
        logger.info("⏳ Creating AsyncBithuman runtime (this may take 20+ seconds)...")
        logger.warning(
            "⚠️  IMPORTANT: Runtime initialization is blocking - TTS will wait until this completes"
        )

        try:
            # Create the AsyncBithuman runtime
            self._runtime = await AsyncBithuman.create(
                model_path=self._model_path,
                api_secret=self._api_secret,
                insecure=True,  # For development
            )
            logger.info("✅ BitHuman runtime created successfully")

            # Get frame size from runtime
            self._frame_size = self._runtime.get_frame_size()
            logger.info(f"📐 Frame size: {self._frame_size}")

            # Get sample rate from runtime settings
            if hasattr(self._runtime, "settings"):
                self._sample_rate = getattr(
                    self._runtime.settings, "INPUT_SAMPLE_RATE", 16000
                )
            logger.info(f"🔊 Audio sample rate: {self._sample_rate}")

            # Start the runtime (reference: example.py line 208)
            # This is required before calling runtime.run()
            logger.info("⏳ Starting BitHuman runtime...")
            await self._runtime.start()
            logger.info("✅ BitHuman runtime started successfully")

            # Start the render loop AFTER runtime.start()
            # Reference: example.py - runtime.start() is called before runtime.run()
            self._running = True
            self._render_task = asyncio.create_task(self._render_loop())
            logger.info("🎬 BitHuman render loop started")

            # Push initial silence to start video generation
            # This ensures video frames are generated even before TTS audio arrives
            await self._push_initial_silence()

            logger.info("✅ BitHuman runtime fully initialized and ready for TTS audio")

        except Exception as e:
            logger.error(f"❌ Failed to initialize BitHuman runtime: {e}")
            import traceback

            logger.error(traceback.format_exc())
            raise

    async def start(self, frame: StartFrame):
        """Initialize the BitHuman runtime when pipeline starts."""
        logger.info("🚀 START METHOD CALLED: Starting BitHuman Avatar Processor")
        logger.info("📥 StartFrame received, initializing BitHuman runtime...")

        # Initialize runtime (this will create runtime and call runtime.start())
        # Reference: bithuman-runtime/python_module/examples/example.py line 208
        await self._initialize_runtime()

        logger.info("✅ BitHuman Avatar Processor start() completed successfully")

    async def _push_initial_silence(self):
        """Push a small amount of silence to start BitHuman video generation."""
        if not self._runtime:
            return

        try:
            # Push 100ms of silence (1600 samples at 16kHz)
            silence_samples = 1600
            silence_bytes = b"\x00" * (silence_samples * 2)  # 16-bit samples

            await self._runtime.push_audio(
                silence_bytes,
                sample_rate=self._sample_rate,
                last_chunk=False,
            )
            logger.info("🔇 Pushed initial silence to start video generation")
        except Exception as e:
            logger.warning(f"⚠️  Failed to push initial silence: {e}")

    async def stop(self, frame: EndFrame):
        """Stop the BitHuman runtime when pipeline ends."""
        logger.info("Stopping BitHuman Avatar Processor")
        self._running = False

        # Cancel pending flush task
        if self._flush_task and not self._flush_task.done():
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        if self._render_task:
            self._render_task.cancel()
            try:
                await self._render_task
            except asyncio.CancelledError:
                pass

        if self._runtime:
            # Flush before stopping to ensure all audio is processed
            await self._runtime.flush()
            await self._runtime.stop()
            logger.info("BitHuman runtime flushed and stopped")

        await super().stop(frame)

    async def cancel(self, frame: CancelFrame):
        """Handle cancellation (interruption)."""
        if self._runtime:
            self._runtime.interrupt()
            # Flush on cancellation to clear the buffer
            await self._runtime.flush()
            logger.debug("BitHuman runtime interrupted and flushed")
        await super().cancel(frame)

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process incoming frames."""
        # CRITICAL: Handle TTS audio frames FIRST - before any other processing
        # This ensures we intercept TTS audio before it goes downstream
        # IMPORTANT: Check TTSAudioRawFrame BEFORE StartFrame and AudioRawFrame
        # DEBUG: Check frame type explicitly
        frame_type = type(frame)
        frame_type_name = frame_type.__name__

        # Check if it's TTSAudioRawFrame using both isinstance and type comparison
        is_tts_audio = isinstance(frame, TTSAudioRawFrame)
        is_tts_audio_by_name = frame_type_name == "TTSAudioRawFrame"

        if is_tts_audio or is_tts_audio_by_name:
            if not is_tts_audio and is_tts_audio_by_name:
                logger.warning(
                    f"⚠️  Frame type name matches TTSAudioRawFrame but isinstance() failed! frame_type={frame_type}, frame_type_name={frame_type_name}"
                )
            logger.info(
                f"🎵🎵🎵 TTS AUDIO FRAME RECEIVED (TTSAudioRawFrame)! sample_rate={frame.sample_rate}, audio_type={type(frame.audio).__name__}"
            )

            # Runtime should be initialized by start() method, but check just in case
            if not self._runtime:
                logger.error(
                    "❌ CRITICAL: BitHuman runtime not initialized! TTS audio arrived before StartFrame."
                )
                logger.error(
                    "❌ This should not happen - runtime should be initialized in start() method."
                )
                logger.warning("⚠️  Attempting lazy initialization as fallback...")
                try:
                    await self._initialize_runtime()
                except Exception as e:
                    logger.error(f"❌ Failed to initialize runtime: {e}")
                    # Don't return - try to process anyway if runtime was created
                    if not self._runtime:
                        return

            if self._runtime:
                # Get audio size before processing
                audio_size = (
                    len(frame.audio) if hasattr(frame.audio, "__len__") else "unknown"
                )

                # Track TTS audio frames for monitoring
                if not hasattr(self, "_tts_audio_frame_count"):
                    self._tts_audio_frame_count = 0
                self._tts_audio_frame_count += 1

                # CRITICAL: Always use last_chunk=False for streaming audio frames
                # We will NOT mark last_chunk=True here or in TTSStoppedFrame handler
                # Instead, we call runtime.flush() in TTSStoppedFrame handler, which pushes
                # end_of_speech=True to the runtime. The runtime will then process all remaining
                # audio and generate all video frames, and yield a VideoFrame with end_of_speech=True
                # when everything is complete. This ensures complete lip-sync.
                is_last_chunk = False

                # Log ALL frames with detailed info for debugging
                audio_bytes_preview = (
                    frame.audio
                    if isinstance(frame.audio, bytes)
                    else frame.audio.tobytes()
                    if hasattr(frame.audio, "tobytes")
                    else b""
                )
                audio_samples = (
                    len(audio_bytes_preview) // 2 if audio_bytes_preview else 0
                )
                audio_duration_ms = (
                    (audio_samples / frame.sample_rate * 1000)
                    if audio_samples > 0
                    else 0
                )

                logger.info(
                    f"🎵 Received TTS audio frame #{self._tts_audio_frame_count} "
                    f"(sample_rate: {frame.sample_rate}Hz, size: {audio_size} bytes, "
                    f"{audio_samples} samples, {audio_duration_ms:.1f}ms duration)"
                )

                # Update last audio frame time - this helps us know when all audio has arrived
                import time

                self._last_audio_frame_time = time.time()

                # Calculate and track input audio duration
                # For int16 audio: duration = len(bytes) / 2 / sample_rate
                audio_bytes = (
                    frame.audio
                    if isinstance(frame.audio, bytes)
                    else frame.audio.tobytes()
                    if hasattr(frame.audio, "tobytes")
                    else b""
                )
                if audio_bytes:
                    audio_duration = (
                        len(audio_bytes) / 2 / frame.sample_rate
                    )  # int16 = 2 bytes per sample
                    self._input_audio_duration += audio_duration
                    logger.debug(
                        f"📊 Input audio duration: {self._input_audio_duration:.3f}s "
                        f"(added {audio_duration:.3f}s from {len(audio_bytes)} bytes)"
                    )

                # Cancel any pending flush task - new audio is arriving
                if self._flush_task and not self._flush_task.done():
                    self._flush_task.cancel()
                    try:
                        await self._flush_task
                    except asyncio.CancelledError:
                        pass
                    logger.debug("🔄 Cancelled pending flush - new TTS audio arrived")

                # Push audio to runtime - this is critical for lip-sync
                # Always use last_chunk=False here - we'll mark the last chunk when TTSStoppedFrame arrives
                await self._push_audio_to_runtime(frame, last_chunk=is_last_chunk)

                # Log successful push with summary
                if (
                    self._tts_audio_frame_count <= 10
                    or self._tts_audio_frame_count % 20 == 0
                ):
                    logger.info(
                        f"✅ Processed TTS audio frame #{self._tts_audio_frame_count} "
                        f"(total input duration: {self._input_audio_duration:.3f}s)"
                    )
            else:
                logger.warning("⚠️  Received TTS audio but runtime not ready")
            # Don't push TTS audio downstream - we'll output our own audio from the render loop
            return  # Don't pass TTS audio downstream

        # DEBUG: Log ALL frames before processing to understand what's arriving
        # NOTE: This logging happens AFTER TTSAudioRawFrame check, so we can see what other frames arrive
        # Use the frame_type_name we already computed above to avoid recomputing
        frame_type = frame_type_name  # Reuse the variable from TTSAudioRawFrame check above (line 263)
        if not hasattr(self, "_all_frames_logged"):
            self._all_frames_logged = set()
        if frame_type not in self._all_frames_logged:
            logger.info(
                f"🔍🔍🔍 ALL FRAMES: First time seeing {frame_type} - checking if it has audio attributes..."
            )
            if hasattr(frame, "audio"):
                logger.info(
                    f"🔍🔍🔍 {frame_type} HAS AUDIO ATTRIBUTE! audio_type={type(getattr(frame, 'audio', None)).__name__}"
                )
            if hasattr(frame, "sample_rate"):
                logger.info(
                    f"🔍🔍🔍 {frame_type} HAS sample_rate ATTRIBUTE! sample_rate={getattr(frame, 'sample_rate', None)}"
                )
            self._all_frames_logged.add(frame_type)

        # CRITICAL: Handle StartFrame - explicitly call start() to initialize runtime
        # This ensures BitHuman runtime is ready before TTS audio arrives
        if isinstance(frame, StartFrame):
            # Call super() first to mark processor as started
            await super().process_frame(frame, direction)
            # Explicitly call start() to initialize runtime immediately
            # This is critical because TTS may start before runtime is ready
            await self.start(frame)
            # Then pass StartFrame downstream
            await self.push_frame(frame, direction)
            return

        # CRITICAL: User audio frames should NOT reach BitHumanAvatarProcessor
        # They should be processed by STT and converted to TranscriptionFrame
        # If we receive AudioRawFrame here, it means STT is not processing it
        #
        # ROOT CAUSE: OpenAISTTService may not process AudioRawFrame directly
        # It might need UserAudioRawFrame or a different frame type
        # OR it might need VAD (Voice Activity Detection) to trigger processing
        #
        # SOLUTION: We should NOT be receiving AudioRawFrame here at all
        # The issue is that STT is not processing user audio frames
        # Let's check if this is UserAudioRawFrame vs AudioRawFrame
        # and log more details to help debug
        # CRITICAL: User audio frames (AudioRawFrame) should be processed by STT BEFORE reaching here
        # If AudioRawFrame reaches BitHumanAvatarProcessor, it means STT is not processing it
        # This is a critical issue - user speech cannot be recognized
        if isinstance(frame, AudioRawFrame):
            # Check frame type name to see if it's UserAudioRawFrame or just AudioRawFrame
            frame_type_name = type(frame).__name__

            # Count how many AudioRawFrame we receive to track if user is speaking
            if not hasattr(self, "_audio_raw_frame_count"):
                self._audio_raw_frame_count = 0
            self._audio_raw_frame_count += 1

            # Log first occurrence and every 100th frame to track audio flow
            if self._audio_raw_frame_count == 1:
                logger.error(
                    "❌ CRITICAL: AudioRawFrame reached BitHumanAvatarProcessor!"
                )
                logger.error(f"❌ Frame type: {frame_type_name}")
                logger.error("❌ This means STT is NOT processing user audio!")
                logger.error("❌ STT should convert AudioRawFrame → TranscriptionFrame")
                logger.error(
                    "❌ Pipeline: transport.input() → stt → ... → bithuman_avatar"
                )
                logger.error("❌ Possible causes:")
                logger.error(
                    "   1. OpenAISTTService doesn't process AudioRawFrame directly"
                )
                logger.error(
                    "   2. STT needs VAD (Voice Activity Detection) to trigger"
                )
                logger.error(
                    "   3. STT service is not correctly configured in pipeline"
                )
                logger.error(
                    "   4. STT might need UserAudioRawFrame instead of AudioRawFrame"
                )
                logger.error(
                    "❌ Frame will be ignored - user audio cannot be processed"
                )
            elif self._audio_raw_frame_count % 100 == 0:
                logger.warning(
                    f"⚠️  Received {self._audio_raw_frame_count} AudioRawFrame frames - STT still not processing!"
                )

            # DO NOT pass AudioRawFrame downstream - it would go to transport.output()
            # which is wrong. User audio should be processed by STT upstream.
            # The real fix is to ensure STT processes frames before they reach here.
            return  # Ignore and don't pass downstream

        # NOTE: TTSAudioRawFrame handling moved to the very beginning of process_frame()
        # to ensure it's checked before any other frame processing

        # CRITICAL: Also check for OutputAudioRawFrame from TTS service
        # Some TTS services may output OutputAudioRawFrame instead of TTSAudioRawFrame
        # We need to intercept these BEFORE they go to transport.output()
        if isinstance(frame, OutputAudioRawFrame):
            # Check if this is from TTS (it should be if it's coming from tts service in pipeline)
            # We can identify TTS audio by checking if TTS is active
            if hasattr(self, "_tts_active") and self._tts_active:
                logger.info(
                    f"🎵🎵🎵 TTS AUDIO FRAME RECEIVED (OutputAudioRawFrame)! sample_rate={frame.sample_rate}, audio_type={type(frame.audio).__name__}"
                )

                # Runtime should be initialized by start() method
                if not self._runtime:
                    logger.error(
                        "❌ CRITICAL: BitHuman runtime not initialized! TTS audio arrived before StartFrame."
                    )
                    return

                if self._runtime:
                    # Get audio size before processing
                    audio_size = (
                        len(frame.audio)
                        if hasattr(frame.audio, "__len__")
                        else "unknown"
                    )

                    # Update last audio frame time - this helps us know when all audio has arrived
                    import time

                    self._last_audio_frame_time = time.time()

                    # Calculate and track input audio duration
                    audio_bytes = (
                        frame.audio
                        if isinstance(frame.audio, bytes)
                        else frame.audio.tobytes()
                        if hasattr(frame.audio, "tobytes")
                        else b""
                    )
                    if audio_bytes:
                        audio_duration = (
                            len(audio_bytes) / 2 / frame.sample_rate
                        )  # int16 = 2 bytes per sample
                        self._input_audio_duration += audio_duration
                        logger.debug(
                            f"📊 Input audio duration: {self._input_audio_duration:.3f}s "
                            f"(added {audio_duration:.3f}s from OutputAudioRawFrame)"
                        )

                    # Cancel any pending flush task - new audio is arriving
                    if self._flush_task and not self._flush_task.done():
                        self._flush_task.cancel()
                        try:
                            await self._flush_task
                        except asyncio.CancelledError:
                            pass
                        logger.debug(
                            "🔄 Cancelled pending flush - new TTS audio (OutputAudioRawFrame) arrived"
                        )

                    # Track TTS audio frames for monitoring
                    if not hasattr(self, "_tts_audio_frame_count"):
                        self._tts_audio_frame_count = 0
                    self._tts_audio_frame_count += 1

                    # Log ALL frames initially to debug
                    logger.info(
                        f"🎵 Received TTS audio frame (OutputAudioRawFrame) #{self._tts_audio_frame_count} (sample_rate: {frame.sample_rate}, size: {audio_size})"
                    )

                    # Convert OutputAudioRawFrame to TTSAudioRawFrame for processing
                    try:
                        tts_frame = TTSAudioRawFrame(
                            audio=frame.audio, sample_rate=frame.sample_rate
                        )
                        # Push audio to runtime - this is critical for lip-sync
                        await self._push_audio_to_runtime(tts_frame)

                        # Log successful push
                        logger.info(
                            f"✅ Pushed TTS audio frame (OutputAudioRawFrame) #{self._tts_audio_frame_count} to BitHuman runtime"
                        )
                    except Exception as e:
                        logger.error(
                            f"❌ Failed to process OutputAudioRawFrame as TTS audio: {e}"
                        )

                # Don't push TTS audio downstream - we'll output our own audio from the render loop
                return  # Don't pass TTS audio downstream

        # DEBUG: Log all frame types to understand what's arriving (after TTS check)
        frame_type = type(frame).__name__
        if not hasattr(self, "_frame_types_seen"):
            self._frame_types_seen = set()
        if frame_type not in self._frame_types_seen:
            logger.info(f"🔍 DEBUG: First time seeing frame type: {frame_type}")
            self._frame_types_seen.add(frame_type)

        # CRITICAL: Check if this is an audio frame that we might have missed
        # Some TTS services might output different frame types
        if hasattr(frame, "audio") or hasattr(frame, "sample_rate"):
            logger.warning(
                f"⚠️  WARNING: Found frame with audio attributes but not TTSAudioRawFrame: {frame_type}"
            )
            logger.warning(
                f"⚠️  Frame attributes: {[attr for attr in dir(frame) if not attr.startswith('_')]}"
            )
            # Try to handle it as audio if it has audio attribute
            if hasattr(frame, "audio") and hasattr(frame, "sample_rate"):
                logger.warning(
                    f"⚠️  Attempting to process as TTS audio: sample_rate={frame.sample_rate}"
                )
                # Create a TTSAudioRawFrame-like object
                try:
                    # TTSAudioRawFrame is already imported at the top
                    tts_frame = TTSAudioRawFrame(
                        audio=frame.audio, sample_rate=frame.sample_rate
                    )
                    # Process it as TTS audio
                    if self._runtime:
                        await self._push_audio_to_runtime(tts_frame)
                    return  # Don't pass downstream
                except Exception as e:
                    logger.error(f"❌ Failed to process audio frame: {e}")

        # CRITICAL: Handle TranscriptionFrame BEFORE calling super().process_frame()
        # This ensures user speech is properly passed to LLM for TTS response
        # TranscriptionFrame comes from STT and MUST reach LLM
        if isinstance(frame, TranscriptionFrame):
            logger.info(f"📝📝📝 TRANSCRIPTION RECEIVED: {frame.text}")
            logger.info(
                f"📝 Transcription details: user_id={getattr(frame, 'user_id', 'unknown')}, timestamp={getattr(frame, 'timestamp', 'unknown')}"
            )
            logger.info(
                "📝 Passing TranscriptionFrame downstream to LLM for response generation..."
            )
            # Call super().process_frame() first to ensure proper frame processing
            await super().process_frame(frame, direction)
            # Then push downstream to LLM
            await self.push_frame(frame, direction)
            logger.info(
                "✅ TranscriptionFrame passed to LLM successfully - expecting TTS response soon"
            )
            return  # Don't process further

        # CRITICAL: Call super().process_frame() for other frame types
        # This ensures frames are properly processed by the framework
        await super().process_frame(frame, direction)

        # Handle TTS lifecycle events - pass through
        # NOTE: super().process_frame() already called above, so we just push downstream
        if isinstance(frame, TTSStartedFrame):
            logger.info("🎤 TTS started")
            # Mark TTS as active
            self._tts_active = True
            # Cancel any pending flush task - new TTS is starting
            if self._flush_task and not self._flush_task.done():
                self._flush_task.cancel()
                try:
                    await self._flush_task
                except asyncio.CancelledError:
                    pass
            # Reset flush timer and audio frame tracking when new TTS starts
            self._last_tts_stop_time = None
            self._last_audio_frame_time = None
            # Reset audio duration tracking for new TTS segment
            self._input_audio_duration = 0.0
            self._output_audio_duration = 0.0
            import time

            self._tts_segment_start_time = time.time()
            # Already called super().process_frame() above, just push downstream
            await self.push_frame(frame, direction)
            return

        elif isinstance(frame, TTSStoppedFrame):
            logger.info("🎤 TTS stopped")
            # Mark TTS as inactive
            self._tts_active = False

            # CRITICAL FIX: Use duration-based detection instead of fixed delay.
            # We track input_audio_duration (TTS audio pushed to runtime) and
            # output_audio_duration (audio output from runtime). When they match,
            # we know all audio has been processed.
            if self._runtime:
                import time

                current_time = time.time()

                logger.info(
                    f"📊 TTSStoppedFrame received. Input audio duration: {self._input_audio_duration:.3f}s, "
                    f"Output audio duration: {self._output_audio_duration:.3f}s"
                )

                # Cancel any existing flush task
                if self._flush_task and not self._flush_task.done():
                    self._flush_task.cancel()
                    try:
                        await self._flush_task
                    except asyncio.CancelledError:
                        pass

                # Schedule smart flush based on duration tracking
                async def _smart_flush():
                    try:
                        # Wait a short time for any remaining TTS audio frames to arrive
                        # This handles network delay between TTSStoppedFrame and last TTSAudioRawFrame
                        initial_wait = 0.1  # 100ms initial wait
                        await asyncio.sleep(initial_wait)

                        # Check if new audio arrived during initial wait
                        if self._last_audio_frame_time is not None:
                            time_since_last_audio = (
                                time.time() - self._last_audio_frame_time
                            )
                            if (
                                time_since_last_audio < 0.05
                            ):  # Audio arrived very recently
                                logger.info(
                                    "🔄 New audio arrived during initial wait, recalculating..."
                                )
                                # Recalculate input duration (it may have increased)
                                # Continue to wait and check

                        # CRITICAL: Wait for output to catch up with input BEFORE flushing
                        # AudioStreamBatcher buffers audio and only yields when enough is accumulated
                        # We MUST wait until all buffered audio is output, otherwise it will be lost
                        # after flush() signals end_of_speech
                        max_wait_time = max(
                            self._flush_delay * 2, 2.0
                        )  # At least 2 seconds, or 2x flush_delay
                        check_interval = 0.05  # Check every 50ms
                        wait_start = time.time()
                        last_output_duration = self._output_audio_duration
                        no_progress_count = 0
                        max_no_progress_checks = (
                            20  # 1 second of no progress (20 * 50ms)
                        )

                        logger.info(
                            f"⏳ Waiting for audio processing to complete before flush... "
                            f"(max wait: {max_wait_time}s)"
                        )

                        while time.time() - wait_start < max_wait_time:
                            # Check if output has caught up with input
                            # We need 98%+ completion to ensure all buffered audio is processed
                            if self._input_audio_duration > 0:
                                completion_ratio = (
                                    self._output_audio_duration
                                    / self._input_audio_duration
                                )

                                # Check if output is making progress
                                if self._output_audio_duration > last_output_duration:
                                    no_progress_count = (
                                        0  # Reset counter if progress made
                                    )
                                    last_output_duration = self._output_audio_duration
                                else:
                                    no_progress_count += 1

                                if (
                                    completion_ratio >= 0.98
                                ):  # 98% of input audio has been output
                                    logger.info(
                                        f"✅ Audio processing complete: {completion_ratio*100:.1f}% "
                                        f"(input: {self._input_audio_duration:.3f}s, "
                                        f"output: {self._output_audio_duration:.3f}s)"
                                    )
                                    break
                                elif no_progress_count >= max_no_progress_checks:
                                    # No progress for 1 second, but check if we're close enough
                                    if (
                                        completion_ratio >= 0.90
                                    ):  # 90% is acceptable if no more progress
                                        logger.warning(
                                            f"⚠️ No audio progress for 1s, but {completion_ratio*100:.1f}% complete. "
                                            f"Proceeding with flush (input: {self._input_audio_duration:.3f}s, "
                                            f"output: {self._output_audio_duration:.3f}s)"
                                        )
                                        break
                                    else:
                                        logger.warning(
                                            f"⚠️ No audio progress for 1s, only {completion_ratio*100:.1f}% complete. "
                                            f"Continuing to wait..."
                                        )
                                        no_progress_count = (
                                            0  # Reset and continue waiting
                                        )
                                else:
                                    logger.debug(
                                        f"⏳ Waiting for audio processing: {completion_ratio*100:.1f}% "
                                        f"(input: {self._input_audio_duration:.3f}s, "
                                        f"output: {self._output_audio_duration:.3f}s, "
                                        f"no_progress: {no_progress_count}/{max_no_progress_checks})"
                                    )
                            else:
                                # No input audio tracked, use time-based fallback
                                if self._last_audio_frame_time is not None:
                                    time_since_last_audio = (
                                        time.time() - self._last_audio_frame_time
                                    )
                                    if (
                                        time_since_last_audio >= 0.3
                                    ):  # 300ms since last audio
                                        logger.info(
                                            f"✅ No new audio for {time_since_last_audio*1000:.0f}ms, "
                                            "proceeding with flush"
                                        )
                                        break

                            await asyncio.sleep(check_interval)
                        else:
                            # Timeout reached
                            final_ratio = (
                                (
                                    self._output_audio_duration
                                    / self._input_audio_duration
                                    * 100
                                )
                                if self._input_audio_duration > 0
                                else 0
                            )
                            logger.warning(
                                f"⚠️ Flush timeout reached ({max_wait_time}s). "
                                f"Input: {self._input_audio_duration:.3f}s, "
                                f"Output: {self._output_audio_duration:.3f}s ({final_ratio:.1f}% complete). "
                                f"Proceeding with flush - some audio may be lost."
                            )

                        # CRITICAL: Before flushing, push a last_chunk=True to trigger AudioStreamBatcher flush
                        # AudioStreamBatcher only flushes when last_chunk=True or data is None
                        # This ensures all buffered audio is processed before end_of_speech is signaled
                        logger.info(
                            "🔚 Pushing final audio chunk with last_chunk=True to trigger AudioStreamBatcher flush"
                        )
                        # Push a small empty/silence chunk with last_chunk=True
                        # This will trigger AudioStreamBatcher.flush() which processes all buffered audio
                        silence_bytes = (
                            b"\x00" * 320
                        )  # 10ms of silence at 16kHz (160 samples * 2 bytes)
                        await self._runtime.push_audio(
                            silence_bytes,
                            sample_rate=self._sample_rate,
                            last_chunk=True,  # CRITICAL: This triggers AudioStreamBatcher flush
                        )
                        logger.info(
                            "✅ Final audio chunk with last_chunk=True pushed, AudioStreamBatcher will flush buffered audio"
                        )

                        # CRITICAL: Wait for AudioStreamBatcher to process the flush and output all buffered audio
                        # We need to wait until output catches up with input
                        flush_wait_start = time.time()
                        flush_wait_timeout = (
                            1.0  # Wait up to 1 second for flush to complete
                        )
                        flush_check_interval = 0.05

                        while time.time() - flush_wait_start < flush_wait_timeout:
                            if self._input_audio_duration > 0:
                                completion_ratio = (
                                    self._output_audio_duration
                                    / self._input_audio_duration
                                )
                                if completion_ratio >= 0.98:  # 98% complete after flush
                                    logger.info(
                                        f"✅ AudioStreamBatcher flush completed: {completion_ratio*100:.1f}% "
                                        f"(input: {self._input_audio_duration:.3f}s, "
                                        f"output: {self._output_audio_duration:.3f}s)"
                                    )
                                    break
                                else:
                                    logger.debug(
                                        f"⏳ Waiting for AudioStreamBatcher flush: {completion_ratio*100:.1f}% "
                                        f"(input: {self._input_audio_duration:.3f}s, "
                                        f"output: {self._output_audio_duration:.3f}s)"
                                    )
                            await asyncio.sleep(flush_check_interval)
                        else:
                            logger.warning(
                                f"⚠️ AudioStreamBatcher flush timeout ({flush_wait_timeout}s). "
                                f"Input: {self._input_audio_duration:.3f}s, "
                                f"Output: {self._output_audio_duration:.3f}s. Proceeding anyway."
                            )

                        # Now flush to signal end_of_speech
                        logger.info(
                            "🔚 Calling runtime.flush() to signal end of speech"
                        )
                        logger.info(
                            "⏳ Runtime will process all remaining audio and generate all video frames"
                        )
                        logger.info(
                            "⏳ We'll detect frame.end_of_speech=True in render loop when processing is complete"
                        )
                        await self._runtime.flush()
                        logger.info(
                            "✅ Flush signal sent to runtime, waiting for end_of_speech frame..."
                        )
                    except asyncio.CancelledError:
                        logger.debug("🔄 Smart flush cancelled")
                    except Exception as e:
                        logger.error(f"❌ Error in smart flush: {e}")
                        import traceback

                        logger.error(traceback.format_exc())

                self._flush_task = asyncio.create_task(_smart_flush())

            # DO NOT flush here - LLM may send more text chunks immediately
            # Flushing will break lip-sync for subsequent audio chunks
            # Only flush on explicit interruption or session end
            # The BitHuman runtime will handle continuous audio streams internally
            # Already called super().process_frame() above, just push downstream
            await self.push_frame(frame, direction)
            return

        # Handle interruptions
        elif isinstance(frame, (StartInterruptionFrame, InterruptionFrame)):
            if self._runtime:
                self._runtime.interrupt()
                # Flush on interruption to clear the buffer
                await self._runtime.flush()
                logger.info("⏸️  BitHuman runtime interrupted and flushed")
            await self.push_frame(frame, direction)

        # Pass through other frames
        elif isinstance(frame, SystemFrame):
            await self.push_frame(frame, direction)
        else:
            # Pass through all other frames
            await self.push_frame(frame, direction)

    async def _push_audio_to_runtime(
        self, frame: TTSAudioRawFrame, last_chunk: bool = False
    ):
        """Push TTS audio to BitHuman runtime for processing."""
        if not self._runtime:
            logger.warning("⚠️  BitHuman runtime not available, cannot push audio")
            return

        try:
            # Convert audio data to bytes if needed
            audio_data = frame.audio
            original_type = type(audio_data).__name__
            input_sample_rate = frame.sample_rate
            target_sample_rate = (
                self._sample_rate
            )  # BitHuman runtime sample rate (16000)

            # Resample if sample rates don't match
            if input_sample_rate != target_sample_rate:
                logger.warning(
                    f"⚠️  Sample rate mismatch: TTS={input_sample_rate}Hz, BitHuman={target_sample_rate}Hz. Resampling..."
                )

                # Convert bytes to numpy array for resampling
                if isinstance(audio_data, bytes):
                    # Assume int16 format
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                elif isinstance(audio_data, memoryview):
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                elif isinstance(audio_data, np.ndarray):
                    audio_array = audio_data
                else:
                    logger.error(
                        f"❌ Cannot resample: unknown audio type {type(audio_data)}"
                    )
                    return

                # Convert to float32 for resampling
                if audio_array.dtype == np.int16:
                    audio_float = audio_array.astype(np.float32) / 32767.0
                else:
                    audio_float = audio_array.astype(np.float32)

                # Use scipy.signal.resample for better quality resampling
                # Calculate the number of samples after resampling
                num_samples = int(
                    len(audio_float) * target_sample_rate / input_sample_rate
                )
                audio_resampled = signal.resample(audio_float, num_samples)

                # Convert back to int16
                audio_array = (np.clip(audio_resampled, -1.0, 1.0) * 32767).astype(
                    np.int16
                )
                audio_bytes = audio_array.tobytes()
                # Only log resampling on first occurrence or if it's unexpected
                if not hasattr(self, "_resample_logged"):
                    logger.info(
                        f"🔄 Resampling audio: {input_sample_rate}Hz -> {target_sample_rate}Hz (first occurrence)"
                    )
                    self._resample_logged = True
                else:
                    logger.debug(
                        f"🔄 Resampled audio: {input_sample_rate}Hz -> {target_sample_rate}Hz ({len(audio_data)} -> {len(audio_bytes)} bytes)"
                    )
            else:
                # No resampling needed
                if isinstance(audio_data, np.ndarray):
                    # Ensure it's int16 format for BitHuman
                    if audio_data.dtype != np.int16:
                        # Convert float32 to int16 if needed
                        if audio_data.dtype == np.float32:
                            # Clamp values to [-1, 1] range before conversion
                            audio_data = np.clip(audio_data, -1.0, 1.0)
                            audio_data = (audio_data * 32767).astype(np.int16)
                            logger.debug(
                                f"🔄 Converted float32 audio to int16 (shape: {audio_data.shape})"
                            )
                        else:
                            audio_data = audio_data.astype(np.int16)
                            logger.debug(
                                f"🔄 Converted {audio_data.dtype} audio to int16"
                            )
                    audio_bytes = audio_data.tobytes()
                elif isinstance(audio_data, memoryview):
                    audio_bytes = bytes(audio_data)
                elif isinstance(audio_data, bytes):
                    audio_bytes = audio_data
                else:
                    logger.warning(
                        f"⚠️  Unknown audio data type: {original_type}, value: {type(audio_data)}"
                    )
                    return

            # CRITICAL: Check if audio_bytes is empty or too small
            # BitHuman runtime's AudioStreamBatcher may require minimum audio size
            if (
                not audio_bytes or len(audio_bytes) < 2
            ):  # At least 1 sample (2 bytes for int16)
                logger.warning(
                    f"⚠️  Skipping empty or too small audio chunk: {len(audio_bytes)} bytes"
                )
                return

            # Log audio chunk size for debugging
            audio_samples = len(audio_bytes) // 2  # int16 = 2 bytes per sample
            audio_duration_ms = (audio_samples / target_sample_rate) * 1000
            if not hasattr(self, "_audio_chunk_sizes"):
                self._audio_chunk_sizes = []
            self._audio_chunk_sizes.append((len(audio_bytes), audio_duration_ms))

            # Log first few chunks and periodically to track audio flow
            if (
                len(self._audio_chunk_sizes) <= 10
                or len(self._audio_chunk_sizes) % 50 == 0
            ):
                logger.info(
                    f"📦 Pushing audio chunk: {len(audio_bytes)} bytes ({audio_samples} samples, "
                    f"{audio_duration_ms:.1f}ms @ {target_sample_rate}Hz)"
                )

            # CRITICAL: Push audio to BitHuman runtime IMMEDIATELY and SYNCHRONOUSLY
            # Do not await other operations before pushing - this ensures audio is available
            # for video frame generation, preventing video frames from being generated before
            # their corresponding audio chunks are processed
            # Use last_chunk parameter to mark the end of an audio segment
            # When last_chunk=True, the runtime will finish processing all buffered audio
            # This is critical for proper lip-sync completion
            try:
                await self._runtime.push_audio(
                    audio_bytes,
                    sample_rate=target_sample_rate,  # Use target sample rate
                    last_chunk=last_chunk,  # Use the provided last_chunk parameter
                )
                # Log successful push
                if len(self._audio_chunk_sizes) <= 10:
                    logger.info(
                        f"✅ Successfully pushed audio chunk #{len(self._audio_chunk_sizes)} "
                        f"({len(audio_bytes)} bytes, {audio_duration_ms:.1f}ms)"
                    )
            except Exception as push_error:
                logger.error(
                    f"❌ Failed to push audio to runtime: {push_error} "
                    f"(chunk size: {len(audio_bytes)} bytes, {audio_duration_ms:.1f}ms)"
                )
                import traceback

                logger.error(traceback.format_exc())
                raise

            # Track audio push timing for debugging
            if not hasattr(self, "_audio_push_count"):
                self._audio_push_count = 0
            self._audio_push_count += 1

            # Log first few audio pushes to verify timing
            if self._audio_push_count <= 5:
                logger.info(
                    f"🎵 Pushed audio chunk #{self._audio_push_count} to runtime (size: {len(audio_bytes)} bytes, sample_rate: {target_sample_rate}Hz, last_chunk: {last_chunk})"
                )
            # Only log occasionally to avoid log spam
            if not hasattr(self, "_push_count"):
                self._push_count = 0
            self._push_count += 1
            if self._push_count <= 5 or self._push_count % 50 == 0:
                logger.debug(
                    f"✅ Pushed audio chunk #{self._push_count} ({len(audio_bytes)} bytes, {target_sample_rate}Hz)"
                )
        except Exception as e:
            logger.error(f"❌ Error pushing audio to BitHuman runtime: {e}")
            import traceback

            logger.error(traceback.format_exc())

    async def _render_loop(self):
        """
        Background task that renders BitHuman frames and pushes them downstream.
        This matches the pattern from LiveKit's BithumanGenerator._stream_impl()

        CRITICAL: Only push what the runtime generates - no empty audio frames.
        The runtime handles audio/video synchronization internally.
        Reference: livekit-plugins-bithuman/avatar.py lines 659-675
        """
        logger.info("🎬 BitHuman render loop starting...")
        frame_count = 0
        video_frame_count = 0
        audio_frame_count = 0

        try:
            # Check if runtime is ready
            if not self._runtime:
                logger.error("❌ Runtime not initialized, cannot start render loop")
                return

            logger.info("✅ Starting to iterate over runtime.run()...")
            logger.info(
                f"📊 Starting render loop - Input audio duration so far: {self._input_audio_duration:.3f}s"
            )
            end_of_speech_detected = False
            frames_after_eos = 0
            last_output_duration_log = 0.0

            async for bh_frame in self._runtime.run():
                if not self._running:
                    break

                frame_count += 1

                # CRITICAL: Track end_of_speech but continue processing all frames
                # The runtime may continue generating frames after end_of_speech=True
                # We must push ALL frames until runtime naturally stops
                if bh_frame.end_of_speech:
                    if not end_of_speech_detected:
                        logger.info(
                            "🎯 END OF SPEECH DETECTED: Runtime signaled end of speech"
                        )
                        logger.info(
                            "🎯 Continuing to process all remaining frames until runtime stops..."
                        )
                        end_of_speech_detected = True
                    frames_after_eos += 1

                    # Log first few frames after EOS to track progress
                    if frames_after_eos <= 5:
                        logger.info(
                            f"🔄 Processing frame #{frame_count} after end_of_speech (frames_after_eos: {frames_after_eos})"
                        )

                # CRITICAL: Match LiveKit BithumanGenerator pattern - only push what runtime generates
                # Reference: livekit-plugins-bithuman/avatar.py lines 659-675
                # - Push video frame if available
                # - Push audio frame if available (runtime generates them together)
                # - DO NOT push empty audio frames - this causes sync issues
                # - The runtime handles audio/video synchronization internally

                # Track frames without audio for debugging
                has_video = bh_frame.bgr_image is not None
                has_audio = bh_frame.audio_chunk is not None

                # Log when video frame has no audio (this is the problem!)
                if has_video and not has_audio:
                    if not hasattr(self, "_video_without_audio_count"):
                        self._video_without_audio_count = 0
                    self._video_without_audio_count += 1

                    # Log first few and periodically
                    if (
                        self._video_without_audio_count <= 5
                        or self._video_without_audio_count % 50 == 0
                    ):
                        logger.warning(
                            f"⚠️  Video frame #{video_frame_count + 1} has NO audio chunk! "
                            f"(total video frames without audio: {self._video_without_audio_count})"
                        )

                # Push video frame if available (matching LiveKit pattern)
                if has_video:
                    # Convert BGR to RGB for Pipecat/Daily (most video encoders expect RGB)
                    rgb_image = cv2.cvtColor(bh_frame.bgr_image, cv2.COLOR_BGR2RGB)

                    # Ensure image is contiguous in memory for better performance
                    if not rgb_image.flags["C_CONTIGUOUS"]:
                        rgb_image = np.ascontiguousarray(rgb_image)

                    # OutputImageRawFrame expects numpy array, not bytes
                    # Use RGB format for video encoding (most codecs expect RGB)
                    video_frame = OutputImageRawFrame(
                        image=rgb_image,  # Pass numpy array directly (RGB format)
                        size=(rgb_image.shape[1], rgb_image.shape[0]),
                        format="RGB",  # Use RGB for video encoding (not RGBA)
                    )
                    await self.push_frame(video_frame)
                    video_frame_count += 1

                    # Log first few video frames
                    if video_frame_count <= 5:
                        logger.info(
                            f"📹 Pushed video frame #{video_frame_count} to pipeline "
                            f"(size: {rgb_image.shape[1]}x{rgb_image.shape[0]}, format: RGB, "
                            f"has_audio: {has_audio})"
                        )

                # Push audio frame if available (matching LiveKit pattern)
                # Runtime generates audio chunks synchronized with video frames
                # We only push what runtime generates - no empty frames
                if has_audio:
                    # Get audio bytes directly (AudioChunk.bytes property returns data.tobytes())
                    # This matches agent.py line 162: data=frame.audio_chunk.bytes
                    audio_bytes = bh_frame.audio_chunk.bytes

                    # Verify it's bytes (should always be from AudioChunk.bytes property)
                    if not isinstance(audio_bytes, bytes):
                        # Fallback: convert from array if needed
                        audio_array = bh_frame.audio_chunk.array
                        if audio_array.dtype != np.int16:
                            audio_array = (audio_array * 32767).astype(np.int16)
                        audio_bytes = audio_array.tobytes()

                    # Track output audio duration for completion detection
                    # AudioChunk has duration property, but we can also calculate it
                    audio_duration = bh_frame.audio_chunk.duration
                    self._output_audio_duration += audio_duration

                    # Log periodically to track progress
                    if (
                        self._output_audio_duration - last_output_duration_log >= 0.5
                    ):  # Every 0.5s
                        completion_ratio = (
                            (
                                self._output_audio_duration
                                / self._input_audio_duration
                                * 100
                            )
                            if self._input_audio_duration > 0
                            else 0
                        )
                        logger.info(
                            f"📊 Audio processing: input={self._input_audio_duration:.3f}s, "
                            f"output={self._output_audio_duration:.3f}s "
                            f"({completion_ratio:.1f}% complete)"
                        )
                        last_output_duration_log = self._output_audio_duration
                    else:
                        logger.debug(
                            f"📊 Output audio duration: {self._output_audio_duration:.3f}s "
                            f"(added {audio_duration:.3f}s)"
                        )

                    # Create audio frame matching agent.py format (rtc.AudioFrame with bytes data)
                    audio_frame = OutputAudioRawFrame(
                        audio=audio_bytes,  # Direct bytes from AudioChunk.bytes
                        sample_rate=bh_frame.audio_chunk.sample_rate,
                        num_channels=1,
                    )
                    await self.push_frame(audio_frame)
                    audio_frame_count += 1

                    # Log first few audio frames
                    if audio_frame_count <= 5:
                        logger.info(
                            f"🔊 Pushed audio frame #{audio_frame_count} to pipeline "
                            f"(sample_rate: {bh_frame.audio_chunk.sample_rate}, "
                            f"size: {len(audio_bytes)} bytes, duration: {audio_duration:.3f}s)"
                        )

                # Log progress periodically
                if frame_count % 250 == 0:
                    logger.info(
                        f"📊 Rendered {frame_count} frames (video: {video_frame_count}, audio: {audio_frame_count})"
                    )
                    if end_of_speech_detected:
                        logger.info(
                            f"📊 Frames after end_of_speech: {frames_after_eos}"
                        )

        except asyncio.CancelledError:
            logger.info("⏹️  BitHuman render loop cancelled")
        except Exception as e:
            logger.error(f"❌ Error in BitHuman render loop: {e}")
            import traceback

            logger.error(traceback.format_exc())
        finally:
            logger.info(
                f"✅ Render loop completed. Total frames: {frame_count} "
                f"(video: {video_frame_count}, audio: {audio_frame_count})"
            )
            if end_of_speech_detected:
                logger.info(
                    f"✅ Processed {frames_after_eos} frames after end_of_speech signal"
                )

            # Final audio duration summary for debugging
            logger.info(
                f"📊 FINAL AUDIO SUMMARY: "
                f"Input={self._input_audio_duration:.3f}s, "
                f"Output={self._output_audio_duration:.3f}s"
            )
            if self._input_audio_duration > 0:
                completion_ratio = (
                    self._output_audio_duration / self._input_audio_duration
                ) * 100
                logger.info(
                    f"📊 Audio completion ratio: {completion_ratio:.1f}% "
                    f"({'✅ Complete' if completion_ratio >= 95 else '⚠️ Incomplete - audio may be missing!'})"
                )
            if hasattr(self, "_tts_audio_frame_count"):
                logger.info(
                    f"📊 Total TTS audio frames received: {self._tts_audio_frame_count}"
                )
            if hasattr(self, "_audio_chunk_sizes") and self._audio_chunk_sizes:
                total_chunks = len(self._audio_chunk_sizes)
                avg_size = (
                    sum(size for size, _ in self._audio_chunk_sizes) / total_chunks
                )
                avg_duration = (
                    sum(dur for _, dur in self._audio_chunk_sizes) / total_chunks
                )
                logger.info(
                    f"📊 Audio chunks pushed to runtime: {total_chunks} "
                    f"(avg size: {avg_size:.0f} bytes, avg duration: {avg_duration:.1f}ms)"
                )

            # CRITICAL: Report video/audio frame mismatch
            if hasattr(self, "_video_without_audio_count"):
                logger.warning(
                    f"⚠️  VIDEO/AUDIO MISMATCH: {self._video_without_audio_count} video frames "
                    f"had NO audio chunk! This causes lip-sync issues."
                )
                logger.warning(
                    f"⚠️  Video frames: {video_frame_count}, Audio frames: {audio_frame_count}, "
                    f"Ratio: {video_frame_count/audio_frame_count if audio_frame_count > 0 else 'N/A'}:1"
                )
                logger.warning(
                    "⚠️  This suggests AudioStreamBatcher is not yielding audio frequently enough, "
                    "or audio is being buffered and not flushed properly."
                )

    @property
    def frame_size(self) -> tuple[int, int]:
        """Get the video frame size."""
        return self._frame_size

    @property
    def sample_rate(self) -> int:
        """Get the audio sample rate."""
        return self._sample_rate


async def create_daily_room(api_key: str, room_name: Optional[str] = None) -> dict:
    """
    Create a Daily.co room using the REST API.

    Args:
        api_key: Daily.co API key
        room_name: Optional room name (auto-generated if not provided)

    Returns:
        Dictionary containing room information including URL
    """
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {}
        if room_name:
            data["name"] = room_name

        async with session.post(
            "https://api.daily.co/v1/rooms",
            headers=headers,
            json=data,
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to create room: {error_text}")
            return await response.json()


async def get_meeting_token(api_key: str, room_name: str, owner: bool = True) -> str:
    """
    Generate a meeting token for joining a Daily.co room.

    Args:
        api_key: Daily.co API key
        room_name: Name of the room
        owner: Whether the token should have owner privileges

    Returns:
        Meeting token string
    """
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {
            "properties": {
                "room_name": room_name,
                "is_owner": owner,
            }
        }

        async with session.post(
            "https://api.daily.co/v1/meeting-tokens",
            headers=headers,
            json=data,
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to create token: {error_text}")
            result = await response.json()
            return result["token"]


async def main(args: argparse.Namespace):
    """
    Main entrypoint for the Pipecat + Daily.co BitHuman agent.

    This sets up the complete pipeline:
    1. Daily.co transport for WebRTC communication
    2. Deepgram for speech-to-text
    3. OpenAI GPT-4 for conversation
    4. BitHuman avatar for video/audio output
    """
    logger.info("Starting BitHuman Pipecat Daily agent")

    # Validate environment variables
    model_path = os.getenv("BITHUMAN_MODEL_PATH") or args.model_path
    api_secret = os.getenv("BITHUMAN_API_SECRET") or args.api_secret
    daily_api_key = os.getenv("DAILY_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not model_path:
        raise ValueError(
            "BITHUMAN_MODEL_PATH environment variable or --model-path argument is required"
        )
    if not api_secret:
        raise ValueError(
            "BITHUMAN_API_SECRET environment variable or --api-secret argument is required"
        )
    if not daily_api_key:
        raise ValueError("DAILY_API_KEY environment variable is required")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    # Get or create Daily room
    room_url = args.room_url
    if not room_url:
        logger.info("Creating new Daily.co room...")
        room_info = await create_daily_room(daily_api_key)
        room_url = room_info["url"]
        logger.info(f"Created room: {room_url}")

    # Extract room name from URL
    room_name = room_url.split("/")[-1]

    # Generate meeting token
    token = await get_meeting_token(daily_api_key, room_name)
    logger.info(f"Generated meeting token for room: {room_name}")

    # Configure Daily transport with default video size
    # Note: We'll update this after BitHuman runtime initializes with actual frame size
    transport = DailyTransport(
        room_url=room_url,
        token=token,
        bot_name="BitHuman Avatar",
        params=DailyParams(
            audio_in_enabled=True,  # Enable audio input for STT
            audio_in_sample_rate=16000,  # Match STT expected sample rate
            audio_out_enabled=True,
            audio_out_sample_rate=16000,
            video_out_enabled=True,
            video_out_width=512,  # Default, will be updated if needed
            video_out_height=512,  # Default, will be updated if needed
            video_out_fps=25,
            transcription_enabled=False,  # Using OpenAI STT instead
        ),
    )
    logger.info("✅ Daily transport configured with audio input enabled")

    # Configure Deepgram STT for real-time speech-to-text
    # SOLUTION: Use Deepgram STT instead of OpenAI STT because:
    # 1. Deepgram supports true streaming audio processing
    # 2. Deepgram properly handles UserAudioRawFrame frames
    # 3. Deepgram provides better real-time performance
    #
    # Get your Deepgram API key from https://console.deepgram.com
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_api_key:
        raise ValueError("DEEPGRAM_API_KEY environment variable is required for STT")

    # Configure Deepgram STT with streaming support
    stt = DeepgramSTTService(
        api_key=deepgram_api_key,
        model="nova-2",  # Use Deepgram's latest model for best accuracy
        language="en",  # Set language code (e.g., "en", "zh", "multi" for multilingual)
    )
    logger.info("✅ Deepgram STT service configured (supports streaming audio)")
    logger.info("🔍 STT will convert user AudioRawFrame → TranscriptionFrame → LLM")

    # Configure OpenAI LLM - using gpt-4o-mini for faster, real-time responses
    llm = OpenAILLMService(api_key=openai_api_key, model="gpt-4o-mini")
    logger.info("✅ OpenAI LLM (gpt-4o-mini) service configured")

    # Configure OpenAI TTS (required to convert LLM text to audio for BitHuman)
    # CRITICAL: OpenAI TTS only supports 24000Hz, so we must use default sample rate
    # We'll resample from 24kHz to 16kHz in BitHumanAvatarProcessor for BitHuman compatibility
    tts = OpenAITTSService(
        api_key=openai_api_key,
        voice="alloy",
        # Do NOT set sample_rate - OpenAI TTS only supports 24000Hz
        # We'll resample in BitHumanAvatarProcessor._push_audio_to_runtime()
    )
    logger.info(
        "✅ OpenAI TTS service configured (will output 24kHz, resample to 16kHz for BitHuman)"
    )

    # Configure LLM context with system prompt
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful and engaging AI assistant with a visual avatar. "
                "Respond naturally and conversationally. Keep responses concise but friendly. "
                "Be warm and welcoming. Adapt your tone to match the conversation context."
            ),
        }
    ]
    context = OpenAILLMContext(messages=messages)
    context_aggregator = llm.create_context_aggregator(context)

    # Configure BitHuman Avatar Processor
    logger.info("🎭 Initializing BitHuman Avatar Processor...")
    bithuman_avatar = BitHumanAvatarProcessor(
        model_path=model_path,
        api_secret=api_secret,
        video_fps=25,
    )
    logger.info("✅ BitHuman Avatar Processor initialized")

    # Get actual frame size from BitHuman runtime (after initialization)
    # We need to wait a bit for the runtime to initialize
    await asyncio.sleep(0.5)  # Give runtime time to initialize
    actual_frame_size = bithuman_avatar.frame_size
    logger.info(f"📐 BitHuman actual frame size: {actual_frame_size}")

    # Build the pipeline
    # Input: User audio from Daily → Deepgram STT → LLM → TTS → BitHuman → Output video/audio to Daily
    # CRITICAL: BitHumanAvatarProcessor must be BEFORE transport.output() to intercept TTS audio
    # CRITICAL: context_aggregator.assistant() should be AFTER transport.output() to avoid blocking
    pipeline = Pipeline(
        [
            transport.input(),  # Receive audio from Daily
            stt,  # Deepgram STT (streaming, real-time)
            context_aggregator.user(),  # Add user message to context
            llm,  # GPT-4o-mini (fast, real-time)
            tts,  # OpenAI TTS (convert text to audio) - outputs TTSAudioRawFrame
            bithuman_avatar,  # Render avatar video/audio with lip-sync - MUST intercept TTSAudioRawFrame
            transport.output(),  # Send video/audio to Daily
            context_aggregator.assistant(),  # Add assistant message to context (after output to avoid blocking)
        ]
    )
    logger.info(
        "✅ Pipeline configured: Daily → Deepgram STT → GPT-4o-mini → TTS → BitHuman → Daily"
    )

    # Create pipeline task
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
        ),
    )

    # Event handlers
    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        """Handle when the first participant joins the room."""
        logger.info(f"First participant joined: {participant['id']}")
        # Send a greeting
        await task.queue_frames(
            [
                TextFrame(
                    text="Hello! I'm your AI assistant with a visual avatar. How can I help you today?"
                )
            ]
        )

    @transport.event_handler("on_participant_joined")
    async def on_participant_joined(transport, participant):
        """Handle when any participant joins."""
        logger.info(f"Participant joined: {participant['id']}")

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        """Handle when a participant leaves."""
        logger.info(f"Participant left: {participant['id']}, reason: {reason}")

    @transport.event_handler("on_call_state_updated")
    async def on_call_state_updated(transport, state):
        """Handle call state changes."""
        logger.info(f"Call state updated: {state}")
        if state == "left":
            await task.queue_frame(EndFrame())

    # Run the pipeline
    runner = PipelineRunner()

    logger.info(f"Agent ready! Join the room at: {room_url}")
    logger.info("Waiting for participants...")

    await runner.run(task)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="BitHuman Avatar Agent with Pipecat and Daily.co"
    )
    parser.add_argument(
        "--room-url",
        type=str,
        help="Daily.co room URL (optional, creates new room if not provided)",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        help="Path to BitHuman model file (.imx format)",
    )
    parser.add_argument(
        "--api-secret",
        type=str,
        help="BitHuman API secret",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    asyncio.run(main(args))
