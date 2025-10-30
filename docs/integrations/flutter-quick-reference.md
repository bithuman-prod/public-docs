# Flutter + LiveKit + bitHuman Quick Reference

> **Copy & Paste Ready** - One-minute setup with latest LiveKit Components

## 🚀 One-Minute Setup

### 1. Create Project
```bash
mkdir flutter-bithuman-avatar && cd flutter-bithuman-avatar
mkdir -p backend frontend/lib
```

### 2. Backend (Python)
```bash
cd backend

# Dependencies
cat > requirements.txt << EOF
# LiveKit Agent bundle with OpenAI, bitHuman and Silero plugins
livekit-agents[openai,bithuman,silero]>=1.2.16

# Environment and configuration
python-dotenv>=1.1.1

# Logging and utilities
loguru>=0.7.3

# Token server
flask>=3.0.3
flask-cors>=4.0.0
livekit>=0.11.0

# Optional utilities
requests>=2.31.0
aiohttp>=3.8.0

# Optional audio processing
numpy>=2.3.3
scipy>=1.16.2
EOF

# Environment
cat > .env << EOF
BITHUMAN_API_SECRET=sk_bh_your_secret_here
BITHUMAN_AVATAR_ID=A33NZN6384
OPENAI_API_KEY=sk-proj_your_key_here
LIVEKIT_API_KEY=APIyour_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
EOF

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend (Flutter)
```bash
cd ../frontend

# Create Flutter project
flutter create . --org com.bithuman.avatar

# Update pubspec.yaml
cat > pubspec.yaml << EOF
name: bithuman_flutter_integration
description: Flutter frontend for bitHuman AI avatar integration with LiveKit
publish_to: 'none'

version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: ">=3.0.0"

dependencies:
  flutter:
    sdk: flutter
  
  # LiveKit components (includes livekit_client) - fixed version
  livekit_components: 1.2.2+hotfix.1
  
  # HTTP requests for token generation
  http: ^1.1.0
  
  # UI components
  cupertino_icons: ^1.0.6
  
  # Structured logging
  logging: ^1.2.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  # Code generation (optional)
  json_serializable: ^6.7.1
  build_runner: ^2.4.7
  
  # Linting
  flutter_lints: ^6.0.0

flutter:
  uses-material-design: true
EOF

flutter pub get
```

## 📱 Complete Flutter Code

### main.dart
```dart
import 'package:flutter/material.dart';
import 'package:livekit_client/livekit_client.dart' as lk;
import 'package:livekit_components/livekit_components.dart';
import 'package:logging/logging.dart';
import 'dart:convert';
import 'dart:math';

// Create logger instance
final _logger = Logger('BitHumanFlutter');

void main() {
  // Initialize logger (show info level and above)
  Logger.root.level = Level.INFO;
  Logger.root.onRecord.listen((record) {
    print('${record.level.name}: ${record.time}: ${record.message}');
  });
  
  runApp(const BitHumanFlutterApp());
}

class BitHumanFlutterApp extends StatelessWidget {
  const BitHumanFlutterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'bitHuman Flutter Integration',
      theme: LiveKitTheme().buildThemeData(context),
      themeMode: ThemeMode.dark,
      home: const ConnectionScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

/// Connection screen - handles token generation and room joining
class ConnectionScreen extends StatefulWidget {
  const ConnectionScreen({super.key});

