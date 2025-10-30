import logging
import os
from typing import Optional

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
logger = logging.getLogger("flutter-bithuman-agent")
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the LiveKit agent with bitHuman avatar integration.
    This agent is specifically designed for Flutter frontend integration.
    
    Architecture:
    Flutter App ←→ LiveKit Room ←→ Python Agent ←→ bitHuman Avatar
    """
    # Connect to the LiveKit room
    await ctx.connect()
    logger.info("Connected to LiveKit room")

    # Log room information
    logger.info(f"Agent connected to room: {ctx.room.name}")
    logger.info(f"Room participants: {len(ctx.room.remote_participants)}")
    
    # Wait for at least one participant to join the room
    # This will block until a participant joins
    logger.info("Waiting for participants to join...")
    await ctx.wait_for_participant()
    logger.info("Participant joined the room")

    # Validate required environment variables
    api_secret = os.getenv("BITHUMAN_API_SECRET")
    if not api_secret:
        raise ValueError("BITHUMAN_API_SECRET environment variable is required")
    
    # Get avatar configuration
    avatar_id = os.getenv("BITHUMAN_AVATAR_ID", "A33NZN6384")
    avatar_image = os.getenv("BITHUMAN_AVATAR_IMAGE")  # Optional custom image
    
    logger.info(f"Using avatar ID: {avatar_id}")
    if avatar_image:
        logger.info(f"Using custom avatar image: {avatar_image}")
    
    # Initialize bitHuman avatar session
    try:
        if avatar_image and os.path.exists(avatar_image):
            # Use custom avatar image
            bithuman_avatar = bithuman.AvatarSession(
                api_url=os.getenv("BITHUMAN_API_URL", "https://auth.api.bithuman.ai/v1/runtime-tokens/request"),
                api_secret=api_secret,
                avatar_image=avatar_image,
            )
            logger.info("BitHuman avatar session initialized with custom image")
        else:
            # Use pre-configured avatar ID
            bithuman_avatar = bithuman.AvatarSession(
                api_url=os.getenv("BITHUMAN_API_URL", "https://auth.api.bithuman.ai/v1/runtime-tokens/request"),
                api_secret=api_secret,
                avatar_id=avatar_id,
            )
            logger.info("BitHuman avatar session initialized with avatar ID")
            
    except Exception as e:
        logger.error(f"Failed to initialize BitHuman avatar session: {str(e)}")
        logger.error("Please check:")
        logger.error("1. BITHUMAN_API_SECRET is valid")
        logger.error(f"2. Avatar ID '{avatar_id}' exists and is accessible")
        logger.error("3. BitHuman service is available")
        if avatar_image:
            logger.error(f"4. Custom image '{avatar_image}' exists and is valid")
        raise

    # Configure the AI agent session with OpenAI Realtime API
    # Optimized for Flutter integration with better voice settings
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice=os.getenv("OPENAI_VOICE", "coral"),  # Configurable voice
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini-realtime-preview"),
        ),
        vad=silero.VAD.load()  # Voice Activity Detection for natural conversation
    )

    # Start the bitHuman avatar session
    try:
        logger.info("Starting BitHuman avatar session...")
        logger.info(f"Room name: {ctx.room.name}")
        logger.info(f"Room participants: {len(ctx.room.remote_participants)}")
        
        await bithuman_avatar.start(
            session, 
            room=ctx.room
        )
        logger.info("BitHuman avatar session started successfully")
        
        # Log room state after avatar start
        logger.info(f"Room participants after avatar start: {len(ctx.room.remote_participants)}")
        for participant in ctx.room.remote_participants.values():
            logger.info(f"Participant: {participant.identity}")
            for publication in participant.track_publications.values():
                logger.info(f"  Track: {publication.kind} - {publication.sid}")
    except Exception as e:
        logger.error(f"Failed to start BitHuman avatar session: {str(e)}")
        logger.error("This could be due to:")
        logger.error("1. Avatar ID not found or inaccessible")
        logger.error("2. Insufficient resources in CPU mode")
        logger.error("3. BitHuman service temporary unavailability")
        logger.error("4. Network connectivity issues")
        raise

    # Configure AI agent with Flutter-optimized instructions
    agent_instructions = os.getenv(
        "AGENT_INSTRUCTIONS", 
        "You are a helpful AI assistant integrated with a Flutter mobile app. "
        "Respond naturally and concisely to user questions. "
        "Keep responses brief and engaging for mobile users. "
        "You can help with general questions, provide information, "
        "and have friendly conversations."
    )

    # Start the AI agent session
    await session.start(
        agent=Agent(
            instructions=agent_instructions
        ),
        room=ctx.room,
        # Disable room audio output since audio is handled by the avatar
        room_output_options=RoomOutputOptions(audio_enabled=False),
    )
    
    logger.info("Flutter integration agent is ready and running")


if __name__ == "__main__":
    # Configure and run the LiveKit agent worker
    # Optimized settings for Flutter integration
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
            job_memory_warn_mb=2000,  # Increased memory for avatar processing
            num_idle_processes=1,     # Maintain one idle process
            initialize_process_timeout=300,  # Increased timeout to 5 minutes for avatar initialization
        )
    )
