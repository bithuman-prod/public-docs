"""
LiveKit Agent with BitHuman Avatar using Custom GPU Endpoint

This example demonstrates how to use a custom GPU avatar worker endpoint
(e.g., self-hosted gpu-avatar-worker, Cerebrium deployment) instead of
the default BitHuman cloud API.

Custom endpoints are useful for:
- Self-hosted GPU avatar workers
- Cerebrium/Replicate/Modal deployments
- Private cloud deployments with custom authentication
- Testing and development environments

Required Environment Variables:
- BITHUMAN_API_SECRET: BitHuman API secret for authorization and authentication
- CUSTOM_GPU_URL: Your custom GPU worker endpoint URL
- CUSTOM_GPU_TOKEN: API token for Bearer authentication with custom GPU endpoint
- LIVEKIT_URL: LiveKit server URL
- LIVEKIT_API_KEY: LiveKit API key
- LIVEKIT_API_SECRET: LiveKit API secret
- OPENAI_API_KEY: OpenAI API key (for realtime model)

Optional Environment Variables:
- BITHUMAN_AVATAR_IMAGE: Path to local image or URL for avatar
- OPENAI_VOICE: Voice for OpenAI realtime model (default: ash)
- AVATAR_PERSONALITY: Custom personality prompt for the avatar
"""

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
from PIL import Image

# Configure logging
logger = logging.getLogger("bithuman-custom-gpu-endpoint")
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()


def get_custom_gpu_endpoint() -> str:
    """
    Get the custom GPU endpoint URL from environment or configuration.

    Supported endpoint formats:
    - Cerebrium: https://api.aws.us-east-1.cerebrium.ai/v4/{project}/gpu-avatar-worker/launch
    - Self-hosted: https://your-domain.com/launch
    - Local development: http://localhost:8089/launch

    Returns:
        str: The custom GPU endpoint URL

    Raises:
        ValueError: If no custom endpoint is configured
    """
    custom_url = os.getenv("CUSTOM_GPU_URL")

    if not custom_url:
        # Fallback to common deployment patterns
        cerebrium_project = os.getenv("CEREBRIUM_PROJECT_ID")
        if cerebrium_project:
            custom_url = (
                f"https://api.aws.us-east-1.cerebrium.ai/v4/"
                f"{cerebrium_project}/gpu-avatar-worker/launch"
            )
            logger.info(f"Using Cerebrium endpoint: {custom_url}")
        else:
            raise ValueError(
                "CUSTOM_GPU_URL environment variable is required. "
                "Set it to your custom GPU avatar worker endpoint URL."
            )

    logger.info(f"Using custom GPU endpoint: {custom_url}")
    return custom_url


def load_avatar_image() -> Image.Image | str | None:
    """
    Load avatar image from various sources.

    Priority order:
    1. BITHUMAN_AVATAR_IMAGE environment variable (URL or file path)
    2. Local avatar.jpg file in the same directory
    3. None (let the worker use its default avatar)

    Returns:
        PIL Image object, URL string, or None
    """
    avatar_source = os.getenv("BITHUMAN_AVATAR_IMAGE")

    if avatar_source:
        # Check if it's a URL
        if avatar_source.startswith(("http://", "https://")):
            logger.info(f"Using avatar image from URL: {avatar_source}")
            return avatar_source
        # Check if it's a local file path
        elif os.path.exists(avatar_source):
            logger.info(f"Loading avatar image from file: {avatar_source}")
            return Image.open(avatar_source)
        else:
            logger.warning(f"Avatar image source not found: {avatar_source}")

    # Try local avatar.jpg in same directory
    local_avatar_path = os.path.join(os.path.dirname(__file__), "avatar.jpg")
    if os.path.exists(local_avatar_path):
        logger.info(f"Using local avatar image: {local_avatar_path}")
        return Image.open(local_avatar_path)

    # No avatar image - worker will use its default
    logger.info("No avatar image specified, using worker default")
    return None


async def entrypoint(ctx: JobContext):
    """
    LiveKit agent entrypoint with custom GPU avatar endpoint.

    This example shows how to connect to a self-hosted or custom-deployed
    GPU avatar worker instead of the default BitHuman cloud service.
    """
    # Connect to the LiveKit room
    await ctx.connect()

    # Wait for a participant to join
    await ctx.wait_for_participant()

    logger.info("Starting bitHuman avatar with custom GPU endpoint")

    # Get custom GPU endpoint URL
    custom_gpu_url = get_custom_gpu_endpoint()

    # Load avatar image (optional)
    avatar_image = load_avatar_image()

    # Initialize bitHuman avatar session with custom GPU endpoint
    # When api_url is a custom endpoint (not default BitHuman API),
    # the plugin automatically uses FormData format compatible with
    # gpu-avatar-worker's /launch endpoint
    bithuman_avatar = bithuman.AvatarSession(
        # BitHuman API secret for authorization and authentication (required)
        api_secret=os.getenv("BITHUMAN_API_SECRET"),
        # Custom GPU endpoint URL - triggers FormData mode
        api_url=custom_gpu_url,
        # API token for Bearer authentication with custom GPU endpoint (required)
        api_token=os.getenv("CUSTOM_GPU_TOKEN"),
        # Avatar image - sent as file upload or URL to the worker
        avatar_image=avatar_image,
        # Optional: Pre-configured avatar ID on the worker
        avatar_id="A82GTB4785",
    )

    # Configure the AI agent session with OpenAI Realtime
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice=os.getenv("OPENAI_VOICE", "ash"),
            model="gpt-4o-mini-realtime-preview",
        ),
        vad=silero.VAD.load(),
    )

    # Start the bitHuman avatar session
    # This will POST to your custom GPU endpoint with:
    # - livekit_url, livekit_token, room_name (form fields)
    # - avatar_image (file) or avatar_image_url (form field)
    # - avatar_id (form field, if provided)
    await bithuman_avatar.start(
        session,
        room=ctx.room,
    )

    # Custom personality for GPU-rendered avatar
    avatar_personality = os.getenv(
        "AVATAR_PERSONALITY",
        "You are a helpful and engaging virtual assistant powered by advanced "
        "GPU rendering technology. Your expressions and movements are fluid "
        "and natural. Maintain a warm, professional demeanor while being "
        "responsive to the user's emotional cues. Speak clearly and expressively.",
    )

    # Start the AI agent session
    await session.start(
        agent=Agent(instructions=avatar_personality),
        room=ctx.room,
        # Audio is handled by the avatar, so disable room audio output
        room_output_options=RoomOutputOptions(audio_enabled=False),
    )

    logger.info("Agent session started successfully with custom GPU endpoint")


if __name__ == "__main__":
    # Run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
            # Higher memory limit for GPU avatar processing
            job_memory_warn_mb=3000,
            num_idle_processes=1,
            # Longer timeout for GPU model initialization
            initialize_process_timeout=240,
        )
    )
