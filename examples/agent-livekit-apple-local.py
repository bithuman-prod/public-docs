import logging
import os

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomOutputOptions,
    WorkerOptions,
    WorkerType,
    cli,
)
from livekit.plugins import bithuman, openai, silero

logger = logging.getLogger("bitHuman")
logger.setLevel(logging.INFO)

load_dotenv()

# This is an example to use Apple's local STT and TTS.
# The service is locally hosted, no need to connect to the internet.

# First, install bithuman-voice from `pip install https://github.com/bithuman-prod/public-sdk-examples/releases/download/v0.1/bithuman_voice-1.3.2-py3-none-any.whl`
# Then, start the service with `bithuman-voice serve --port 8091` from system terminal.
# This may need an approval in system for it to access the Apple Speech API.


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    logger.info("staring bithuman runtime")
    bithuman_avatar = bithuman.AvatarSession(
        model_path=os.getenv("BITHUMAN_MODEL_PATH"),
        api_secret=os.getenv("BITHUMAN_API_SECRET"),
    )

    session = AgentSession(
        llm=openai.LLM(),
        tts=openai.TTS(base_url="http://localhost:8091/v1", voice=""),
        stt=openai.STT(base_url="http://localhost:8091/v1"),
        vad=silero.VAD.load(),
    )
    await bithuman_avatar.start(session, room=ctx.room)

    await session.start(
        agent=Agent(
            instructions=(
                "Your are a helpful assistant! Response shortly and concisely."
            )
        ),
        room=ctx.room,
        room_output_options=RoomOutputOptions(audio_enabled=False),
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
            job_memory_warn_mb=1500,
            num_idle_processes=1,
            initialize_process_timeout=120,
        )
    )
