# Gemini Live Avatar

Self-hosted bitHuman avatar with Gemini Live API (gemini-2.0-flash-exp) integration.

## Overview

This example demonstrates a conversational AI avatar using:

- **Gemini Live API (gemini-2.0-flash-exp)** - Real-time STT/TTS/LLM
- **bitHuman AsyncBithuman** - Avatar rendering with lip-sync
- **Local mode** - OpenCV video display, sounddevice audio I/O (default)
- **Server mode** - WebSocket-based remote audio/video streaming (optional)
- **Dynamics/Gestures** - Keyword-based gesture triggering

## Architecture

### Local Mode
```
┌─────────────────┐                    ┌──────────────────┐
│   Microphone    │ ─────────────────► │  Gemini Live API │
│   (sounddevice) │                    │  (STT/LLM/TTS)   │
└─────────────────┘                    └────────┬─────────┘
                                                │
                                                │ Audio Response
                                                ▼
┌─────────────────┐                    ┌──────────────────┐
│   Speaker       │ ◄───────────────── │  bitHuman        │
│   (sounddevice) │                    │  AsyncBithuman   │
└─────────────────┘                    └────────┬─────────┘
                                                │
                                                │ Video Frames
                                                ▼
                                       ┌──────────────────┐
                                       │  OpenCV Display  │
                                       └──────────────────┘
```

### Server Mode (WebSocket Streaming)
```
┌─────────────────┐     WebSocket      ┌──────────────────┐
│   Web Client    │ ◄──────────────────│  WebSocket       │
│   (Browser)     │     Video+Audio    │  Server          │
└────────┬────────┘                    └────────┬─────────┘
         │                                      │
         │ Audio Input                          │
         ▼                                      ▼
┌─────────────────┐                    ┌──────────────────┐
│  Gemini Live    │ ◄──────────────────│  bitHuman        │
│  API            │     Audio          │  AsyncBithuman   │
└─────────────────┘                    └──────────────────┘
```

## Features

- **Local Mode** (default): Microphone input, OpenCV video display, speaker output
- **Server Mode** (optional): WebSocket-based remote audio/video streaming
- **Gemini Live API**: Real-time speech-to-speech conversation
- **Avatar Lip-sync**: bitHuman avatar synchronized with speech
- **Gesture Support**: Automatic gesture triggering based on conversation keywords
- **Audio File Input**: Support for pre-recorded audio file input

## Prerequisites