  @override
  State<ConnectionScreen> createState() => _ConnectionScreenState();
}

class _ConnectionScreenState extends State<ConnectionScreen> {
  final Logger _logger = Logger('ConnectionScreen');
  bool _isConnecting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    // Auto-connect on startup
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _connect();
    });
  }

  Future<void> _connect() async {
    setState(() {
      _isConnecting = true;
      _error = null;
    });

    try {
      // Generate random room and participant names
      final roomName = _generateRoomName();
      final participantName = _generateParticipantName();
      
      _logger.info('Connecting to room: $roomName as $participantName');
      
      // Get token from server
      final tokenData = await _getToken(roomName, participantName);
      
      // Navigate to video room using LiveKit Components
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => VideoRoomScreen(
              url: tokenData['server_url'],
              token: tokenData['token'],
              roomName: roomName,
            ),
          ),
        );
      }
    } catch (e) {
      _logger.severe('Connection failed: $e');
      setState(() {
        _error = e.toString();
        _isConnecting = false;
      });
    }
  }

  String _generateRoomName() {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    final random = Random();
    return 'room-${String.fromCharCodes(Iterable.generate(12, (_) => chars.codeUnitAt(random.nextInt(chars.length))))}';
  }

  String _generateParticipantName() {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    final random = Random();
    return 'user-${String.fromCharCodes(Iterable.generate(8, (_) => chars.codeUnitAt(random.nextInt(chars.length))))}';
  }

  Future<Map<String, dynamic>> _getToken(String roomName, String participantName) async {
    const tokenEndpoint = 'http://localhost:3000/token';
    
    try {
      final response = await http.post(
        Uri.parse(tokenEndpoint),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'room': roomName,
          'participant': participantName,
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Token server returned ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to get token: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1a1a1a),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
            ),
            const SizedBox(height: 20),
            Text(
              _isConnecting ? 'Connecting to AI Avatar...' : 'Connection Failed',
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 18,
              ),
            ),
            if (_error != null) ...[
              const SizedBox(height: 16),
              Text(
                _error!,
                style: const TextStyle(
                  color: Colors.red,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _connect,
                child: const Text('Retry'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Video room screen using LiveKit Components for full-screen AI Avatar display
class VideoRoomScreen extends StatefulWidget {
  final String url;
  final String token;
  final String roomName;

  const VideoRoomScreen({
    super.key,
    required this.url,
    required this.token,
    required this.roomName,
  });

  @override
  State<VideoRoomScreen> createState() => _VideoRoomScreenState();
}

class _VideoRoomScreenState extends State<VideoRoomScreen> {
  @override
  Widget build(BuildContext context) {
    // Use LiveKit Components' LivekitRoom widget
    return LivekitRoom(
      roomContext: RoomContext(
        url: widget.url,
        token: widget.token,
        connect: true,
        roomOptions: lk.RoomOptions(
          adaptiveStream: true,
          dynacast: true,
          defaultAudioPublishOptions: lk.AudioPublishOptions(dtx: true),
          defaultVideoPublishOptions: lk.VideoPublishOptions(simulcast: true),
        ),
      ),
      builder: (context, roomCtx) {
        // Enable microphone by default
        WidgetsBinding.instance.addPostFrameCallback((_) {
          try {
            roomCtx.room.localParticipant?.setMicrophoneEnabled(true);
          } catch (error) {
            _logger.warning('Could not enable microphone: $error');
          }
        });

        return Scaffold(
          appBar: AppBar(
            title: Text('Room: ${widget.roomName}'),
            backgroundColor: const Color(0xFF1a1a1a),
          ),
          backgroundColor: const Color(0xFF1a1a1a),
          body: Stack(
            children: [
              // Full-screen video for AI Avatar
              Positioned.fill(
                child: Container(
                  color: Colors.black,
                  child: _VideoDisplayWidget(roomCtx: roomCtx),
                ),
              ),
              
              // Audio handling
              Positioned.fill(
                child: _AudioHandlerWidget(roomCtx: roomCtx),
              ),
              
              // Loading overlay
              Positioned.fill(
                child: _LoadingOverlay(),
              ),
            ],
          ),
        );
      },
    );
  }
}

/// Video display widget with caching to prevent re-rendering
class _VideoDisplayWidget extends StatefulWidget {
  final RoomContext roomCtx;
  
  const _VideoDisplayWidget({required this.roomCtx});
  
  @override
  State<_VideoDisplayWidget> createState() => _VideoDisplayWidgetState();
}

class _VideoDisplayWidgetState extends State<_VideoDisplayWidget> {
  lk.VideoTrackRenderer? _cachedVideoRenderer;
  String? _lastVideoTrackId;
  
  @override
  void initState() {
    super.initState();
    widget.roomCtx.room.addListener(_onRoomChanged);
  }
  
  @override
  void dispose() {
    widget.roomCtx.room.removeListener(_onRoomChanged);
    super.dispose();
  }
  
  void _onRoomChanged() {
    if (mounted) setState(() {});
  }
  
  @override
  Widget build(BuildContext context) {
    final remoteParticipants = widget.roomCtx.room.remoteParticipants.values.toList();
    
    if (remoteParticipants.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(valueColor: AlwaysStoppedAnimation<Color>(Colors.blue)),
            SizedBox(height: 16),
            Text('Waiting for AI Avatar...', style: TextStyle(color: Colors.white70)),
          ],
        ),
      );
    }
    
    for (final participant in remoteParticipants) {
      final videoTracks = participant.videoTrackPublications
          .where((pub) => pub.track != null)
          .toList();
      
      if (videoTracks.isNotEmpty) {
        final videoTrack = videoTracks.first.track as lk.VideoTrack;
        
        if (_lastVideoTrackId != videoTrack.sid) {
          _cachedVideoRenderer = lk.VideoTrackRenderer(
            videoTrack,
            fit: lk.VideoViewFit.cover,
          );
          _lastVideoTrackId = videoTrack.sid;
        }
        
        return Container(
          color: Colors.black,
          child: _cachedVideoRenderer!,
        );
      }
    }
    
    return const Center(
      child: Text('AI Avatar connected but no video yet', 
        style: TextStyle(color: Colors.white70)),
    );
  }
}

/// Audio handler widget
class _AudioHandlerWidget extends StatefulWidget {
  final RoomContext roomCtx;
  const _AudioHandlerWidget({required this.roomCtx});
  
  @override
  State<_AudioHandlerWidget> createState() => _AudioHandlerWidgetState();
}

class _AudioHandlerWidgetState extends State<_AudioHandlerWidget> {
  @override
  Widget build(BuildContext context) {
    // Audio is handled automatically by LiveKit Components
    return const SizedBox.shrink();
  }
}

/// Loading overlay
class _LoadingOverlay extends StatefulWidget {
  @override
  State<_LoadingOverlay> createState() => _LoadingOverlayState();
}

class _LoadingOverlayState extends State<_LoadingOverlay> {
  @override
  Widget build(BuildContext context) {
    final roomContext = RoomContext.of(context);
    
    if (roomContext != null) {
      final hasRemoteVideo = roomContext.room.remoteParticipants.values
          .any((participant) => participant.videoTrackPublications.isNotEmpty);
      
      if (!hasRemoteVideo) {
        return Container(
          color: Colors.black.withOpacity(0.8),
          child: const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(valueColor: AlwaysStoppedAnimation<Color>(Colors.blue)),
                SizedBox(height: 16),
                Text('Waiting for AI Avatar video...', style: TextStyle(color: Colors.white70)),
              ],
            ),
          ),
        );
      }
    }
    
    return const SizedBox.shrink();
  }
