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

    # Validate required environment variables
    api_secret = os.getenv("BITHUMAN_API_SECRET")
    if not api_secret:
        raise ValueError("BITHUMAN_API_SECRET environment variable is required")
    
    avatar_id = os.getenv("BITHUMAN_AVATAR_ID", "A33NZN6384")
    logger.info(f"Using avatar ID: {avatar_id}")
    
    # Initialize bitHuman avatar session with avatar_id
    # The avatar_id references a pre-configured avatar model in the cloud
    try:
        bithuman_avatar = bithuman.AvatarSession(
            api_url=os.getenv("BITHUMAN_API_URL", "https://auth.api.bithuman.ai/v1/runtime-tokens/request"),  # Default API URL
            api_secret=api_secret,
            avatar_id=avatar_id,  # Make avatar_id configurable
        )
        logger.info("BitHuman avatar session initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize BitHuman avatar session: {str(e)}")
        logger.error("Please check:")
        logger.error("1. BITHUMAN_API_SECRET is valid")
        logger.error(f"2. Avatar ID '{avatar_id}' exists and is accessible")
        logger.error("3. BitHuman service is available")
        raise

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
    try:
        logger.info("Starting BitHuman avatar session...")
        await bithuman_avatar.start(
            session, 
            room=ctx.room
        )
        logger.info("BitHuman avatar session started successfully")
    except Exception as e:
        logger.error(f"Failed to start BitHuman avatar session: {str(e)}")
        logger.error("This could be due to:")
        logger.error("1. Avatar ID not found or inaccessible")
        logger.error("2. Insufficient resources in CPU mode")
        logger.error("3. BitHuman service temporary unavailability")
        logger.error("4. Network connectivity issues")
        
        # Try to provide more specific guidance based on error message
        error_msg = str(e).lower()
        if "avatar session failed" in error_msg:
            logger.error("💡 Suggested fixes:")
            logger.error("   - Try a different avatar ID from https://imaginex.bithuman.ai/#community")
            logger.error("   - Check if the avatar supports CPU mode")
            logger.error("   - Verify your account has access to this avatar")
        
        raise

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
