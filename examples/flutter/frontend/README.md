# Flutter Frontend for bitHuman Integration

This Flutter application provides a cross-platform frontend for interacting with bitHuman AI avatars through LiveKit.

## 🏗️ Architecture

```
Flutter App
├── LiveKit Client SDK
├── Camera/Microphone Access
├── Real-time Video/Audio Streaming
└── UI Components
    ├── Video View (Remote Avatar)
    ├── Local Video Preview
    ├── Connection Status
    └── Controls (Mute, Camera, etc.)
```

## ✨ Features

- **Cross-platform**: iOS, Android, and Web support
- **Real-time Video**: Live avatar video streaming
- **Audio Communication**: Two-way voice interaction
- **Responsive UI**: Adaptive design for different screen sizes
- **Connection Management**: Automatic reconnection and error handling
- **Permissions Handling**: Camera and microphone permission management

## 🚀 Quick Start

### Prerequisites

- Flutter SDK 3.0 or higher
- Dart 3.0 or higher
- iOS 12.0+ / Android API 21+ / Modern web browser
- LiveKit backend running (see [Backend README](../backend/README.md))

### 1. Install Flutter

Follow the official [Flutter installation guide](https://docs.flutter.dev/get-started/install).

### 2. Get Dependencies

```bash
flutter pub get
```

### 3. Configure LiveKit

Edit `lib/config.dart`:

```dart
class LiveKitConfig {
  static const String serverUrl = 'wss://your-project.livekit.cloud';
  static const String token = 'your_livekit_token';
  // Or use token generation endpoint
  static const String tokenEndpoint = 'http://your-backend.com/token';
}
```

### 4. Run the App

```bash
# For mobile
flutter run

# For web
flutter run -d chrome

# For specific device
flutter devices
flutter run -d <device-id>
```

## 🔧 Configuration

### LiveKit Server Configuration

Update `lib/config.dart` with your LiveKit credentials:

```dart
class LiveKitConfig {
  // Option 1: Direct token (for testing)
  static const String serverUrl = 'wss://your-project.livekit.cloud';
  static const String token = 'your_livekit_token';
  
  // Option 2: Token generation endpoint (recommended for production)
  static const String tokenEndpoint = 'http://your-backend.com/token';
  static const String roomName = 'flutter-avatar-room';
  static const String participantName = 'Flutter User';
}
```

### UI Customization

Modify `lib/theme/app_theme.dart`:

```dart
class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      primarySwatch: Colors.blue,
      // Customize colors, fonts, etc.
    );
  }
}
```

### Camera/Microphone Settings

Update `lib/services/media_service.dart`:

```dart
class MediaService {
  static const CameraResolution resolution = CameraResolution.hd;
  static const AudioQuality audioQuality = AudioQuality.high;
  static const bool enableEchoCancellation = true;
}
```

## 📱 Platform-Specific Setup

### iOS Setup

1. **Camera/Microphone Permissions**

Add to `ios/Runner/Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>This app needs camera access for video calls with AI avatar</string>
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access for voice interaction with AI avatar</string>
```

2. **Minimum iOS Version**

Ensure `ios/Podfile` has:

```ruby
platform :ios, '12.0'
```

### Android Setup

1. **Camera/Microphone Permissions**

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

2. **Minimum Android Version**

Ensure `android/app/build.gradle` has:

```gradle
minSdkVersion 21
```

### Web Setup

1. **HTTPS Requirement**

LiveKit requires HTTPS for web. Use:

```bash
# Development
flutter run -d chrome --web-port 8080

# Production: Deploy to HTTPS-enabled hosting
```

2. **Web Permissions**

The app will automatically request camera/microphone permissions in the browser.

## 🎨 UI Components

### Main Components

- **`VideoCallScreen`**: Main video call interface
- **`RemoteVideoView`**: Displays the AI avatar video
- **`LocalVideoView`**: Shows local camera feed
- **`ConnectionStatus`**: Shows connection state
- **`MediaControls`**: Mute, camera, disconnect buttons

### Customization

```dart
// Customize video view
RemoteVideoView(
  track: remoteVideoTrack,
  fit: RTCVideoViewObjectFit.cover,
  mirror: false,
)

// Customize controls
MediaControls(
  onMuteToggle: () => toggleMicrophone(),
  onCameraToggle: () => toggleCamera(),
  onDisconnect: () => disconnect(),
)
```

## 🔌 Integration with Backend

### Token Generation

For production, implement token generation:

```dart
Future<String> generateToken() async {
  final response = await http.post(
    Uri.parse('${LiveKitConfig.tokenEndpoint}'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'room': LiveKitConfig.roomName,
      'identity': LiveKitConfig.participantName,
    }),
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['token'];
  } else {
    throw Exception('Failed to generate token');
  }
}
```

### Room Connection

```dart
Future<void> connectToRoom() async {
  try {
    // Generate or use token
    final token = await generateToken();
    
    // Create room
    final room = Room();
    
    // Connect to room
    await room.connect(LiveKitConfig.serverUrl, token);
    
    // Enable local media
    await room.localParticipant?.setMicrophoneEnabled(true);
    await room.localParticipant?.setCameraEnabled(true);
    
  } catch (e) {
    print('Connection failed: $e');
  }
}
```

## 🧪 Testing

### Unit Tests

```bash
flutter test
```

### Integration Tests

```bash
flutter test integration_test/
```

### Manual Testing

1. **Start Backend**: Run the Python agent
2. **Run Flutter App**: `flutter run`
3. **Test Connection**: Verify avatar appears
4. **Test Audio**: Speak and verify avatar responds
5. **Test Controls**: Test mute, camera, disconnect

### Debug Mode

```bash
# Enable debug logging
flutter run --debug

# Check logs
flutter logs
```

## 🚀 Deployment

### Mobile Deployment

#### iOS

1. **Configure signing** in Xcode
2. **Build for release**:
   ```bash
   flutter build ios --release
   ```
3. **Upload to App Store** via Xcode or App Store Connect

#### Android

1. **Generate signed APK**:
   ```bash
   flutter build apk --release
   ```
2. **Or generate App Bundle**:
   ```bash
   flutter build appbundle --release
   ```
3. **Upload to Google Play Console**

### Web Deployment

1. **Build for web**:
   ```bash
   flutter build web --release
   ```
2. **Deploy to hosting** (Firebase, Vercel, Netlify, etc.)
3. **Ensure HTTPS** is enabled

### Environment Configuration

For different environments:

```dart
// lib/config/environment.dart
enum Environment { development, staging, production }

class AppConfig {
  static const Environment env = Environment.development;
  
  static String get liveKitUrl {
    switch (env) {
      case Environment.development:
        return 'wss://dev-project.livekit.cloud';
      case Environment.staging:
        return 'wss://staging-project.livekit.cloud';
      case Environment.production:
        return 'wss://prod-project.livekit.cloud';
    }
  }
}
```

## 🔍 Troubleshooting

### Common Issues

1. **"No camera found"**
   - Check device permissions
   - Verify camera is not used by another app
   - Test on different device

2. **"Connection failed"**
   - Verify LiveKit server URL
   - Check token validity
   - Ensure backend is running

3. **"No audio"**
   - Check microphone permissions
   - Verify audio settings
   - Test with different browser/device

4. **"Avatar not showing"**
   - Check backend logs
   - Verify bitHuman API key
   - Test with LiveKit Playground

### Debug Information

Enable debug logging:

```dart
import 'package:flutter/foundation.dart';

void main() {
  if (kDebugMode) {
    // Enable debug logging
    Logger.root.level = Level.ALL;
  }
  runApp(MyApp());
}
```

### Performance Optimization

1. **Video Quality**: Adjust resolution based on device capabilities
2. **Memory Management**: Dispose resources properly
3. **Network Usage**: Optimize bitrate settings
4. **Battery Life**: Implement proper lifecycle management

## 📚 API Reference

### Key Classes

- **`VideoCallScreen`**: Main video call interface
- **`LiveKitService`**: LiveKit connection management
- **`MediaService`**: Camera/microphone handling
- **`ConnectionManager`**: Connection state management

### Key Methods

```dart
// Connect to room
Future<void> connectToRoom(String token)

// Toggle microphone
Future<void> toggleMicrophone()

// Toggle camera
Future<void> toggleCamera()

// Disconnect from room
Future<void> disconnect()
```

## 🆘 Support

- 💬 [Discord Community](https://discord.gg/ES953n7bPA)
- 📖 [Flutter Docs](https://docs.flutter.dev)
- 🔧 [LiveKit Flutter SDK](https://pub.dev/packages/livekit_client)
- 🎯 [bitHuman Docs](https://docs.bithuman.ai)

## 🎯 Next Steps

1. **Customize UI**: Modify the interface to match your brand
2. **Add Features**: Implement chat, screen sharing, etc.
3. **Optimize Performance**: Fine-tune for your use case
4. **Deploy**: Publish to app stores or web

---

**Ready to start?** Follow the setup instructions above and check the [Backend README](../backend/README.md) to get the full system running!
