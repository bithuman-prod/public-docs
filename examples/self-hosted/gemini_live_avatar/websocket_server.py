"""
WebSocket Media Server

This module provides WebSocket-based audio/video streaming for remote clients.

Features:
- Accept audio clips from remote clients via WebSocket
- Stream video frames to remote clients
- Stream audio to remote clients
- Support multiple concurrent clients
- JSON protocol for control messages, binary for media data

Protocol:
- Control messages are JSON: {"type": "...", "data": {...}}
- Audio input: {"type": "audio", "sample_rate": 16000, "data": "<base64>"}
- Video output: Binary JPEG frames with header
- Audio output: Binary PCM data with header

Usage:
    server = MediaWebSocketServer(host="0.0.0.0", port=8765)
    server.set_audio_callback(on_audio_received)
    server.set_video_source(video_generator)
    await server.start()
"""

import asyncio
import base64
import json
import struct
import time
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Any, Optional

import cv2
import numpy as np
from loguru import logger

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except ImportError:
    logger.error("websockets is not installed. Please run: pip install websockets")
    websockets = None


# Message types for the WebSocket protocol
class MessageType:
    # Client -> Server
    AUDIO_INPUT = "audio_input"  # Audio data from client
    TEXT_INPUT = "text_input"  # Text message from client
    CONTROL = "control"  # Control commands (interrupt, gesture, etc.)

    # Server -> Client
    VIDEO_FRAME = "video_frame"  # Video frame data
    AUDIO_OUTPUT = "audio_output"  # Audio data to client
    TRANSCRIPTION = "transcription"  # Transcription text
    STATUS = "status"  # Status updates
    ERROR = "error"  # Error messages


@dataclass
class AudioChunk:
    """Audio chunk data structure."""

    data: bytes
    sample_rate: int
    channels: int = 1
    timestamp: float = 0.0


@dataclass
class VideoFrame:
    """Video frame data structure for WebSocket transmission."""

    data: bytes  # JPEG encoded
    width: int
    height: int
    timestamp: float
    fps: float = 0.0


@dataclass
class ClientConnection:
    """Represents a connected client."""

    websocket: WebSocketServerProtocol
    client_id: str
    connected_at: float
    last_activity: float
    subscribed_video: bool = True
    subscribed_audio: bool = True


