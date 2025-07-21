# bitHuman LiveKit WebRTC Integration

This example demonstrates how to stream a bitHuman avatar to a LiveKit room using WebRTC, while controlling the avatar's speech through a WebSocket interface. This allows you to create interactive avatar experiences that can be viewed in real-time by multiple users.

## Overview

The integration consists of two main components:

1. **bitHuman Server (`bithuman_server.py`)**: Runs the bitHuman runtime, streams the avatar to a LiveKit room, and accepts audio input via WebSocket.

2. **WebSocket Client (`websocket_client.py`)**: Sends audio data to the bitHuman server to control the avatar's speech.

## How It Works

### Architecture

```
┌─────────────────┐     WebRTC     ┌─────────────────┐
│                 │◄──────────────►│                 │
│  LiveKit Room   │                │ LiveKit Client  │
│      (SFU)      │                │   (Viewers)     │
│                 │                │                 │
└─────────────────┘                └─────────────────┘
         ▲
         │
         │ WebRTC
         │
┌────────┴────────┐     WebSocket    ┌─────────────────┐
│                 │◄────────────────►│                 │
│ bitHuman Server │                  │ WebSocket Client│
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
         │
         │ API
         ▼
┌─────────────────┐
│                 │
│ bitHuman Runtime│
│                 │
└─────────────────┘
```

### Process Flow

1. The bitHuman server initializes the bitHuman runtime with your avatar model.
2. The server connects to a LiveKit room and publishes video and audio tracks.
3. The server starts a WebSocket server to accept audio input.
4. The WebSocket client sends audio data to the server.
5. The server processes the audio with the bitHuman runtime, generating avatar animations.
6. The animated avatar is streamed to the LiveKit room in real-time.
7. Viewers can connect to the LiveKit room to see and hear the avatar.

## Prerequisites

- Python 3.10+
- A bitHuman Runtime API token
- A LiveKit server (cloud or self-hosted)
- LiveKit API key and secret

## Installation

Install the required dependencies:

```bash
pip install bithuman livekit livekit-api websockets python-dotenv
```

## Configuration

Create a `.env` file in the same directory as the scripts with the following variables:

```
# bitHuman Configuration
BITHUMAN_RUNTIME_TOKEN=your_bithuman_token
BITHUMAN_AVATAR_MODEL=/path/to/model.imx

# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

## Usage

### Starting the bitHuman Server

```bash
python bithuman_server.py --room "my-room-name"
```

Command-line arguments:

- `--avatar-model`: The Bithuman avatar model to use (defaults to env var)
- `--room`: LiveKit room name (required)
- `--token`: bitHuman runtime token (defaults to env var)
- `--livekit-url`: LiveKit server URL (defaults to env var)
- `--api-key`: LiveKit API key (defaults to env var)
- `--api-secret`: LiveKit API secret (defaults to env var)
- `--identity`: Identity in LiveKit room (default: "bithuman-avatar")
- `--ws-port`: WebSocket server port (default: 8765)

### Streaming Audio to the Avatar

Use the WebSocket client to stream audio to the avatar:

```bash
# Stream an audio file
python websocket_client.py stream path/to/audio.wav

