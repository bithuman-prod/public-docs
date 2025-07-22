# bitHuman SDK Examples

Transform any application into an interactive experience with **photorealistic AI avatars**. The bitHuman SDK makes it incredibly simple to add conversational AI avatars to your projects.

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
# bitHuman SDK (Required)
BITHUMAN_API_SECRET=sk_bh_1234567890abcdef...
BITHUMAN_MODEL_PATH=/path/to/model.imx

# Audio file (Optional - only for avatar-with-audio-clip.py)
BITHUMAN_AUDIO_PATH=/path/to/audio.wav

# OpenAI (Optional - for OpenAI agent example)
OPENAI_API_KEY=sk-proj-1234567890abcdef...

# LiveKit (Optional - for web-based agent examples)
LIVEKIT_API_KEY=APIabcdef123456...
LIVEKIT_API_SECRET=secretABCDEF123456...
LIVEKIT_URL=wss://your-project.livekit.cloud
```

**Get Started:**
- 🔑 Get your API secret at [console.bithuman.io](https://console.bithuman.io)
- 🎭 Download avatar models from the [Community page](https://console.bithuman.io/#community)

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

| Example | Command | Perfect For | Key Features |
|---------|---------|-------------|--------------|
| **🎵 Audio Clip Playback** | `python examples/avatar-with-audio-clip.py` | Presentations, demos, voice-overs, tutorials | 📁 File playback<br/>🎮 Interactive controls<br/>📊 FPS monitoring |
| **🎤 Live Microphone Input** | `python examples/avatar-with-microphone.py` | Voice assistants, interactive kiosks, local chatbots | 🔊 Real-time capture<br/>🔇 Silence detection<br/>🎛️ Volume control |

**🎮 Controls for Audio Clip Example:**
- Press `1` → Play audio file
- Press `2` → Interrupt playback  
- Press `q` → Quit application

### 🌐 LiveKit Agent Examples

Perfect for **web applications**, **multiplayer experiences**, and **scalable services**. These examples show how to integrate bitHuman into LiveKit agents for browser-based interactions.

| Agent Type | Command | Privacy Level | Perfect For | Key Features |
|------------|---------|---------------|-------------|--------------|
| **🤖 OpenAI Conversational** | `python examples/agent-livekit-openai.py console dev` | Cloud-based | Customer service, virtual assistants | ☁️ Real-time LLM<br/>🌐 Web interface<br/>⚡ Low latency |
| **🍎 Apple Local (Privacy-First)** | `python examples/agent-livekit-apple-local.py console dev` | Fully Local | Privacy-sensitive apps, offline demos | 🔒 Local STT/TTS<br/>🏠 Offline capable<br/>🛡️ Complete privacy |
| **🔧 Raspberry Pi Optimized** | `python examples/agent-livekit-rasp-pi.py console dev` | Cloud-based | IoT devices, edge computing | ⚡ Memory optimized<br/>🔄 Sync loading<br/>📱 ARM compatible |

### 🛠️ Setup Instructions

#### LiveKit Playground (Web UI)

1. **Register free LiveKit account** at [livekit.io](https://livekit.io)

2. **Download & setup playground:**
   ```bash
   git clone https://github.com/livekit/agents-playground.git
   cd agents-playground && npm install
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

#### Apple Local Agent (100% Private)

For **maximum privacy** and **offline operation**, you can run everything locally:

```bash
# 1. Install local voice service
pip install bithuman-voice

# 2. Start Apple Speech service
bithuman-voice serve --port 8091

# 3. (Optional) Use local LLM with Ollama for complete privacy
# Install Ollama: https://ollama.com
# ollama serve --port 11434
# ollama pull llama2  # or your preferred model

# 4. Run the agent
python examples/agent-livekit-apple-local.py console dev
```

**🏠 Complete Local Setup:** With both `bithuman-voice` and `ollama`, you can run an entire conversational AI avatar **completely offline** on devices like Mac Mini, with zero data leaving your device!

5. **Connect:** Open `http://localhost:3000` and join a room to chat with your avatar!

