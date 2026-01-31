# BitHuman Avatar Agents with Pipecat

Self-hosted avatar agents that integrate BitHuman avatar runtime with Pipecat framework. This directory contains examples for both Daily.co and LiveKit transports.

## Available Examples

| Example | Transport | Framework | Description |
|---------|-----------|-----------|-------------|
| `agent_pipecat_daily.py` | Daily.co | Pipecat | Agent using Pipecat Cloud through Daily.co |
| `agent_pipecat_livekit.py` | LiveKit | Pure Pipecat | Pure Pipecat with LiveKitTransport (no Agents framework, simpler code) |

## Test Client Files

| File | Description |
|------|-------------|
| `test_client.html` | Web-based test client for testing `agent_pipecat_livekit.py` (opens in browser) |
| `token_server.py` | Simple token server for generating LiveKit access tokens (required by test client) |

### Key Features

**`agent_pipecat_livekit.py` (Pure Pipecat + LiveKitTransport):**
- ✅ Pure Pipecat Pipeline architecture (no LiveKit Agents framework)
- ✅ Uses Pipecat's built-in `LiveKitTransport`
- ✅ Simpler code, easier to understand
- ✅ Full control over Pipeline
- ✅ Uses Pipecat services (Deepgram STT, OpenAI LLM/TTS)
- ✅ Custom BitHumanAvatarProcessor for avatar rendering
- ❌ **NOT automatically registered as Agent** (connects as regular participant)
- ❌ Requires manual room management

## Overview

These agents demonstrate how to build conversational AI avatars using:
- **Pipecat**: Frame-based pipeline architecture for processing real-time media streams
- **BitHuman Runtime**: Avatar rendering with lip-sync synchronization
- **OpenAI GPT-4o-mini**: Fast, real-time LLM for conversation
- **Deepgram STT**: Real-time speech-to-text with streaming support
- **OpenAI TTS**: Text-to-speech conversion

## Architecture

Both agents use the same pipeline architecture:

```
User Audio → Deepgram STT → GPT-4o-mini → OpenAI TTS → BitHuman Runtime
                                                                     ↓
User Display ← Video/Audio Frames ← BitHuman Avatar Generation ←─────┘
```

The `BitHumanAvatarProcessor` is a custom Pipecat `FrameProcessor` that:
1. Receives TTS audio frames from the pipeline
2. Pushes audio to the BitHuman runtime for lip-sync processing
3. Outputs synchronized video and audio frames
4. Handles interruptions gracefully

## Prerequisites

- Python 3.10 or higher
- BitHuman model file (`.imx` format)
- API keys for:
  - BitHuman (API secret)
  - OpenAI (for LLM and TTS)
  - Deepgram (for STT)
  - Daily.co API key (for `agent_pipecat_daily.py`) OR LiveKit credentials (for `agent_pipecat_livekit.py`)

## Installation

1. Install required dependencies:

```bash
cd examples/self-hosted/pipecat
pip install -r requirements.txt
```

Or using `uv`:

```bash
uv pip install -r requirements.txt
```

**Key Dependencies:**
- `pipecat-ai[daily,livekit,openai,deepgram]` - Pipecat framework with all transports and services
  - Includes `LiveKitTransport` for WebRTC communication (used by `agent_pipecat_livekit.py`)
- `livekit>=0.11.0` - LiveKit SDK for token generation (used by `agent_pipecat_livekit.py`)
- `bithuman>=0.7.0` - BitHuman runtime SDK for avatar rendering
- `opencv-python`, `numpy`, `scipy` - Image and audio processing
- `python-dotenv` - Environment variable management
- `aiohttp` - HTTP client for Daily.co API (only needed for `agent_pipecat_daily.py`)

**Note:** The `agent_pipecat_livekit.py` uses pure Pipecat with `LiveKitTransport`, so it does **NOT** require `livekit-agents` package.

2. Set up environment variables (create a `.env` file or export them):

### For Daily.co Agent

```bash
export BITHUMAN_MODEL_PATH="path/to/your/model.imx"
export BITHUMAN_API_SECRET="your_bithuman_api_secret"
export DAILY_API_KEY="your_daily_api_key"
export OPENAI_API_KEY="your_openai_api_key"
export DEEPGRAM_API_KEY="your_deepgram_api_key"
```

### For LiveKit Agent

