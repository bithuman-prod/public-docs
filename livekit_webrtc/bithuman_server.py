import argparse
import asyncio
import json
import os
import signal
import sys

import cv2
import dotenv
import numpy as np
import websockets
from livekit import api, rtc
from loguru import logger

from bithuman import AsyncBithuman
from bithuman.utils import FPSController

logger.remove()
logger.add(sys.stdout, level="INFO")

dotenv.load_dotenv()

# WebSocket message types
MSG_TYPE_AUDIO = "audio"
MSG_TYPE_INTERRUPT = "interrupt"
MSG_TYPE_END = "end"


class BithumanLiveKitStreamer:
    """Stream Bithuman avatar to a LiveKit room and accept audio via WebSocket."""

    def __init__(
        self,
        runtime: AsyncBithuman,
        livekit_url: str,
        livekit_api_key: str,
        livekit_api_secret: str,
        room_name: str,
        identity: str = "bithuman-avatar",
        ws_port: int = 8765,
    ):
        self.runtime = runtime
        self.livekit_url = livekit_url
        self.livekit_api_key = livekit_api_key
        self.livekit_api_secret = livekit_api_secret
        self.room_name = room_name
        self.identity = identity
        self.ws_port = ws_port

        # Media settings
        self.video_fps = 25
        self.audio_sample_rate = 16000
        self._buffer_size_ms = 100

        # LiveKit components
        self._room = rtc.Room()
        self._video_source = None
        self._audio_source = None
        self._av_sync = None

        # Control flags
        self._running = False
        self._connected_clients: dict[str, websockets.WebSocketServerProtocol] = {}

        # FPS controller for smooth video
        self._fps_controller = FPSController(target_fps=self.video_fps)

        # Queue for audio processing
        self._audio_queue = asyncio.Queue[bytes]()

        # Tasks
        self._tasks: list[asyncio.Task] = []
        self._ws_server = None

    async def start(self):
        """Start the Bithuman runtime, LiveKit connection, and WebSocket server."""
        self._running = True

        # Start Bithuman runtime
        await self.runtime.start()
        frame_size = self.runtime.get_frame_size()

        # Create LiveKit token
        token = (
            api.AccessToken(
                api_key=self.livekit_api_key, api_secret=self.livekit_api_secret
            )
            .with_identity(self.identity)
            .with_name("Bithuman Avatar")
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=self.room_name,
                )
            )
            .with_kind("agent")
            .to_jwt()
        )

        # Connect to LiveKit room
        try:
            await self._room.connect(self.livekit_url, token)
            logger.info(f"Connected to LiveKit room: {self.room_name}")
        except rtc.ConnectError as e:
            logger.error(f"Failed to connect to LiveKit room: {e}")
            return False

        # Create video and audio sources
        self._video_source = rtc.VideoSource(
            width=frame_size[0],
            height=frame_size[1],
        )

        self._audio_source = rtc.AudioSource(
            sample_rate=self.audio_sample_rate,
            num_channels=1,
            queue_size_ms=self._buffer_size_ms,
        )

        # Create tracks
        video_track = rtc.LocalVideoTrack.create_video_track(
            "video", self._video_source
        )
        audio_track = rtc.LocalAudioTrack.create_audio_track(
            "audio", self._audio_source
        )

        # Publish tracks
        video_options = rtc.TrackPublishOptions(
            source=rtc.TrackSource.SOURCE_CAMERA,
            video_encoding=rtc.VideoEncoding(
                max_framerate=self.video_fps,
                max_bitrate=5_000_000,
            ),
        )
        audio_options = rtc.TrackPublishOptions(
            source=rtc.TrackSource.SOURCE_MICROPHONE
        )

        await self._room.local_participant.publish_track(video_track, video_options)
        await self._room.local_participant.publish_track(audio_track, audio_options)

        # Create AV synchronizer
        self._av_sync = rtc.AVSynchronizer(
            audio_source=self._audio_source,
            video_source=self._video_source,
            video_fps=self.video_fps,
            video_queue_size_ms=self._buffer_size_ms,
        )

        # Start WebSocket server
        self._ws_server = await websockets.serve(
            self._handle_websocket,
            "0.0.0.0",
            self.ws_port,
        )
        logger.info(f"WebSocket server started on port {self.ws_port}")

        # Start audio processing task
        audio_task = asyncio.create_task(self._process_audio_queue())
        self._tasks.append(audio_task)

        return True

    async def stop(self):
        """Stop all components."""
        self._running = False

        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._tasks.clear()

        # Close WebSocket server
        if self._ws_server:
            self._ws_server.close()
            await self._ws_server.wait_closed()
            self._ws_server = None

        # Close all WebSocket connections
        for client in list(self._connected_clients.values()):
            await client.close()
        self._connected_clients.clear()

        # Stop LiveKit components
        if self._av_sync:
            await self._av_sync.aclose()
            self._av_sync = None

        if self._audio_source:
            await self._audio_source.aclose()
            self._audio_source = None

        if self._video_source:
            await self._video_source.aclose()
            self._video_source = None

        # Disconnect from LiveKit room
        await self._room.disconnect()

        # Stop Bithuman runtime
        await self.runtime.stop()

        logger.info("All components stopped")

    async def _handle_websocket(self, websocket):
        """Handle incoming WebSocket connections."""
        client_id = str(id(websocket))
        self._connected_clients[client_id] = websocket
        logger.info(f"New WebSocket client connected: {client_id}")

        try:
            async for message in websocket:
                try:
                    # Parse the message
                    if isinstance(message, str):
                        data = json.loads(message)
                        msg_type = data.get("type")

                        if msg_type == MSG_TYPE_INTERRUPT:
                            # Interrupt the current audio processing
                            logger.info("Received interrupt command")
                            self.runtime.interrupt()

                        elif msg_type == MSG_TYPE_END:
                            # End of audio segment
                            logger.info("Received end of audio segment")
                            await self.runtime.flush()

                        else:
                            logger.warning(f"Unknown message type: {msg_type}")

                    elif isinstance(message, bytes):
                        # Assume binary data is audio
                        await self._audio_queue.put(message)

                except json.JSONDecodeError:
                    logger.error("Failed to parse WebSocket message as JSON")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket client disconnected: {client_id}")

        finally:
            if client_id in self._connected_clients:
                del self._connected_clients[client_id]

    async def _process_audio_queue(self):
        """Process audio chunks from the queue."""
        while self._running:
            try:
                audio_bytes = await self._audio_queue.get()
                await self.runtime.push_audio(
                    audio_bytes, self.audio_sample_rate, last_chunk=False
                )
                self._audio_queue.task_done()

            except asyncio.CancelledError:
                logger.info("Audio processing task cancelled")
                break
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                await asyncio.sleep(0.1)

    async def run(self):
        """Main loop to process frames from Bithuman and send to LiveKit."""
        if not self._running:
            logger.error("Streamer not started. Call start() first.")
            return

        try:
            async for frame in self.runtime.run():
                # Control frame rate
                sleep_time = self._fps_controller.wait_next_frame(sleep=False)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

                # Process video frame
                if frame.has_image:
                    # Convert BGR to RGB
                    rgb_image = cv2.cvtColor(frame.bgr_image, cv2.COLOR_BGR2RGB)

                    # Create RGBA frame (required by LiveKit)
                    rgba = (
                        np.ones(
                            (rgb_image.shape[0], rgb_image.shape[1], 4), dtype=np.uint8
                        )
                        * 255
                    )
                    rgba[:, :, :3] = rgb_image

                    # Create VideoFrame for LiveKit
                    video_frame = rtc.VideoFrame(
                        width=rgba.shape[1],
                        height=rgba.shape[0],
                        type=rtc.VideoBufferType.RGBA,
                        data=rgba.tobytes(),
                    )

                    # Push to AV synchronizer
                    await self._av_sync.push(video_frame)

                # Process audio frame
                if frame.audio_chunk:
                    audio_data = frame.audio_chunk.array  # int16 16kHz mono

                    # Create AudioFrame for LiveKit
                    audio_frame = rtc.AudioFrame(
                        data=audio_data.tobytes(),
                        sample_rate=16000,
                        num_channels=1,
                        samples_per_channel=len(audio_data),
                    )
                    await self._av_sync.push(audio_frame)

                self._fps_controller.update()

        except asyncio.CancelledError:
            logger.info("Runtime task cancelled")
        finally:
            await self.stop()


