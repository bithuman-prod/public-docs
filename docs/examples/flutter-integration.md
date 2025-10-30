# Flutter Integration Example

> **Cross-platform mobile app with AI avatar integration**

Build a Flutter app that connects to bitHuman AI avatars through LiveKit for real-time video chat experiences.

![Flutter Integration](../assets/images/flutter-integration-preview.jpg)
*Flutter app with AI avatar integration*

---

## ✨ What This Example Does

- **Cross-platform**: Works on iOS, Android, and Web
- **Real-time Video**: Live AI avatar video streaming
- **Voice Interaction**: Two-way audio communication
- **Modern UI**: Beautiful, responsive interface
- **Easy Setup**: Follow the guide to get running quickly

## 🏗️ Architecture

```
Flutter App ←→ LiveKit Room ←→ Python Agent ←→ bitHuman Avatar
     ↓              ↓              ↓              ↓
  Video/Audio   Real-time      AI Processing   Avatar Rendering
  Capture      Streaming       (OpenAI)        (Cloud)
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Navigate to backend
cd examples/flutter/backend

# Create environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run diagnostic check
python diagnose.py

# Start the agent
python agent.py dev
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd examples/flutter/frontend

# Install dependencies
flutter pub get

# Configure LiveKit settings
# Edit lib/config/livekit_config.dart

# Run the app
flutter run
```

## 🔧 Configuration

### Backend Configuration

Create `.env` file in `backend/` directory:

```bash
# bitHuman API Configuration
BITHUMAN_API_SECRET=sk_bh_your_api_secret_here
BITHUMAN_AVATAR_ID=A33NZN6384  # Optional: Use specific avatar

# OpenAI Configuration
OPENAI_API_KEY=sk-proj_your_openai_api_key_here

# LiveKit Configuration
LIVEKIT_API_KEY=APIyour_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

### Frontend Configuration

Edit `lib/config/livekit_config.dart`:

```dart
class LiveKitConfig {
  static const String serverUrl = 'wss://your-project.livekit.cloud';
  static const String? tokenEndpoint = 'http://localhost:3000/token';
  static const String roomName = 'flutter-avatar-room';
  static const String participantName = 'Flutter User';
}
```

## 📱 Features

### Core Features
- **Real-time Video Chat**: Connect with AI avatar through LiveKit
- **Voice Interaction**: Natural conversation with OpenAI Realtime API
- **Cross-platform**: Single codebase for mobile and web
- **Responsive UI**: Adaptive design for different screen sizes

### UI Components
- **Video Views**: Remote avatar and local camera preview
- **Media Controls**: Mute, camera, speaker, disconnect
- **Connection Status**: Real-time connection indicators
- **Error Handling**: Graceful error management

### Platform Support
- **iOS**: 12.0+ with camera/microphone permissions
- **Android**: API 21+ with required permissions
- **Web**: Modern browsers with HTTPS support

## 🧪 Testing

### Backend Testing

1. **Diagnostic Check**:
   ```bash
   python diagnose.py
   ```

2. **LiveKit Playground**:
   - Start agent: `python agent.py dev`
   - Visit: https://agents-playground.livekit.io
   - Use same LiveKit credentials

### Flutter Testing

1. **Unit Tests**:
   ```bash
   flutter test
   ```

2. **Manual Testing**:
   - Test on different devices
   - Test camera/microphone permissions
   - Test network connectivity
   - Test avatar loading

## 🎨 Customization

### Avatar Selection

Edit `backend/agent.py`:

```python
# Use specific avatar ID
avatar_id = os.getenv("BITHUMAN_AVATAR_ID", "A33NZN6384")

# Or use custom avatar image
bithuman_avatar = bithuman.AvatarSession(
    api_secret=api_secret,
    avatar_image="path/to/your/image.jpg"
)
```

### AI Personality

Customize the AI instructions:

```python
agent_instructions = """
You are a helpful AI assistant integrated with a Flutter mobile app.
Respond naturally and concisely to user questions.
Keep responses brief and engaging for mobile users.
"""
```

### UI Customization

Modify `lib/theme/app_theme.dart`:

```dart
class AppTheme {
  static const Color primaryColor = Color(0xFF2196F3);
  static const Color videoBackgroundColor = Color(0xFF1E1E1E);
  static const Color controlActiveColor = Color(0xFF4CAF50);
}
```

## 🚀 Deployment

### Backend Deployment

#### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "agent.py", "start"]
```

#### Cloud Platforms
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Heroku
- Railway

### Flutter Deployment

#### Mobile
```bash
# iOS
flutter build ios --release

# Android
flutter build apk --release
flutter build appbundle --release
```

#### Web
```bash
flutter build web --release
# Deploy to Firebase, Vercel, Netlify, etc.
```

## 🔍 Troubleshooting

### Common Issues

1. **"No camera found"**
   - Check device permissions
   - Verify camera not in use
   - Test on different device

2. **"Connection failed"**
   - Verify LiveKit server URL
   - Check token validity
   - Ensure backend is running

3. **"Avatar not showing"**
   - Check backend logs
   - Verify bitHuman API key
   - Test with LiveKit Playground

### Debug Mode

#### Backend
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Flutter
```dart
import 'package:logger/logger.dart';
final logger = Logger('MyApp');
logger.d('Debug message');
```

## 📚 Next Steps

1. **Customize UI**: Modify the interface to match your brand
2. **Add Features**: Implement chat, screen sharing, etc.
3. **Optimize Performance**: Fine-tune for your use case
4. **Deploy**: Publish to app stores or web

## 🆘 Support

- 💬 [Discord Community](https://discord.gg/ES953n7bPA)
- 📖 [Flutter Documentation](https://docs.flutter.dev)
- 🔧 [LiveKit Flutter SDK](https://pub.dev/packages/livekit_client)
- 🎯 [bitHuman Documentation](https://docs.bithuman.ai)

---

**Ready to start?** Follow the setup instructions above and check the [Complete Integration Guide](../integrations/flutter-integration.md) for detailed documentation!
