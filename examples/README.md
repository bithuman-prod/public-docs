# bitHuman SDK Examples

Welcome to the bitHuman SDK examples! This directory contains practical examples demonstrating different ways to integrate interactive avatars into your applications.

## 📁 Example Categories

### 🌐 **Cloud Examples** - LiveKit Agent Integration
For web applications, multiplayer experiences, and scalable services.

#### [Cloud/Essence](./cloud/essence/) - Basic Cloud Setup ⭐
- **File**: `agent.py`
- **Complexity**: Beginner
- **Setup time**: 5 minutes
- **Description**: Simple cloud-based avatar using pre-configured avatar ID
- **Best for**: Learning, quick prototyping

#### [Cloud/Expression](./cloud/expression/) - Advanced Cloud Setup 🎨
- **Files**: `agent_with_avatar_id.py`, `agent_with_avatar_image.py`
- **Complexity**: Intermediate
- **Setup time**: 10-15 minutes
- **Description**: Advanced avatar customization with custom images and enhanced controls
- **Best for**: Production apps, custom branding

### 🖥️ **Standalone Examples** - Direct SDK Integration
For desktop applications, custom UIs, and embedded systems.

#### [Avatar with Audio Clip](./avatar-with-audio-clip.py) 🎵
- **Complexity**: Beginner
- **Description**: Play pre-recorded audio files with synchronized avatar animation
- **Use cases**: Presentations, demos, voice-overs, tutorials
- **Features**: Audio file playback, OpenCV display, FPS control

#### [Avatar with Microphone](./avatar-with-microphone.py) 🎤
- **Complexity**: Beginner
- **Description**: Real-time avatar animation from microphone input
- **Use cases**: Voice assistants, interactive kiosks, local chatbots
- **Features**: Live audio capture, volume control, silence detection

### 🤖 **Agent Examples** - LiveKit Integration
For conversational AI agents with web interfaces.

#### [OpenAI Agent](./agent-livekit-openai.py) 🧠
- **Complexity**: Intermediate
- **Description**: Full conversational AI using OpenAI's real-time model
- **Use cases**: Customer service, virtual assistants, interactive demos
- **Features**: Real-time conversation, web interface, cloud-based LLM

#### [Apple Local Agent](./agent-livekit-apple-local.py) 🍎
- **Complexity**: Advanced
- **Description**: Completely local processing using Apple's Speech APIs
- **Use cases**: Privacy-sensitive applications, offline demos
- **Features**: Local STT/TTS, no internet required for voice processing

#### [Raspberry Pi Agent](./agent-livekit-rasp-pi.py) 🥧
- **Complexity**: Intermediate
- **Description**: Optimized for low-power devices like Raspberry Pi
- **Use cases**: IoT devices, edge computing, embedded systems
- **Features**: Sync loading mode, memory optimization

## 🚀 Quick Start Guide

### 1. Choose Your Path

**🆕 New to bitHuman?**
→ Start with [Cloud/Essence](./cloud/essence/) for the easiest setup

**🖥️ Building desktop apps?**
→ Try [Avatar with Audio Clip](./avatar-with-audio-clip.py)

**🌐 Need web integration?**
→ Explore [Cloud Examples](./cloud/)

**🔒 Privacy-focused?**
→ Check out [Apple Local Agent](./agent-livekit-apple-local.py)

### 2. Prerequisites

All examples require:
```bash
# Create environment
conda create -n bithuman python=3.11
conda activate bithuman

# Basic installation
pip install bithuman --upgrade
```

**📦 Install dependencies:**
```bash
# Navigate to your chosen example directory
cd cloud/essence/     # or any other example directory

# Install from requirements.txt (each example has its own)
pip install -r requirements.txt
```

### 3. Get Credentials

