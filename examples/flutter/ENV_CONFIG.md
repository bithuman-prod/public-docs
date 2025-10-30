# Environment Configuration

This document explains how to configure the Flutter integration using environment variables.

## Quick Setup

1. **Create a `.env` file** in the `flutter` directory:
   ```bash
   cd /Users/cathyli/Code/bitHuman/public-docs/examples/flutter
   cp .env.example .env  # If .env.example exists
   # Or create .env manually
   ```

2. **Add your configuration** to `.env`:
   ```bash
   # LiveKit Configuration
   LIVEKIT_SERVER_URL=wss://your-project.livekit.cloud
   LIVEKIT_TOKEN_ENDPOINT=http://localhost:3000/token
   # LIVEKIT_ROOM_NAME=my-custom-room  # Optional: auto-generated if not set
   LIVEKIT_PARTICIPANT_NAME=Flutter Dev User
   
   # Optional: Direct token (for testing without token server)
   # LIVEKIT_TOKEN=your_jwt_token_here
   ```

3. **Run the development script**:
   ```bash
   ./start_flutter_dev.sh
   ```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LIVEKIT_SERVER_URL` | Your LiveKit project WebSocket URL | `` | Yes |
| `LIVEKIT_TOKEN_ENDPOINT` | Token server endpoint | `http://localhost:3000/token` | Yes |
| `LIVEKIT_ROOM_NAME` | Room name to join | Auto-generated random name | No |
| `LIVEKIT_PARTICIPANT_NAME` | Participant name | `Flutter Dev User` | No |
| `LIVEKIT_TOKEN` | Direct JWT token (optional) | - | No |

## Alternative: Direct Environment Variables

You can also set environment variables directly before running the script:

```bash
export LIVEKIT_SERVER_URL="wss://your-project.livekit.cloud"
export LIVEKIT_TOKEN_ENDPOINT="http://localhost:3000/token"
# export LIVEKIT_ROOM_NAME="my-room"  # Optional: auto-generated if not set
# export LIVEKIT_PARTICIPANT_NAME="My Name"  # Optional: auto-generated if not set
./start_flutter_dev.sh
```

## How It Works

The Flutter integration supports multiple configuration methods:

1. **Environment Variables** (`.env` file or system env vars)
2. **Dart Defines** (compile-time constants passed via `--dart-define`)
3. **URL Parameters** (for web only, passed via query string)

**Priority Order:**
1. URL Parameters (highest priority, web only)
2. Environment Variables (from `.env` or system)
3. Dart Defines (compile-time constants)
4. Default values (lowest priority)

**For Web Platform:**
- Flutter Web cannot access system environment variables directly
- The script uses `--dart-define` to pass environment variables as compile-time constants
- URL parameters are also supported for runtime configuration

**For Mobile/Desktop:**
- Can access system environment variables directly
- Also supports dart-define for consistency

## Web URL Parameters

For Flutter Web, you can also pass configuration via URL parameters:

```
http://localhost:8080/?serverUrl=wss://your-project.livekit.cloud&tokenEndpoint=http://localhost:3000/token&room=my-room&participant=My%20Name
```

**Note:** Both `room` and `participant` parameters are optional. If not provided, Flutter will generate random names like `flutter-room-1234` and `user-5678` respectively.

## Backend Configuration

Make sure your backend `.env` file has the matching LiveKit credentials:

```bash
# In backend/.env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

The `LIVEKIT_URL` in the backend must match the `LIVEKIT_SERVER_URL` in the frontend.
