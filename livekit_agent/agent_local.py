import asyncio
import logging
import os
import signal
import sys

import numpy as np
from dotenv import load_dotenv
from livekit.agents import utils
from livekit.agents.voice import Agent, AgentSession
from livekit.agents.voice.avatar import AvatarOptions, QueueAudioOutput
from livekit.plugins import openai
from loguru import logger

from bithuman import AsyncBithuman
from bithuman.utils.agent import LocalAudioIO, LocalAvatarRunner, LocalVideoPlayer

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")
logging.getLogger("numba").setLevel(logging.WARNING)

# Load environment variables
load_dotenv()


class AlloyVoiceAgent(Agent):
    """Agent implementation using the Alloy voice model."""

    def __init__(self) -> None:
        super().__init__(
            instructions="You are Alloy.",
            llm=openai.realtime.RealtimeModel(voice="alloy"),
        )


async def create_bithuman_runtime() -> AsyncBithuman:
    """Create and initialize the BitHuman runtime."""
    avatar_model = os.getenv("BITHUMAN_AVATAR_MODEL")
    bithuman_api_secret = os.getenv("BITHUMAN_API_SECRET")

    if not (avatar_model or bithuman_api_secret):
        raise ValueError(
            "BITHUMAN_AVATAR_MODEL and BITHUMAN_API_SECRET are required"  # noqa: E501
        )

    return await AsyncBithuman.create(
        model_path=avatar_model, api_secret=bithuman_api_secret
    )


def create_avatar_options(first_frame: np.ndarray | None) -> AvatarOptions:
    """Create avatar options based on the first frame."""
    if first_frame is None:
        raise ValueError("Failed to get the first frame")

    output_width, output_height = first_frame.shape[1], first_frame.shape[0]
    return AvatarOptions(
        video_width=output_width,
        video_height=output_height,
        video_fps=25,
        audio_sample_rate=16000,
        audio_channels=1,
    )


async def entrypoint() -> None:
    # Init http context for livekit agent
    utils.http_context._new_session_ctx()

    # Initialize bitHuman runtime
    runtime = await create_bithuman_runtime()
    first_frame = runtime.get_first_frame()
    avatar_options = create_avatar_options(first_frame)

    buffer_size = 3
    video_player = LocalVideoPlayer(
        window_size=(avatar_options.video_width, avatar_options.video_height),
        buffer_size=buffer_size,
    )

    # Create agent and audio components
    # Path: agent audio -> interim audio buffer -> bitHuman runtime -> speaker output
    #                                                               -> video player
    interim_audio_buffer = QueueAudioOutput(
        sample_rate=avatar_options.audio_sample_rate
    )
    session = AgentSession()
    session.output.audio = interim_audio_buffer

    local_audio = LocalAudioIO(
        session=session,
        agent_audio_output=interim_audio_buffer,
        buffer_size=buffer_size,
    )
    await local_audio.start()

    # Create and start avatar runner
    avatar_runner = LocalAvatarRunner(
        bithuman_runtime=runtime,
        audio_input=interim_audio_buffer,
        audio_output=local_audio,
        video_output=video_player,
        options=avatar_options,
    )
    await avatar_runner.start()

    # Start agent
    await session.start(agent=AlloyVoiceAgent())


async def main() -> None:
    await entrypoint()

    stop_event = asyncio.Event()
    try:

        def signal_handler():
            stop_event.set()

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, signal_handler)

        # Wait until stopped
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass


if __name__ == "__main__":
    asyncio.run(main())