```bash
export BITHUMAN_MODEL_PATH="path/to/your/model.imx"
export BITHUMAN_API_SECRET="your_bithuman_api_secret"
export LIVEKIT_URL="wss://your-project.livekit.cloud"
export LIVEKIT_API_KEY="your_livekit_api_key"
export LIVEKIT_API_SECRET="your_livekit_api_secret"
export OPENAI_API_KEY="your_openai_api_key"
export DEEPGRAM_API_KEY="your_deepgram_api_key"
```

## Usage

### Daily.co Agent (`agent_pipecat_daily.py`)

For users running Pipecat Cloud through Daily.co:

```bash
# Create a new room automatically
python agent_pipecat_daily.py

# Or join an existing room
python agent_pipecat_daily.py --room-url https://your-domain.daily.co/your-room

# Enable debug logging
python agent_pipecat_daily.py --debug
```

**Command Line Arguments:**
- `--room-url`: Daily.co room URL (optional, creates new room if not provided)
- `--model-path`: Path to BitHuman model file (.imx format)
- `--api-secret`: BitHuman API secret
- `--debug`: Enable debug logging

**Required Environment Variables:**
- `BITHUMAN_MODEL_PATH`: Path to BitHuman model file (.imx)
- `BITHUMAN_API_SECRET`: BitHuman API secret
- `DAILY_API_KEY`: Daily.co API key
- `OPENAI_API_KEY`: OpenAI API key (for LLM and TTS)
- `DEEPGRAM_API_KEY`: Deepgram API key (for STT)

### Pure Pipecat with LiveKit (`agent_pipecat_livekit.py`)

**Simplest implementation using pure Pipecat.** This version uses Pipecat's built-in `LiveKitTransport` without the LiveKit Agents framework.

```bash
# Run with auto-generated room name
python agent_pipecat_livekit.py

# Run with specific room name
python agent_pipecat_livekit.py --room-name my-room

# Enable debug logging
python agent_pipecat_livekit.py --debug
```

**Key Features:**
- ✅ Pure Pipecat architecture (no LiveKit Agents framework)
- ✅ Uses Pipecat's built-in `LiveKitTransport`
- ✅ Simpler code, easier to understand
- ✅ Full control over Pipeline
- ✅ Uses Pipecat services (Deepgram STT, OpenAI LLM/TTS)
- ✅ Custom BitHumanAvatarProcessor for avatar rendering
- ❌ **NOT automatically registered as Agent** (connects as regular participant)
- ❌ Requires manual room management

**When to Use:**
- When you want the simplest Pipecat implementation
- When you don't need Agent registration/dispatch
- When you want full control over the Pipeline
- When you're learning Pipecat architecture

**Command Line Arguments:**
- `--room-name`: LiveKit room name (optional, auto-generated if not provided)
- `--model-path`: Path to BitHuman model file (.imx format)
- `--api-secret`: BitHuman API secret
- `--debug`: Enable debug logging

**Required Environment Variables:**
- `BITHUMAN_MODEL_PATH`: Path to BitHuman model file (.imx)
- `BITHUMAN_API_SECRET`: BitHuman API secret
- `LIVEKIT_URL`: LiveKit server WebSocket URL
- `LIVEKIT_API_KEY`: LiveKit API key
- `LIVEKIT_API_SECRET`: LiveKit API secret
- `OPENAI_API_KEY`: OpenAI API key (for LLM and TTS)
- `DEEPGRAM_API_KEY`: Deepgram API key (for STT)

## How It Works

### Pipeline Flow

1. **User Audio Input**: LiveKitTransport receives audio from LiveKit room → Converts to Pipecat AudioRawFrame
2. **Speech-to-Text**: Deepgram STT converts audio to text transcripts
3. **LLM Processing**: OpenAI GPT-4o-mini generates responses
4. **Text-to-Speech**: OpenAI TTS converts text to audio
5. **Avatar Rendering**: BitHuman runtime generates synchronized video and audio frames
6. **Output**: LiveKitTransport sends video/audio frames to LiveKit room → Participants receive video/audio

### Key Features

- **Real-time Lip-sync**: Avatar mouth movements are synchronized with speech audio
- **Streaming Audio**: Supports streaming audio processing for low latency
- **Interruption Handling**: Properly handles user interruptions
- **Audio Resampling**: Automatically resamples TTS audio to BitHuman's required sample rate
- **Smart Flushing**: Waits for all audio to be processed before signaling end of speech