class MediaWebSocketServer:
    """
    WebSocket server for media streaming.

    Features:
    - Receive audio clips from remote clients
    - Stream video frames to connected clients
    - Stream audio to connected clients
    - Support control messages (interrupt, gestures, etc.)
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8765,
        video_quality: int = 80,  # JPEG quality 0-100
        max_clients: int = 10,
    ):
        self.host = host
        self.port = port
        self.video_quality = video_quality
        self.max_clients = max_clients

        # Connected clients
        self.clients: dict[str, ClientConnection] = {}
        self._client_counter = 0

        # Callbacks
        self._on_audio_input: Optional[Callable[[AudioChunk, str], None]] = None
        self._on_text_input: Optional[Callable[[str, str], None]] = None
        self._on_control: Optional[Callable[[str, Any, str], None]] = None

        # Server state
        self._server = None
        self._running = False

        # Output queues for each client
        self._video_queues: dict[str, asyncio.Queue] = {}
        self._audio_queues: dict[str, asyncio.Queue] = {}

    def set_audio_callback(self, callback: Callable[[AudioChunk, str], None]) -> None:
        """Set callback for received audio input."""
        self._on_audio_input = callback

    def set_text_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set callback for received text input."""
        self._on_text_input = callback

    def set_control_callback(self, callback: Callable[[str, Any, str], None]) -> None:
        """Set callback for control commands."""
        self._on_control = callback

    async def start(self) -> None:
        """Start the WebSocket server."""
        if websockets is None:
            raise RuntimeError("websockets package is not installed")

        self._running = True
        self._server = await websockets.serve(
            self._handle_client,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10,
        )
        logger.info(f"WebSocket server started at ws://{self.host}:{self.port}")

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        # Close all client connections
        for _client_id, client in list(self.clients.items()):
            await client.websocket.close()
        self.clients.clear()
        logger.info("WebSocket server stopped")

    async def broadcast_video_frame(
        self,
        frame_bgr: np.ndarray,
        fps: float = 0.0,
        timestamp: float = 0.0,
    ) -> None:
        """Broadcast video frame to all subscribed clients."""
        if not self.clients:
            return

        # Encode frame as JPEG
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.video_quality]
        _, jpeg_data = cv2.imencode(".jpg", frame_bgr, encode_params)
        jpeg_bytes = jpeg_data.tobytes()

        height, width = frame_bgr.shape[:2]

        # Create video frame message
        video_frame = VideoFrame(
            data=jpeg_bytes,
            width=width,
            height=height,
            timestamp=timestamp or time.time(),
            fps=fps,
        )

        # Send to all subscribed clients
        for client_id, client in list(self.clients.items()):
            if client.subscribed_video:
                try:
                    await self._send_video_frame(client.websocket, video_frame)
                except Exception as e:
                    logger.warning(f"Failed to send video to {client_id}: {e}")

    async def broadcast_audio_chunk(
        self,
        audio_data: bytes | np.ndarray,
        sample_rate: int = 16000,
        timestamp: float = 0.0,
    ) -> None:
        """Broadcast audio chunk to all subscribed clients."""
        if not self.clients:
            return

        # Convert numpy array to bytes if needed
        if isinstance(audio_data, np.ndarray):
            if audio_data.dtype == np.float32:
                audio_data = (audio_data * 32768).astype(np.int16)
            audio_data = audio_data.tobytes()

        audio_chunk = AudioChunk(
            data=audio_data,
            sample_rate=sample_rate,
            timestamp=timestamp or time.time(),
        )

        # Send to all subscribed clients
        for client_id, client in list(self.clients.items()):
            if client.subscribed_audio:
                try:
                    await self._send_audio_chunk(client.websocket, audio_chunk)
                except Exception as e:
                    logger.warning(f"Failed to send audio to {client_id}: {e}")

    async def send_transcription(
        self, text: str, is_final: bool = True, role: str = "assistant"
    ) -> None:
        """Send transcription text to all clients."""
        message = {
            "type": MessageType.TRANSCRIPTION,
            "data": {
                "text": text,
                "is_final": is_final,
                "role": role,
                "timestamp": time.time(),
            },
        }
        await self._broadcast_json(message)

    async def send_status(self, status: str, details: Optional[dict] = None) -> None:
        """Send status update to all clients."""
        message = {
            "type": MessageType.STATUS,
            "data": {
                "status": status,
                "details": details or {},
                "timestamp": time.time(),
            },
        }
        await self._broadcast_json(message)

    async def _handle_client(
        self, websocket: WebSocketServerProtocol, path: str
    ) -> None:
        """Handle a new client connection."""
        # Check max clients
        if len(self.clients) >= self.max_clients:
            await websocket.close(1013, "Maximum clients reached")
            return

        # Register client
        self._client_counter += 1
        client_id = f"client_{self._client_counter}"
        client = ClientConnection(
            websocket=websocket,
            client_id=client_id,
            connected_at=time.time(),
            last_activity=time.time(),
        )
        self.clients[client_id] = client
        self._video_queues[client_id] = asyncio.Queue(maxsize=30)
        self._audio_queues[client_id] = asyncio.Queue(maxsize=100)

        logger.info(f"Client {client_id} connected from {websocket.remote_address}")

        # Send welcome message
        await self._send_json(
            websocket,
            {
                "type": MessageType.STATUS,
                "data": {
                    "status": "connected",
                    "client_id": client_id,
                    "timestamp": time.time(),
                },
            },
        )

        try:
            async for message in websocket:
                client.last_activity = time.time()
                await self._process_message(client_id, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Cleanup
            del self.clients[client_id]
            del self._video_queues[client_id]
            del self._audio_queues[client_id]
            logger.info(f"Client {client_id} cleaned up")

    async def _process_message(self, client_id: str, message: bytes | str) -> None:
        """Process a message from a client."""
        try:
            # Parse JSON message
            if isinstance(message, str):
                data = json.loads(message)
            else:
                # Binary message - could be raw audio
                data = {"type": MessageType.AUDIO_INPUT, "raw_data": message}

            msg_type = data.get("type", "")

            if msg_type == MessageType.AUDIO_INPUT:
                await self._handle_audio_input(client_id, data)
            elif msg_type == MessageType.TEXT_INPUT:
                await self._handle_text_input(client_id, data)
            elif msg_type == MessageType.CONTROL:
                await self._handle_control(client_id, data)
            else:
                logger.warning(f"Unknown message type from {client_id}: {msg_type}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {client_id}: {e}")
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")

    async def _handle_audio_input(self, client_id: str, data: dict) -> None:
        """Handle audio input from client."""
        if "raw_data" in data:
            # Binary audio data
            audio_bytes = data["raw_data"]
            sample_rate = 16000  # Default
        else:
            # Base64 encoded audio
            audio_b64 = data.get("data", "")
            audio_bytes = base64.b64decode(audio_b64)
            sample_rate = data.get("sample_rate", 16000)

        audio_chunk = AudioChunk(
            data=audio_bytes,
            sample_rate=sample_rate,
            channels=data.get("channels", 1),
            timestamp=data.get("timestamp", time.time()),
        )

        if self._on_audio_input:
            try:
                # Call callback (could be sync or async)
                result = self._on_audio_input(audio_chunk, client_id)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in audio callback: {e}")

    async def _handle_text_input(self, client_id: str, data: dict) -> None:
        """Handle text input from client."""
        text = data.get("data", {}).get("text", "")
        if not text:
            return

        if self._on_text_input:
            try:
                result = self._on_text_input(text, client_id)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in text callback: {e}")

    async def _handle_control(self, client_id: str, data: dict) -> None:
        """Handle control command from client."""
        command = data.get("data", {}).get("command", "")
        params = data.get("data", {}).get("params", {})

        # Handle subscription changes
        if command == "subscribe":
            client = self.clients.get(client_id)
            if client:
                client.subscribed_video = params.get("video", True)
                client.subscribed_audio = params.get("audio", True)
                logger.info(
                    f"Client {client_id} subscriptions: "
                    f"video={client.subscribed_video}, audio={client.subscribed_audio}"
                )
            return

        if self._on_control:
            try:
                result = self._on_control(command, params, client_id)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in control callback: {e}")

    async def _send_video_frame(
        self, websocket: WebSocketServerProtocol, frame: VideoFrame
    ) -> None:
        """Send video frame to a client."""
        # Pack header: type(1) + width(2) + height(2) + fps(4) + timestamp(8) + len(4)
        header = struct.pack(
            "!BHHFI",
            0x01,  # Video frame type
            frame.width,
            frame.height,
            frame.fps,
            len(frame.data),
        )
        # Also send timestamp as double
        timestamp_bytes = struct.pack("!d", frame.timestamp)

        await websocket.send(header + timestamp_bytes + frame.data)

    async def _send_audio_chunk(
        self, websocket: WebSocketServerProtocol, chunk: AudioChunk
    ) -> None:
        """Send audio chunk to a client."""
        # Pack header: type(1) + sample_rate(4) + channels(1) + data_len(4)
        header = struct.pack(
            "!BIBI",
            0x02,  # Audio chunk type
            chunk.sample_rate,
            chunk.channels,
            len(chunk.data),
        )
        # Also send timestamp as double
        timestamp_bytes = struct.pack("!d", chunk.timestamp)

        await websocket.send(header + timestamp_bytes + chunk.data)

    async def _send_json(self, websocket: WebSocketServerProtocol, data: dict) -> None:
        """Send JSON message to a client."""
        await websocket.send(json.dumps(data))

    async def _broadcast_json(self, data: dict) -> None:
        """Broadcast JSON message to all clients."""
        message = json.dumps(data)
        for client_id, client in list(self.clients.items()):
            try:
                await client.websocket.send(message)
            except Exception as e:
                logger.warning(f"Failed to send to {client_id}: {e}")

    @property
    def client_count(self) -> int:
        """Get number of connected clients."""
        return len(self.clients)

    def get_client_ids(self) -> list[str]:
        """Get list of connected client IDs."""
        return list(self.clients.keys())


class WebSocketAudioInput:
    """
    Audio input source from WebSocket clients.

    Collects audio from connected clients and provides it as an async iterator.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self._queue: asyncio.Queue[AudioChunk] = asyncio.Queue(maxsize=100)
        self._running = False

    def start(self) -> None:
        """Start the audio input."""
        self._running = True

    def stop(self) -> None:
        """Stop the audio input."""
        self._running = False
        # Clear queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    async def push_audio(self, chunk: AudioChunk, client_id: str) -> None:
        """Push audio chunk from WebSocket callback."""
        if not self._running:
            return

        try:
            self._queue.put_nowait(chunk)
        except asyncio.QueueFull:
            # Drop oldest
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(chunk)
            except asyncio.QueueEmpty:
                pass

    async def get_chunk(self, timeout: float = 1.0) -> Optional[AudioChunk]:
        """Get next audio chunk."""
        try:
            return await asyncio.wait_for(self._queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def __aiter__(self) -> AsyncIterator[AudioChunk]:
        """Async iterator for audio chunks."""
        while self._running:
            chunk = await self.get_chunk(timeout=0.5)
            if chunk:
                yield chunk


class WebSocketVideoOutput:
    """
    Video output sink to WebSocket clients.

    Accepts video frames and broadcasts them to connected clients.
    """

    def __init__(
        self,
        server: MediaWebSocketServer,
        fps: float = 25.0,
    ):
        self.server = server
        self.target_fps = fps
        self._frame_interval = 1.0 / fps
        self._last_frame_time = 0.0

    async def push_frame(
        self,
        frame_bgr: np.ndarray,
        fps: float = 0.0,
    ) -> None:
        """Push a video frame to broadcast."""
        current_time = time.time()

        # Rate limiting
        if current_time - self._last_frame_time < self._frame_interval * 0.9:
            return

        await self.server.broadcast_video_frame(
            frame_bgr=frame_bgr,
            fps=fps or self.target_fps,
            timestamp=current_time,
        )
        self._last_frame_time = current_time


class WebSocketAudioOutput:
    """
    Audio output sink to WebSocket clients.

    Accepts audio chunks and broadcasts them to connected clients.
    """

    def __init__(
        self,
        server: MediaWebSocketServer,
        sample_rate: int = 16000,
    ):
        self.server = server
        self.sample_rate = sample_rate

    async def push_audio(
        self,
        audio_data: bytes | np.ndarray,
        sample_rate: Optional[int] = None,
    ) -> None:
        """Push audio chunk to broadcast."""
        await self.server.broadcast_audio_chunk(
            audio_data=audio_data,
            sample_rate=sample_rate or self.sample_rate,
            timestamp=time.time(),
        )