```

## 🐍 Complete Python Backend

### agent.py
```python
import asyncio
import os
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero
from livekit import rtc
from bithuman import BitHumanAvatar

async def entrypoint(ctx: JobContext):
    # Initialize voice assistant
    assistant = VoiceAssistant(
        vad=await silero.VAD.create(),
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
    )
    
    # Initialize bitHuman avatar
    avatar = BitHumanAvatar(
        api_secret=os.getenv("BITHUMAN_API_SECRET"),
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID", "A33NZN6384"),
    )
    
    # Connect avatar to room
    await avatar.connect(ctx.room)
    
    # Start voice assistant
    await assistant.start(ctx.room, ctx.participant)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

### token_server.py
```python
from flask import Flask, request, jsonify
from livekit import api
from datetime import timedelta
import os

app = Flask(__name__)

@app.route('/token', methods=['POST'])
def create_token():
    data = request.get_json() or {}
    room = data.get('room', 'flutter-avatar-room')
    identity = data.get('participant', 'Flutter User')
    
    at = api.AccessToken(
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET"),
        identity=identity
    )
    at.add_grant(api.VideoGrant(room_join=True, room=room))
    at.ttl = timedelta(hours=1)
    
    return jsonify({
        'token': at.to_jwt(),
        'server_url': os.getenv("LIVEKIT_URL")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
```

## 🚀 Run Everything

### 1. Start Backend
```bash
cd backend
source .venv/bin/activate
python agent.py &
python token_server.py &
```

### 2. Start Frontend
```bash
cd frontend
flutter run
```

## ✅ Success Criteria

- ✅ Flutter app connects to LiveKit room
- ✅ AI Avatar appears in video
- ✅ Audio works (speech recognition + synthesis)
- ✅ No flashing during speech
- ✅ Clean console output (INFO level logs)

## 🐛 Common Issues

- **No video**: Check if backend agent is running
- **No audio**: Verify microphone permissions
- **Connection failed**: Check token server and LiveKit credentials

## 📚 Next Steps

- Customize avatar appearance
- Add more conversation features
- Deploy to production
- Add error handling

## 📚 Full Documentation

For detailed implementation guide, see [Flutter Integration Guide](./flutter-integration.md)
