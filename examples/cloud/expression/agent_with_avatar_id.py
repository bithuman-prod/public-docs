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
logger = logging.getLogger("bithuman-expression-avatar-id")
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()


async def entrypoint(ctx: JobContext):
    """
    Advanced LiveKit agent with bitHuman avatar using avatar_id.
    This example demonstrates expression-focused setup with enhanced customization.
    """
    # Connect to the LiveKit room
    await ctx.connect()

    # Wait for at least one participant to join the room
    await ctx.wait_for_participant()

    logger.info("Starting bitHuman expression avatar with avatar_id")

    # Initialize bitHuman avatar session with avatar_id
    # This uses a pre-configured avatar model from the bitHuman cloud platform
    bithuman_avatar = bithuman.AvatarSession(
        api_secret=os.getenv("BITHUMAN_API_SECRET"),
        avatar_id=os.getenv(
            "BITHUMAN_AVATAR_ID", "A05XGC2284"
        ),  # Use env var for flexibility
        model="expression",
        # Optional: Additional avatar configuration
        # avatar_voice_id="your_voice_id",  # Custom voice if available
        # avatar_motion_scale=1.0,          # Motion intensity (0.0-2.0)
        # avatar_expression_scale=1.2,      # Expression intensity (0.0-2.0)
    )

    # Configure the AI agent session with enhanced settings
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice=os.getenv("OPENAI_VOICE", "coral"),  # Configurable voice
            model="gpt-4o-mini-realtime-preview",
            # Optional: Add custom instructions for voice modulation
            # modalities=["text", "audio"],
        ),
        vad=silero.VAD.load(
            # Fine-tune voice activity detection
            # min_silence_duration=0.5,  # Minimum silence before stopping
            # min_speech_duration=0.2,   # Minimum speech duration to trigger
        ),
    )

    # Start the bitHuman avatar session
    await bithuman_avatar.start(session, room=ctx.room)

    # Get avatar personality from environment or use default
    avatar_personality = os.getenv(
        "AVATAR_PERSONALITY",
        "You are an expressive and engaging virtual assistant. "
        "Use natural gestures and facial expressions to communicate. "
        "Be enthusiastic and personable in your responses. "
        "Keep conversations lively and respond with appropriate emotional tone.",
    )

    # Start the AI agent session with enhanced instructions
    await session.start(
        agent=Agent(instructions=avatar_personality),
        room=ctx.room,
        # Audio is handled by the avatar, so disable room audio output
        room_output_options=RoomOutputOptions(audio_enabled=False),
    )


if __name__ == "__main__":
    # Configure and run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
            job_memory_warn_mb=2000,  # Higher memory limit for expression processing
            num_idle_processes=1,
            initialize_process_timeout=120,
        )
    )
