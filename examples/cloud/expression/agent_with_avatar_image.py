import logging
import os
from PIL import Image

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
logger = logging.getLogger("bithuman-expression-avatar-image")
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()


def load_avatar_image():
    """
    Load avatar image from various sources: local file, URL, or environment variable.
    Returns a PIL Image object or URL string.
    """
    # Option 1: Load from environment variable (URL or file path)
    avatar_image_source = os.getenv("BITHUMAN_AVATAR_IMAGE")
    
    if avatar_image_source:
        # Check if it's a URL
        if avatar_image_source.startswith(('http://', 'https://')):
            logger.info(f"Using avatar image from URL: {avatar_image_source}")
            return avatar_image_source
        # Check if it's a local file path
        elif os.path.exists(avatar_image_source):
            logger.info(f"Loading avatar image from file: {avatar_image_source}")
            return Image.open(avatar_image_source)
        else:
            logger.warning(f"Avatar image source not found: {avatar_image_source}")
    
    # Option 2: Load from local file in the same directory
    local_avatar_path = os.path.join(os.path.dirname(__file__), "avatar.jpg")
    if os.path.exists(local_avatar_path):
        logger.info(f"Using local avatar image: {local_avatar_path}")
        return Image.open(local_avatar_path)
    
    # Option 3: Use a default URL image (example)
    default_avatar_url = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face"
    logger.info(f"Using default avatar image from URL: {default_avatar_url}")
    return default_avatar_url


async def entrypoint(ctx: JobContext):
    """
    Advanced LiveKit agent with bitHuman avatar using custom avatar_image.
    This example demonstrates how to use custom images (local files or URLs) for avatars.
    """
    # Connect to the LiveKit room
    await ctx.connect()

    # Wait for at least one participant to join the room
    await ctx.wait_for_participant()

    logger.info("Starting bitHuman expression avatar with custom avatar_image")
    
    # Load the avatar image
    avatar_image = load_avatar_image()
    
    # Initialize bitHuman avatar session with custom avatar_image
    bithuman_avatar = bithuman.AvatarSession(
        api_secret=os.getenv("BITHUMAN_API_SECRET"),
        avatar_image=avatar_image,  # Can be PIL Image object or URL string
        
        # Optional: Additional avatar configuration for custom images
        # avatar_voice_id="your_voice_id",     # Custom voice if available
        # avatar_motion_scale=1.0,             # Motion intensity (0.0-2.0)
        # avatar_expression_scale=1.5,         # Expression intensity (0.0-2.0)
        # enable_face_detection=True,          # Auto-detect face in image
        # crop_to_face=True,                   # Auto-crop image to face region
    )

    # Configure the AI agent session
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice=os.getenv("OPENAI_VOICE", "ash"),  # Use a different default voice
            model="gpt-4o-mini-realtime-preview",
        ),
        vad=silero.VAD.load()
    )

    # Start the bitHuman avatar session
    await bithuman_avatar.start(
        session, 
        room=ctx.room
    )

    # Customized personality for image-based avatars
    avatar_personality = os.getenv("AVATAR_PERSONALITY", 
        "You are a personalized virtual assistant with a unique appearance. "
        "Embrace your custom look and be confident in your interactions. "
        "Use expressive gestures and maintain an engaging personality. "
        "Respond naturally and show genuine interest in conversations."
    )

    # Start the AI agent session
    await session.start(
        agent=Agent(
            instructions=avatar_personality
        ),
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
            job_memory_warn_mb=2500,  # Higher memory for image processing
            num_idle_processes=1,
            initialize_process_timeout=180,  # Longer timeout for image processing
        )
    )
