# bitHuman SDK Examples

bitHuman SDK enables you to build interactive agents that respond realistically to audio input. This repository contains comprehensive examples demonstrating various use cases and integrations.

## Prerequisites

**Supported Python Versions:**
- Python 3.10 to 3.13

**Supported Operating Systems:**
- Linux (x86_64 and arm64)
- macOS (Apple Silicon, macOS >= 15)

## Setup

### 1. Register and Get API Secret

1. Go to [https://console.bithuman.io](https://console.bithuman.io) and register for free
2. After registration, navigate to the **SDK** page to create a new API secret
3. Copy your API secret for use in the examples

### 2. Download Avatar Model

You'll need a bitHuman avatar model (`.imx` file) to run these examples. These models define the appearance and behavior of your virtual avatar.

1. Visit the [Community page](https://console.bithuman.io/#community)
2. Browse the available avatar models
3. Click on any agent card to download the `.imx` model file directly

### 3. Environment Setup

Set your API secret and model path as environment variables:

```bash
export BITHUMAN_API_SECRET='your_api_secret'
export BITHUMAN_AVATAR_MODEL='/path/to/model/avatar.imx'
```

Or create a `.env` file in the project root:

```bash
BITHUMAN_API_SECRET='your_api_secret'
BITHUMAN_AVATAR_MODEL='/path/to/model/avatar.imx'
```

## Installation

1. Install the bitHuman SDK:
```bash
pip install bithuman
```

2. Install additional dependencies based on the example you want to run (see the README in each example folder).

## Examples Overview

### 1. Basic Usage (`basic_usage/`)

Simple keyboard-controlled example that demonstrates core functionality with audio file playback.

```bash
cd basic_usage
pip install sounddevice
python example.py --audio-file <audio_file> --model <model_file>
```

**Features:**
- Load and play audio files through the avatar
- Keyboard controls (play, interrupt, quit)
- Basic audio and video rendering

### 2. Avatar Echo (`avatar/`)

Real-time microphone input processing with local avatar display.

```bash
cd avatar
pip install -r requirements.txt
python echo.py
```

**Features:**
- Real-time microphone audio capture
- Live avatar animation
- Local video window display
- Audio echo processing

### 3. LiveKit Agent (`livekit_agent/`)

AI-powered conversational agent using OpenAI Realtime API with bitHuman visual rendering.

```bash
cd livekit_agent
pip install -r requirements.txt

# Add to your .env:
# OPENAI_API_KEY=your_openai_key
# LIVEKIT_URL=wss://your-livekit-server.com (for WebRTC)
# LIVEKIT_API_KEY=your_livekit_key (for WebRTC)
# LIVEKIT_API_SECRET=your_livekit_secret (for WebRTC)

# Run locally
python agent_local.py

# Run in a LiveKit room
python agent_webrtc.py dev
```

**Features:**
- OpenAI Realtime API integration
- Voice-to-voice conversations
- Live avatar responses
- Local and WebRTC deployment options

<table>
<td width="100%">
<h4>Albert Einstein Agent Example</h4>
<video width="100%" src="https://github.com/user-attachments/assets/99081a20-bc17-43c4-afbc-3dcf4f274227" controls></video>
</td>
</table>

### 4. LiveKit WebRTC Integration (`livekit_webrtc/`)

Stream bitHuman avatars to LiveKit rooms with WebSocket control interface.

```bash
cd livekit_webrtc
pip install -r requirements.txt

# Add to your .env:
# LIVEKIT_URL=wss://your-livekit-server.com
# LIVEKIT_API_KEY=your_livekit_key
# LIVEKIT_API_SECRET=your_livekit_secret

# Start the server
python bithuman_server.py --room test_room

# Send audio to the avatar (in another terminal)
python websocket_client.py stream /path/to/audio.wav
```

**Features:**
- WebRTC streaming to multiple viewers
- WebSocket-based audio control
- Real-time avatar animation
- Multi-user viewing capabilities

### 5. FastRTC (`fastrtc/`)

Simplified WebRTC implementation using FastRTC library.

```bash
cd fastrtc
pip install -r requirements.txt
python fastrtc_example.py
```

**Features:**
- Simplified WebRTC setup
- Similar capabilities to LiveKit
- Alternative WebRTC implementation

## Directory Structure

```
sdk-examples-python/
├── README.md                    # This file
├── .gitignore                   # Git ignore patterns
├── ruff.toml                    # Python linting configuration
├── basic_usage/                 # Simple keyboard-controlled example
│   ├── example.py
│   └── README.md
├── avatar/                      # Microphone echo example
│   ├── echo.py
│   ├── requirements.txt
│   └── README.md
├── livekit_agent/              # AI agent with OpenAI integration
│   ├── agent_local.py
│   ├── agent_webrtc.py
│   ├── requirements.txt
│   └── README.md
├── livekit_webrtc/             # LiveKit WebRTC streaming
│   ├── bithuman_server.py
│   ├── websocket_client.py
│   ├── requirements.txt
│   └── README.md
└── fastrtc/                    # FastRTC WebRTC example
    ├── fastrtc_example.py
    ├── requirements.txt
    └── README.md
```

## API Overview

### Creating a Runtime Instance

All examples use the bitHuman Runtime (`AsyncBithuman`) to process audio and generate avatar animations:

```python
from bithuman.runtime import AsyncBithuman

# Initialize with API secret and model path
runtime = await AsyncBithuman.create(
    api_secret="your_api_secret", 
    model_path="/path/to/model.imx"
)
```

### Core Components

1. **AsyncBithuman**: Main class for avatar processing
   - Initialize with API secret: `await AsyncBithuman.create(...)`
   - Process audio input to generate avatar animations
   - Interrupt ongoing speech: `runtime.interrupt()`

2. **AudioChunk**: Audio data representation
   - Supports 16kHz, mono, int16 format
   - Can be created from bytes or numpy arrays
   - Provides duration and format utilities

3. **VideoFrame**: Avatar output data
   - BGR image data (numpy array)
   - Synchronized audio chunks
   - Frame metadata (index, message ID)

### Input/Output Flow

1. **Input**: Send 16kHz, mono, int16 audio data to the runtime
2. **Processing**: Runtime analyzes audio for facial movements and expressions
3. **Output**: 25 FPS video frames with synchronized audio chunks

## Getting Help

- [bitHuman Documentation](https://docs.bithuman.io)
- [bitHuman Console](https://console.bithuman.io)
- [LiveKit Agents](https://github.com/livekit/agents)

For questions or issues, visit the [Community page](https://console.bithuman.io/#community) or check the documentation.