1. **bitHuman API Credentials**
   - API Secret from [bitHuman Platform](https://www.bithuman.ai/#api-keys)
   - Avatar model file (`.imx` format)

2. **Google AI API Key** (for Gemini Live API)
   - Get API key from [Google AI Studio](https://aistudio.google.com/apikey)

3. **System Requirements**
   - Python 3.10+
   - For local mode: working microphone and speakers
   - For server mode: network access on specified port

## Installation

1. **Navigate to the example directory**:
   ```bash
   cd examples/self-hosted/gemini_live_avatar
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment configuration**:
   ```bash
   cp ../env.example .env
   ```

4. **Configure your `.env` file**:
   ```env
   # bitHuman Configuration
   BITHUMAN_API_SECRET=your_bithuman_api_secret
   BITHUMAN_MODEL_PATH=/path/to/your/avatar.imx
   BITHUMAN_AGENT_ID=your_agent_id  # Optional, for dynamics

   # Google AI API Key (get from https://aistudio.google.com/apikey)
   GOOGLE_API_KEY=your_google_api_key
   ```

## Usage

### Local Mode (Microphone + Display)

Run the avatar with local microphone input and OpenCV display:
```bash
python main.py --model /path/to/avatar.imx --api-secret YOUR_API_SECRET --gemini-api-key YOUR_GOOGLE_API_KEY
```

Or with environment variables:
```bash
export GOOGLE_API_KEY=your_google_api_key
python main.py --model /path/to/avatar.imx --api-secret YOUR_API_SECRET
```

### Local Mode with Audio File

Run with a pre-recorded audio file instead of microphone:

```bash
python main.py --model /path/to/avatar.imx --api-secret YOUR_API_SECRET --audio-file /path/to/audio.wav
```

### Server Mode (WebSocket Streaming)

Start the WebSocket server for remote client connections:

```bash
python main.py --model /path/to/avatar.imx --api-secret YOUR_API_SECRET --server --port 8765
```

With local display enabled (for debugging):

```bash
python main.py --model /path/to/avatar.imx --api-secret YOUR_API_SECRET --server --port 8765 --local-display
```

### Using Environment Variables

If you've configured `.env`:

```bash
# Local mode
python main.py

# Server mode
python main.py --server
```

### All Options

```bash
python main.py \
  --model /path/to/avatar.imx \
  --api-secret YOUR_BITHUMAN_API_SECRET \
  --gemini-api-key YOUR_GOOGLE_API_KEY \
  --agent-id YOUR_AGENT_ID \
  --gemini-model gemini-2.0-flash-exp \
  --gemini-voice Puck \
  --instructions "You are a friendly assistant." \
  --audio-file /path/to/audio.wav \
  --server \
  --host 0.0.0.0 \
  --port 8765 \
  --local-display
```

## Command Line Arguments

| Argument | Environment Variable | Description |
|----------|---------------------|-------------|
| `--model` | `BITHUMAN_MODEL_PATH` | Path to bitHuman avatar model (.imx) |
| `--api-secret` | `BITHUMAN_API_SECRET` | bitHuman API Secret |
| `--gemini-api-key` | `GOOGLE_API_KEY` | Google AI API Key (required) |
| `--agent-id` | `BITHUMAN_AGENT_ID` | Agent ID for dynamics (optional) |
| `--gemini-model` | - | Gemini model (default: gemini-2.0-flash-exp) |
| `--gemini-voice` | - | Voice: Puck, Charon, Kore, Fenrir, Aoede |
| `--instructions` | - | System instructions for Gemini |
| `--audio-file` | `BITHUMAN_AUDIO_PATH` | Audio file input (optional) |
| `--server` | - | Enable WebSocket server mode |
| `--host` | - | Server host (default: 0.0.0.0) |
| `--port` | - | Server port (default: 8765) |
| `--local-display` | - | Show local window in server mode |

## Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py", "--server"]
```

```yaml
# docker-compose.yml
services:
  gemini-avatar:
    build: .
    environment:
      - GOOGLE_API_KEY=your_google_api_key
      - BITHUMAN_API_SECRET=your_secret
      - BITHUMAN_MODEL_PATH=/app/models/avatar.imx
    volumes:
      - ./models:/app/models:ro
    ports:
      - "8765:8765"
```

## WebSocket Protocol

### Connecting

```javascript
const ws = new WebSocket('ws://localhost:8765');
```

### Client -> Server Messages (JSON)

**Audio Input:**
```json
{
  "type": "audio_input",
  "sample_rate": 16000,
  "channels": 1,
  "data": "<base64_encoded_pcm_audio>"
}
```

**Text Input:**
```json
{
  "type": "text_input",
  "data": {
    "text": "Hello, how are you?"
  }
}
```

**Control Commands:**
```json
{
  "type": "control",
  "data": {
    "command": "interrupt"
  }
}
```

```json
{
  "type": "control",
  "data": {
    "command": "gesture",
    "params": {
      "gesture": "mini_wave_hello"
    }
  }
}
```

**Subscription Control:**
```json
{
  "type": "control",
  "data": {
    "command": "subscribe",
    "params": {
      "video": true,
      "audio": true
    }
  }
}
```

### Server -> Client Messages

**Video Frame (Binary):**
```
Header (17 bytes):
  - Type: 1 byte (0x01)
  - Width: 2 bytes (uint16)
  - Height: 2 bytes (uint16)
  - FPS: 4 bytes (float32)
  - Data length: 4 bytes (uint32)
  - Timestamp: 8 bytes (float64)
Body:
  - JPEG data
```

**Audio Chunk (Binary):**
```
Header (18 bytes):
  - Type: 1 byte (0x02)
  - Sample rate: 4 bytes (uint32)
  - Channels: 1 byte (uint8)
  - Data length: 4 bytes (uint32)
  - Timestamp: 8 bytes (float64)
Body:
  - PCM int16 audio data
```

**Status/Transcription (JSON):**
```json
{
  "type": "status",
  "data": {
    "status": "connected",
    "client_id": "client_1",
    "timestamp": 1234567890.123
  }
}
```

```json
{
  "type": "transcription",
  "data": {
    "text": "Hello there!",
    "is_final": true,
    "role": "user",
    "timestamp": 1234567890.123
  }
}
```

## Web Client Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>Gemini Live Avatar Client</title>
</head>
<body>
  <video id="video" autoplay></video>
  <button id="talk">Talk</button>

  <script>
    const ws = new WebSocket('ws://localhost:8765');
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Audio context for playback
    const audioCtx = new AudioContext({ sampleRate: 16000 });

    ws.binaryType = 'arraybuffer';

    ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        // JSON message
        const msg = JSON.parse(event.data);
        console.log('Received:', msg);
      } else {
        // Binary message
        const view = new DataView(event.data);
        const type = view.getUint8(0);

        if (type === 0x01) {
          // Video frame
          const width = view.getUint16(1);
          const height = view.getUint16(3);
          const jpegData = new Uint8Array(event.data.slice(17 + 8));
          
          // Display JPEG frame
          const blob = new Blob([jpegData], { type: 'image/jpeg' });
          const url = URL.createObjectURL(blob);
          const img = new Image();
          img.onload = () => {
            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0);
            video.srcObject = canvas.captureStream();
            URL.revokeObjectURL(url);
          };
          img.src = url;
        } else if (type === 0x02) {
          // Audio chunk - play it
          const sampleRate = view.getUint32(1);
          const pcmData = new Int16Array(event.data.slice(18 + 8));
          
          // Convert to float and play
          const audioBuffer = audioCtx.createBuffer(1, pcmData.length, sampleRate);
          const channelData = audioBuffer.getChannelData(0);
          for (let i = 0; i < pcmData.length; i++) {
            channelData[i] = pcmData[i] / 32768;
          }
          const source = audioCtx.createBufferSource();
          source.buffer = audioBuffer;
          source.connect(audioCtx.destination);
          source.start();
        }
      }
    };

    // Send audio from microphone
    document.getElementById('talk').onclick = async () => {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorder.ondataavailable = (e) => {
        // Convert to PCM and send
        // (simplified - actual implementation needs AudioWorklet)
      };
      
      mediaRecorder.start(100); // 100ms chunks
    };
  </script>
