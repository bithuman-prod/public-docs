# Flutter + LiveKit + bitHuman Quick Start

Get your Flutter app with AI avatar integration running in 5 minutes!

## 🛠️ Install Flutter (macOS quick steps)

```bash
# 1) Install Flutter SDK
brew install --cask flutter

# 2) Add Flutter to PATH (zsh)
echo 'export PATH="$PATH:/Applications/flutter/bin"' >> ~/.zprofile
source ~/.zprofile

# 3) Verify
flutter --version

# 4) Doctor (toolchains)
flutter doctor

# iOS (optional): accept Xcode license if prompted
sudo xcodebuild -license

# Android (optional): accept Android licenses after installing Android Studio SDK
flutter doctor --android-licenses

# Enable Web for fastest run from browser
flutter config --enable-web
```

If you installed Flutter by extracting to $HOME/flutter, add that to PATH instead:
```bash
echo 'export PATH="$PATH:$HOME/flutter/bin"' >> ~/.zprofile
source ~/.zprofile
```

### Platform Support

This Flutter app supports:
- **Web**: Run in browser (fastest to test)
- **Android**: Mobile app
- **iOS**: Mobile app

**Quick test on web:**
```bash
cd frontend
flutter run -d chrome
```

**Available devices:**
```bash
flutter devices
```

### Troubleshooting

If you encounter shader compilation errors on macOS:
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter run -d chrome --web-port 8080

# Alternative: Use different port
flutter run -d chrome --web-port 3000
```

If Flutter doctor shows issues:
```bash
# Install missing dependencies
brew install cocoapods
flutter doctor --android-licenses
```

## 🚀 One-Command Setup

### Option 1: Backend + Token Server (Recommended for Production)

```bash
# Terminal 1: Start backend with avatar
./start_backend.sh

# Terminal 2: Start token server
./start_token_server.sh
```

**Note**: The Agent will automatically connect to any room that the Flutter app creates, no need to manually specify room name.

# Terminal 3: Start Flutter app
cd frontend
flutter run
```

### Option 2: Backend Only (Development/Testing)

```bash
# Start backend
./start_backend.sh

# Start Flutter app with direct token
cd frontend
# Edit lib/config/livekit_config.dart to use directToken
flutter run
```

**Why Token Server?**
- 🔐 **Security**: Keeps LiveKit API secret on server-side
- ⏰ **Time-limited**: Generates short-lived tokens (1 hour)
- 🎯 **Control**: Per-user, per-room permissions
- 📊 **Auditing**: Track usage and access

## ⚡ Super Quick Test

1. **Get your credentials**:
   - bitHuman API Secret: [imaginex.bithuman.ai](https://imaginex.bithuman.ai/#developer)
   - OpenAI API Key: [platform.openai.com](https://platform.openai.com/api-keys)
   - LiveKit Credentials: [livekit.io](https://livekit.io)

2. **Configure backend**:
   ```bash
   cd backend
   cp env.example .env
   # Edit .env with your credentials
   ```

3. **Start everything**:
   ```bash
   # Terminal 1
   ./start_backend.sh
   
   # Terminal 2  
   ./start_token_server.sh
   
   # Terminal 3
   cd frontend && flutter run
   ```

4. **Test with LiveKit Playground**:
   - Visit: https://agents-playground.livekit.io
   - Use your LiveKit credentials
   - Connect and see the avatar!

## 🔧 Configuration

### Backend (.env)
```bash
BITHUMAN_API_SECRET=sk_bh_your_secret_here
OPENAI_API_KEY=sk-proj_your_key_here
LIVEKIT_API_KEY=APIyour_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

### Flutter (Quick Test - No Backend Required)
```bash
# For quick testing without backend setup
cd frontend
flutter run -d chrome --web-port 8080
```

The app will use demo configuration and test tokens automatically.

### Flutter (With Custom Configuration)
```bash
# Set LiveKit server URL
export LIVEKIT_SERVER_URL="wss://your-project.livekit.cloud"

# Set token endpoint (recommended)
export LIVEKIT_TOKEN_ENDPOINT="http://localhost:3000/token"

# Or set direct token for testing (NOT for production)
export LIVEKIT_TOKEN="your-jwt-token-here"

# Optional: Set room and participant names
export LIVEKIT_ROOM_NAME="flutter-avatar-room"
export LIVEKIT_PARTICIPANT_NAME="Flutter User"
```

See `frontend/CONFIG.md` for detailed configuration options.

## 🎯 What You'll See

- **Flutter App**: Cross-platform mobile/web interface
- **AI Avatar**: Real-time video with synchronized speech
- **Voice Chat**: Natural conversation with OpenAI
- **Media Controls**: Mute, camera, speaker controls

## 🆘 Troubleshooting

### Backend Issues
```bash
# Run diagnostics
cd backend
python diagnose.py

# Check logs
python agent.py dev
```

### Flutter Issues
```bash
# Check dependencies
flutter pub get

# Clean and rebuild
flutter clean
flutter pub get
flutter run
```

### Common Fixes
- **"Avatar not showing"**: Check bitHuman API key
- **"Connection failed"**: Verify LiveKit credentials
- **"No camera"**: Check device permissions

## 📚 Next Steps

1. **Customize Avatar**: Change avatar ID in backend
2. **Modify UI**: Edit Flutter theme and components
3. **Add Features**: Implement chat, screen sharing
4. **Deploy**: Publish to app stores

## 🆘 Need Help?

- 💬 [Discord Community](https://discord.gg/ES953n7bPA)
- 📖 [Complete Guide](../docs/integrations/flutter-integration.md)
- 🔧 [Backend README](./backend/README.md)
- 📱 [Frontend README](./frontend/README.md)

---

**Ready?** Run `./start_backend.sh` and start building! 🚀