#### bitHuman API Secret (Required for all)
1. Visit [imaginex.bithuman.ai](https://imaginex.bithuman.ai/#developer)
2. Create account → Developer section → Generate API secret

#### Download Avatar Models (Required for standalone)
1. Go to [Community page](https://imaginex.bithuman.ai/#community)
2. Download `.imx` model files

#### LiveKit Account (For cloud/agent examples)
1. Sign up at [livekit.io](https://livekit.io)
2. Create project → Get API keys

#### OpenAI API Key (For AI conversation)
1. Visit [platform.openai.com](https://platform.openai.com/api-keys)
2. Create API key with Realtime API access

## 🎯 Example Comparison

| Example | Platform | AI | Voice | Setup | Use Case |
|---------|----------|----|---------:|-------|----------|
| **Cloud/Essence** | Web | ✅ | Cloud | Easy | Quick start, learning |
| **Cloud/Expression** | Web | ✅ | Cloud | Medium | Production, custom avatars |
| **Audio Clip** | Desktop | ❌ | File | Easy | Presentations, demos |
| **Microphone** | Desktop | ❌ | Live | Easy | Voice assistants, kiosks |
| **OpenAI Agent** | Web | ✅ | Cloud | Medium | Customer service, chat |
| **Apple Local** | macOS | ✅ | Local | Hard | Privacy, offline |
| **Raspberry Pi** | Linux | ✅ | Cloud | Medium | IoT, edge computing |

## 🛠️ Common Setup Steps

### Environment Variables Template

Create `.env` file for your chosen example:

```bash
# bitHuman (Required for all)
BITHUMAN_API_SECRET=sk_bh_your_secret_here
BITHUMAN_MODEL_PATH=/path/to/model.imx  # For standalone examples

# OpenAI (For AI conversation)
OPENAI_API_KEY=sk-proj_your_key_here

# LiveKit (For cloud/agent examples)
LIVEKIT_API_KEY=APIyour_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=wss://your-project.livekit.cloud

# Optional: Custom settings
OPENAI_VOICE=coral
AVATAR_PERSONALITY="You are a helpful assistant..."
```

### Running Examples

**Standalone examples:**
```bash
python avatar-with-audio-clip.py
python avatar-with-microphone.py
```

**Agent examples:**
```bash
# Development mode with web UI
python agent-livekit-openai.py dev

# Production mode  
python agent-livekit-openai.py start

# Console testing
python agent-livekit-openai.py console
```

**🎮 Testing with LiveKit Playground:**
1. Start any agent in `dev` mode
2. Visit [agents-playground.livekit.io](https://agents-playground.livekit.io)
3. Use your **same LiveKit credentials** from `.env`
4. **Connection times**: Essence (~30s), Expression (~1 min)
5. Grant microphone access and start chatting!

## 🎨 Customization Tips

### Avatar Selection
- **Standalone**: Download different `.imx` models from community
- **Cloud**: Use different `avatar_id` values or custom `avatar_image`

### Voice Customization
- **OpenAI voices**: alloy, echo, fable, onyx, nova, shimmer, coral
- **Local voices**: Use Apple Speech (macOS) or other TTS engines

### Personality Tuning
Modify AI instructions for different use cases:
```python
instructions="You are a [ROLE] with [PERSONALITY]. Respond in [STYLE]."
```

## 🔧 Troubleshooting

### Common Issues

1. **Import errors**: Check dependencies are installed
2. **API failures**: Verify API keys are correct and active
3. **Audio issues**: Check microphone permissions and drivers
4. **Performance**: Monitor CPU/memory usage, adjust settings

### Getting Help

- 📖 Check individual example README files for detailed instructions
- 💬 Join [Discord community](https://discord.gg/ES953n7bPA) for support
- 🔍 Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`

## 📚 Learning Path

**Week 1: Basics**
1. Start with [Cloud/Essence](./cloud/essence/)
2. Try [Avatar with Audio Clip](./avatar-with-audio-clip.py)
3. Understand basic concepts

**Week 2: Interaction**
1. Explore [Avatar with Microphone](./avatar-with-microphone.py)
2. Set up [OpenAI Agent](./agent-livekit-openai.py)
3. Practice voice interactions

**Week 3: Customization**
1. Try [Cloud/Expression](./cloud/expression/) examples
2. Experiment with custom images and voices
3. Build your first custom application

**Week 4: Advanced**
1. Explore [Apple Local Agent](./agent-livekit-apple-local.py)
2. Try [Raspberry Pi Agent](./agent-livekit-rasp-pi.py)
3. Deploy to production

## 🌟 Community Showcase

Share your creations:
- 💬 [Discord Community](https://discord.gg/ES953n7bPA)
- 🎥 Demo videos and screenshots welcome
- 🔄 Contribute improvements via GitHub

## 📖 Additional Resources

- 🏠 [bitHuman Console](https://imaginex.bithuman.ai) - Manage API keys and models
- 📚 [Complete Documentation](https://docs.bithuman.ai) - Comprehensive guides
- 🔧 [LiveKit Docs](https://docs.livekit.io/agents) - Platform documentation
- 🎯 [Integration Guide](https://docs.livekit.io/agents/integrations/avatar/bithuman/) - Official LiveKit integration

---

**Ready to start building?** Choose an example above and follow its README for detailed setup instructions! 🚀