</body>
</html>
```

## Keyboard Controls (Local Mode)

| Key | Action |
|-----|--------|
| `1` | Replay audio file (if using audio file mode) |
| `2` | Interrupt current response |
| `3` | Trigger wave gesture |
| `q` | Quit application |

## Dynamics / Gestures

### Default Keyword Mappings

| Keywords | Gesture |
|----------|---------|
| hello, hi, hey, bye, wave | `mini_wave_hello` |
| laugh, haha, funny, lol | `laugh_react` |
| yes, yeah, agree, nod | `nod_agree` |
| love, heart, kiss | `heart_gesture` |
| thanks, great, awesome | `thumbs_up` |

### Triggering Gestures via WebSocket

```json
{
  "type": "control",
  "data": {
    "command": "gesture",
    "params": {
      "gesture": "mini_wave_hello"
    }
  }
}
```

## File Structure

```
gemini_live_avatar/
├── main.py              # Main application (local + server modes)
├── websocket_server.py  # WebSocket media streaming server
├── dynamics.py          # Gesture/dynamics handling module
├── requirements.txt     # Python dependencies
└── README.md            # This documentation
```

## Module Overview

### main.py

Main application containing:
- `AudioPlayer` - Local audio output via sounddevice
- `AudioRecorder` - Local audio input via sounddevice
- `VideoPlayer` - Local video display via OpenCV
- `GeminiLiveSession` - Gemini Live API WebSocket client
- `GeminiLiveAvatarApp` - Main application (local + server modes)

### websocket_server.py

WebSocket streaming server containing:
- `MediaWebSocketServer` - WebSocket server for media streaming
- `WebSocketAudioInput` - Audio input from WebSocket clients
- `WebSocketVideoOutput` - Video output to WebSocket clients
- `WebSocketAudioOutput` - Audio output to WebSocket clients

### dynamics.py

Gesture handling module containing:
- `DynamicsHandler` - Main gesture management class
- `DEFAULT_KEYWORD_ACTION_MAP` - Default keyword-to-gesture mappings
- `get_available_gestures()` - Fetch gestures from bitHuman API

## Troubleshooting

### WebSocket Connection Issues

1. **Connection refused**:
   - Ensure server is running with `--server` flag
   - Check firewall settings for the port

2. **No video/audio received**:
   - Verify client subscription settings
   - Check browser console for errors

### Gemini API Issues

1. **Connection failed**:
   - Verify Google API key is valid
   - Check network connectivity

### bitHuman Issues

1. **Model loading failed**:
   - Verify model file path
   - Check API secret is valid

## License

This example is provided under the MIT License.

## Support

- [bitHuman Documentation](https://docs.bithuman.ai)
- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs/live)
