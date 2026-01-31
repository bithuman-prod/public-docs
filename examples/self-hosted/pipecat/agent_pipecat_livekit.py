"""
Pure Pipecat Agent with LiveKit Transport

This example uses pure Pipecat framework with LiveKitTransport (no LiveKit Agents framework).
It demonstrates how to build a BitHuman avatar agent using only Pipecat's architecture.

Features:
- Pure Pipecat Pipeline architecture (no LiveKit Agents framework)
- LiveKitTransport for WebRTC communication (Pipecat's built-in transport)
- BitHuman AsyncBithuman runtime for avatar rendering with lip-sync
- OpenAI GPT-4o-mini for fast, real-time LLM conversation
- Deepgram STT for real-time speech-to-text (supports streaming audio)
- OpenAI TTS for text-to-speech
- Custom FrameProcessor for BitHuman video/audio generation

Architecture:
    User Audio (LiveKit) → LiveKitTransport → Pipecat Pipeline → BitHuman Runtime
                                                                           ↓
    User Display ← LiveKitTransport ← Video/Audio Frames ← BitHuman Avatar ←────┘

Key Differences from LiveKit Agents version:
- Uses Pipecat's LiveKitTransport directly (no JobContext)
- No LiveKit Agents framework dependency
- Simpler code, but requires manual room management
- NOT automatically registered as Agent (connects as regular participant)

Performance Note:
- Avatar worker model connection and loading typically takes approximately 20 seconds
  on first initialization.

Requirements:
- Python 3.10+
- BitHuman model file (.imx format)
- LiveKit server URL and API credentials
- OpenAI API key (for LLM and TTS)
- Deepgram API key (for STT - get from https://console.deepgram.com)

Usage:
    # Set environment variables
    export BITHUMAN_MODEL_PATH="path/to/model.imx"
    export BITHUMAN_API_SECRET="your_bithuman_api_secret"
    export LIVEKIT_URL="wss://your-project.livekit.cloud"
    export LIVEKIT_API_KEY="your_livekit_api_key"
    export LIVEKIT_API_SECRET="your_livekit_api_secret"
    export OPENAI_API_KEY="your_openai_api_key"
    export DEEPGRAM_API_KEY="your_deepgram_api_key"

    # Run the agent
    python agent_pipecat_livekit.py --room-name my-room
"""

import argparse
import asyncio
import logging
import os
import time
from typing import Optional

import cv2
import numpy as np
from dotenv import load_dotenv

# LiveKit API for token generation
from livekit import api

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
    TextFrame,
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
from pipecat.transports.livekit.transport import LiveKitParams, LiveKitTransport
from scipy import signal

# BitHuman imports
from bithuman import AsyncBithuman

