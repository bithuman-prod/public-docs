#!/usr/bin/env python3
"""
Simple token server for testing LiveKit Pipecat agent.

This server generates LiveKit access tokens for the test client.
Run this before using test_client.html.

Usage:
    python token_server.py

Then access test_client.html in your browser.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

try:
    from livekit import api
except ImportError:
    print("Error: livekit package not installed.")
    print("Install it with: pip install livekit")
    sys.exit(1)


class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for token generation."""
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        if parsed_path.path != "/token":
            self.send_error(404, "Not Found")
            return

        # Get parameters
        room_name = query_params.get("room", [None])[0]
        identity = query_params.get("identity", ["test-user"])[0]

        if not room_name:
            self.send_error(400, "Missing 'room' parameter")
            return

        # Get LiveKit credentials from environment
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")

        if not api_key or not api_secret:
            self.send_error(500, "LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")
            return

        try:
            # Generate token
            token = (
                api.AccessToken(api_key=api_key, api_secret=api_secret)
                .with_identity(identity)
                .with_name(identity)
                .with_grants(
                    api.VideoGrants(
                        room_join=True,
                        room=room_name,
                        can_publish=True,
                        can_subscribe=True,
                    )
                )
                .to_jwt()
            )

            # Return token as JSON
            response = {
                "token": token,
                "room": room_name,
                "identity": identity,
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header(
                "Access-Control-Allow-Origin", "*"
            )  # Allow CORS for local testing
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, f"Error generating token: {str(e)}")

    def log_message(self, format, *args):
        """Override to use print instead of stderr."""
        print(f"[TokenServer] {format % args}")


def main():
    """Run the token server."""
    port = 8080

    # Check environment variables
    if not os.getenv("LIVEKIT_API_KEY") or not os.getenv("LIVEKIT_API_SECRET"):
        print("Error: LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")
        print("\nSet them with:")
        print("  export LIVEKIT_API_KEY='your-api-key'")
        print("  export LIVEKIT_API_SECRET='your-api-secret'")
        sys.exit(1)

    server = HTTPServer(("localhost", port), TokenHandler)
    print(f"🚀 Token server running on http://localhost:{port}")
    print("📝 Make sure LIVEKIT_API_KEY and LIVEKIT_API_SECRET are set")
    print("\n💡 Usage:")
    print("   1. Keep this server running")
    print("   2. Open test_client.html in your browser")
    print(
        "   3. Start your agent: python agent_pipecat_livekit.py --room-name test-room"
    )
    print("\nPress Ctrl+C to stop the server")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Token server stopped")
        server.shutdown()


if __name__ == "__main__":
    main()