async def main(args: argparse.Namespace) -> None:
    """Main function to run the example."""
    # Validate required arguments
    assert args.token or args.api_secret, "Bithuman token or API secret is required"
    assert args.livekit_url, "LiveKit URL is required"
    assert args.livekit_api_key, "LiveKit API key is required"
    assert args.livekit_api_secret, "LiveKit API secret is required"
    assert args.room, "LiveKit room name is required"
    assert args.avatar_model, "Avatar model is required"

    # Create Bithuman runtime
    runtime = await AsyncBithuman.create(
        token=args.token, api_secret=args.api_secret, model_path=args.avatar_model
    )

    # Create streamer
    streamer = BithumanLiveKitStreamer(
        runtime=runtime,
        livekit_url=args.livekit_url,
        livekit_api_key=args.livekit_api_key,
        livekit_api_secret=args.livekit_api_secret,
        room_name=args.room,
        identity=args.identity,
        ws_port=args.ws_port,
    )

    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()

    async def cleanup():
        await streamer.stop()
        loop.stop()

    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, lambda: asyncio.ensure_future(cleanup()))

    # Start the streamer
    if await streamer.start():
        # Run the main loop
        await streamer.run()
    else:
        logger.error("Failed to start streamer")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Stream Bithuman avatar to LiveKit room"
    )

    # Bithuman arguments
    parser.add_argument(
        "--avatar-model",
        type=str,
        default=os.environ.get("BITHUMAN_AVATAR_MODEL"),
        help="Bithuman avatar model name",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=os.environ.get("BITHUMAN_RUNTIME_TOKEN"),
        help="Bithuman runtime token",
    )
    parser.add_argument(
        "--api-secret",
        type=str,
        default=os.environ.get("BITHUMAN_API_SECRET"),
        help="Bithuman API secret",
    )

    # LiveKit arguments
    parser.add_argument(
        "--livekit-url",
        type=str,
        default=os.environ.get("LIVEKIT_URL"),
        help="LiveKit server URL",
    )
    parser.add_argument(
        "--livekit-api-key",
        type=str,
        default=os.environ.get("LIVEKIT_API_KEY"),
        help="LiveKit API key",
    )
    parser.add_argument(
        "--livekit-api-secret",
        type=str,
        default=os.environ.get("LIVEKIT_API_SECRET"),
        help="LiveKit API secret",
    )
    parser.add_argument("--room", type=str, required=True, help="LiveKit room name")
    parser.add_argument(
        "--identity",
        type=str,
        default="bithuman-avatar",
        help="Identity in LiveKit room",
    )

    # WebSocket arguments
    parser.add_argument(
        "--ws-port", type=int, default=8765, help="WebSocket server port"
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
