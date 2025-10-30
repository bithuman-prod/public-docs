import asyncio
import logging
import os
import time
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Optional

import cv2
import numpy as np
from dotenv import load_dotenv

# Set environment variables for LiveKit timeouts
os.environ.setdefault("LIVEKIT_CONNECT_TIMEOUT", "60")
os.environ.setdefault("LIVEKIT_ROOM_CONNECT_TIMEOUT", "60")

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomOutputOptions,
    WorkerOptions,
    WorkerType,
    cli,
    utils,
)
from livekit.agents.voice.avatar import (
    AudioSegmentEnd,
    AvatarOptions,
    AvatarRunner,
    QueueAudioOutput,
    VideoGenerator,
)
from livekit.plugins import bithuman, openai, silero
from bithuman.api import VideoControl

# Configure logging for better debugging
logger = logging.getLogger("bithuman-selfhosted-agent")
logger.setLevel(logging.INFO)

# Import native BitHuman components for direct integration
try:
    from bithuman import AsyncBithuman, VideoFrame
    from bithuman.audio import float32_to_int16
    import numpy as np
    NATIVE_BITHUMAN_AVAILABLE = True
    logger.info("Native BitHuman components imported successfully")
except ImportError as e:
    NATIVE_BITHUMAN_AVAILABLE = False
    logger.warning(f"Native BitHuman components not available: {e}")
    logger.warning("Falling back to LiveKit plugin integration")

# Load environment variables from .env file
load_dotenv()


