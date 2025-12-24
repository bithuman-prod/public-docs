"""
Agent with Dynamics - Self-Hosted Avatar Agent with Dynamic Gestures

This example extends the basic agent.py with dynamic gesture triggering.
It demonstrates how to trigger avatar gestures based on user speech keywords,
enabling reactive and contextual avatar animations.

Features:
- All functionality from agent.py (basic avatar agent)
- Direct VideoControl-based gesture triggers (self-hosted pattern)
- Keyword-based gesture activation from voice transcription (e.g., "laugh" -> laugh_react)
- Keyword-based gesture activation from text input (e.g., typing "funny" -> laugh_react)
- Functional programming patterns with reusable abstractions
- Automatic gesture discovery from Dynamics API

Performance Note:
- Avatar worker model connection and loading typically takes approximately 20 seconds
  on first initialization.
"""

import asyncio
import logging
import os
import time
from collections.abc import Callable

import requests
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    UserInputTranscribedEvent,
    WorkerOptions,
    WorkerType,
    cli,
)
from livekit.agents.voice.room_io import TextInputEvent
from livekit.plugins import bithuman, openai, silero

from bithuman import AsyncBithuman
from bithuman.api import VideoControl

# Configure logging
logger = logging.getLogger("bithuman-selfhosted-dynamics-agent")
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

# Default keyword-to-action mapping (can be overridden by Dynamics API)
DEFAULT_KEYWORD_ACTION_MAP: dict[str, str] = {
    "laugh": "laugh_react",
    "laughing": "laugh_react",
    "haha": "laugh_react",
    "funny": "laugh_react",
    "hello": "mini_wave_hello",
    "hi": "mini_wave_hello",
    "hey": "mini_wave_hello",
    "goodbye": "mini_wave_hello",
    "bye": "mini_wave_hello",
}


def get_available_gestures(agent_id: str, api_secret: str) -> dict[str, str]:
    """
    Get available gestures from Dynamics API.

    Args:
        agent_id: Agent ID to get dynamics for
        api_secret: API secret for authentication

    Returns:
        Dictionary mapping gesture keys to video URLs, or empty dict if failed
    """
    try:
        url = f"https://public.api.bithuman.ai/v1/dynamics/{agent_id}"
        headers = {"api-secret": api_secret}

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                gestures = data["data"].get("gestures", {})
                logger.info(f"Retrieved {len(gestures)} gestures from Dynamics API")
                return gestures
            else:
                logger.warning("Dynamics API returned success=false")
        else:
            logger.warning(f"Dynamics API returned status {response.status_code}")
    except Exception as e:
        logger.warning(f"Failed to get gestures from Dynamics API: {e}")

    return {}


def create_keyword_map_from_gestures(gestures: dict[str, str]) -> dict[str, str]:
    """
    Create a keyword-to-action mapping from available gestures.

    This creates basic keyword mappings based on gesture names.
    Users can customize this mapping as needed.

    Args:
        gestures: Dictionary of gesture keys to video URLs

    Returns:
        Keyword-to-action mapping dictionary
    """
    keyword_map = {}

    # Create mappings based on gesture names
    for gesture_key in gestures.keys():
        gesture_lower = gesture_key.lower()

        # Map common gesture patterns to keywords
        if "wave" in gesture_lower or "hello" in gesture_lower:
            keyword_map.update(
                {
                    "hello": gesture_key,
                    "hi": gesture_key,
                    "hey": gesture_key,
                    "goodbye": gesture_key,
                    "bye": gesture_key,
                }
            )
        elif "laugh" in gesture_lower:
            keyword_map.update(
                {
                    "laugh": gesture_key,
                    "laughing": gesture_key,
                    "haha": gesture_key,
                    "funny": gesture_key,
                }
            )
        elif "nod" in gesture_lower:
            keyword_map.update(
                {
                    "yes": gesture_key,
                    "nod": gesture_key,
                    "agree": gesture_key,
                }
            )
        elif "kiss" in gesture_lower or "heart" in gesture_lower:
            keyword_map.update(
                {
                    "kiss": gesture_key,
                    "love": gesture_key,
                }
            )

    return keyword_map


def detect_keyword_action(transcript: str, keyword_map: dict[str, str]) -> str | None:
    """
    Detect if transcript contains any keywords and return corresponding action.

    Uses case-insensitive matching for robust keyword detection.

    Args:
        transcript: User transcript text
        keyword_map: Mapping from keywords to actions

    Returns:
        Action string if keyword found, None otherwise
    """
    transcript_lower = transcript.lower()

    for keyword, action in keyword_map.items():
        if keyword in transcript_lower:
            logger.info(f"Keyword '{keyword}' detected -> action: {action}")
            return action

    return None


