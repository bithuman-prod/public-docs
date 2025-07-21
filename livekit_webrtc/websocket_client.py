#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from pathlib import Path

import numpy as np
import websockets
from loguru import logger

try:
    import resampy
    import soundfile as sf
except ImportError:
    logger.error(
        "soundfile and resampy are required to run this example, install with `pip install soundfile resampy`"  # noqa: E501
    )
    sys.exit(1)

logger.remove()
logger.add(sys.stdout, level="INFO")


class AudioStreamerClient:
    """Client to stream audio files to the Bithuman WebSocket server."""

    def __init__(
        self,
        ws_url: str,
        chunk_size_ms: int = 100,
        sample_rate: int = 16000,
    ):
        """Initialize the audio streamer client.

        Args:
            ws_url: WebSocket server URL (e.g., ws://localhost:8765)
            chunk_size_ms: Size of audio chunks to send in milliseconds
            sample_rate: Target sample rate for audio
        """
        self.ws_url = ws_url
        self.chunk_size_ms = chunk_size_ms
        self.sample_rate = sample_rate
        self.chunk_samples = int(self.sample_rate * self.chunk_size_ms / 1000)
        self.websocket = None
        self._running = False

    async def connect(self) -> bool:
        """Connect to the WebSocket server.

        Returns:
            True if connection was successful, False otherwise
        """
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self._running = True
            logger.info(f"Connected to WebSocket server at {self.ws_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self._running = False
            logger.info("Disconnected from WebSocket server")

    async def send_interrupt(self):
        """Send an interrupt command to the server."""
        if not self.websocket:
            logger.error("Not connected to WebSocket server")
            return False

        try:
            message = json.dumps({"type": "interrupt"})
            await self.websocket.send(message)
            logger.info("Sent interrupt command")
            return True
        except Exception as e:
            logger.error(f"Failed to send interrupt command: {e}")
            return False

    async def stream_audio_file(self, audio_file: str) -> bool:
        """Stream an audio file to the WebSocket server.

        Args:
            audio_file: Path to the audio file

        Returns:
            True if streaming was successful, False otherwise
        """
        if not self.websocket:
            logger.error("Not connected to WebSocket server")
            return False

        try:
            # Load and resample audio file
            logger.info(f"Loading audio file: {audio_file}")
            audio_data, file_sr = sf.read(audio_file)

            # Convert to mono if stereo
            if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
                audio_data = np.mean(audio_data, axis=1)

            # Resample if needed
            if file_sr != self.sample_rate:
                logger.info(f"Resampling from {file_sr}Hz to {self.sample_rate}Hz")
                audio_data = resampy.resample(
                    audio_data, sr_orig=file_sr, sr_new=self.sample_rate
                )

            # Convert to int16
            if audio_data.dtype != np.int16:
                if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                    audio_data = (audio_data * 32767).astype(np.int16)
                else:
                    audio_data = audio_data.astype(np.int16)

            # Stream audio in chunks
            logger.info(
                f"Streaming audio file ({len(audio_data) / self.sample_rate:.2f}s)"
            )

            chunk_count = 0

            for i in range(0, len(audio_data), self.chunk_samples):
                if not self._running:
                    break

                # Get chunk
                chunk = audio_data[i : i + self.chunk_samples]

                # Send chunk
                await self.websocket.send(chunk.tobytes())
                chunk_count += 1

            # Send end-of-audio command
            message = json.dumps({"type": "end"})
            await self.websocket.send(message)

            logger.info(f"Finished streaming audio file ({chunk_count} chunks)")
            return True

        except Exception as e:
            logger.error(f"Failed to stream audio file: {e}")
            return False


async def main(args: argparse.Namespace):
    """Main function to run the example."""
    # Create client
    client = AudioStreamerClient(
        ws_url=args.ws_url,
        chunk_size_ms=args.chunk_size,
        sample_rate=args.sample_rate,
    )

    # Connect to server
    if not await client.connect():
        return

    try:
        # Process commands
        if args.command == "stream":
            # Check if file exists
            audio_file = Path(args.audio_file)
            if not audio_file.exists():
                logger.error(f"Audio file not found: {audio_file}")
                return

            # Stream audio file
            await client.stream_audio_file(str(audio_file))

        elif args.command == "interrupt":
            # Send interrupt command
            await client.send_interrupt()

        await asyncio.sleep(0.5)

    finally:
        # Disconnect from server
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Stream audio files to Bithuman WebSocket server"
    )

    # WebSocket arguments
    parser.add_argument(
        "--ws-url",
        type=str,
        default="ws://localhost:8765",
        help="WebSocket server URL",
    )

    # Audio arguments
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Target sample rate for audio",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100,
        help="Size of audio chunks to send in milliseconds",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Stream command
    stream_parser = subparsers.add_parser("stream", help="Stream an audio file")
    stream_parser.add_argument(
        "audio_file",
        type=str,
        help="Path to the audio file",
    )

    # Interrupt command
    interrupt_parser = subparsers.add_parser("interrupt", help="Send interrupt command")

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