# Send an interrupt command
python websocket_client.py interrupt
```

Command-line arguments:

- `--ws-url`: WebSocket server URL (default: "ws://localhost:8765")
- `--sample-rate`: Target sample rate for audio (default: 16000)
- `--chunk-size`: Size of audio chunks in milliseconds (default: 100)
- `stream` command:
  - `audio_file`: Path to the audio file

### Viewing the Avatar

To view the avatar, you can:

1. Use the [LiveKit Playground](https://docs.livekit.io/agents/playground/)
2. Create your own LiveKit client using the [LiveKit SDKs](https://docs.livekit.io/home/client/connect/)

## WebSocket Protocol

The WebSocket server accepts the following messages:

1. **Binary data**: Raw audio bytes (16kHz, mono, int16 format)
2. **JSON commands**:
   - Interrupt: `{"type": "interrupt"}`
   - End of audio: `{"type": "end"}`

## Advanced Configuration

### LiveKit Room Settings

You can configure the LiveKit room settings by modifying the `TrackPublishOptions` in the `bithuman_server.py` file:

```python
video_options = rtc.TrackPublishOptions(
    source=rtc.TrackSource.SOURCE_CAMERA,
    video_encoding=rtc.VideoEncoding(
        max_framerate=25,
        max_bitrate=5_000_000,
    ),
)
```

### Audio Processing

You can adjust audio processing parameters in the `websocket_client.py` file:

```python
client = AudioStreamerClient(
    ws_url=args.ws_url,
    chunk_size_ms=args.chunk_size,
    sample_rate=args.sample_rate,
)
```

### Using LiveKit Data Streams for Audio Transfer

As an alternative to WebSockets, you can use LiveKit's Data Streams feature to send audio data to the bitHuman avatar server. This approach offers several advantages:

1. **Unified Infrastructure**: Use LiveKit for both media streaming and control data
2. **Built-in Security**: Leverage LiveKit's authentication and encryption
3. **Scalability**: Benefit from LiveKit's distributed architecture
4. **Reduced Complexity**: No need to manage a separate WebSocket server

#### Implementation Overview

To implement this approach:

1. **Server Side**: The bitHuman server registers a byte stream handler for audio data:

```python
# In bithuman_server.py
async def setup_livekit_data_streams(self):
    # Register handler for audio data
    self._room.register_byte_stream_handler("audio-data", self._handle_audio_stream)

async def _handle_audio_stream(self, reader, participant_info):
    """Handle incoming audio data from LiveKit Data Stream."""
    logger.info(f"Receiving audio stream from {participant_info.identity}")
    
    # Process chunks as they arrive
    async for chunk in reader:
        # Convert bytes to audio format and send to bitHuman runtime
        await self.runtime.push_audio(
            chunk,
            sample_rate=16000,
            last_chunk=False
        )
    
    # End of stream
    await self.runtime.flush()
    logger.info(f"Audio stream from {participant_info.identity} completed")
```

2. **Client Side**: Clients use LiveKit's byte stream API to send audio data:

```python
# Example client code
async def stream_audio_file(room, audio_file_path):
    # Load audio file
    audio_data, sample_rate = load_audio_file(audio_file_path)
    
    # Convert to chunks
    chunks = split_into_chunks(audio_data, chunk_size_ms=100)
    
    # Open a byte stream
    writer = await room.local_participant.stream_bytes(
        name="audio-chunk",
        topic="audio-data"
    )
    
    # Send chunks
    for chunk in chunks:
        await writer.write(chunk.tobytes())
    
    # Close the stream
    await writer.aclose()
```

For more details on LiveKit Data Streams, refer to the documents of [LiveKit Data Streams](https://docs.livekit.io/home/client/data/byte-streams/) and [Remote method calls](https://docs.livekit.io/home/client/data/rpc/).

## Resources

- [bitHuman Documentation](https://docs.bithuman.io/api-reference/runtime/introduction)
- [LiveKit Documentation](https://docs.livekit.io/)

## Troubleshooting

### Common Issues

1. **Connection errors**: Ensure your LiveKit server URL is correct and accessible.
2. **Authentication errors**: Verify your API key and secret are correct.
3. **Audio not playing**: Check that your audio files are in a supported format (WAV recommended).
4. **WebSocket connection issues**: Ensure the WebSocket server port is not blocked by a firewall.

### Logs

Both scripts use the `loguru` library for logging. You can adjust the log level in the scripts:

```python
logger.remove()
logger.add(sys.stdout, level="INFO")  # Change to "DEBUG" for more detailed logs
```

## License

This example is provided as part of the bitHuman SDK and is subject to the bitHuman license agreement.