def create_keyword_handler(
    bithuman_avatar: bithuman.AvatarSession,
    keyword_map: dict[str, str],
    gesture_cooldowns: dict[str, float],
    cooldown_seconds: float = 3.0,
) -> Callable[[UserInputTranscribedEvent], None]:
    """
    Create a keyword detection handler for user input transcription events.

    Args:
        bithuman_avatar: BitHuman avatar session instance
        keyword_map: Keyword to action mapping
        gesture_cooldowns: Dictionary to track gesture cooldown timestamps
        cooldown_seconds: Cooldown period in seconds between same gesture triggers

    Returns:
        Event handler function for user_input_transcribed events
    """

    async def handle_keyword_trigger(event: UserInputTranscribedEvent) -> None:
        """Handle user input transcription and trigger dynamics if keyword detected."""
        if not event.is_final:
            return

        transcript = event.transcript.strip()
        if not transcript:
            return

        logger.info(f"User transcript (final): {transcript}")

        # Detect keyword and corresponding action
        action = detect_keyword_action(transcript, keyword_map)

        if action:
            # Check cooldown
            current_time = time.time()
            last_trigger = gesture_cooldowns.get(action, 0)

            if current_time - last_trigger < cooldown_seconds:
                logger.debug(f"Gesture {action} is on cooldown, skipping")
                return

            logger.info(f"🎭 Triggering dynamics action: {action}")

            try:
                # Use VideoControl to trigger gesture (self-hosted pattern)
                await bithuman_avatar.runtime.push(VideoControl(action=action))
                gesture_cooldowns[action] = current_time
            except Exception as e:
                logger.error(f"Failed to trigger dynamics: {str(e)}")

    return handle_keyword_trigger


def create_text_input_handler(
    bithuman_avatar: bithuman.AvatarSession,
    keyword_map: dict[str, str],
    gesture_cooldowns: dict[str, float],
    cooldown_seconds: float = 3.0,
) -> Callable[[AgentSession, TextInputEvent], None]:
    """
    Create a text input handler for detecting keywords and triggering dynamics.

    Args:
        bithuman_avatar: BitHuman avatar session instance
        keyword_map: Keyword to action mapping
        gesture_cooldowns: Dictionary to track gesture cooldown timestamps
        cooldown_seconds: Cooldown period in seconds between same gesture triggers

    Returns:
        Text input callback function
    """

    async def handle_text_input(session: AgentSession, event: TextInputEvent) -> None:
        """Handle text input and trigger dynamics if keyword detected."""
        text = event.text.strip()
        if not text:
            return

        logger.info(f"User text input received: {text}")

        # Detect keyword and corresponding action
        action = detect_keyword_action(text, keyword_map)

        if action:
            # Check cooldown
            current_time = time.time()
            last_trigger = gesture_cooldowns.get(action, 0)

            if current_time - last_trigger < cooldown_seconds:
                logger.debug(f"Gesture {action} is on cooldown, skipping")
            else:
                logger.info(f"🎭 Triggering dynamics action from text input: {action}")

                try:
                    # Use VideoControl to trigger gesture (self-hosted pattern)
                    await bithuman_avatar.runtime.push(VideoControl(action=action))
                    gesture_cooldowns[action] = current_time
                except Exception as e:
                    logger.error(
                        f"Failed to trigger dynamics from text input: {str(e)}"
                    )

        # Also generate a normal reply to the text input
        session.interrupt()
        session.generate_reply(user_input=text)

    return handle_text_input


