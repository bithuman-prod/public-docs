"""
Dynamics Handler Module

This module provides gesture/dynamics triggering functionality for the
Gemini Live Avatar application. It supports:
- Keyword-based gesture activation from transcription
- Automatic gesture discovery from bitHuman Dynamics API
- Cooldown management to prevent gesture spam
- Direct VideoControl-based gesture triggers

Usage:
    handler = DynamicsHandler(bithuman_runtime, agent_id, api_secret)
    await handler.initialize()
    await handler.check_and_trigger("hello there!")  # Triggers wave gesture
"""

import logging
import time
from typing import Optional

import requests

from bithuman import AsyncBithuman
from bithuman.api import VideoControl

# Configure logging
logger = logging.getLogger("gemini-live-avatar-dynamics")
logger.setLevel(logging.INFO)

# Default keyword-to-action mapping
DEFAULT_KEYWORD_ACTION_MAP: dict[str, str] = {
    # Greetings
    "hello": "mini_wave_hello",
    "hi": "mini_wave_hello",
    "hey": "mini_wave_hello",
    "goodbye": "mini_wave_hello",
    "bye": "mini_wave_hello",
    "wave": "mini_wave_hello",
    # Laughter
    "laugh": "laugh_react",
    "laughing": "laugh_react",
    "haha": "laugh_react",
    "funny": "laugh_react",
    "hilarious": "laugh_react",
    "lol": "laugh_react",
}


def get_available_gestures(agent_id: str, api_secret: str) -> dict[str, str]:
    """
    Get available gestures from bitHuman Dynamics API.

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
                    "wave": gesture_key,
                }
            )
        elif "laugh" in gesture_lower:
            keyword_map.update(
                {
                    "laugh": gesture_key,
                    "laughing": gesture_key,
                    "haha": gesture_key,
                    "funny": gesture_key,
                    "hilarious": gesture_key,
                    "lol": gesture_key,
                }
            )

    return keyword_map


def detect_keyword_action(
    transcript: str, keyword_map: dict[str, str]
) -> Optional[str]:
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


class DynamicsHandler:
    """
    Handler for avatar dynamics/gestures.

    Manages gesture triggering based on:
    - Keyword detection in transcriptions
    - Manual trigger requests
    - Cooldown management to prevent spam
    """

    def __init__(
        self,
        bithuman_runtime: AsyncBithuman,
        agent_id: Optional[str] = None,
        api_secret: Optional[str] = None,
        cooldown_seconds: float = 3.0,
    ):
        """
        Initialize the dynamics handler.

        Args:
            bithuman_runtime: bitHuman runtime instance
            agent_id: Optional agent ID for fetching dynamics from API
            api_secret: Optional API secret for authentication
            cooldown_seconds: Cooldown period between same gesture triggers
        """
        self.runtime = bithuman_runtime
        self.agent_id = agent_id
        self.api_secret = api_secret
        self.cooldown_seconds = cooldown_seconds

        # Gesture state
        self.keyword_map: dict[str, str] = DEFAULT_KEYWORD_ACTION_MAP.copy()
        self.available_gestures: dict[str, str] = {}
        self.gesture_cooldowns: dict[str, float] = {}

        self._initialized = False

    async def initialize(self):
        """Initialize the dynamics handler by fetching available gestures."""
        if self._initialized:
            return

        logger.info("Initializing dynamics handler...")

        # Try to fetch gestures from API if credentials provided
        if self.agent_id and self.api_secret:
            logger.info("Fetching gestures from Dynamics API...")
            self.available_gestures = get_available_gestures(
                self.agent_id, self.api_secret
            )

            if self.available_gestures:
                # Create keyword map from available gestures
                api_keyword_map = create_keyword_map_from_gestures(
                    self.available_gestures
                )
                # Merge with defaults (API gestures take precedence)
                self.keyword_map.update(api_keyword_map)
                logger.info(
                    f"Loaded {len(self.available_gestures)} gestures from Dynamics API"
                )
                logger.info(
                    f"Available gestures: {list(self.available_gestures.keys())}"
                )
            else:
                logger.info("No gestures found from API, using default mappings")
        else:
            logger.info("No agent ID provided, using default keyword mappings")

        logger.info(f"Keyword mappings configured: {list(self.keyword_map.keys())}")
        self._initialized = True

    async def trigger_gesture(self, action: str) -> bool:
        """
        Trigger a gesture action on the avatar.

        Args:
            action: The gesture action name to trigger

        Returns:
            True if gesture was triggered, False if on cooldown or failed
        """
        # Check cooldown
        current_time = time.time()
        last_trigger = self.gesture_cooldowns.get(action, 0)

        if current_time - last_trigger < self.cooldown_seconds:
            logger.debug(f"Gesture '{action}' is on cooldown, skipping")
            return False

        # Trigger the gesture
        try:
            logger.info(f"🎭 Triggering gesture: {action}")
            await self.runtime.push(VideoControl(action=action))
            self.gesture_cooldowns[action] = current_time
            return True
        except Exception as e:
            logger.error(f"Failed to trigger gesture '{action}': {e}")
            return False

    async def check_and_trigger(self, transcript: str) -> Optional[str]:
        """
        Check transcript for keywords and trigger corresponding gesture.

        Args:
            transcript: The transcribed text to check

        Returns:
            The triggered action name, or None if no keyword matched
        """
        if not transcript:
            return None

        # Detect keyword and corresponding action
        action = detect_keyword_action(transcript, self.keyword_map)

        if action:
            triggered = await self.trigger_gesture(action)
            if triggered:
                return action

        return None

    def add_keyword_mapping(self, keyword: str, action: str):
        """
        Add a custom keyword-to-action mapping.

        Args:
            keyword: The keyword to detect (case-insensitive)
            action: The gesture action to trigger
        """
        self.keyword_map[keyword.lower()] = action
        logger.info(f"Added keyword mapping: '{keyword}' -> '{action}'")

    def remove_keyword_mapping(self, keyword: str):
        """
        Remove a keyword mapping.

        Args:
            keyword: The keyword to remove
        """
        keyword_lower = keyword.lower()
        if keyword_lower in self.keyword_map:
            del self.keyword_map[keyword_lower]
            logger.info(f"Removed keyword mapping: '{keyword}'")

    def set_cooldown(self, seconds: float):
        """
        Set the cooldown period for gesture triggers.

        Args:
            seconds: Cooldown period in seconds
        """
        self.cooldown_seconds = seconds
        logger.info(f"Gesture cooldown set to {seconds} seconds")

    def reset_cooldowns(self):
        """Reset all gesture cooldowns."""
        self.gesture_cooldowns.clear()
        logger.info("All gesture cooldowns reset")

    def get_available_actions(self) -> list[str]:
        """
        Get list of all available gesture actions.

        Returns:
            List of action names
        """
        actions = set(self.keyword_map.values())
        if self.available_gestures:
            actions.update(self.available_gestures.keys())
        return sorted(actions)

    def get_keyword_mappings(self) -> dict[str, str]:
        """
        Get current keyword-to-action mappings.

        Returns:
            Dictionary of keyword to action mappings
        """
        return self.keyword_map.copy()
