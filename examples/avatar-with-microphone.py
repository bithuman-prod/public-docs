import argparse
import asyncio
import os
import sys
from collections.abc import AsyncIterator

import numpy as np
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AgentSession, utils
from livekit.agents.voice.avatar import QueueAudioOutput
from loguru import logger

from bithuman import AsyncBithuman
from bithuman.utils import FPSController
from bithuman.utils.agent import LocalAudioIO, LocalVideoPlayer

load_dotenv()

logger.remove()
logger.add(sys.stdout, level="INFO")


@utils.log_exceptions(logger=logger)
async def read_audio_from_microphone(
    runtime: AsyncBithuman,
    audio_io: LocalAudioIO,
    volume: float,
    slient_threshold_db: int = -40,
) -> None:
    async def _read_audio(
        audio_input: AsyncIterator[rtc.AudioFrame],
        buffer: asyncio.Queue[rtc.AudioFrame],
        sample_rate: int = 24000,
    ):
        audio_stream = utils.audio.AudioByteStream(
            sample_rate=sample_rate,
            num_channels=1,
            samples_per_channel=sample_rate // 100,
        )
        async for frame in audio_input:
            for f in audio_stream.push(frame.data):
                await buffer.put(f)

    @utils.log_exceptions(logger=logger)
    async def _push_audio(buffer: asyncio.Queue[rtc.AudioFrame]):
        last_speaking_time = asyncio.get_running_loop().time()
        slient_timeout = 3  # seconds
        is_speaking = True

        while True:
            frame = await buffer.get()

            if volume != 1.0 and is_speaking:
                # apply volume multiplier if the user is speaking
                audio_data = np.frombuffer(frame.data, dtype=np.int16)
                audio_data = np.clip(audio_data * volume, -32768, 32767).astype(
                    np.int16
                )
                audio_data = audio_data.tobytes()
            else:
                audio_data = bytes(frame.data)

            await runtime.push_audio(audio_data, frame.sample_rate, last_chunk=False)

            current_time = asyncio.get_running_loop().time()
            if audio_io._micro_db > slient_threshold_db:
                last_speaking_time = current_time
                is_speaking = True
            elif current_time - last_speaking_time > slient_timeout:
                # drop the frames if the buffer is big when the user is not speaking
                while buffer.qsize() > 10:
                    try:
                        buffer.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                is_speaking = False

    audio_buffer = asyncio.Queue[rtc.AudioFrame]()

    while True:
        # wait for audio input
        start_time = asyncio.get_running_loop().time()
        if audio_io._agent.input.audio is None:
            if asyncio.get_running_loop().time() - start_time > 20:
                raise RuntimeError("No audio input connected after 20 seconds")
            await asyncio.sleep(0.1)
            continue

        logger.info("Audio input ready")

        read_audio_atask = asyncio.create_task(
            _read_audio(audio_io._agent.input.audio, audio_buffer)
        )
        push_audio_atask = asyncio.create_task(_push_audio(audio_buffer))

        await asyncio.gather(read_audio_atask, push_audio_atask)


async def run_bithuman(runtime: AsyncBithuman, args: argparse.Namespace) -> None:
    """Run the Bithuman runtime with audio and video players."""
    # Initialize Video Player and Audio Input
    audio_io = LocalAudioIO(AgentSession(), QueueAudioOutput(), buffer_size=3)
    await audio_io.start()
    push_audio_task = asyncio.create_task(
        read_audio_from_microphone(
            runtime, audio_io, args.volume, args.slient_threshold_db
        )
    )

    video_player = LocalVideoPlayer(
        window_size=runtime.get_frame_size(),
        buffer_size=3,  # use a small input buffer to avoid latency
    )
    try:
        fps_controller = FPSController(target_fps=25)
        async for frame in runtime.run(
            out_buffer_empty=video_player.buffer_empty,
            idle_timeout=0.5,  # increase the idle timeout since input audio is a stream
        ):
            sleep_time = fps_controller.wait_next_frame(sleep=False)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

            if frame.has_image:
                await video_player.capture_frame(
                    frame,
                    fps=fps_controller.average_fps,
                    exp_time=runtime.get_expiration_time(),
                )

            if args.echo and frame.audio_chunk is not None:
                await audio_io.capture_frame(frame.audio_chunk)

            fps_controller.update()

    except asyncio.CancelledError:
        logger.info("Runtime task cancelled")
    finally:
        # Clean up
        if push_audio_task and not push_audio_task.done():
            push_audio_task.cancel()
        await video_player.aclose()
        await audio_io.aclose()
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
        input_buffer_size=5,  # 5 frames, 10ms per frame
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
    await run_bithuman(runtime, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", type=str, default=os.environ.get("BITHUMAN_AVATAR_MODEL")
    )
    parser.add_argument(
        "--token",
        type=str,
        default=os.environ.get("BITHUMAN_RUNTIME_TOKEN"),
        help="JWT token for authentication (optional if --api-secret is provided)",
    )
    parser.add_argument(
        "--api-secret",
        type=str,
        default=os.environ.get("BITHUMAN_API_SECRET"),
        help="API Secret for API authentication (optional if --token is provided)",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL certificate verification (not recommended for production use)",  # noqa: E501
    )
    parser.add_argument(
        "--volume",
        type=float,
        default=1.0,
        help="Volume multiplier for the audio output",
    )
    parser.add_argument(
        "--slient-threshold-db",
        type=int,
        default=-40,
        help="Slient threshold for the audio output",
    )
    parser.add_argument(
        "--echo",
        action="store_true",
        help="Enable echo for the audio output",
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
