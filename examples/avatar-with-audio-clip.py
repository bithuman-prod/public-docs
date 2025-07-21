import argparse
import asyncio
import os
import sys
import threading
import time
from typing import Optional, Tuple

import cv2
import numpy as np
from loguru import logger

from bithuman import AsyncBithuman, VideoFrame
from bithuman.audio import float32_to_int16, load_audio
from bithuman.utils import FPSController

try:
    import sounddevice as sd
except ImportError:
    logger.warning("sounddevice is not installed. Audio will not be played.")
    sd = None

logger.remove()
logger.add(sys.stdout, level="INFO")


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

    def output_callback(self, outdata, frames, time, status):
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


class VideoPlayer:
    """Video player for displaying frames."""

    def __init__(self, window_size: Tuple[int, int], window_name: str = "Bithuman"):
        self.window_name = window_name
        self.start_time = None
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, window_size[0], window_size[1])

    def start(self):
        """Start the video player."""
        self.start_time = asyncio.get_event_loop().time()

    def stop(self):
        """Stop the video player."""
        cv2.destroyAllWindows()

    async def display_frame(
        self, frame: VideoFrame, fps: float = 0.0, exp_time: float = 0.0
    ) -> int:
        """Display a frame and return the key pressed."""
        if not frame.has_image:
            await asyncio.sleep(0.01)
            return -1

        # Render the frame
        image = await self.render_image(frame, fps, exp_time)

        # Display the frame
        cv2.imshow(self.window_name, image)
        key = cv2.waitKey(1) & 0xFF

        return key

    async def render_image(
        self, frame: VideoFrame, fps: float = 0.0, exp_time: float = 0.0
    ) -> np.ndarray:
        """Render a frame with additional information."""
        image = frame.bgr_image.copy()

        # Add FPS information
        cv2.putText(
            image,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        # Add elapsed time
        current_time = asyncio.get_event_loop().time()
        if self.start_time is not None:
            elapsed = current_time - self.start_time
            cv2.putText(
                image,
                f"Time: {elapsed:.1f}s",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

        # Add expiration time if available
        if exp_time > 0:
            exp_in_seconds = exp_time - time.time()
            cv2.putText(
                image,
                f"Exp in: {exp_in_seconds:.1f}s",
                (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

        return image


async def push_audio(
    runtime: AsyncBithuman, audio_file: str, delay: float = 0.0
) -> None:
    """Push audio from a file to the runtime."""
    logger.info(f"Pushing audio file: {audio_file}")
    audio_np, sr = load_audio(audio_file)
    audio_np = float32_to_int16(audio_np)

    await asyncio.sleep(delay)
    # Simulate streaming audio bytes
    chunk_size = sr // 100
    for i in range(0, len(audio_np), chunk_size):
        chunk = audio_np[i : i + chunk_size]
        # Send to runtime
        await runtime.push_audio(chunk.tobytes(), sr, last_chunk=False)

    # Flush the audio, mark the end of speech
    await runtime.flush()


async def run_bithuman(
    runtime: AsyncBithuman, audio_file: Optional[str] = None
) -> None:
    """Run the Bithuman runtime with audio and video players."""
    # Initialize players
    audio_player = AudioPlayer()
    video_player = VideoPlayer(window_size=runtime.get_frame_size())
    fps_controller = FPSController(target_fps=25)

    # Start players
    audio_player.start()
    video_player.start()

    # Start runtime
    await runtime.start()

    # Initial audio push task
    push_audio_task = None
    if audio_file:
        push_audio_task = asyncio.create_task(
            push_audio(runtime, audio_file, delay=1.0)
        )

    try:
        async for frame in runtime.run():
            sleep_time = fps_controller.wait_next_frame(sleep=False)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

            # Display frame and get key press
            exp_time = runtime.get_expiration_time()
            key = await video_player.display_frame(
                frame, fps_controller.average_fps, exp_time
            )
            # Add audio to the buffer
            if frame.audio_chunk and audio_player.is_started():
                audio_player.add_audio(frame.audio_chunk.array)  # int16 16kHz mono

            # Handle key presses
            if key == ord("1") and audio_file:
                # Play audio file
                if push_audio_task and not push_audio_task.done():
                    logger.info("Cancelling previous push_audio task")
                    push_audio_task.cancel()
                push_audio_task = asyncio.create_task(push_audio(runtime, audio_file))
            elif key == ord("2"):
                # Interrupt playback
                logger.info("Interrupting")
                if push_audio_task and not push_audio_task.done():
                    push_audio_task.cancel()
                runtime.interrupt()
            elif key == ord("q"):
                logger.info("Exiting...")
                break

            fps_controller.update()

    except asyncio.CancelledError:
        logger.info("Runtime task cancelled")
    finally:
        # Clean up
        if push_audio_task and not push_audio_task.done():
            push_audio_task.cancel()
        audio_player.stop()
        video_player.stop()
        await runtime.stop()


async def main(args: argparse.Namespace) -> None:
    """Main entry point for the example application.

    This function demonstrates the proper way to initialize and use the
    AsyncBithuman runtime in an asynchronous context.

    Args:
        args: Command line arguments parsed by argparse.
    """
    logger.info(f"Initializing AsyncBithuman with model: {args.model}")

    # Use the factory method to create a fully initialized instance
    runtime = await AsyncBithuman.create(
        model_path=args.model,
        token=args.token,
        api_secret=args.api_secret,
        insecure=args.insecure,
    )

    # Verify model was set successfully
    try:
        frame_size = runtime.get_frame_size()
        logger.info(f"Model initialized successfully, frame size: {frame_size}")
    except Exception as e:
        logger.error(f"Model initialization verification failed: {e}")
        raise

    # Run the application with the main business logic
    logger.info("Starting runtime...")
    await run_bithuman(runtime, args.audio_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument(
        "--token",
        type=str,
        default=os.environ.get("BITHUMAN_RUNTIME_TOKEN"),
        help="JWT token for authentication (optional if --api-secret is provided)",
    )
    parser.add_argument("--audio-file", type=str, default=None)
    parser.add_argument(
        "--api-secret",
        type=str,
        default=os.environ.get("BITHUMAN_API_SECRET"),
        help="API Secret for API authentication (optional if --token is provided)",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL certificate verification (not recommended for production use)",
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