## 🛠️ Custom Integration Guide

### 🎯 Choose Your Integration Pattern

| Pattern | Best For | Complexity | Control Level | Example Files |
|---------|----------|------------|---------------|---------------|
| **🖥️ Direct SDK** | Desktop apps, custom UIs, embedded systems | Low | Maximum | `avatar-with-*.py` |
| **🌐 LiveKit Plugin** | Web apps, multiplayer, scalable services | Medium | High | `agent-livekit-*.py` |

### 🔧 Integration Points

| Component | Options | Use Cases |
|-----------|---------|-----------|
| **🎤 Audio Input** | 📁 Files, 🎙️ Microphone, 🌐 Streams, 🔧 Custom | Voice commands, music, podcasts, real-time chat |
| **🖼️ Video Output** | 🖥️ OpenCV, 🌐 WebRTC, 📱 Mobile, 🤖 Headless | Desktop display, web streaming, mobile apps, server processing |
| **🚀 Deployment** | 💻 Desktop, ☁️ Cloud, 🏠 Edge, 📱 Mobile | Local apps, web services, IoT devices, mobile experiences |
| **🌍 Platforms** | 🍎 macOS, 🐧 Linux, 🪟 Windows (WSL), 🔧 ARM | Development, production, edge computing, embedded systems |

### ⚡ Architecture Benefits

<table>
<tr>
<td>

**🚀 Performance**
- Async-first design
- High-throughput processing  
- Optimized for real-time

</td>
<td>

**🧩 Flexibility**
- Modular components
- Custom pipeline integration
- Framework agnostic

</td>
</tr>
<tr>
<td>

**📈 Scalability** 
- Single-user to multi-tenant
- Cloud-native ready
- Auto-scaling compatible

</td>
<td>

**🛡️ Reliability**
- Production-tested
- Error handling built-in
- Graceful degradation

</td>
</tr>
</table>

## 📋 System Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **🐍 Python** | 3.11+ | Required for all examples |
| **💻 Platform** | macOS (Apple Silicon), Linux | Windows via WSL |
| **🔑 API Key** | OpenAI (optional) | Only for OpenAI agent example |
| **🌐 LiveKit** | Free account (optional) | Only for web UI examples |
| **💾 Memory** | 4GB+ RAM | 8GB+ recommended for optimal performance |
| **🔊 Audio** | Microphone/speakers | For interactive examples |

### 🎯 Quick Decision Guide

| I want to... | Use this example | Why? |
|--------------|------------------|------|
| **Build a desktop voice assistant** | `avatar-with-microphone.py` | Full control, local processing |
| **Create interactive presentations** | `avatar-with-audio-clip.py` | Perfect for demos and tutorials |
| **Build a web-based customer service** | `agent-livekit-openai.py` | Scalable, cloud-based intelligence |
| **Ensure complete privacy** | `agent-livekit-apple-local.py` | Everything runs locally |
| **Deploy on Raspberry Pi** | `agent-livekit-rasp-pi.py` | Optimized for low-power devices |

## 🆘 Support & Resources

### 📚 Documentation & Guides
- [📖 bitHuman Documentation](https://docs.bithuman.io) - Complete API reference and tutorials
- [🔌 LiveKit Integration Guide](https://docs.livekit.io/agents/integrations/avatar/bithuman/) - Web deployment guide
- [🤖 LiveKit Agents Docs](https://docs.livekit.io/agents) - Agent framework documentation

### 🤝 Community & Support
- [💬 bitHuman Discord](https://discord.gg/yM7wRRqu) - Get help from the community
- [🎭 Community Agents](https://console.bithuman.io/#community) - Explore pre-built avatars

### 🚀 Ready to Build?

1. **🔑 Get your API key** → [console.bithuman.io](https://console.bithuman.io)
2. **🎭 Download an avatar** → [Community page](https://console.bithuman.io/#community) 
3. **⚡ Run an example** → `python examples/avatar-with-audio-clip.py`
4. **🛠️ Build something amazing!**

---
*Transform your applications with photorealistic AI avatars. The future of human-computer interaction starts here.* ✨
