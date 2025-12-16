"""
Gemini Live Avatar - Self-Hosted Avatar with Gemini Live API

This example demonstrates a conversational AI avatar using Gemini Live API
(gemini-2.0-flash-exp) with bitHuman avatar rendering.

Features:
- Gemini Live API (gemini-2.0-flash-exp) for STT/TTS/LLM
- Local mode (default): microphone input, OpenCV video display, speaker output
- Server mode (optional): WebSocket-based remote audio/video streaming
- bitHuman AsyncBithuman for avatar rendering with lip-sync
- Dynamics/gesture support with keyword detection
- Support for audio file input

Requirements:
- Python 3.10+
- google-genai SDK
- bithuman SDK
- sounddevice for audio I/O
- opencv-python for video display
- websockets (optional, for server mode)

Usage:
    # Local mode with microphone (default)
    python main.py --model /path/to/avatar.imx --api-secret YOUR_API_SECRET

    # Local mode with audio file
    python main.py --model /path/to/avatar.imx --api-secret YOUR_API_SECRET --audio-file /path/to/audio.wav

    # Server mode with WebSocket streaming
    python main.py --model /path/to/avatar.imx --api-secret YOUR_API_SECRET --server --port 8765
"""

import argparse
import asyncio
import os
import sys
import threading
import time
from typing import Optional

import cv2
import numpy as np
from dotenv import load_dotenv

# Import dynamics module
from dynamics import DynamicsHandler
from loguru import logger

from bithuman import AsyncBithuman, VideoFrame
from bithuman.audio import float32_to_int16, load_audio
from bithuman.utils import FPSController

# Import WebSocket server for remote streaming
try:
    from websocket_server import (
        AudioChunk,
        MediaWebSocketServer,
        WebSocketAudioInput,
        WebSocketAudioOutput,
        WebSocketVideoOutput,
    )

    WEBSOCKET_AVAILABLE = True
except ImportError:
    logger.warning("WebSocket server module not available")
    WEBSOCKET_AVAILABLE = False

try:
    import sounddevice as sd
except ImportError:
    logger.warning("sounddevice is not installed. Local audio I/O will not work.")
    sd = None

try:
    from google import genai
    from google.genai import types
except ImportError:
    logger.error("google-genai is not installed. Please run: pip install google-genai")
    sys.exit(1)

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")

# Gemini Live API constants
GEMINI_INPUT_SAMPLE_RATE = 16000
GEMINI_OUTPUT_SAMPLE_RATE = 24000
GEMINI_CHANNELS = 1


def list_audio_devices():
    """List all available audio input/output devices."""
    if sd is None:
        print("sounddevice is not installed")
        return

    print("\n=== Available Audio Devices ===\n")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        device_type = []
        if device["max_input_channels"] > 0:
            device_type.append("INPUT")
        if device["max_output_channels"] > 0:
            device_type.append("OUTPUT")
        type_str = "/".join(device_type)
        default_marker = ""
        if i == sd.default.device[0]:
            default_marker = " [DEFAULT INPUT]"
        if i == sd.default.device[1]:
            default_marker += " [DEFAULT OUTPUT]"
        print(f"  {i}: {device['name']} ({type_str}){default_marker}")

    print(f"\nDefault input device: {sd.default.device[0]}")
    print(f"Default output device: {sd.default.device[1]}")
    print("\nUse --audio-device <id> to select a specific input device")


