# 🚀 Welcome to bitHuman SDK

> **Create lifelike digital avatars that respond to audio in real-time**

![bitHuman Banner](assets/images/bithuman-banner.jpg)
*[Transform your applications with engaging, interactive avatars](https://console.bithuman.io/#create)*

---

## ✨ What is bitHuman SDK?

bitHuman SDK lets you build **interactive avatars** that bring your applications to life:

🎯 **Real-time Animation** - 25 FPS video with dynamic movement  
🎤 **Audio-driven** - Realistic facial movements from any audio input  
⚡ **Easy Integration** - 3 lines of code to get started  
🌐 **Web Ready** - Deploy to browsers with LiveKit integration  

---

## 🏃‍♂️ Quick Start

### 1️⃣ Get Your Credentials
- 🔑 **Free API Secret** → [console.bithuman.io](https://console.bithuman.io)
- 🤖 **Download Avatar** → [Community Models](https://console.bithuman.io/#community)

### 2️⃣ Install & Setup
```bash
# Install SDK
pip install bithuman

# Set environment
export BITHUMAN_API_SECRET="your_secret"
export BITHUMAN_MODEL_PATH="/path/to/model.imx"
```

### 3️⃣ Your First Avatar (3 lines!)
```python
from bithuman import AsyncBithuman

runtime = await AsyncBithuman.create(model_path="model.imx", api_secret="secret")
async for frame in runtime.run():
    display_frame(frame)  # Your magic here!
```

---

## 🎯 What You Can Build

### 🖥️ **Desktop Apps**
- Voice assistants
- Interactive kiosks  
- Custom interfaces

### 🌐 **Web Applications**
- Video chat avatars
- Customer service bots
- Virtual receptionists

### 🔧 **IoT & Edge**
- Smart home assistants
- Retail demonstrations
- Industrial interfaces

---

## 📚 Documentation Structure

### 🚀 **[Getting Started](getting-started/overview.md)**
Quick setup, prompts, media uploads, and animal mode

### 💡 **[Examples](examples/overview.md)**
5 simple examples from basic to advanced

---

## 🖥️ Platform Support

| Platform | Status | Notes |
|----------|---------|-------|
| 🐧 **Linux (x86_64)** | ✅ **Full Support** | Production ready |
| 🦾 **Linux (ARM64)** | ✅ **Full Support** | Perfect for edge |
| 🍎 **macOS (Apple Silicon)** | ✅ **Full Support** | M2+ recommended, M4 ideal |
| 🪟 **Windows** | 🔄 **Coming Soon** | Beta available |

---

## 🎯 Why Choose bitHuman?

✅ **3-Line Integration** - Get started instantly  
✅ **Production Ready** - Scales from prototype to millions of users  
✅ **Privacy Focused** - Local processing options available  
✅ **Developer Friendly** - Comprehensive docs and examples  
✅ **Active Community** - Discord support and shared models  

---

## 🚀 Ready to Start?

1. **📖 Read** [Getting Started](getting-started/overview.md)
2. **🛠️ Try** [Audio Clip Example](examples/avatar-with-audio-clip.md) 
3. **📦 Browse** [Source Code](https://github.com/bithuman-prod/public-sdk-examples) on GitHub
4. **💬 Join** [Discord Community](https://discord.gg/yM7wRRqu) for discussions and requests

*Let's build the future of human-computer interaction together!* 🌟