# Configure logging
logger = logging.getLogger("bithuman-pipecat-livekit-agent")
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
        self._flush_task: Optional[asyncio.Task] = None
        self._tts_active: bool = False
        self._last_audio_frame_time: Optional[float] = None
        self._flush_delay: float = flush_delay

        # Audio duration tracking for precise completion detection
        self._input_audio_duration: float = 0.0
        self._output_audio_duration: float = 0.0
        self._tts_segment_start_time: Optional[float] = None

    async def _initialize_runtime(self):
        """Initialize the BitHuman runtime."""
        if self._runtime:
            logger.info("✅ BitHuman runtime already initialized")
            return

        logger.info(
            f"🚀 Initializing BitHuman Avatar Processor with model: {self._model_path}"
        )
        logger.info("⏳ Creating AsyncBithuman runtime (this may take 20+ seconds)...")

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

            # Start the runtime
            logger.info("⏳ Starting BitHuman runtime...")
            await self._runtime.start()
            logger.info("✅ BitHuman runtime started successfully")

            # Start the render loop
            self._running = True
            self._render_task = asyncio.create_task(self._render_loop())
            logger.info("🎬 BitHuman render loop started")

            # Push initial silence to start video generation
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
            await self._runtime.flush()
            await self._runtime.stop()
            logger.info("BitHuman runtime flushed and stopped")

        await super().stop(frame)

    async def cancel(self, frame: CancelFrame):
        """Handle cancellation (interruption)."""
        if self._runtime:
            self._runtime.interrupt()
            await self._runtime.flush()
            logger.debug("BitHuman runtime interrupted and flushed")
        await super().cancel(frame)

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process incoming frames."""
        # Handle TTS audio frames first
        if isinstance(frame, TTSAudioRawFrame):
            if not self._runtime:
                logger.warning("⚠️  Attempting lazy initialization as fallback...")
                try:
                    await self._initialize_runtime()
                except Exception as e:
                    logger.error(f"❌ Failed to initialize runtime: {e}")
                    if not self._runtime:
                        return

            if self._runtime:
                # Track audio duration
                audio_bytes = (
                    frame.audio
                    if isinstance(frame.audio, bytes)
                    else frame.audio.tobytes()
                    if hasattr(frame.audio, "tobytes")
                    else b""
                )
                if audio_bytes:
                    audio_duration = len(audio_bytes) / 2 / frame.sample_rate
                    self._input_audio_duration += audio_duration

                # Update last audio frame time
                self._last_audio_frame_time = time.time()

                # Cancel any pending flush task
                if self._flush_task and not self._flush_task.done():
                    self._flush_task.cancel()
                    try:
                        await self._flush_task
                    except asyncio.CancelledError:
                        pass

                # Push audio to runtime
                await self._push_audio_to_runtime(frame, last_chunk=False)
            return  # Don't pass TTS audio downstream

        # Handle StartFrame
        if isinstance(frame, StartFrame):
            await super().process_frame(frame, direction)
            await self.start(frame)
            await self.push_frame(frame, direction)
            return

        # User audio frames should be processed by STT upstream
        if isinstance(frame, AudioRawFrame):
            return  # Ignore user audio frames

        # Call super().process_frame() for other frame types
        await super().process_frame(frame, direction)

        # Handle TTS lifecycle events
        if isinstance(frame, TTSStartedFrame):
            logger.info("🎤 TTS started")
            self._tts_active = True
            if self._flush_task and not self._flush_task.done():
                self._flush_task.cancel()
                try:
                    await self._flush_task
                except asyncio.CancelledError:
                    pass
            self._last_audio_frame_time = None
            self._input_audio_duration = 0.0
            self._output_audio_duration = 0.0
            self._tts_segment_start_time = time.time()
            await self.push_frame(frame, direction)
            return

        elif isinstance(frame, TTSStoppedFrame):
            logger.info("🎤 TTS stopped")
            self._tts_active = False

            if self._runtime:
                logger.info(
                    f"📊 TTSStoppedFrame received. Input audio duration: {self._input_audio_duration:.3f}s, "
                    f"Output audio duration: {self._output_audio_duration:.3f}s"
                )

                if self._flush_task and not self._flush_task.done():
                    self._flush_task.cancel()
                    try:
                        await self._flush_task
                    except asyncio.CancelledError:
                        pass

                async def _smart_flush():
                    try:
                        # Push empty chunk with last_chunk=True to force AudioStreamBatcher flush
                        logger.info(
                            "📦 Pushing empty audio chunk with last_chunk=True to force AudioStreamBatcher flush"
                        )
                        await self._runtime.push_audio(
                            b"", sample_rate=self._sample_rate, last_chunk=True
                        )
                        await asyncio.sleep(0.05)  # Give runtime a moment to process

                        # Wait for output to catch up with input
                        max_wait_time = self._flush_delay * 2
                        check_interval = 0.05
                        wait_start = time.time()

                        while time.time() - wait_start < max_wait_time:
                            if self._input_audio_duration > 0:
                                completion_ratio = (
                                    self._output_audio_duration
                                    / self._input_audio_duration
                                )
                                if completion_ratio >= 0.95:
                                    logger.info(
                                        f"✅ Audio processing complete: {completion_ratio*100:.1f}%"
                                    )
                                    break
                            await asyncio.sleep(check_interval)

                        logger.info(
                            "🔚 Calling runtime.flush() to signal end of speech"
                        )
                        await self._runtime.flush()
                        logger.info("✅ Flush signal sent to runtime")
                    except asyncio.CancelledError:
                        logger.debug("🔄 Smart flush cancelled")
                    except Exception as e:
                        logger.error(f"❌ Error in smart flush: {e}")
                        import traceback

                        logger.error(traceback.format_exc())

                self._flush_task = asyncio.create_task(_smart_flush())
            await self.push_frame(frame, direction)
            return

        # Handle interruptions
        elif isinstance(frame, (StartInterruptionFrame, InterruptionFrame)):
            if self._runtime:
                self._runtime.interrupt()
                await self._runtime.flush()
                logger.info("⏸️  BitHuman runtime interrupted and flushed")
            await self.push_frame(frame, direction)

        # Pass through other frames
        else:
            await self.push_frame(frame, direction)

    async def _push_audio_to_runtime(
        self, frame: TTSAudioRawFrame, last_chunk: bool = False
    ):
        """Push TTS audio to BitHuman runtime for processing."""
        if not self._runtime:
            logger.warning("⚠️  BitHuman runtime not available, cannot push audio")
            return

        try:
            audio_data = frame.audio
            input_sample_rate = frame.sample_rate
            target_sample_rate = self._sample_rate

            # Resample if sample rates don't match
            if input_sample_rate != target_sample_rate:
                if isinstance(audio_data, bytes):
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

                # Resample
                num_samples = int(
                    len(audio_float) * target_sample_rate / input_sample_rate
                )
                audio_resampled = signal.resample(audio_float, num_samples)
                audio_array = (np.clip(audio_resampled, -1.0, 1.0) * 32767).astype(
                    np.int16
                )
                audio_bytes = audio_array.tobytes()
            else:
                # No resampling needed
                if isinstance(audio_data, np.ndarray):
                    if audio_data.dtype != np.int16:
                        if audio_data.dtype == np.float32:
                            audio_data = np.clip(audio_data, -1.0, 1.0)
                            audio_data = (audio_data * 32767).astype(np.int16)
                        else:
                            audio_data = audio_data.astype(np.int16)
                    audio_bytes = audio_data.tobytes()
                elif isinstance(audio_data, memoryview):
                    audio_bytes = bytes(audio_data)
                elif isinstance(audio_data, bytes):
                    audio_bytes = audio_data
                else:
                    logger.warning(f"⚠️  Unknown audio data type: {type(audio_data)}")
                    return

            if not audio_bytes or len(audio_bytes) < 2:
                logger.warning(
                    f"⚠️  Skipping empty or too small audio chunk: {len(audio_bytes)} bytes"
                )
                return

            # Push audio to runtime
            await self._runtime.push_audio(
                audio_bytes,
                sample_rate=target_sample_rate,
                last_chunk=last_chunk,
            )

        except Exception as e:
            logger.error(f"❌ Error pushing audio to BitHuman runtime: {e}")
            import traceback

            logger.error(traceback.format_exc())

    async def _render_loop(self):
        """Background task that renders BitHuman frames and pushes them downstream."""
        logger.info("🎬 BitHuman render loop starting...")
        frame_count = 0
        video_frame_count = 0
        audio_frame_count = 0

        try:
            if not self._runtime:
                logger.error("❌ Runtime not initialized, cannot start render loop")
                return

            async for bh_frame in self._runtime.run():
                if not self._running:
                    break

                frame_count += 1

                # Push video frame if available
                if bh_frame.bgr_image is not None:
                    rgb_image = cv2.cvtColor(bh_frame.bgr_image, cv2.COLOR_BGR2RGB)
                    if not rgb_image.flags["C_CONTIGUOUS"]:
                        rgb_image = np.ascontiguousarray(rgb_image)

                    video_frame = OutputImageRawFrame(
                        image=rgb_image,
                        size=(rgb_image.shape[1], rgb_image.shape[0]),
                        format="RGB",
                    )
                    await self.push_frame(video_frame)
                    video_frame_count += 1

                # Push audio frame if available
                if bh_frame.audio_chunk is not None:
                    audio_bytes = bh_frame.audio_chunk.bytes
                    if not isinstance(audio_bytes, bytes):
                        audio_array = bh_frame.audio_chunk.array
                        if audio_array.dtype != np.int16:
                            audio_array = (audio_array * 32767).astype(np.int16)
                        audio_bytes = audio_array.tobytes()

                    # Track output audio duration
                    audio_duration = bh_frame.audio_chunk.duration
                    self._output_audio_duration += audio_duration

                    audio_frame = OutputAudioRawFrame(
                        audio=audio_bytes,
                        sample_rate=bh_frame.audio_chunk.sample_rate,
                        num_channels=1,
                    )
                    await self.push_frame(audio_frame)
                    audio_frame_count += 1

                # Log progress periodically
                if frame_count % 250 == 0:
                    logger.info(
                        f"📊 Rendered {frame_count} frames (video: {video_frame_count}, audio: {audio_frame_count})"
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

    @property
    def frame_size(self) -> tuple[int, int]:
        """Get the video frame size."""
        return self._frame_size

    @property
    def sample_rate(self) -> int:
        """Get the audio sample rate."""
        return self._sample_rate


def generate_livekit_token(
    api_key: str, api_secret: str, room_name: str, identity: str = "bithuman-agent"
) -> str:
    """
    Generate a LiveKit access token for joining a room.

    Args:
        api_key: LiveKit API key
        api_secret: LiveKit API secret
        room_name: Name of the room to join
        identity: Participant identity (default: "bithuman-agent")

    Returns:
        JWT token string
    """
    token = (
        api.AccessToken(api_key=api_key, api_secret=api_secret)
        .with_identity(identity)
        .with_name("BitHuman Avatar")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )
    return token


async def main(args: argparse.Namespace):
    """
    Main entrypoint for the pure Pipecat + LiveKit BitHuman agent.

    This sets up the complete pipeline:
    1. LiveKit transport for WebRTC communication
    2. Deepgram for speech-to-text
    3. OpenAI GPT-4 for conversation
    4. BitHuman avatar for video/audio output
    """
    logger.info("Starting BitHuman Pipecat LiveKit agent (Pure Pipecat)")

    # Validate environment variables
    model_path = os.getenv("BITHUMAN_MODEL_PATH") or args.model_path
    api_secret = os.getenv("BITHUMAN_API_SECRET") or args.api_secret
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")

    if not model_path:
        raise ValueError(
            "BITHUMAN_MODEL_PATH environment variable or --model-path argument is required"
        )
    if not api_secret:
        raise ValueError(
            "BITHUMAN_API_SECRET environment variable or --api-secret argument is required"
        )
    if not livekit_url:
        raise ValueError("LIVEKIT_URL environment variable is required")
    if not livekit_api_key:
        raise ValueError("LIVEKIT_API_KEY environment variable is required")
    if not livekit_api_secret:
        raise ValueError("LIVEKIT_API_SECRET environment variable is required")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    if not deepgram_api_key:
        raise ValueError("DEEPGRAM_API_KEY environment variable is required for STT")

    # Get or generate room name
    room_name = args.room_name or f"bithuman-room-{int(time.time())}"
    logger.info(f"Using room: {room_name}")

    # Generate LiveKit token
    token = generate_livekit_token(livekit_api_key, livekit_api_secret, room_name)
    logger.info(f"Generated LiveKit token for room: {room_name}")

    # Configure BitHuman Avatar Processor first to get actual frame size
    logger.info("🎭 Initializing BitHuman Avatar Processor...")
    bithuman_avatar = BitHumanAvatarProcessor(
        model_path=model_path,
        api_secret=api_secret,
        video_fps=25,
    )
    logger.info("✅ BitHuman Avatar Processor initialized")

    # Initialize runtime BEFORE configuring transport to get actual frame size
    logger.info("⏳ Initializing BitHuman runtime (this may take 20+ seconds)...")
    await bithuman_avatar._initialize_runtime()
    actual_frame_size = bithuman_avatar.frame_size
    logger.info(f"📐 BitHuman actual frame size: {actual_frame_size}")

    # Configure LiveKit transport with video output enabled
    transport = LiveKitTransport(
        url=livekit_url,
        token=token,
        room_name=room_name,
        params=LiveKitParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            video_out_enabled=True,  # Enable video output
            video_out_width=actual_frame_size[0],  # Use actual frame width
            video_out_height=actual_frame_size[1],  # Use actual frame height
            video_out_fps=25,  # Match BitHuman FPS
        ),
    )
    logger.info("✅ LiveKit transport configured with video output enabled")

    # Configure Deepgram STT
    stt = DeepgramSTTService(
        api_key=deepgram_api_key,
        model="nova-2",
        language="en",
    )
    logger.info("✅ Deepgram STT service configured")

    # Configure OpenAI LLM
    llm = OpenAILLMService(api_key=openai_api_key, model="gpt-4o-mini")
    logger.info("✅ OpenAI LLM (gpt-4o-mini) service configured")

    # Configure OpenAI TTS
    tts = OpenAITTSService(
        api_key=openai_api_key,
        voice="alloy",
    )
    logger.info("✅ OpenAI TTS service configured")

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

    # Build the pipeline
    pipeline = Pipeline(
        [
            transport.input(),  # Receive audio from LiveKit
            stt,  # Deepgram STT
            context_aggregator.user(),  # Add user message to context
            llm,  # GPT-4o-mini
            tts,  # OpenAI TTS
            bithuman_avatar,  # Render avatar video/audio with lip-sync
            transport.output(),  # Send video/audio to LiveKit
            context_aggregator.assistant(),  # Add assistant message to context
        ]
    )
    logger.info("✅ Pipeline configured")

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
    async def on_first_participant_joined(transport, participant_id):
        """Handle when the first participant joins the room."""
        logger.info(f"First participant joined: {participant_id}")
        # Send a greeting
        await task.queue_frames(
            [
                TextFrame(
                    text="Hello! I'm your AI assistant with a visual avatar. How can I help you today?"
                )
            ]
        )

    @transport.event_handler("on_participant_joined")
    async def on_participant_joined(transport, participant_id):
        """Handle when any participant joins."""
        logger.info(f"Participant joined: {participant_id}")

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant_id):
        """Handle when a participant leaves."""
        logger.info(f"Participant left: {participant_id}")

    # Run the pipeline
    runner = PipelineRunner()

    logger.info(f"Agent ready! Room: {room_name}")
    logger.info("Waiting for participants...")

    await runner.run(task)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="BitHuman Avatar Agent with Pure Pipecat and LiveKit"
    )
    parser.add_argument(
        "--room-name",
        type=str,
        help="LiveKit room name (optional, auto-generated if not provided)",
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
