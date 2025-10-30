# Flutter Frontend Configuration

## Environment Variables

The Flutter app supports the following environment variables for configuration:

### Required Configuration

- `LIVEKIT_SERVER_URL`: LiveKit server WebSocket URL
  - Example: `wss://your-project.livekit.cloud`
  - Default: `wss://your-project.livekit.cloud`

### Token Configuration (Choose One)

#### Option 1: Direct Token (Testing Only)
- `LIVEKIT_TOKEN`: JWT token for direct connection
  - Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
  - **Warning**: Only use for testing, not production

#### Option 2: Token Server Endpoint (Recommended)
- `LIVEKIT_TOKEN_ENDPOINT`: URL to token generation server
  - Example: `http://localhost:3000/token`
  - Default: `http://localhost:3000/token`

### Room Configuration

- `LIVEKIT_ROOM_NAME`: Name of the LiveKit room
  - Example: `flutter-avatar-room`
  - Default: `flutter-avatar-room`

- `LIVEKIT_PARTICIPANT_NAME`: Name of the participant
  - Example: `Flutter User`
  - Default: `Flutter User`

## Setting Environment Variables

### Mobile/Desktop Platforms

#### Option 1: Command Line (Temporary)
```bash
# Set environment variables before running
export LIVEKIT_SERVER_URL="wss://your-project.livekit.cloud"
export LIVEKIT_TOKEN_ENDPOINT="http://localhost:3000/token"
flutter run -d android  # or ios, macos
```

#### Option 2: IDE Configuration
In your IDE (VS Code, Android Studio, etc.), set environment variables in run configuration.

#### Option 3: System Environment Variables
Set environment variables in your system's environment configuration.

### Web Platform

**Note**: Web platform cannot access system environment variables directly. For web development:

#### Option 1: Modify Configuration Directly
Edit `lib/config/livekit_config.dart` and change the default values:

```dart
static String get serverUrl => 
    _getEnvVar('LIVEKIT_SERVER_URL') ?? 
    'wss://your-actual-project.livekit.cloud';  // Change this

static String? get tokenEndpoint => 
    _getEnvVar('LIVEKIT_TOKEN_ENDPOINT') ?? 
    'http://localhost:3000/token';  // Change this if needed
```

#### Option 2: URL Parameters (Future Enhancement)
The configuration supports URL parameters for web deployment:
```
http://localhost:8080?serverUrl=wss://your-project.livekit.cloud&tokenEndpoint=http://localhost:3000/token
```

## Example Configurations

### Development (Local LiveKit Server)
```bash
export LIVEKIT_SERVER_URL="wss://localhost:7880"
export LIVEKIT_TOKEN_ENDPOINT="http://localhost:3000/token"
export LIVEKIT_ROOM_NAME="dev-room"
export LIVEKIT_PARTICIPANT_NAME="Dev User"
```

### Production (LiveKit Cloud)
```bash
export LIVEKIT_SERVER_URL="wss://your-project.livekit.cloud"
export LIVEKIT_TOKEN_ENDPOINT="https://your-api.com/token"
export LIVEKIT_ROOM_NAME="production-room"
export LIVEKIT_PARTICIPANT_NAME="Production User"
```

### Testing (Direct Token)
```bash
export LIVEKIT_SERVER_URL="wss://your-project.livekit.cloud"
export LIVEKIT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export LIVEKIT_ROOM_NAME="test-room"
export LIVEKIT_PARTICIPANT_NAME="Test User"
```

## Configuration Validation

The app will validate configuration on startup. If configuration is invalid, you'll see an error message with details about what's missing.

## Debug Information

To see current configuration, check the debug console for configuration summary logs.
