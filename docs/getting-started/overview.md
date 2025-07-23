# Getting Started

Welcome to bitHuman SDK! Create lifelike digital avatars that respond to audio in real-time.

![bitHuman Banner](../assets/images/bithuman-banner.jpg)
*[Transform your applications with engaging, interactive avatars](https://console.bithuman.io/#create)*

---

## What is bitHuman?

bitHuman SDK lets you build **interactive avatars** that:
- ✅ Animate realistically from audio input
- ✅ Show dynamic movement with speech
- ✅ Work in real-time (25 FPS)
- ✅ Integrate easily into any app

## Quick Setup

For complete setup instructions, see our **[README.md](https://github.com/bithuman-prod/public-sdk-examples/blob/main/README.md)** which covers:

### 🚀 Installation
```bash
# 1. Create conda environment
conda create -n bithuman python=3.11
conda activate bithuman

# 2. Install SDK
pip install bithuman --upgrade
```

### 🔑 API Setup
1. Get your API secret at [console.bithuman.io](https://console.bithuman.io)
2. Download an avatar model from the Community page
3. Set environment variables:
```bash
BITHUMAN_API_SECRET=sk_bh_1234567890abcdef...
BITHUMAN_MODEL_PATH=/path/to/model.imx
```

### ⚡ First Avatar (3 lines of code!)
```python
from bithuman import AsyncBithuman

runtime = await AsyncBithuman.create(model_path="model.imx", api_secret="your_secret")
async for frame in runtime.run():
    display_frame(frame)  # Your display logic here
```

## What You Can Build

**Desktop Apps** (Standalone SDK):
- Voice assistants
- Interactive kiosks  
- Custom interfaces

**Web Apps** (LiveKit Integration):
- Video chat avatars
- Customer service bots
- Virtual receptionists

## Ready to Build?

**First**: Learn [✨ Prompt Guide](getting-started/prompts.md) - Master the award-winning CO-STAR framework

**Then**: Explore our guides:

- **[🎬 Media Guide](getting-started/media-guide.md)** - Upload voice, image, and video
- **[🐾 Animal Mode](getting-started/animal-mode.md)** - Create animal avatars

**Finally**: Try **[Examples](examples/overview.md)**:

1. **[Audio Clip Avatar](examples/avatar-with-audio-clip.md)** - Start here (5 minutes)
2. **[Live Microphone Avatar](examples/avatar-with-microphone.md)** - Real-time interaction
3. **[OpenAI Agent](examples/livekit-openai-agent.md)** - Full AI conversation in browser

## Next Steps

1. **Read the [README](https://github.com/bithuman-prod/public-sdk-examples/blob/main/README.md)** for complete setup
2. **Master [✨ CO-STAR Prompts](getting-started/prompts.md)** for effective avatars
3. **Try the [first example](examples/avatar-with-audio-clip.md)**
4. **Browse [Source Code](https://github.com/bithuman-prod/public-sdk-examples)** on GitHub
5. **Join our [Discord](https://discord.gg/yM7wRRqu)** for discussions and requests

## System Requirements

**Minimum:**
- Python 3.11
- 4+ CPU cores  
- 8GB RAM

**Platforms:**
- ✅ macOS (M2+ recommended, M4 ideal)
- ✅ Linux (x64, ARM64)
- ⚠️ Windows (via WSL)

---

*For detailed instructions, troubleshooting, and advanced features, see our **[README.md](https://github.com/bithuman-prod/public-sdk-examples/blob/main/README.md)*** 