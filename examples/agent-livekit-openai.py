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
from livekit.plugins import bithuman, openai

logger = logging.getLogger("bitHuman")
logger.setLevel(logging.INFO)

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    logger.info("staring bithuman runtime")
    bithuman_avatar = bithuman.AvatarSession(
        model_path=os.getenv("BITHUMAN_MODEL_PATH"),
        api_secret=os.getenv("BITHUMAN_API_SECRET")
    )

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
           voice="ash",
           model="gpt-4o-mini-realtime-preview",
        )
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
