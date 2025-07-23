# 🍎 Apple Local Agent

![Apple](https://img.shields.io/badge/Apple-000000?style=for-the-badge&logo=apple&logoColor=white)

> **Private AI using Mac's built-in speech**

Full privacy - speech never leaves your Mac.

---

## 🚀 Quick Start

### 1. Requirements
- macOS 13+ (Apple Silicon recommended)
- Microphone permissions

### 2. Install voice service
```bash
pip install https://github.com/bithuman-prod/public-sdk-examples/releases/download/v0.1/bithuman_voice-1.3.2-py3-none-any.whl
```

### 3. Start voice service
```bash
bithuman-voice serve --port 8091
```
*macOS will ask for Speech permissions - approve this!*

### 4. Install dependencies
```bash
pip install bithuman --upgrade livekit-agents openai silero
```

### 5. Set environment
```bash
export BITHUMAN_API_SECRET="your_secret"
export BITHUMAN_MODEL_PATH="/path/to/model.imx"
export LIVEKIT_API_KEY="your_livekit_key"
export LIVEKIT_API_SECRET="your_livekit_secret"
export LIVEKIT_URL="wss://your-project.livekit.cloud"
export OPENAI_API_KEY="your_openai_key"  # Only for AI brain
```

### 6. Setup web interface (optional)
```bash
git clone https://github.com/livekit/agents-playground.git
cd agents-playground
npm install && npm run dev
```

### 7. Run agent

**Choose your mode:**

**For web streaming:**
```bash
python examples/agent-livekit-apple-local.py dev
```

**For command line testing:**
```bash
python examples/agent-livekit-apple-local.py console
```

---

## 💡 What it does

**Stays on your Mac:**
✅ Speech-to-text (Apple Speech Framework)  
✅ Text-to-speech (Apple Voice Synthesis)  
✅ Avatar animation (bitHuman)  
✅ Voice activity detection (Silero)  

**Uses internet:**
❌ Only AI conversation (OpenAI LLM)

**Privacy benefits:**
- Voice patterns never leave your device
- Apple's hardware-accelerated speech processing
- Full control over your data

---

## 🔧 Common Issues

**Voice service won't start?**
- Check microphone permissions in System Preferences
- Enable "Speech Recognition" in Privacy & Security
- Ensure port 8091 is available

**No speech recognition?**
- Restart the `bithuman-voice` service
- Test with built-in dictation first
- Check microphone input levels

**Permission errors?**
- Run the voice service from Terminal (not IDE)
- Allow Terminal access to microphone in System Preferences

---

## 🎯 Perfect for

✅ **Privacy-sensitive applications**  
✅ **Healthcare/legal/finance**  
✅ **Offline demonstrations**  
✅ **Corporate internal tools**  
✅ **HIPAA/GDPR compliance scenarios**

---

## 🔒 Make it 100% Private

Replace OpenAI with local AI for complete privacy:

```bash
# Install Ollama for local LLM
curl -fsSL https://ollama.ai/install.sh | sh
ollama run llama2
```

Then modify the agent to use local LLM:
```python
# Replace openai.LLM() with local model
llm=openai.LLM(base_url="http://localhost:11434/v1")
```

---

## 📊 Performance

**Apple Silicon benefits:**
- Hardware-accelerated speech processing
- Low power consumption
- Fast local inference

**Recommended specs:**
- M2+ Mac (M4 ideal)  
- 16GB+ RAM
- macOS 13+

---

## ➡️ Next Steps

**Want edge deployment?** → Try [Raspberry Pi Agent](examples/livekit-raspberry-pi.md)

**Need simpler setup?** → Try [OpenAI Agent](examples/livekit-openai-agent.md)

---

*Privacy-first AI made simple!* 🔒 