#!/usr/bin/env python3
"""
Simple token generation server for Flutter integration.
This server generates LiveKit access tokens for the Flutter app.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from livekit import api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for all routes (allow all origins for development)
CORS(app, origins='*')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# LiveKit configuration
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

# Default room configuration
DEFAULT_ROOM_NAME = "flutter-avatar-room"
DEFAULT_PARTICIPANT_NAME = "Flutter User"

def validate_config():
    """Validate required configuration."""
    if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL]):
        raise ValueError("Missing required LiveKit configuration")

def generate_token(room_name: str, participant_name: str, identity: str = None) -> str:
    """Generate LiveKit access token."""
    try:
        # Use identity if provided, otherwise use participant_name
        if not identity:
            identity = participant_name
        
        # Create access token with proper parameters using the correct API
        token = (api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
                .with_identity(identity)
                .with_ttl(timedelta(hours=1))
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                )))
        
        # Generate JWT token
        jwt_token = token.to_jwt()
        
        logger.info(f"Generated token for participant '{identity}' in room '{room_name}'")
        return jwt_token
        
    except Exception as e:
        logger.error(f"Failed to generate token: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "livekit-token-server"
    })

@app.route('/token', methods=['POST'])
def create_token():
    """Create LiveKit access token."""
    try:
        # Get request data
        data = request.get_json() or {}
        
        room_name = data.get('room', DEFAULT_ROOM_NAME)
        participant_name = data.get('participant', DEFAULT_PARTICIPANT_NAME)
        identity = data.get('identity', participant_name)
        
        # Validate inputs
        if not room_name or not participant_name:
            return jsonify({
                "error": "Missing required parameters: room and participant"
            }), 400
        
        # Generate token
        token = generate_token(room_name, participant_name, identity)
        
        return jsonify({
            "token": token,
            "room": room_name,
            "participant": participant_name,
            "identity": identity,
            "expires_in": 3600,  # 1 hour
            "server_url": LIVEKIT_URL,
            "issuer": LIVEKIT_API_KEY  # for local debugging only
        })
        
    except Exception as e:
        logger.error(f"Token generation error: {e}")
        return jsonify({
            "error": "Failed to generate token",
            "message": str(e)
        }), 500

@app.route('/token', methods=['GET'])
def create_token_get():
    """Create LiveKit access token via GET request."""
    try:
        # Get query parameters
        room_name = request.args.get('room', DEFAULT_ROOM_NAME)
        participant_name = request.args.get('participant', DEFAULT_PARTICIPANT_NAME)
        identity = request.args.get('identity', participant_name)
        
        # Generate token
        token = generate_token(room_name, participant_name, identity)
        
        return jsonify({
            "token": token,
            "room": room_name,
            "participant": participant_name,
            "identity": identity,
            "expires_in": 3600,
            "server_url": LIVEKIT_URL,
            "issuer": LIVEKIT_API_KEY  # for local debugging only
        })
        
    except Exception as e:
        logger.error(f"Token generation error: {e}")
        return jsonify({
            "error": "Failed to generate token",
            "message": str(e)
        }), 500

@app.route('/config', methods=['GET'])
def get_config():
    """Get server configuration."""
    return jsonify({
        "livekit_url": LIVEKIT_URL,
        "default_room": DEFAULT_ROOM_NAME,
        "default_participant": DEFAULT_PARTICIPANT_NAME,
        "token_expiry_hours": 1
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /health",
            "GET /token",
            "POST /token",
            "GET /config"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500

if __name__ == '__main__':
    try:
        # Validate configuration
        validate_config()
        
        # Get configuration
        port = int(os.getenv('TOKEN_SERVER_PORT', 3000))
        host = os.getenv('TOKEN_SERVER_HOST', '0.0.0.0')
        debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        
        logger.info(f"Starting token server on {host}:{port}")
        logger.info(f"LiveKit URL: {LIVEKIT_URL}")
        logger.info(f"Default room: {DEFAULT_ROOM_NAME}")
        
        # Run the server
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start token server: {e}")
        exit(1)