def prewarm(proc: JobProcess):
    """Prewarm shared resources for faster connection times."""
    try:
        # Load VAD model
        proc.userdata["vad"] = silero.VAD.load(
            min_speech_duration=0.1,
            min_silence_duration=0.5,
            prefix_padding_duration=0.1,
        )
        logger.info("VAD model preloaded")

        # Check if runtime already prewarmed
        if "bithuman_runtime" in proc.userdata:
            logger.info("Runtime already prewarmed")
            return

        # Get model path
        model_path = os.getenv("BITHUMAN_MODEL_PATH")
        if not model_path:
            logger.warning("BITHUMAN_MODEL_PATH not set, skipping runtime prewarm")
            return

        # Prewarm runtime
        logger.info(f"Prewarming runtime: {model_path}")
        runtime = AsyncBithuman(
            model_path=model_path,
            api_secret=os.getenv("BITHUMAN_API_SECRET"),
            load_model=True,
        )
        proc.userdata["bithuman_runtime"] = runtime
        logger.info("Runtime prewarmed successfully")

    except Exception as e:
        logger.error(f"Prewarm failed: {e}")
        raise


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the self-hosted LiveKit agent with bitHuman avatar integration
    and dynamic gesture triggering.

    This extends the basic agent.py with:
    - VideoControl-based dynamic gesture triggering (self-hosted pattern)
    - Keyword-based gesture activation from voice transcription
    - Keyword-based gesture activation from text input
    - Automatic gesture discovery from Dynamics API
    """
    # Connect to the LiveKit room
    await ctx.connect()

    # Wait for at least one participant to join the room
    await ctx.wait_for_participant()

    logger.info("Starting bitHuman avatar runtime with dynamics support")

    # Validate required environment variables
    model_path = os.getenv("BITHUMAN_MODEL_PATH")
    api_secret = os.getenv("BITHUMAN_API_SECRET")
    agent_id = os.getenv("BITHUMAN_AGENT_ID")  # Optional, for fetching dynamics

    if not model_path:
        raise ValueError("BITHUMAN_MODEL_PATH environment variable is required")
    if not api_secret:
        raise ValueError("BITHUMAN_API_SECRET environment variable is required")

    # Initialize bitHuman avatar session with model_path (self-hosted mode)
    # Check if runtime was prewarmed
    runtime = ctx.proc.userdata.get("bithuman_runtime")

    try:
        avatar_kwargs = {
            "api_secret": api_secret,
            "model_path": model_path,  # Use model_path for self-hosted mode
        }

        # Use prewarmed runtime if available
        if runtime:
            logger.info("Using prewarmed runtime")
            avatar_kwargs["runtime"] = runtime

        bithuman_avatar = bithuman.AvatarSession(**avatar_kwargs)
        logger.info("BitHuman avatar session initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize BitHuman avatar session: {str(e)}")
        logger.error("Please check:")
        logger.error("1. BITHUMAN_API_SECRET is valid")
        logger.error(f"2. Model path '{model_path}' exists and is accessible")
        logger.error("3. BitHuman service is available")
        raise

    # Configure the AI agent session with OpenAI Realtime API
    # Use prewarmed VAD if available
    vad = ctx.proc.userdata.get("vad")
    if not vad:
        vad = silero.VAD.load(
            min_speech_duration=0.1,
            min_silence_duration=0.5,
            prefix_padding_duration=0.1,
        )

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral",
            model="gpt-4o-realtime-preview-2025-06-03",
            temperature=0.7,
        ),
        vad=vad,
    )

    # Start the bitHuman avatar session
    try:
        logger.info("Starting BitHuman avatar session...")
        await bithuman_avatar.start(session, room=ctx.room)
        logger.info("BitHuman avatar session started successfully")
    except Exception as e:
        logger.error(f"Failed to start BitHuman avatar session: {str(e)}")
        raise

    # Setup dynamics gestures
    gesture_cooldowns: dict[str, float] = {}
    keyword_map = DEFAULT_KEYWORD_ACTION_MAP.copy()

    if agent_id and api_secret:
        logger.info("🎭 Setting up dynamics gestures...")
        gestures = get_available_gestures(agent_id, api_secret)
        if gestures:
            # Create keyword map from available gestures
            keyword_map = create_keyword_map_from_gestures(gestures)
            logger.info(f"✅ Loaded {len(gestures)} gestures from Dynamics API")
            logger.info(f"   Available gestures: {list(gestures.keys())}")
        else:
            logger.info(
                "⚠️  No gestures found from Dynamics API, using default mappings"
            )
    else:
        logger.info("⚠️  Agent ID not provided, using default keyword mappings")

    logger.info(f"✅ Keyword mappings configured: {list(keyword_map.keys())}")

    # Setup keyword-based dynamics trigger handler for voice
    keyword_handler = create_keyword_handler(
        bithuman_avatar=bithuman_avatar,
        keyword_map=keyword_map,
        gesture_cooldowns=gesture_cooldowns,
        cooldown_seconds=3.0,
    )

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):
        """Handle user input transcription and trigger dynamics if keyword detected."""
        asyncio.create_task(keyword_handler(event))

    logger.info("✅ Keyword-based dynamics trigger handler registered for voice input")

    # Setup text input handler for dynamics triggering
    text_input_handler = create_text_input_handler(
        bithuman_avatar=bithuman_avatar,
        keyword_map=keyword_map,
        gesture_cooldowns=gesture_cooldowns,
        cooldown_seconds=3.0,
    )

    # Configure room input options with text input enabled
    room_input_options = RoomInputOptions(
        text_enabled=True,
        text_input_cb=text_input_handler,
    )

    logger.info("✅ Text input handler registered for dynamics triggering")

    # Start the AI agent session
    await session.start(
        agent=Agent(
            instructions=(
                "You are a helpful and engaging AI assistant with a visual avatar. "
                "Respond naturally and conversationally. Keep responses concise but friendly. "
                "You can express emotions through gestures, so feel free to be expressive."
            )
        ),
        room=ctx.room,
        room_input_options=room_input_options,
        room_output_options=RoomOutputOptions(audio_enabled=False),
    )

    logger.info("✅ Agent session started with dynamics support")


if __name__ == "__main__":
    # Configure and run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
            job_memory_warn_mb=8000,
            num_idle_processes=1,
            initialize_process_timeout=180,
            job_memory_limit_mb=8000,
            prewarm_fnc=prewarm,
        )
    )
