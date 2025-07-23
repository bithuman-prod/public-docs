# 🤖 OpenAI Agent

![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

> **Full AI conversation with avatar in browser**

Complete chatbot with avatar that users can talk to on the web.

---

## 🚀 Quick Start

### 1. Install
```bash
pip install bithuman livekit-agents openai
```

### 2. Get accounts
- **bitHuman**: [console.bithuman.io](https://console.bithuman.io)
- **OpenAI**: [openai.com](https://openai.com)
- **LiveKit**: [livekit.io](https://livekit.io) (free)

### 3. Set environment
```bash
export BITHUMAN_API_SECRET="your_secret"
export BITHUMAN_MODEL_PATH="/path/to/model.imx"
export OPENAI_API_KEY="your_openai_key"
export LIVEKIT_API_KEY="your_livekit_key"
export LIVEKIT_API_SECRET="your_livekit_secret"
export LIVEKIT_URL="wss://your-project.livekit.cloud"
```

### 4. Setup web interface
```bash
git clone https://github.com/livekit/agents-playground.git
cd agents-playground
npm install && npm run dev
```

### 5. Run agent

**Choose your mode:**

**For web streaming (recommended):**
```bash
python examples/agent-livekit-openai.py dev
```

**For command line testing:**
```bash
python examples/agent-livekit-openai.py console
```

### 6. Open browser
Go to `http://localhost:3000` and join a room to chat!

---

## 💡 What it does

1. User speaks in browser
2. AI processes speech and responds intelligently
3. Avatar shows AI's response with dynamic movement
4. Works from any device with internet

**Built with:**
- **OpenAI GPT-4** for intelligent conversation
- **LiveKit** for web streaming
- **bitHuman** for avatar animation

---

## 🔧 Run Modes

**`dev` mode** (streaming to web):
- Connects to LiveKit for web browsers
- Users interact through web interface
- Best for production deployment

**`console` mode** (command line):  
- Runs in terminal for testing
- Useful for debugging
- No web interface needed

---

## 🛠️ Common Issues

**Agent won't start?**
- Check all API keys are set
- Verify LiveKit credentials at [livekit.io](https://livekit.io)

**No audio in browser?**
- Allow microphone permissions
- Try different browser (Chrome recommended)

**Can't connect?**
- Check LiveKit URL format: `wss://your-project.livekit.cloud`
- Ensure agents-playground is running on port 3000

---

## 🎯 Perfect for

✅ **Customer service bots**  
✅ **Educational assistants**  
✅ **Website chatbots**  
✅ **Interactive demos**

---

## ⚙️ Customization

Change the agent's personality by editing the `instructions`:

```python
agent=Agent(
    instructions=(
        "You are a helpful customer service assistant. "
        "Be friendly, professional, and solve problems quickly."
    )
)
```

**Example personalities:**
- **Tech Support**: "You are a patient tech expert who explains things simply"
- **Sales Assistant**: "You are an enthusiastic product advisor who helps customers find what they need"
- **Teacher**: "You are an encouraging tutor who makes learning fun"

---

## ➡️ Next Steps

**Want privacy?** → Try [Apple Local Agent](examples/livekit-apple-local.md)

**Using IoT?** → Try [Raspberry Pi Agent](examples/livekit-raspberry-pi.md)

---

*Full AI conversation made easy!* 🚀 