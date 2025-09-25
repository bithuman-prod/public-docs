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

# Configure logging for better debugging
logger = logging.getLogger("bithuman-livekit-agent")
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the LiveKit agent with bitHuman avatar integration.
    This example demonstrates the simplest cloud-based setup using avatar_id.
    """
    # Connect to the LiveKit room
    await ctx.connect()

    # Wait for at least one participant to join the room
    await ctx.wait_for_participant()

    logger.info("Starting bitHuman avatar runtime")
    
    # Initialize bitHuman avatar session with avatar_id
    # The avatar_id references a pre-configured avatar model in the cloud
    bithuman_avatar = bithuman.AvatarSession(
        api_secret=os.getenv("BITHUMAN_API_SECRET"),
        avatar_id="A05XGC2284",  # Replace with your avatar ID from bitHuman platform
    )

    # Configure the AI agent session with OpenAI Realtime API
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral",  # Available voices: alloy, echo, fable, onyx, nova, shimmer, coral
            model="gpt-4o-mini-realtime-preview",  # Use the realtime preview model
        ),
        vad=silero.VAD.load()  # Voice Activity Detection for better conversation flow
    )

    # Start the bitHuman avatar session
    # This connects the avatar to the LiveKit room and agent session
    await bithuman_avatar.start(
        session, 
        room=ctx.room
    )

    # Start the AI agent session
    await session.start(
        agent=Agent(
            instructions=(
                "You are a helpful assistant. Talk to users naturally and respond "
                "shortly and concisely. Keep conversations engaging and friendly."
            )
        ),
        room=ctx.room,
        # Disable room audio output since audio is handled by the avatar
        room_output_options=RoomOutputOptions(audio_enabled=False),
    )


if __name__ == "__main__":
    # Configure and run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
            job_memory_warn_mb=1500,  # Warning threshold for memory usage
            num_idle_processes=1,     # Number of idle processes to maintain
            initialize_process_timeout=120,  # Timeout for process initialization
        )
    )
