# bitHuman SDK Examples

Interactive avatar examples using the bitHuman SDK for real-time conversational AI.

> 📚 **Complete Documentation Available**: For detailed guides, tutorials, and comprehensive documentation, visit **[public-sdk-examples.vercel.app](https://public-sdk-examples.vercel.app/#/)**

## 🚀 Quick Start

### Installation

```bash
# 1. Create conda environment
conda create -n bithuman python=3.11
conda activate bithuman

# 2. Install dependencies
pip install -r requirements.txt
pip install bithuman --upgrade
```

### Setup Environment

Create `.env` file in the root directory:
```bash
# bitHuman SDK
BITHUMAN_API_SECRET=sk_bh_1234567890abcdef...
BITHUMAN_MODEL_PATH=/path/to/model.imx
BITHUMAN_AUDIO_PATH=/path/to/audio.wav  # Optional: only for avatar-with-audio-clip.py

# OpenAI (for OpenAI agent example)
OPENAI_API_KEY=sk-proj-1234567890abcdef...

# LiveKit (for LiveKit agent examples)
LIVEKIT_API_KEY=APIabcdef123456...
LIVEKIT_API_SECRET=secretABCDEF123456...
LIVEKIT_URL=wss://your-project.livekit.cloud
```

Get your API secret at [imaginex.bithuman.ai](https://imaginex.bithuman.ai) and download avatar models from the [Community page](https://imaginex.bithuman.ai/#community).

## 💡 Integration Made Simple

bitHuman SDK is designed for **effortless integration** into any application. Whether you're building a desktop app, web service, or IoT device, adding an interactive avatar takes just a few lines of code:

### Standalone Integration (3 lines of code!)

```python
from bithuman import AsyncBithuman

# Initialize with your model
runtime = await AsyncBithuman.create(model_path="model.imx", api_secret="your_secret")

# Start generating frames
async for frame in runtime.run():
    # Your custom logic here - display frame, play audio, etc.
    pass
```

### LiveKit Integration (2 lines of code!)

```python
from livekit.plugins import bithuman

# Add avatar to any LiveKit agent
avatar = bithuman.AvatarSession(model_path="model.imx", api_secret="your_secret")
await avatar.start(session, room=room)
```

## 📖 Examples

### 🖥️ Standalone SDK Examples

Perfect for **desktop applications**, **custom UIs**, or **embedded systems**. These examples show direct SDK integration with full control over audio/video processing.

#### 1. Audio Clip Playback
```bash
python examples/avatar-with-audio-clip.py
```
- **What it does**: Plays pre-recorded audio files with synchronized avatar animation
- **Use case**: Presentations, demos, voice-overs, tutorials
- **Features**: Audio file playback, OpenCV display, FPS control
- **Controls**: Press `1` to play audio, `2` to interrupt, `q` to quit

#### 2. Live Microphone Input
```bash
python examples/avatar-with-microphone.py
```
- **What it does**: Real-time avatar animation from microphone input
- **Use case**: Voice assistants, interactive kiosks, local chatbots
- **Features**: Live audio capture, volume control, silence detection
- **Perfect for**: Custom voice interfaces and standalone applications

### 🌐 LiveKit Agent Examples

Perfect for **web applications**, **multiplayer experiences**, and **scalable services**. These examples show how to integrate bitHuman into LiveKit agents for browser-based interactions.

**Setup LiveKit Playground for Web UI:**

1. **Register free LiveKit account** at [livekit.io](https://livekit.io)
   - Create a new project in your LiveKit Cloud dashboard
   - Note your API keys and project URL

2. **Quick option - Use hosted playground:**
   ```bash
   # Just run your agent in dev mode and use the hosted playground
   python examples/agent-livekit-openai.py dev
   # Then visit: https://agents-playground.livekit.io
   ```

3. **Local playground setup (optional):**
   ```bash
   git clone https://github.com/livekit/agents-playground.git
   cd agents-playground
   npm install
   
   # Configure .env file:
   echo "LIVEKIT_API_KEY=your_api_key" > .env
   echo "LIVEKIT_API_SECRET=your_api_secret" >> .env  
   echo "NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud" >> .env
   
   npm run dev
   ```

#### 3. OpenAI Conversational Agent
```bash
python examples/agent-livekit-openai.py dev
```
- **What it does**: Full conversational AI with OpenAI's real-time model
- **Use case**: Customer service, virtual assistants, interactive demos
- **Features**: Real-time conversation, web interface, cloud-based LLM

#### 4. Apple Local Agent (Privacy-First)
```bash
# First install: pip install bithuman-voice
# Start service: bithuman-voice serve --port 8091
python examples/agent-livekit-apple-local.py dev
```
- **What it does**: Completely local processing using Apple's Speech APIs
- **Use case**: Privacy-sensitive applications, offline demos
- **Features**: Local STT/TTS, no internet required for voice processing
- **💡 Pro tip**: Replace OpenAI LLM with local models (e.g., ollama) for **100% local operation** on devices like Mac Mini

#### 5. Raspberry Pi Optimized Agent
```bash
python examples/agent-livekit-rasp-pi.py dev
```
- **What it does**: Optimized for low-power devices like Raspberry Pi
- **Use case**: IoT devices, edge computing, embedded systems
- **Features**: Sync loading mode, memory optimization

5. **Connect:** Open `http://localhost:3000` and join a room to chat with your avatar!

## 🎮 Agent CLI Modes

The LiveKit agent examples support three mutually exclusive CLI modes:

| Mode | Command | Purpose | When to Use |
|------|---------|---------|-------------|
| **`console`** | `python agent.py console` | Local terminal testing | Quick testing without web UI |
| **`dev`** | `python agent.py dev` | Development with LiveKit | Testing with web interface, hot reloading |
| **`start`** | `python agent.py start` | Production deployment | Production environments |

**⚠️ Important**: Only use ONE mode at a time - they are mutually exclusive!

## 🛠️ Custom Integration Guide

### Building Your Own Application

The examples in `/examples` demonstrate different integration patterns:

1. **Direct SDK Usage** (`avatar-with-*.py`): For maximum control and custom UIs
2. **LiveKit Integration** (`agent-livekit-*.py`): For web-based applications

### Key Integration Points

- **Audio Input**: File playback, microphone, network streams, custom sources
- **Video Output**: OpenCV, WebRTC, custom renderers, headless processing  
- **Deployment**: Desktop apps, web services, IoT devices, cloud functions
- **Platforms**: macOS, Linux, Windows (via WSL), ARM devices

### Architecture Benefits

- **Async-first**: Built on Python asyncio for high performance
- **Modular**: Use only the components you need
- **Flexible**: Integrate with any audio/video pipeline
- **Scalable**: From single-user desktop apps to multi-tenant web services

## 📋 System Requirements

### Hardware Recommendations
- **Mac**: M2+ (ideally M4) for optimal performance
- **CPU**: 4+ cores with 8GB RAM minimum
- **Raspberry Pi**: Use headless mode with separate web UI device for best experience

### Software Requirements
- **Python 3.11+** (3.9+ supported, 3.11+ recommended)
- **Operating System**: macOS (Apple Silicon), Linux, or Windows (via WSL)
- **API Keys**: OpenAI API key (for OpenAI agent example)
- **LiveKit Account**: Free account for web UI examples ([livekit.io](https://livekit.io))

## 🆘 Support & Community

### Documentation & Guides
- 📖 [Complete Documentation](https://public-sdk-examples.vercel.app) - Comprehensive guides and examples
- 🔧 [LiveKit Agents Docs](https://docs.livekit.io/agents) - Official LiveKit documentation
- 🎯 [bitHuman's LiveKit Plugin](https://docs.livekit.io/agents/integrations/avatar/bithuman/) - Integration guide

### Community & Support
- 💬 [Join our Discord](https://discord.gg/yM7wRRqu) - Get help and discuss with the community
- 🌟 [Community Agents](https://imaginex.bithuman.ai/#community) - Browse and download avatar models
- 🏠 [bitHuman Console](https://imaginex.bithuman.ai) - Manage your API keys and models

**Get help, share your creations, and connect with other developers building with bitHuman!** 🚀
