# bitHuman SDK Examples

Interactive avatar examples using the bitHuman SDK for real-time conversational AI.

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

Get your API secret at [console.bithuman.io](https://console.bithuman.io) and download avatar models from the [Community page](https://console.bithuman.io/#community).

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

2. **Download & setup playground:**
   ```bash
   git clone https://github.com/livekit/agents-playground.git
   cd agents-playground
   npm install
   ```

3. **Configure playground** (create `.env` in agents-playground repo):
   ```bash
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud
   ```

4. **Start playground:**
   ```bash
   npm run dev
   ```

#### 3. OpenAI Conversational Agent
```bash
python examples/agent-livekit-openai.py console dev
```
- **What it does**: Full conversational AI with OpenAI's real-time model
- **Use case**: Customer service, virtual assistants, interactive demos
- **Features**: Real-time conversation, web interface, cloud-based LLM

#### 4. Apple Local Agent (Privacy-First)
```bash
# First install: pip install bithuman-voice
# Start service: bithuman-voice serve --port 8091
python examples/agent-livekit-apple-local.py console dev
```
- **What it does**: Completely local processing using Apple's Speech APIs
- **Use case**: Privacy-sensitive applications, offline demos
- **Features**: Local STT/TTS, no internet required for voice processing
- **💡 Pro tip**: Replace OpenAI LLM with local models (e.g., ollama) for **100% local operation** on devices like Mac Mini

#### 5. Raspberry Pi Optimized Agent
```bash
python examples/agent-livekit-rasp-pi.py console dev
```
- **What it does**: Optimized for low-power devices like Raspberry Pi
- **Use case**: IoT devices, edge computing, embedded systems
- **Features**: Sync loading mode, memory optimization

5. **Connect:** Open `http://localhost:3000` and join a room to chat with your avatar!

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

## 📋 Requirements

- Python 3.11
- macOS (Apple Silicon) or Linux
- OpenAI API key (for OpenAI agent example)
- LiveKit account (for web UI examples)

## 🆘 Support
- [bitHuman Documentation](https://docs.bithuman.io)
- [bitHuman Discord](https://discord.gg/yM7wRRqu)
- [LiveKit Agents Docs](https://docs.livekit.io/agents)
- [bitHuman's LiveKit plugin](https://docs.livekit.io/agents/integrations/avatar/bithuman/)
- [bitHuman Community Agents](https://console.bithuman.io/#community)