class AudioPlayer:
    """Audio player that uses a buffer and callback for smooth playback."""

    def __init__(self, sample_rate: int = 16000, block_per_second: int = 25):
        self.sample_rate = sample_rate
        self.output_buf = bytearray()
        self.output_lock = threading.Lock()
        self.stream = None
        self.blocksize = self.sample_rate // block_per_second

    def is_started(self) -> bool:
        """Check if the audio output stream is started."""
        return self.stream is not None

    def start(self) -> bool:
        """Start the audio output stream."""
        if sd is None:
            return False
        self.stream = sd.OutputStream(
            callback=self.output_callback,
            dtype="int16",
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.blocksize,
        )
        self.stream.start()
        return True

    def stop(self):
        """Stop the audio output stream."""
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def clear(self):
        """Clear the audio buffer."""
        with self.output_lock:
            self.output_buf.clear()

    def add_audio(self, audio_data):
        """Add audio data to the buffer."""
        # Convert float32 to int16 if needed
        if isinstance(audio_data, np.ndarray) and audio_data.dtype == np.float32:
            audio_data = (audio_data * 32768.0).astype(np.int16)

        with self.output_lock:
            if isinstance(audio_data, bytes) or isinstance(audio_data, bytearray):
                self.output_buf.extend(audio_data)
            else:
                self.output_buf.extend(audio_data.tobytes())

    def output_callback(self, outdata, frames, time_info, status):
        """Callback for the sounddevice output stream."""
        with self.output_lock:
            bytes_needed = frames * 2  # 2 bytes per sample for int16
            if len(self.output_buf) < bytes_needed:
                # Not enough data, fill what we can and zero the rest
                available_bytes = len(self.output_buf)
                outdata[: available_bytes // 2, 0] = np.frombuffer(
                    self.output_buf, dtype=np.int16, count=available_bytes // 2
                )
                outdata[available_bytes // 2 :, 0] = 0
                del self.output_buf[:available_bytes]
            else:
                # We have enough data
                chunk = self.output_buf[:bytes_needed]
                outdata[:, 0] = np.frombuffer(chunk, dtype=np.int16, count=frames)
                del self.output_buf[:bytes_needed]


class AudioRecorder:
    """Audio recorder that captures microphone input via sounddevice."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration_ms: int = 100,
        device: Optional[int] = None,  # None = default device
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        self.device = device
        self.input_buf = asyncio.Queue()
        self.stream = None
        self._running = False

    def is_started(self) -> bool:
        """Check if the audio input stream is started."""
        return self.stream is not None and self._running

    def start(self) -> bool:
        """Start the audio input stream."""
        if sd is None:
            return False

        self._running = True
        self.stream = sd.InputStream(
            callback=self.input_callback,
            dtype="int16",
            channels=self.channels,
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            device=self.device,  # None = default input device
        )
        self.stream.start()
        if self.device is not None:
            logger.info(f"Using audio input device: {self.device}")
        return True

    def stop(self):
        """Stop the audio input stream."""
        self._running = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def input_callback(self, indata, frames, time_info, status):
        """Callback for the sounddevice input stream."""
        if self._running:
            # Convert to bytes and put in queue
            audio_bytes = indata.copy().tobytes()
            try:
                self.input_buf.put_nowait(audio_bytes)
            except asyncio.QueueFull:
                pass  # Drop frames if queue is full

    async def get_audio_chunk(self, timeout: float = 1.0) -> Optional[bytes]:
        """Get the next audio chunk from the buffer."""
        try:
            return await asyncio.wait_for(self.input_buf.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None


class VideoPlayer:
    """Video player for displaying frames using OpenCV."""

    def __init__(self, window_size: tuple, window_name: str = "Gemini Live Avatar"):
        self.window_name = window_name
        self.start_time = None
        self.window_size = window_size
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, window_size[0], window_size[1])

    def start(self):
        """Start the video player."""
        self.start_time = time.time()

    def stop(self):
        """Stop the video player."""
        cv2.destroyAllWindows()

    def display_frame(
        self,
        frame: VideoFrame,
        fps: float = 0.0,
        exp_time: float = 0.0,
        gemini_status: str = "",
    ) -> int:
        """Display a frame and return the key pressed."""
        if not frame.has_image:
            return -1

        # Render the frame with overlays
        image = self.render_image(frame, fps, exp_time, gemini_status)

        # Display the frame
        cv2.imshow(self.window_name, image)
        key = cv2.waitKey(1) & 0xFF

        return key

    def render_image(
        self,
        frame: VideoFrame,
        fps: float = 0.0,
        exp_time: float = 0.0,
        gemini_status: str = "",
    ) -> np.ndarray:
        """Render a frame with additional information overlays."""
        image = frame.bgr_image.copy()

        # Add FPS information
        cv2.putText(
            image,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        # Add elapsed time
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            cv2.putText(
                image,
                f"Time: {elapsed:.1f}s",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        # Add expiration time if available
        if exp_time > 0:
            exp_in_seconds = exp_time - time.time()
            cv2.putText(
                image,
                f"Exp: {exp_in_seconds:.1f}s",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        # Add Gemini status
        if gemini_status:
            cv2.putText(
                image,
                f"Gemini: {gemini_status}",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

        # Add key hints at the bottom
        h = image.shape[0]
        cv2.putText(
            image,
            "Keys: [1] Play audio | [2] Interrupt | [q] Quit",
            (10, h - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        return image


class GeminiLiveSession:
    """
    Gemini Live API session manager using WebSocket.

    Handles bidirectional audio streaming with Gemini Live API
    for STT/TTS/LLM capabilities.

    Authentication: Get API key from https://aistudio.google.com/apikey
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-exp",
        voice: str = "Kore",
        instructions: str = "",
    ):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.model = model
        self.voice = voice
        self.instructions = instructions
        self.client = None
        self._session_context = None
        self._active_session = None
        self._running = False
        self._audio_output_queue = asyncio.Queue()
        self._transcription_queue = asyncio.Queue()
        self._status = "disconnected"

    @property
    def status(self) -> str:
        return self._status

    async def connect(self) -> bool:
        """Connect to Gemini Live API via WebSocket."""
        try:
            self._status = "connecting"
            logger.info(f"Connecting to Gemini Live API with model: {self.model}")

            if not self.api_key:
                raise ValueError(
                    "GOOGLE_API_KEY is required. Get one from https://aistudio.google.com/apikey"
                )

            self.client = genai.Client(api_key=self.api_key)

            # Configure the live session
            config = types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self.voice,
                        )
                    )
                ),
                # Enable input audio transcription for dynamics/keyword detection
                input_audio_transcription=types.AudioTranscriptionConfig(),
            )

            # Add system instructions if provided
            if self.instructions:
                config.system_instruction = types.Content(
                    parts=[types.Part(text=self.instructions)]
                )

            # Create the session context manager
            self._session_context = self.client.aio.live.connect(
                model=self.model,
                config=config,
            )

            # Enter the session context and keep it open
            self._active_session = await self._session_context.__aenter__()

            self._running = True
            self._status = "connected"
            logger.info("Connected to Gemini Live API successfully")
            return True

        except Exception as e:
            self._status = "error"
            logger.error(f"Failed to connect to Gemini Live API: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Gemini Live API."""
        self._running = False
        self._status = "disconnecting"

        if self._session_context:
            try:
                await self._session_context.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
            self._session_context = None
            self._active_session = None

        self._status = "disconnected"
        logger.info("Disconnected from Gemini Live API")

    async def send_audio(self, audio_bytes: bytes, sample_rate: int = 16000):
        """Send audio data to Gemini Live API."""
        if not self._running or not self._active_session:
            return

        try:
            # Send audio as realtime input
            await self._active_session.send(
                input=types.LiveClientRealtimeInput(
                    media_chunks=[
                        types.Blob(
                            mime_type=f"audio/pcm;rate={sample_rate}",
                            data=audio_bytes,
                        )
                    ]
                ),
                end_of_turn=False,
            )
        except Exception as e:
            # If connection is closed, stop trying to send
            if "close frame" in str(e).lower() or "closed" in str(e).lower():
                logger.warning("Gemini connection closed, stopping audio send")
                self._running = False
                self._status = "disconnected"
            else:
                logger.error(f"Error sending audio to Gemini: {e}")

    async def send_text(self, text: str):
        """Send text message to Gemini Live API."""
        if not self._running or not self._active_session:
            return

        try:
            await self._active_session.send(
                input=types.LiveClientContent(
                    turns=[
                        types.Content(
                            role="user",
                            parts=[types.Part(text=text)],
                        )
                    ],
                    turn_complete=True,
                ),
                end_of_turn=True,
            )
            logger.info(f"Sent text to Gemini: {text}")
        except Exception as e:
            logger.error(f"Error sending text to Gemini: {e}")

    async def receive_responses(self):
        """
        Receive responses from Gemini Live API.

        Yields:
            Tuple of (audio_bytes, transcription) where:
            - audio_bytes: Raw PCM audio data (24kHz, 16-bit, mono)
            - transcription: Text transcription if available
        """
        if not self._running or not self._active_session:
            return

        try:
            self._status = "listening"

            async for response in self._active_session.receive():
                if not self._running:
                    break

                # Handle server content (audio/text responses)
                if response.server_content:
                    server_content = response.server_content

                    # Check for model turn (audio response)
                    if server_content.model_turn:
                        self._status = "speaking"
                        for part in server_content.model_turn.parts or []:
                            # Handle audio data
                            if part.inline_data:
                                audio_data = part.inline_data.data
                                if isinstance(audio_data, bytes):
                                    yield (audio_data, None)

                            # Handle text
                            if part.text:
                                yield (None, part.text)

                    # Check for turn complete
                    if server_content.turn_complete:
                        self._status = "listening"
                        yield (None, "[TURN_COMPLETE]")

                    # Check for input transcription
                    if hasattr(server_content, "input_transcription"):
                        if server_content.input_transcription:
                            transcript = server_content.input_transcription.text
                            if transcript:
                                yield (None, f"[USER]: {transcript}")

        except asyncio.CancelledError:
            logger.info("Receive task cancelled")
        except Exception as e:
            # If connection is closed, stop trying to receive
            if "close frame" in str(e).lower() or "closed" in str(e).lower():
                logger.warning("Gemini connection closed, stopping receive")
                self._running = False
                self._status = "disconnected"
            else:
                self._status = "error"
                logger.error(f"Error receiving from Gemini: {e}")

    async def interrupt(self):
        """Interrupt the current response."""
        if not self._running or not self._active_session:
            return

        try:
            # Send empty input to interrupt
            await self._active_session.send(
                input=types.LiveClientRealtimeInput(media_chunks=[]),
                end_of_turn=True,
            )
            logger.info("Sent interrupt to Gemini")
        except Exception as e:
            logger.error(f"Error sending interrupt: {e}")


class GeminiLiveAvatarApp:
    """
    Main application that integrates Gemini Live API with bitHuman Avatar.

    Features:
    - Local mode: microphone input, OpenCV video display, speaker output
    - Server mode: WebSocket-based audio input, video/audio streaming output
    - Gemini Live API for STT/TTS/LLM
    - Dynamics/gesture support based on transcription keywords
    """

    def __init__(
        self,
        model_path: str,
        api_secret: str,
        gemini_api_key: Optional[str] = None,
        agent_id: Optional[str] = None,
        audio_file: Optional[str] = None,
        gemini_model: str = "gemini-2.0-flash-exp",
        gemini_voice: str = "Kore",
        instructions: str = "",
        audio_device: Optional[int] = None,
        # Server mode options
        server_mode: bool = False,
        server_host: str = "0.0.0.0",
        server_port: int = 8765,
        enable_local_display: bool = True,
    ):
        self.model_path = model_path
        self.api_secret = api_secret
        self.gemini_api_key = gemini_api_key or os.environ.get("GOOGLE_API_KEY", "")
        self.agent_id = agent_id
        self.audio_file = audio_file
        self.gemini_model = gemini_model
        self.gemini_voice = gemini_voice
        self.instructions = instructions
        self.audio_device = audio_device

        # Server mode settings
        self.server_mode = server_mode
        self.server_host = server_host
        self.server_port = server_port
        self.enable_local_display = enable_local_display

        # Components
        self.bithuman_runtime: Optional[AsyncBithuman] = None
        self.gemini_session: Optional[GeminiLiveSession] = None
        self.audio_player: Optional[AudioPlayer] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.video_player: Optional[VideoPlayer] = None
        self.dynamics_handler: Optional[DynamicsHandler] = None

        # WebSocket server components (server mode)
        self.ws_server: Optional[MediaWebSocketServer] = None
        self.ws_audio_input: Optional[WebSocketAudioInput] = None
        self.ws_video_output: Optional[WebSocketVideoOutput] = None
        self.ws_audio_output: Optional[WebSocketAudioOutput] = None

        # State
        self._running = False
        self._current_transcription = ""

    async def initialize(self):
        """Initialize all components."""
        logger.info("Initializing Gemini Live Avatar application...")
        mode_str = "Server" if self.server_mode else "Local"
        logger.info(f"Running in {mode_str} mode")

        # Initialize bitHuman runtime
        logger.info(f"Loading bitHuman model: {self.model_path}")
        self.bithuman_runtime = await AsyncBithuman.create(
            model_path=self.model_path,
            api_secret=self.api_secret,
            insecure=True,
        )
        frame_size = self.bithuman_runtime.get_frame_size()
        logger.info(f"bitHuman model loaded, frame size: {frame_size}")

        # Initialize WebSocket server (server mode)
        if self.server_mode:
            if not WEBSOCKET_AVAILABLE:
                raise RuntimeError(
                    "WebSocket server not available. Install websockets package."
                )

            logger.info(
                f"Starting WebSocket server on {self.server_host}:{self.server_port}"
            )
            self.ws_server = MediaWebSocketServer(
                host=self.server_host,
                port=self.server_port,
            )

            # Setup WebSocket audio input
            self.ws_audio_input = WebSocketAudioInput(
                sample_rate=GEMINI_INPUT_SAMPLE_RATE
            )
            self.ws_audio_input.start()

            # Setup WebSocket callbacks
            self.ws_server.set_audio_callback(self._on_ws_audio_input)
            self.ws_server.set_text_callback(self._on_ws_text_input)
            self.ws_server.set_control_callback(self._on_ws_control)

            # Setup WebSocket video/audio output
            self.ws_video_output = WebSocketVideoOutput(self.ws_server, fps=25.0)
            self.ws_audio_output = WebSocketAudioOutput(
                self.ws_server, sample_rate=16000
            )

            await self.ws_server.start()
            logger.info("WebSocket server started")

        # Initialize local audio player (for both modes)
        if not self.server_mode or self.enable_local_display:
            self.audio_player = AudioPlayer(sample_rate=16000)
            self.audio_player.start()

        # Initialize local audio recorder (local mode without audio file)
        if not self.server_mode and not self.audio_file:
            self.audio_recorder = AudioRecorder(
                sample_rate=GEMINI_INPUT_SAMPLE_RATE,
                device=self.audio_device,
            )
            self.audio_recorder.start()
            logger.info("Audio recorder started (microphone mode)")

        # Initialize local video player
        if not self.server_mode or self.enable_local_display:
            self.video_player = VideoPlayer(window_size=frame_size)
            self.video_player.start()

        # Initialize Gemini Live session
        if self.gemini_api_key:
            default_instructions = (
                "You are a helpful and engaging AI assistant with a visual avatar. "
                "Respond naturally and conversationally. Keep responses concise but friendly. "
                "You can express emotions, so feel free to be expressive."
            )
            self.gemini_session = GeminiLiveSession(
                api_key=self.gemini_api_key,
                model=self.gemini_model,
                voice=self.gemini_voice,
                instructions=self.instructions or default_instructions,
            )
            await self.gemini_session.connect()

        # Initialize dynamics handler
        self.dynamics_handler = DynamicsHandler(
            bithuman_runtime=self.bithuman_runtime,
            agent_id=self.agent_id,
            api_secret=self.api_secret,
        )
        await self.dynamics_handler.initialize()

        self._running = True
        logger.info("All components initialized successfully")

    async def _on_ws_audio_input(self, chunk: AudioChunk, client_id: str) -> None:
        """Handle audio input from WebSocket client."""
        if self.ws_audio_input:
            await self.ws_audio_input.push_audio(chunk, client_id)

    async def _on_ws_text_input(self, text: str, client_id: str) -> None:
        """Handle text input from WebSocket client."""
        logger.info(f"Text from {client_id}: {text}")
        # Send to Gemini if connected
        if self.gemini_session:
            await self.gemini_session.send_text(text)
        # Check for dynamics keywords
        if self.dynamics_handler:
            await self.dynamics_handler.check_and_trigger(text)

    async def _on_ws_control(self, command: str, params: dict, client_id: str) -> None:
        """Handle control command from WebSocket client."""
        logger.info(f"Control from {client_id}: {command} {params}")

        if command == "interrupt":
            # Interrupt current response
            self.bithuman_runtime.interrupt()
            if self.audio_player:
                self.audio_player.clear()
            if self.gemini_session:
                await self.gemini_session.interrupt()

        elif command == "gesture":
            # Trigger gesture
            gesture = params.get("gesture", "")
            if gesture and self.dynamics_handler:
                await self.dynamics_handler.trigger_gesture(gesture)

        elif command == "audio_file":
            # Play audio file
            audio_path = params.get("path", "")
            if audio_path:
                asyncio.create_task(self.push_audio_file(audio_path))

    async def cleanup(self):
        """Clean up all resources."""
        logger.info("Cleaning up resources...")
        self._running = False

        # Stop WebSocket server
        if self.ws_server:
            await self.ws_server.stop()
        if self.ws_audio_input:
            self.ws_audio_input.stop()

        # Stop local components
        if self.audio_recorder:
            self.audio_recorder.stop()
        if self.audio_player:
            self.audio_player.stop()
        if self.video_player:
            self.video_player.stop()
        if self.gemini_session:
            await self.gemini_session.disconnect()
        if self.bithuman_runtime:
            await self.bithuman_runtime.stop()

        logger.info("Cleanup completed")

    async def push_audio_file(self, audio_file: str, delay: float = 0.0):
        """Push audio from a file to bitHuman runtime."""
        logger.info(f"Pushing audio file: {audio_file}")

        await asyncio.sleep(delay)

        audio_np, sr = load_audio(audio_file)
        audio_np = float32_to_int16(audio_np)

        # Simulate streaming audio bytes
        chunk_size = sr // 100  # 10ms chunks
        for i in range(0, len(audio_np), chunk_size):
            if not self._running:
                break
            chunk = audio_np[i : i + chunk_size]
            await self.bithuman_runtime.push_audio(
                chunk.tobytes(), sr, last_chunk=False
            )
            await asyncio.sleep(0.008)  # Small delay to simulate streaming

        # Flush to mark end of speech
        await self.bithuman_runtime.flush()
        logger.info("Audio file push completed")

    async def run_microphone_to_gemini(self):
        """Stream microphone audio to Gemini Live API."""
        if not self.audio_recorder or not self.gemini_session:
            return

        logger.info("Starting microphone to Gemini streaming...")

        while self._running:
            # Check if Gemini session is still connected
            if not self.gemini_session or self.gemini_session.status not in [
                "connected",
                "listening",
                "speaking",
            ]:
                logger.warning(
                    "Gemini session disconnected, stopping microphone stream"
                )
                break

            try:
                audio_chunk = await self.audio_recorder.get_audio_chunk(timeout=0.5)
                if audio_chunk:
                    await self.gemini_session.send_audio(
                        audio_chunk, GEMINI_INPUT_SAMPLE_RATE
                    )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in microphone streaming: {e}")
                # If connection error, wait a bit before retrying
                if "close frame" in str(e).lower() or "closed" in str(e).lower():
                    break
                await asyncio.sleep(0.1)

    async def run_gemini_to_bithuman(self):
        """Stream Gemini audio output to bitHuman runtime."""
        if not self.gemini_session:
            return

        logger.info("Starting Gemini to bitHuman streaming...")

        # Buffer for resampling (24kHz -> 16kHz)
        resample_ratio = GEMINI_INPUT_SAMPLE_RATE / GEMINI_OUTPUT_SAMPLE_RATE

        # Keep running until explicitly stopped
        while self._running:
            # Check if Gemini session is still connected
            if not self.gemini_session or self.gemini_session.status not in [
                "connected",
                "listening",
                "speaking",
            ]:
                logger.warning("Gemini session disconnected, stopping receive stream")
                break

            try:
                async for (
                    audio_data,
                    transcription,
                ) in self.gemini_session.receive_responses():
                    if not self._running:
                        break

                    # Handle audio data
                    if audio_data:
                        # Convert 24kHz Gemini output to 16kHz for bitHuman
                        audio_np = np.frombuffer(audio_data, dtype=np.int16)

                        # Simple resampling (for production, use proper resampler)
                        if resample_ratio != 1.0:
                            # Linear interpolation resampling
                            old_indices = np.arange(len(audio_np))
                            new_length = int(len(audio_np) * resample_ratio)
                            new_indices = np.linspace(0, len(audio_np) - 1, new_length)
                            audio_np = np.interp(
                                new_indices, old_indices, audio_np
                            ).astype(np.int16)

                        # Push to bitHuman runtime
                        await self.bithuman_runtime.push_audio(
                            audio_np.tobytes(),
                            GEMINI_INPUT_SAMPLE_RATE,
                            last_chunk=False,
                        )

                    # Handle transcription
                    if transcription:
                        if transcription == "[TURN_COMPLETE]":
                            # End of Gemini response, flush bitHuman
                            await self.bithuman_runtime.flush()
                        elif transcription.startswith("[USER]:"):
                            # User transcription - check for dynamics keywords
                            user_text = transcription[7:].strip()
                            self._current_transcription = user_text
                            logger.info(f"User said: {user_text}")
                            await self.dynamics_handler.check_and_trigger(user_text)
                        else:
                            # Agent text response
                            logger.debug(f"Agent: {transcription}")

                # If receive_responses ended without error, keep listening
                if self._running:
                    logger.debug("Gemini receive loop ended, continuing to listen...")
                    await asyncio.sleep(0.1)
                else:
                    break

            except asyncio.CancelledError:
                break
            except Exception as e:
                # If connection closed, stop the loop
                if "close frame" in str(e).lower() or "closed" in str(e).lower():
                    logger.warning("Gemini connection closed, stopping receive loop")
                    break
                logger.error(f"Error in Gemini streaming: {e}")
                if self._running:
                    await asyncio.sleep(1)  # Wait before retry
                else:
                    break

    async def run_websocket_to_gemini(self):
        """Stream WebSocket audio input to Gemini Live API (server mode)."""
        if not self.ws_audio_input or not self.gemini_session:
            return

        logger.info("Starting WebSocket to Gemini streaming...")

        async for chunk in self.ws_audio_input:
            if not self._running:
                break
            try:
                await self.gemini_session.send_audio(chunk.data, chunk.sample_rate)
            except Exception as e:
                logger.error(f"Error sending WebSocket audio to Gemini: {e}")

    async def run_bithuman_rendering(self):
        """Run the bitHuman avatar rendering loop."""
        fps_controller = FPSController(target_fps=25)

        await self.bithuman_runtime.start()
        logger.info("bitHuman rendering started")

        push_audio_task = None
        if self.audio_file:
            push_audio_task = asyncio.create_task(
                self.push_audio_file(self.audio_file, delay=1.0)
            )

        try:
            async for frame in self.bithuman_runtime.run():
                if not self._running:
                    break

                sleep_time = fps_controller.wait_next_frame(sleep=False)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

                # Get status for display
                gemini_status = (
                    self.gemini_session.status if self.gemini_session else "N/A"
                )

                # Broadcast to WebSocket clients (server mode)
                if self.server_mode and frame.has_image:
                    if self.ws_video_output:
                        await self.ws_video_output.push_frame(
                            frame.bgr_image, fps=fps_controller.average_fps
                        )
                    if self.ws_audio_output and frame.audio_chunk:
                        await self.ws_audio_output.push_audio(frame.audio_chunk.array)

                # Local display (local mode or server mode with local display enabled)
                key = -1
                if self.video_player:
                    exp_time = self.bithuman_runtime.get_expiration_time()
                    key = self.video_player.display_frame(
                        frame,
                        fps=fps_controller.average_fps,
                        exp_time=exp_time,
                        gemini_status=gemini_status,
                    )

                # Add audio to local player buffer
                if (
                    frame.audio_chunk
                    and self.audio_player
                    and self.audio_player.is_started()
                ):
                    self.audio_player.add_audio(frame.audio_chunk.array)

                # Handle key presses (local mode)
                if key == ord("1") and self.audio_file:
                    # Replay audio file
                    if push_audio_task and not push_audio_task.done():
                        push_audio_task.cancel()
                    push_audio_task = asyncio.create_task(
                        self.push_audio_file(self.audio_file)
                    )
                elif key == ord("2"):
                    # Interrupt
                    logger.info("Interrupting...")
                    if push_audio_task and not push_audio_task.done():
                        push_audio_task.cancel()
                    self.bithuman_runtime.interrupt()
                    if self.audio_player:
                        self.audio_player.clear()
                    if self.gemini_session:
                        await self.gemini_session.interrupt()
                elif key == ord("3"):
                    # Trigger wave gesture
                    await self.dynamics_handler.trigger_gesture("mini_wave_hello")
                elif key == ord("q"):
                    logger.info("Quit requested")
                    self._running = False
                    break

                fps_controller.update()

        except asyncio.CancelledError:
            logger.info("Rendering task cancelled")
        finally:
            if push_audio_task and not push_audio_task.done():
                push_audio_task.cancel()

    async def run(self):
        """Run the main application loop."""
        await self.initialize()

        try:
            tasks = [
                asyncio.create_task(self.run_bithuman_rendering()),
            ]

            # Add Gemini tasks if connected
            if self.gemini_session and self.gemini_session.status == "connected":
                tasks.append(asyncio.create_task(self.run_gemini_to_bithuman()))

                # Audio input source depends on mode
                if self.server_mode and self.ws_audio_input:
                    # Server mode: WebSocket audio input
                    tasks.append(asyncio.create_task(self.run_websocket_to_gemini()))
                elif self.audio_recorder:
                    # Local mode: microphone audio input
                    tasks.append(asyncio.create_task(self.run_microphone_to_gemini()))

            # In server mode, keep running until explicitly stopped
            if self.server_mode:
                logger.info(
                    f"Server running at ws://{self.server_host}:{self.server_port}"
                )
                logger.info("Press Ctrl+C to stop")

            # Wait for any task to complete (usually rendering)
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()

        except asyncio.CancelledError:
            logger.info("Application cancelled")
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            await self.cleanup()


async def main(args: argparse.Namespace):
    """Main entry point."""
    app = GeminiLiveAvatarApp(
        model_path=args.model,
        api_secret=args.api_secret,
        gemini_api_key=args.gemini_api_key,
        agent_id=args.agent_id,
        audio_file=args.audio_file,
        gemini_model=args.gemini_model,
        gemini_voice=args.gemini_voice,
        instructions=args.instructions,
        audio_device=args.audio_device,
        # Server mode options
        server_mode=args.server,
        server_host=args.host,
        server_port=args.port,
        enable_local_display=args.local_display,
    )

    await app.run()


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Gemini Live Avatar - Self-hosted avatar with Gemini Live API"
    )

    # bitHuman configuration
    parser.add_argument(
        "--model",
        type=str,
        default=os.environ.get("BITHUMAN_MODEL_PATH"),
        help="Path to bitHuman avatar model file (.imx)",
    )
    parser.add_argument(
        "--api-secret",
        type=str,
        default=os.environ.get("BITHUMAN_API_SECRET"),
        help="bitHuman API Secret for authentication",
    )
    parser.add_argument(
        "--agent-id",
        type=str,
        default=os.environ.get("BITHUMAN_AGENT_ID"),
        help="bitHuman Agent ID for dynamics (optional)",
    )

    # Gemini configuration
    parser.add_argument(
        "--gemini-api-key",
        type=str,
        default=os.environ.get("GOOGLE_API_KEY"),
        help="Google AI API Key (from https://aistudio.google.com/apikey)",
    )
    parser.add_argument(
        "--gemini-model",
        type=str,
        default="gemini-2.0-flash-exp",
        help="Gemini model to use (default: gemini-2.0-flash-exp)",
    )
    parser.add_argument(
        "--gemini-voice",
        type=str,
        default="Kore",
        choices=["Puck", "Charon", "Kore", "Fenrir", "Aoede"],
        help="Gemini voice to use",
    )
    parser.add_argument(
        "--instructions",
        type=str,
        default="",
        help="System instructions for Gemini",
    )

    # Audio input
    parser.add_argument(
        "--audio-file",
        type=str,
        default=os.environ.get("BITHUMAN_AUDIO_PATH"),
        help="Path to audio file to play (optional, uses microphone if not provided)",
    )
    parser.add_argument(
        "--list-audio-devices",
        action="store_true",
        help="List available audio devices and exit",
    )
    parser.add_argument(
        "--audio-device",
        type=int,
        default=None,
        help="Audio input device ID (use --list-audio-devices to see available devices)",
    )

    # Server mode options
    parser.add_argument(
        "--server",
        action="store_true",
        help="Enable WebSocket server mode for remote streaming",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server host address (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Server port (default: 8765)",
    )
    parser.add_argument(
        "--local-display",
        action="store_true",
        help="Enable local video display even in server mode",
    )

    args = parser.parse_args()

    # Handle --list-audio-devices
    if args.list_audio_devices:
        list_audio_devices()
        sys.exit(0)

    # Validate required arguments
    if not args.model:
        logger.error("BITHUMAN_MODEL_PATH is required")
        sys.exit(1)
    if not args.api_secret:
        logger.error("BITHUMAN_API_SECRET is required")
        sys.exit(1)

    # Validate Gemini API key
    if not args.gemini_api_key:
        logger.error(
            "GOOGLE_API_KEY is required. Get one from https://aistudio.google.com/apikey"
        )
        sys.exit(1)

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