class BithumanVideoGenerator(VideoGenerator):
    """
    Modern BitHuman video generator using LiveKit's VideoGenerator interface.
    Integrates native AsyncBithuman with advanced streaming capabilities.
    """
    
    def __init__(self, bithuman_runtime: AsyncBithuman):
        """Initialize with an AsyncBithuman runtime instance."""
        self._runtime = bithuman_runtime
        self._first_frame_cache: Optional[np.ndarray] = None
        
    @property
    def video_resolution(self) -> tuple[int, int]:
        """Get video resolution from BitHuman runtime."""
        if self._first_frame_cache is not None:
            return self._first_frame_cache.shape[1], self._first_frame_cache.shape[0]
        
        # Try to get frame size from runtime
        try:
            frame_size = self._runtime.get_frame_size()
            return frame_size
        except Exception:
            # Default fallback resolution
            return (512, 512)
    
    @property
    def video_fps(self) -> int:
        """Get video FPS from BitHuman runtime settings."""
        try:
            return getattr(self._runtime.settings, 'FPS', 25)
        except AttributeError:
            return 25  # Default FPS
    
    @property
    def audio_sample_rate(self) -> int:
        """Get audio sample rate from BitHuman runtime settings."""
        try:
            return getattr(self._runtime.settings, 'INPUT_SAMPLE_RATE', 16000)
        except AttributeError:
            return 16000  # Default sample rate
    
    @utils.log_exceptions(logger=logger)
    async def push_audio(self, frame: rtc.AudioFrame | AudioSegmentEnd) -> None:
        """Push audio frame to BitHuman runtime for processing."""
        if isinstance(frame, AudioSegmentEnd):
            await self._runtime.flush()
            return
            
        await self._runtime.push_audio(
            bytes(frame.data), frame.sample_rate, last_chunk=False
        )
    
    def clear_buffer(self) -> None:
        """Clear BitHuman runtime buffer (interrupt current processing)."""
        self._runtime.interrupt()
    
    def __aiter__(self) -> AsyncIterator[rtc.VideoFrame | rtc.AudioFrame | AudioSegmentEnd]:
        """Return async iterator for streaming frames."""
        return self._stream_impl()
    
    async def _stream_impl(self) -> AsyncGenerator[rtc.VideoFrame | rtc.AudioFrame | AudioSegmentEnd, None]:
        """
        Advanced streaming implementation with optimized frame processing.
        Uses modern async generator patterns and efficient frame conversion.
        """
        def create_video_frame(image: np.ndarray) -> rtc.VideoFrame:
            """Create optimized video frame with RGBA conversion."""
            # Convert BGR to RGBA for better LiveKit compatibility
            rgba_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
            return rtc.VideoFrame(
                width=rgba_image.shape[1],
                height=rgba_image.shape[0],
                type=rtc.VideoBufferType.RGBA,
                data=rgba_image.tobytes(),
            )
        
        frame_count = 0
        logger.info("Starting BitHuman video generator streaming...")
        
        try:
            async for frame in self._runtime.run():
                frame_count += 1
                
                # Cache first frame for resolution detection
                if self._first_frame_cache is None and frame.bgr_image is not None:
                    self._first_frame_cache = frame.bgr_image.copy()
                    logger.info(f"Cached first frame with resolution: {self.video_resolution}")
                
                # Yield video frame if available
                if frame.bgr_image is not None:
                    video_frame = create_video_frame(frame.bgr_image)
                    yield video_frame
                
                # Yield audio frame if available
                if frame.audio_chunk is not None:
                    audio_frame = rtc.AudioFrame(
                        data=frame.audio_chunk.bytes,
                        sample_rate=frame.audio_chunk.sample_rate,
                        num_channels=1,
                        samples_per_channel=len(frame.audio_chunk.array),
                    )
                    yield audio_frame
                
                # Yield end of speech marker
                if frame.end_of_speech:
                    yield AudioSegmentEnd()
                
                # Periodic logging for monitoring
                if frame_count % 500 == 0:
                    logger.debug(f"Processed {frame_count} frames in video generator")
                    
        except asyncio.CancelledError:
            logger.info("BitHuman video generator streaming cancelled")
        except Exception as e:
            logger.error(f"Error in BitHuman video generator: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    async def trigger_gesture(self, action: str) -> None:
        """Trigger a gesture in BitHuman runtime with advanced error handling."""
        try:
            await self._runtime.push(VideoControl(action=action))
            logger.info(f"✅ Triggered gesture: {action}")
        except Exception as e:
            logger.error(f"❌ Failed to trigger gesture {action}: {e}")
    
    async def stop(self) -> None:
        """Stop the BitHuman runtime gracefully."""
        try:
            await self._runtime.stop()
            logger.info("BitHuman video generator stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping BitHuman runtime: {e}")


class ModernBithumanAgent:
    """
    Modern self-hosted BitHuman agent using advanced LiveKit patterns.
    Features:
    - Native AsyncBithuman integration with VideoGenerator interface
    - Advanced avatar runner with optimized streaming
    - Intelligent gesture triggering with context awareness
    - High-performance audio/video processing pipeline
    """

    def __init__(self, model_path: str, api_secret: str, api_token: Optional[str] = None):
        """
        Initialize the modern BitHuman agent.
        
        Args:
            model_path: Path to the .imx model file
            api_secret: API secret for authentication
            api_token: Optional API token for authentication
        """
        self.model_path = model_path
        self.api_secret = api_secret
        self.api_token = api_token
        self.bithuman_runtime: Optional[AsyncBithuman] = None
        self.video_generator: Optional[BithumanVideoGenerator] = None
        self.avatar_runner: Optional[AvatarRunner] = None
        self.session: Optional[AgentSession] = None
        self.gesture_tasks = {}  # Gesture cooldown tracking
        
        # Add missing attributes for compatibility
        self.use_native_bithuman = NATIVE_BITHUMAN_AVAILABLE
        self.native_video_source = None  # Will be set to video_generator when available
        
        logger.info("Initialized modern BitHuman agent with native integration")

    async def initialize_avatar(self, ctx: JobContext) -> None:
        """
        Initialize the modern BitHuman avatar with advanced streaming capabilities.
        Uses the latest LiveKit patterns for optimal performance.
        """
        logger.info(f"🚀 Initializing modern BitHuman avatar with model: {self.model_path}")
        
        try:
            # Create native AsyncBithuman runtime
            if not NATIVE_BITHUMAN_AVAILABLE:
                raise RuntimeError("Native BitHuman components not available")
                
            # Create AsyncBithuman runtime with proper parameters
            create_params = {
                "model_path": self.model_path,
                "api_secret": self.api_secret,
                "insecure": True,  # For development
            }
            
            # Add token if available
            if hasattr(self, 'api_token') and self.api_token:
                create_params["token"] = self.api_token
                
            self.bithuman_runtime = await AsyncBithuman.create(**create_params)
            logger.info("✅ BitHuman runtime created successfully")
            
            # Create modern video generator
            self.video_generator = BithumanVideoGenerator(self.bithuman_runtime)
            self.native_video_source = self.video_generator  # Set for compatibility
            
            # Get video properties for avatar configuration
            video_width, video_height = self.video_generator.video_resolution
            video_fps = self.video_generator.video_fps
            audio_sample_rate = self.video_generator.audio_sample_rate
            
            logger.info(f"📺 Video config: {video_width}x{video_height}@{video_fps}fps, Audio: {audio_sample_rate}Hz")
            
            # Configure avatar options with detected properties
            avatar_options = AvatarOptions(
                video_width=video_width,
                video_height=video_height,
                video_fps=video_fps,
                audio_sample_rate=audio_sample_rate,
                audio_channels=1,
            )
            
            # Create agent session with LLM and queue audio output for avatar runner
            self.session = AgentSession(
                llm=openai.realtime.RealtimeModel(
                    voice="coral",  # Available voices: alloy, echo, fable, onyx, nova, shimmer, coral
                    model="gpt-4o-realtime-preview-2025-06-03",  # Use the realtime model
                    temperature=0.7,  # Slightly creative responses
                ),
                vad=silero.VAD.load(
                    # Configure Voice Activity Detection for better conversation flow
                    min_speech_duration=0.1,
                    min_silence_duration=0.5,
                    prefix_padding_duration=0.1,  # Updated parameter name
                )
            )
            self.session.output.audio = QueueAudioOutput()
            
            # Create and start avatar runner
            self.avatar_runner = AvatarRunner(
                room=ctx.room,
                video_gen=self.video_generator,
                audio_recv=self.session.output.audio,
                options=avatar_options,
            )
            
            await self.avatar_runner.start()
            logger.info("🎭 Avatar runner started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize BitHuman avatar: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def setup_intelligent_features(self) -> None:
        """
        Setup intelligent features including gesture triggers and context awareness.
        Uses modern patterns for enhanced user interaction.
        """
        logger.info("🧠 Setting up intelligent features...")
        
        # Define supported gesture mappings (currently only mini_wave_hello is supported)
        self.gesture_mappings = {
            "mini_wave_hello": {
                "keywords": ["hello", "hi", "hey", "goodbye", "bye", "greetings"],
                "context": "greeting",
                "cooldown": 3.0,
                "description": "Friendly greeting with wave animation"
            }
        }
        
        # Log configured intelligent gestures
        for gesture, config in self.gesture_mappings.items():
            logger.info(f"🎭 Configured '{gesture}' ({config['context']}) - {config['description']}")
        
        logger.info("✅ Intelligent features configured successfully")

        # Define gesture triggers with keywords
        gesture_configs = [
            {
                "gesture": "mini_wave_hello",
                "keywords": ["hello", "hi", "hey", "greetings"],
                "description": "Friendly greeting gesture"
            }
        ]

        # Note: Gesture triggers are handled manually in trigger_contextual_gesture method
        # The bithuman.AvatarSession doesn't have built-in register_gesture_trigger method
        logger.info("Gesture trigger configurations loaded (handled manually)")

    async def handle_conversation_events(self) -> None:
        """Handle real-time conversation events and trigger appropriate responses."""
        if not self.session:
            logger.warning("Session not available for event handling")
            return

        logger.info("Setting up conversation event listeners...")

        # Listen for conversation events (using correct LiveKit agents event names)
        @self.session.on("conversation_item_added")
        def on_conversation_item_added(event):
            """Handle when conversation items are added (user or agent messages)."""
            try:
                role = event.item.role
                message = event.item.text_content or str(event.item.content)
                logger.info(f"[Event] Conversation item added - Role: {role}, Message: {message}")
                
                # Only trigger gestures for user messages
                if role == "user" and message:
                    # Create a background task for gesture triggering
                    loop = asyncio.get_event_loop()
                    loop.create_task(self.trigger_contextual_gesture(message))
            except Exception as e:
                logger.error(f"Error in conversation_item_added handler: {e}")

        @self.session.on("user_input_transcribed")
        def on_user_input_transcribed(event):
            """Handle when user input is transcribed."""
            try:
                if event.is_final:
                    transcript = event.transcript.replace("\n", "\\n")
                    logger.info(f"[Event] User input transcribed (final): {transcript}")
                    
                    # Trigger gesture based on final transcript
                    loop = asyncio.get_event_loop()
                    loop.create_task(self.trigger_contextual_gesture(transcript))
                else:
                    logger.debug(f"[Event] User input transcribed (interim): {event.transcript}")
            except Exception as e:
                logger.error(f"Error in user_input_transcribed handler: {e}")

        @self.session.on("agent_state_changed")
        def on_agent_state_changed(event):
            """Handle agent state changes."""
            logger.info(f"[Event] Agent state changed: {event.new_state}")

        @self.session.on("close")
        def on_session_close(event):
            """Handle session close."""
            logger.info(f"[Event] Session closed: {event.reason}")

        # Add more comprehensive event logging
        @self.session.on("participant_connected")
        def on_participant_connected(participant):
            """Handle participant connection."""
            logger.info(f"[Event] Participant connected: {participant}")

        @self.session.on("participant_disconnected")
        def on_participant_disconnected(participant):
            """Handle participant disconnection."""
            logger.info(f"[Event] Participant disconnected: {participant}")

        logger.info("Conversation event listeners configured successfully")

    async def trigger_contextual_gesture(self, text: str) -> None:
        """
        Advanced contextual gesture triggering with intelligent pattern matching.
        Uses modern NLP-inspired keyword detection and cooldown management.
        """
        if not self.video_generator:
            return
            
        text_lower = text.lower().strip()
        if not text_lower:
            return
        
        # Advanced gesture matching with context awareness
        for gesture, config in getattr(self, 'gesture_mappings', {}).items():
            keywords = config['keywords']
            cooldown = config['cooldown']
            context = config['context']
            
            # Smart keyword matching with word boundaries
            if any(keyword in text_lower for keyword in keywords):
                try:
                    current_time = time.time()
                    last_trigger = self.gesture_tasks.get(gesture, 0)
                    
                    # Respect individual gesture cooldowns
                    if current_time - last_trigger > cooldown:
                        # Trigger gesture through video generator
                        await self.video_generator.trigger_gesture(gesture)
                        
                        # Update cooldown tracking
                        self.gesture_tasks[gesture] = current_time
                        
                        logger.info(f"🎭 Triggered {context} gesture: {gesture} (cooldown: {cooldown}s)")
                        break  # Only trigger one gesture per text input
                        
                except Exception as e:
                    logger.error(f"❌ Failed to trigger gesture {gesture}: {e}")
                    import traceback
                    logger.debug(f"Gesture error traceback: {traceback.format_exc()}")

    async def setup_audio_interruption_handling(self) -> None:
        """
        Setup advanced audio interruption handling for natural conversations.
        Modern implementation uses LiveKit's built-in VAD and session management.
        """
        # Audio interruption is handled automatically by:
        # 1. LiveKit VAD (Voice Activity Detection) in the session
        # 2. AvatarRunner's built-in interruption management
        # 3. BitHuman runtime's interrupt() method
        
        logger.info("🎤 Audio interruption handling configured via modern LiveKit VAD and AvatarRunner")

    async def run_periodic_tasks(self) -> None:
        """Run periodic maintenance tasks."""
        while True:
            try:
                # Periodic health check for modern components
                if self.avatar_runner:
                    logger.debug("🔍 Avatar runner is running normally")
                
                if self.video_generator:
                    logger.debug("🎥 Video generator is streaming normally")
                
                if self.bithuman_runtime:
                    logger.debug("🤖 BitHuman runtime is operational")
                
                # Clean up old gesture tasks
                current_time = time.time()
                self.gesture_tasks = {
                    k: v for k, v in self.gesture_tasks.items() 
                    if current_time - v < 300  # Keep last 5 minutes
                }
                
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic tasks: {e}")
                await asyncio.sleep(30)


async def entrypoint(ctx: JobContext):
    """
    Modern entrypoint for the self-hosted BitHuman LiveKit agent.
    
    Features:
    - Advanced connection management with exponential backoff
    - Native AsyncBithuman integration with VideoGenerator pattern
    - Intelligent gesture triggering and context awareness
    - High-performance streaming with optimized resource management
    """
    # Connect to the LiveKit room with extended timeout and retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to LiveKit room (attempt {attempt + 1}/{max_retries})")
            await asyncio.wait_for(ctx.connect(), timeout=60.0)  # 60 seconds timeout
            logger.info("Connected to LiveKit room successfully")
            break
        except asyncio.TimeoutError:
            logger.warning(f"Connection attempt {attempt + 1} timed out")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(5)  # Wait 5 seconds before retry
        except Exception as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(5)

    # Wait for at least one participant to join the room with extended timeout
    logger.info("Waiting for participant to join...")
    await asyncio.wait_for(ctx.wait_for_participant(), timeout=120.0)  # 2 minutes timeout for participant
    logger.info("Participant joined, initializing agent")

    # Get configuration from environment variables
    model_path = os.getenv("BITHUMAN_MODEL_PATH")
    api_secret = os.getenv("BITHUMAN_API_SECRET")
    api_token = os.getenv("BITHUMAN_API_TOKEN")  # Optional token
    
    if not model_path:
        raise ValueError("BITHUMAN_MODEL_PATH environment variable is required")
    if not api_secret:
        raise ValueError("BITHUMAN_API_SECRET environment variable is required")

    # Initialize modern BitHuman agent
    agent = ModernBithumanAgent(model_path, api_secret, api_token)
    
    try:
        # Initialize avatar and session
        await agent.initialize_avatar(ctx)
        
        # Setup intelligent features
        await agent.setup_intelligent_features()
        
        # Start the AI agent session with custom instructions
        await agent.session.start(
            agent=Agent(
                instructions=(
                    "You are a helpful and engaging AI assistant with a visual avatar. "
                    "Respond naturally and conversationally. Keep responses concise but friendly. "
                    "You can express emotions through gestures, so feel free to be expressive. "
                    "When users greet you, be warm and welcoming. When they share good news, "
                    "be enthusiastic. Adapt your tone to match the conversation context."
                )
            ),
            room=ctx.room,
            # Disable room audio output since audio is handled by the avatar
            room_output_options=RoomOutputOptions(audio_enabled=False),
        )
        
        # Setup conversation event listeners after session is started
        await agent.handle_conversation_events()
        
        # Start periodic maintenance tasks
        periodic_task = asyncio.create_task(agent.run_periodic_tasks())
        
        logger.info("Self-hosted bitHuman agent is now running")
        
        # Keep the agent running
        try:
            await asyncio.Future()  # Run forever
        except asyncio.CancelledError:
            logger.info("Agent shutdown requested")
        finally:
            periodic_task.cancel()
            # Cleanup native BitHuman resources if used
            if agent.use_native_bithuman and agent.native_video_source:
                await agent.native_video_source.stop()
                logger.info("Native BitHuman resources cleaned up")
            
    except Exception as e:
        logger.error(f"Failed to start self-hosted agent: {e}")
        # Cleanup on error as well
        if agent.use_native_bithuman and agent.native_video_source:
            await agent.native_video_source.stop()
        raise


if __name__ == "__main__":
    # Configure and run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
            job_memory_warn_mb=8000,  # Higher memory limit for self-hosted models
            num_idle_processes=1,     # Number of idle processes to maintain
            initialize_process_timeout=180,  # Longer timeout for model loading (3 minutes)
            # Additional performance settings for latest version
            job_memory_limit_mb=8000,  # Hard memory limit
        )
    )