## Performance Notes

- **Initialization Time**: Avatar runtime initialization typically takes ~20 seconds on first startup
- **Latency**: End-to-end latency depends on network conditions and model processing time
- **Resource Usage**: Requires sufficient CPU/GPU resources for real-time video generation

## Troubleshooting

### Avatar Not Appearing

- Check that the BitHuman model file path is correct
- Verify that `BITHUMAN_API_SECRET` is set correctly
- Check logs for initialization errors

### Audio Not Working

- Verify Deepgram API key is valid
- Check that transport has audio enabled
- Review logs for STT/TTS errors

### Lip-sync Issues

- Ensure TTS audio is being received by the processor
- Check that audio resampling is working correctly
- Review flush timing in logs

### Connection Issues

**For Daily.co:**
- Verify Daily.co API key is valid
- Check that room URL is correct
- Ensure network connectivity to Daily.co

**For LiveKit:**
- Verify LiveKit URL is correct (should start with `wss://`)
- Check that API keys and secrets are valid
- Ensure network connectivity to LiveKit server

## Testing

### Testing the LiveKit Agent

Since `agent_pipecat_livekit.py` uses pure Pipecat (not LiveKit Agents framework), it won't appear in LiveKit Playground. You have several options:

#### Option 1: LiveKit CLI (Recommended - Official Tool)

The simplest way to test is using LiveKit's official CLI:

```bash
# Install LiveKit CLI
npm install -g livekit-cli

# Connect to room (replace with your credentials)
lk join \
  --url wss://your-project.livekit.cloud \
  --api-key YOUR_KEY \
  --api-secret YOUR_SECRET \
  --room test-room
```

#### Option 2: LiveKit Official Examples

Use LiveKit's official client examples from their GitHub repository:

```bash
# Clone LiveKit examples
git clone https://github.com/livekit/client-examples-js.git
cd client-examples-js

# Follow the README to set up and run
# Examples include: Web, React, Vue, Next.js, etc.
```

#### Option 3: Custom Test Client (Provided)

Use the provided test client:

1. **Start the token server** (in a separate terminal):
   ```bash
   # Set environment variables
   export LIVEKIT_API_KEY="your-api-key"
   export LIVEKIT_API_SECRET="your-api-secret"
   
   # Start token server
   python token_server.py
   ```

2. **Start your agent** (in another terminal):
   ```bash
   python agent_pipecat_livekit.py --room-name test-room
   ```

3. **Open the test client**:
   - Open `test_client.html` in your browser
   - Fill in the configuration:
     - LiveKit URL (e.g., `wss://your-project.livekit.cloud`)
     - API Key and Secret (same as used for token server)
     - Room Name: `test-room` (must match the room name used by your agent)
     - Your Name: any name
   - Click "Connect"
   - Enable your microphone to talk to the agent

**Alternative: Use LiveKit CLI (Official Tool)**

LiveKit 官方提供了 CLI 工具，这是最简单的测试方式：

```bash
# Install LiveKit CLI
npm install -g livekit-cli

# Connect to room
lk join \
  --url wss://your-project.livekit.cloud \
  --api-key YOUR_KEY \
  --api-secret YOUR_SECRET \
  --room test-room
```

**Or use LiveKit Official Examples:**

LiveKit 官方仓库提供了多个客户端示例，你可以直接使用：

```bash
# Clone LiveKit examples repository
git clone https://github.com/livekit/client-examples-js.git
cd client-examples-js

# Follow the README to set up and run the example
# The examples include Web, React, Vue, etc.
```

**Note:** LiveKit Playground (https://agents-playground.livekit.io/) only supports LiveKit Agents framework, not pure Pipecat implementations. For pure Pipecat + LiveKitTransport, use the CLI or examples above.

## Development

### Debug Mode

Enable debug logging for detailed information:

```bash
# For Daily.co agent
python agent_pipecat_daily.py --debug

# For LiveKit agent
python agent_pipecat_livekit.py --debug
```

### Customization

You can customize the agent by:
- Modifying the system prompt in `main()` function
- Adjusting TTS voice settings
- Changing LLM model or parameters
- Modifying flush delay timing


## License

This example is provided as-is for demonstration purposes.
