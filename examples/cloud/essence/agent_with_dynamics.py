"""
Agent with Dynamics - Enhanced Avatar Agent with RPC-based Dynamic Gestures

This example extends the basic agent.py with dynamic gesture triggering via RPC.
It demonstrates how to trigger avatar gestures based on user speech keywords,
enabling reactive and contextual avatar animations.

Features:
- All functionality from agent.py (basic avatar agent)
- Point-to-point RPC messaging for gesture triggers
- Keyword-based gesture activation from voice transcription (e.g., "laugh" -> laugh_react)
- Keyword-based gesture activation from text input (e.g., typing "funny" -> laugh_react)
- Functional programming patterns with reusable abstractions

Performance Note:
- Avatar worker model connection and loading typically takes approximately 20 seconds
  on first initialization.
"""

import asyncio
import json
import logging
import os
from collections.abc import Callable
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    RoomOutputOptions,
    UserInputTranscribedEvent,
    WorkerOptions,
    WorkerType,
    cli,
)
from livekit.agents.voice.room_io import TextInputEvent
from livekit.plugins import bithuman, openai, silero

# Configure logging
logger = logging.getLogger("bithuman-dynamics-agent")
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

# Keyword-to-action mapping for dynamic gesture triggers
KEYWORD_ACTION_MAP: dict[str, str] = {
    "laugh": "laugh_react",
    "laughing": "laugh_react",
    "haha": "laugh_react",
    "funny": "laugh_react",
    # Add more keyword mappings as needed
    # "nod": "nod_react",
    # "yes": "nod_react",
    # "smile": "smile_react",
}

# RPC method name for dynamics triggers
RPC_METHOD_TRIGGER_DYNAMICS = "trigger_dynamics"


