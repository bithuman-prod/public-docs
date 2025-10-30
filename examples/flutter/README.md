# Flutter + LiveKit + bitHuman Integration

This example demonstrates how to build a cross-platform Flutter app that integrates with [LiveKit Components](https://github.com/livekit/components-flutter) and bitHuman AI avatars for real-time video conversations.

## 🏗️ Architecture

```
Flutter App (livekit_components) ←→ LiveKit Cloud ←→ Python Agent ←→ bitHuman Avatar
     ↓                                   ↓
  User Video                       Token Server
```

### Key Components

- **Flutter Frontend**: Uses official `livekit_components` for production-ready UI
  - `LivekitRoom`: High-level wrapper for room connection
  - `ParticipantLoop`: Automatic participant grid with video rendering
  - `ControlBar`: Ready-to-use media controls
- **Token Server**: Generates secure JWT tokens
- **Python Agent**: Connects AI avatar to LiveKit room

## 🔑 Token Server

LiveKit requires JWT tokens for authentication. The token server generates these securely without exposing your API credentials to the client.

**Benefits**:
- 🔐 Keeps API secrets server-side
- ⏰ Short-lived tokens (1 hour)
- 🎯 Per-user, per-room permissions

## 🚀 Quick Start

### Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install) 3.0+
- Python 3.11+
- [LiveKit Cloud account](https://cloud.livekit.io) or self-hosted server
- [bitHuman API Secret](https://imaginex.bithuman.ai/#developer)
- [OpenAI API Key](https://platform.openai.com/api-keys)

### Setup Steps

#### 1. Configure Backend

```bash
cd backend
cp env.example .env
# Edit .env with your API keys
```

Required environment variables:
```bash
LIVEKIT_API_KEY=APIyour_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
BITHUMAN_API_SECRET=sk_bh_your_secret
OPENAI_API_KEY=sk-proj_your_key
```

#### 2. Start Services (3 terminals)

**Terminal 1 - Token Server:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python token_server.py
```

**Terminal 2 - LiveKit Agent:**
```bash
cd backend
source .venv/bin/activate
python agent.py dev
```

**Terminal 3 - Flutter App:**
```bash
cd frontend
export LIVEKIT_SERVER_URL="wss://your-project.livekit.cloud"
export LIVEKIT_TOKEN_ENDPOINT="http://localhost:3000/token"
flutter pub get
flutter run -d chrome --web-port 8080
```

## 📱 Features

- ✅ Real-time video chat with AI avatar
- ✅ Voice interaction with OpenAI Realtime API
- ✅ Cross-platform (Web, iOS, Android)
- ✅ Automatic agent connection
- ✅ Secure token-based authentication
- ✅ Production-ready UI with LiveKit Components

## 🔧 Key Configuration

### LiveKit Components Integration

This app uses the official [livekit_components](https://github.com/livekit/components-flutter) package for a clean, maintainable architecture:

**Key Features:**
- 🎥 Full-screen AI Avatar video display
- 🔊 Automatic audio playback from AI Avatar
- 🚫 Automatic filtering of local user video (only shows remote AI Avatar)
- 🎨 Floating control bar with gradient overlay
- ⏳ Loading indicator while waiting for avatar connection

### Backend Integration

The Flutter frontend connects to a Python LiveKit agent that handles AI avatar generation:

**Backend Architecture:**
```
Flutter App → LiveKit Cloud → Python Agent → bitHuman Avatar API
```

**Key Backend Components:**
- **Token Server**: Flask app generating JWT tokens
- **LiveKit Agent**: Python agent connecting as `bithuman-avatar-agent`
- **Audio Pipeline**: `RoomIO` → `AgentSession` → `TranscriptSynchronizer` → `DataStreamIO`
- **Video Pipeline**: Real-time avatar video generation and streaming

```dart
// Full-screen AI Avatar with automatic audio playback
LivekitRoom(
  roomContext: RoomContext(
    url: serverUrl,
    token: token,
    connect: true,
  ),
  builder: (context, roomCtx) {
    return Scaffold(
      body: Stack(
        children: [
          // Full-screen video for AI Avatar
          Positioned.fill(
            child: ParticipantLoop(
              participantTrackBuilder: (context, trackIdentifier) {
                final participant = trackIdentifier.participant;
                final track = trackIdentifier.track?.track;
                
                // Only show remote participants (AI Avatar)
                if (participant is! RemoteParticipant) {
                  return const SizedBox.shrink();
                }
                
                // Render video full-screen
                if (track is VideoTrack) {
                  return VideoTrackRenderer(
                    track,
                    fit: VideoViewFit.cover,
                  );
                }
                
                return const SizedBox.shrink();
              },
              showAudioTracks: true,  // Automatic audio playback
              showVideoTracks: true,
              layoutBuilder: _FullScreenLayoutBuilder(),
            ),
          ),
          
          // Floating control bar
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: ControlBar(),
          ),
        ],
      ),
    );
  },
)
```

### Room and Participant Names

The app generates random room and participant names on startup:

- **Room Name**: `room-{12-char alphanumeric}` (e.g., `room-a3b5c7d9e1f2`)
- **Participant Name**: `user-{random}` (e.g., `user-5678`)

Names are cached for the session, so they stay the same throughout the app lifecycle.

You can override these with environment variables:
```bash
export LIVEKIT_ROOM_NAME="my-custom-room"
export LIVEKIT_PARTICIPANT_NAME="my-user"
```

## 🔍 Troubleshooting

### "Waiting for AI Avatar..." Forever

**Cause**: Agent runs with `WorkerType.ROOM` which automatically joins any room when a participant enters

**Solution**: 
1. Check agent logs to see which room it joined
2. Check Flutter logs to see which room it created
3. The agent should automatically join the Flutter room
4. If not, restart the agent to ensure it's listening for new rooms

### "Failed to get token"

**Cause**: Token server not running

**Solution**:
```bash
cd backend
python token_server.py
# Test: curl http://localhost:3000/health
```

### Connection Failed

**Cause**: Wrong LiveKit URL or credentials

**Solution**:
1. Verify `backend/.env` has correct `LIVEKIT_URL`
2. Export same URL in Flutter:
   ```bash
   export LIVEKIT_SERVER_URL="wss://your-project.livekit.cloud"
   ```
3. Test with [LiveKit Playground](https://agents-playground.livekit.io)

### No Video Display

**Cause**: Track subscription issues or rendering problems

**Solution**: Using `livekit_components` handles track subscription and rendering automatically. Check:
1. Agent is publishing video track (check LiveKit dashboard)
2. Network connectivity is stable
3. Browser has video codec support

## 📚 Documentation

- [LiveKit Flutter SDK](https://docs.livekit.io/home/quickstarts/flutter/) - Official Flutter quickstart
- [LiveKit Components Flutter](https://github.com/livekit/components-flutter) - Official UI components (used in this app)
- [Backend README](./backend/README.md) - Agent setup details
- [Frontend README](./frontend/README.md) - Flutter configuration

## 🆘 Support

- 💬 [Discord](https://discord.gg/ES953n7bPA)
- 📖 [bitHuman Docs](https://docs.bithuman.ai)
- 🔧 [LiveKit Docs](https://docs.livekit.io)

---

**Ready to start?** Follow the Quick Start steps above!