def create_dynamics_payload(action: str, identity: str) -> dict[str, Any]:
    """
    Create a standardized payload for dynamics RPC messages.

    Args:
        action: The gesture action to trigger
        identity: The identity of the participant triggering the action

    Returns:
        Dictionary containing action, identity, and timestamp
    """
    return {
        "action": action,
        "identity": identity,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def send_rpc_message(
    local_participant: rtc.LocalParticipant,
    destination_identity: str,
    method: str,
    payload: dict[str, Any],
    timeout: int = 10,
) -> dict[str, Any] | None:
    """
    Send a point-to-point RPC message to a specific participant.

    This is a functional abstraction for RPC communication, following
    the pattern from core-agent-worker/handlers/rpc_handler.py.

    Args:
        local_participant: The local participant instance
        destination_identity: Target participant identity
        method: RPC method name
        payload: Message payload dictionary
        timeout: Timeout in seconds

    Returns:
        Response data dictionary or None if failed
    """
    try:
        payload_str = json.dumps(payload)

        logger.info(
            f"Sending RPC message to {destination_identity}: {method} (action: {payload.get('action')})"
        )
        logger.debug(f"RPC payload: {payload_str}")

        response = await local_participant.perform_rpc(
            destination_identity=destination_identity,
            method=method,
            payload=payload_str,
            response_timeout=timeout,
        )

        if response:
            logger.info(f"RPC response received from {destination_identity}")
            logger.debug(f"RPC response: {response}")
            return json.loads(response) if isinstance(response, str) else response

        return None

    except rtc.RpcError as e:
        if e.code == 1400:  # Method not supported
            logger.debug(
                f"RPC method '{method}' not supported by {destination_identity}"
            )
        else:
            logger.error(f"RPC error {e.code}: {e.message}")
            if e.data:
                logger.error(f"Error data: {e.data}")
        return None
    except Exception as e:
        logger.error(f"Failed to send RPC message: {str(e)}")
        return None


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


async def trigger_dynamics_for_participants(
    room: rtc.Room,
    local_participant: rtc.LocalParticipant,
    action: str,
    exclude_identities: list[str] | None = None,
) -> dict[str, Any]:
    """
    Trigger dynamics action for all remote participants in the room.

    Sends point-to-point RPC messages to each participant concurrently.

    Args:
        room: LiveKit room instance
        local_participant: Local participant instance
        action: The gesture action to trigger
        exclude_identities: Optional list of identities to exclude

    Returns:
        Dictionary mapping participant identity to response
    """
    exclude_identities = exclude_identities or []
    results = {}

    # Get all remote participants
    participants = [
        identity
        for identity in room.remote_participants.keys()
        if identity not in exclude_identities
    ]

    if not participants:
        logger.warning("No participants to send dynamics trigger to")
        return results

    logger.info(
        f"Triggering dynamics action '{action}' for {len(participants)} participants"
    )

    # Create payload once
    payload = create_dynamics_payload(
        action=action,
        identity=local_participant.identity,
    )

    # Send to all participants concurrently
    tasks = [
        (
            identity,
            asyncio.create_task(
                send_rpc_message(
                    local_participant=local_participant,
                    destination_identity=identity,
                    method=RPC_METHOD_TRIGGER_DYNAMICS,
                    payload=payload,
                )
            ),
        )
        for identity in participants
    ]

    # Wait for all responses
    for identity, task in tasks:
        try:
            response = await task
            results[identity] = response
        except Exception as e:
            logger.error(f"Failed to get response from {identity}: {str(e)}")
            results[identity] = None

    return results


def create_keyword_handler(
    room: rtc.Room,
    local_participant: rtc.LocalParticipant,
    keyword_map: dict[str, str] = KEYWORD_ACTION_MAP,
) -> Callable[[UserInputTranscribedEvent], None]:
    """
    Create a keyword detection handler for user input transcription events.

    This is a higher-order function that returns a configured event handler,
    following functional programming principles for reusability.

    Args:
        room: LiveKit room instance
        local_participant: Local participant instance
        keyword_map: Keyword to action mapping

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
            logger.info(f"🎭 Triggering dynamics action: {action}")

            # Trigger dynamics for all participants
            try:
                results = await trigger_dynamics_for_participants(
                    room=room,
                    local_participant=local_participant,
                    action=action,
                )

                # Log results
                success_count = sum(1 for r in results.values() if r is not None)
                logger.info(
                    f"Dynamics trigger completed: {success_count}/{len(results)} successful"
                )
            except Exception as e:
                logger.error(f"Failed to trigger dynamics: {str(e)}")

    return handle_keyword_trigger


def create_text_input_handler(
    room: rtc.Room,
    local_participant: rtc.LocalParticipant,
    keyword_map: dict[str, str] = KEYWORD_ACTION_MAP,
) -> Callable[[AgentSession, TextInputEvent], None]:
    """
    Create a text input handler for detecting keywords and triggering dynamics.

    This is a higher-order function that returns a configured text input callback,
    following functional programming principles for reusability.

    Args:
        room: LiveKit room instance
        local_participant: Local participant instance
        keyword_map: Keyword to action mapping

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
            logger.info(f"🎭 Triggering dynamics action from text input: {action}")

            # Trigger dynamics for all participants
            try:
                results = await trigger_dynamics_for_participants(
                    room=room,
                    local_participant=local_participant,
                    action=action,
                )

                # Log results
                success_count = sum(1 for r in results.values() if r is not None)
                logger.info(
                    f"Dynamics trigger from text input completed: {success_count}/{len(results)} successful"
                )
            except Exception as e:
                logger.error(f"Failed to trigger dynamics from text input: {str(e)}")

        # Also generate a normal reply to the text input
        session.interrupt()
        session.generate_reply(user_input=text)

    return handle_text_input


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the LiveKit agent with bitHuman avatar integration
    and dynamic gesture triggering via RPC.

    This extends the basic agent.py with:
    - RPC-based dynamic gesture triggering
    - Keyword-based gesture activation from voice transcription
    - Keyword-based gesture activation from text input
    - Point-to-point communication with avatar workers
    """
    # Connect to the LiveKit room
    await ctx.connect()

    # Wait for at least one participant to join the room
    await ctx.wait_for_participant()

    logger.info("Starting bitHuman avatar runtime with dynamics support")

    # Validate required environment variables
    api_secret = os.getenv("BITHUMAN_API_SECRET")
    if not api_secret:
        raise ValueError("BITHUMAN_API_SECRET environment variable is required")

    avatar_id = os.getenv("BITHUMAN_AVATAR_ID", "A31KJC8622")
    logger.info(f"Using avatar ID: {avatar_id}")

    # Initialize bitHuman avatar session with avatar_id
    try:
        bithuman_avatar = bithuman.AvatarSession(
            api_secret=api_secret,
            avatar_id=avatar_id,
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
            voice="coral",
            model="gpt-4o-mini-realtime-preview",
        ),
        min_interruption_words=0,
        resume_false_interruption=False,
        min_interruption_duration=0.1,
        min_endpointing_delay=0.3,
        vad=silero.VAD.load(),
        turn_detection="vad",
    )

    # Start the bitHuman avatar session
    try:
        logger.info("Starting BitHuman avatar session...")
        await bithuman_avatar.start(session, room=ctx.room)
        logger.info("BitHuman avatar session started successfully")
    except Exception as e:
        logger.error(f"Failed to start BitHuman avatar session: {str(e)}")
        logger.error("This could be due to:")
        logger.error("1. Avatar ID not found or inaccessible")
        logger.error("2. Insufficient resources in CPU mode")
        logger.error("3. BitHuman service temporary unavailability")
        logger.error("4. Network connectivity issues")

        error_msg = str(e).lower()
        if "avatar session failed" in error_msg:
            logger.error("💡 Suggested fixes:")
            logger.error(
                "   - Try a different avatar ID from https://imaginex.bithuman.ai/#community"
            )
            logger.error("   - Check if the avatar supports CPU mode")
            logger.error("   - Verify your account has access to this avatar")

        raise

    # Setup event handlers to monitor interruption behavior
    @session.on("user_state_changed")
    def on_user_state_changed(event):
        logger.info(f"👤 [USER_STATE] {event.old_state} -> {event.new_state}")
        if event.new_state == "speaking":
            logger.info(
                "🎤 [INTERRUPTION] User started speaking - interruption should trigger now"
            )

    @session.on("agent_state_changed")
    def on_agent_state_changed(event):
        logger.info(f"🤖 [AGENT_STATE] {event.old_state} -> {event.new_state}")
        if event.new_state == "speaking":
            logger.info(
                "🔊 [INTERRUPTION] Agent started speaking - can be interrupted now"
            )

    @session.on("agent_false_interruption")
    def on_agent_false_interruption(event):
        logger.warning(f"⚠️  [FALSE_INTERRUPTION] Detected at {event.created_at}")

    # Setup keyword-based dynamics trigger handler
    keyword_handler = create_keyword_handler(
        room=ctx.room,
        local_participant=ctx.room.local_participant,
        keyword_map=KEYWORD_ACTION_MAP,
    )

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):
        """Handle user input transcription and trigger dynamics if keyword detected."""
        asyncio.create_task(keyword_handler(event))

    logger.info("✅ Keyword-based dynamics trigger handler registered")
    logger.info(f"   Supported keywords: {list(KEYWORD_ACTION_MAP.keys())}")

    # Setup text input handler for dynamics triggering
    text_input_handler = create_text_input_handler(
        room=ctx.room,
        local_participant=ctx.room.local_participant,
        keyword_map=KEYWORD_ACTION_MAP,
    )

    # Configure room input options with text input enabled and custom callback
    room_input_options = RoomInputOptions(
        text_enabled=True,
        text_input_cb=text_input_handler,
    )

    logger.info("✅ Text input handler registered for dynamics triggering")

    # Start the AI agent session
    await session.start(
        agent=Agent(
            instructions=(
                "You are a helpful assistant. Talk to users naturally and respond "
                "shortly and concisely. Keep conversations engaging and friendly."
            )
        ),
        room=ctx.room,
        room_input_options=room_input_options,
        room_output_options=RoomOutputOptions(audio_enabled=False),
    )

    logger.info(
        "✅ Agent session started with VAD-based interruption and dynamics support"
    )


if __name__ == "__main__":
    # Configure and run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
            job_memory_warn_mb=1500,
            num_idle_processes=1,
            initialize_process_timeout=120,
        )
    )
