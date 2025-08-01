# 🚀 bitHuman SDK

> **Create lifelike digital avatars that respond to audio in real-time**

<style>
@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); }
  50% { box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5); }
}
@keyframes pulseGlowPink {
  0%, 100% { box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3); }
  50% { box-shadow: 0 8px 25px rgba(240, 147, 251, 0.5); }
}
.panel-openai {
  animation: pulseGlow 3s ease-in-out infinite;
}
.panel-apple {
  animation: pulseGlowPink 3s ease-in-out infinite;
}
</style>

<div style="display: flex; gap: 20px; margin: 30px 0; flex-wrap: wrap;">

<div class="panel-openai" style="flex: 1; min-width: 300px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 25px; color: white; text-align: center; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.transform='translateY(-5px) scale(1.02)'; this.style.boxShadow='0 15px 35px rgba(102, 126, 234, 0.6)'; this.style.animation='none'" onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 8px 25px rgba(102, 126, 234, 0.3)'; this.className='panel-openai'">
  <a href="https://github.com/bithuman-prod/public-docker-example" style="text-decoration: none; color: white; display: block;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 15px;">
      <img src="assets/images/openai.svg" alt="OpenAI" style="width: 40px; height: 40px; background: white; border-radius: 8px; padding: 5px;">
      <h3 style="margin: 0; font-size: 24px;">bitHuman + OpenAI</h3>
    </div>
    <p style="margin: 0 0 15px 0; font-size: 16px; opacity: 0.9;">Complete Docker setup with web UI</p>
    <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; margin: 15px 0;">
      <strong>✨ Cloud-Powered AI Conversations</strong>
    </div>
    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.8;">LiveKit + OpenAI + Web Interface</p>
  </a>
</div>

<div class="panel-apple" style="flex: 1; min-width: 300px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; padding: 25px; color: white; text-align: center; box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3); transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.transform='translateY(-5px) scale(1.02)'; this.style.boxShadow='0 15px 35px rgba(240, 147, 251, 0.6)'; this.style.animation='none'" onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 8px 25px rgba(240, 147, 251, 0.3)'; this.className='panel-apple'">
  <a href="https://github.com/bithuman-prod/public-macos-offline-example" style="text-decoration: none; color: white; display: block;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 15px;">
      <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/apple/apple-original.svg" alt="Apple" style="width: 40px; height: 40px; filter: invert(1);">
      <h3 style="margin: 0; font-size: 24px;">bitHuman + Apple</h3>
    </div>
    <p style="margin: 0 0 15px 0; font-size: 16px; opacity: 0.9;">100% local, most cost effective</p>
    <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; margin: 15px 0;">
      <strong>🔒 Private On-Device AI</strong>
    </div>
    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.8;">Apple Speech + Siri + Ollama LLM</p>
  </a>
</div>

</div>

---

## ✨ What is bitHuman SDK?

bitHuman SDK lets you build **interactive avatars** that bring your applications to life:

💻 **🌟 CPU-Only Operation** - Runs entirely on host CPU, **no GPU required!**  
💰 **10x Lower Costs** - Choose host device or CPU cloud for dramatic cost savings  
🎯 **Real-time Animation** - 25 FPS video with dynamic movement  
🎤 **Audio-driven** - Realistic facial movements from any audio input  
⚡ **Easy Integration** - 3 lines of code to get started  
🌐 **Web Ready** - Deploy to browsers with LiveKit integration  

---

## 🔮 Preview API

> **Early Access: bitHuman Cloud API**  
> Experience the power of bitHuman avatars through our cloud-hosted API service.

### 🔑 Authentication

Get your API secret from [imaginex.bithuman.ai](https://imaginex.bithuman.ai/#api)

### 📡 Base URL
```
https://public.api.bithuman.ai
```

### 🚀 Endpoints

#### Generate Agent

**`POST /v1/agent/generate`**

Create a new interactive avatar agent with customizable parameters.

**Headers:**
```http
Content-Type: application/json
api-secret: YOUR_API_SECRET
```

**Request Body:**
```json
{
  "prompt": "string (optional)",
  "agent_id": "string (optional)",
  "aspect_ratio": "string (optional)",
  "video_aspect_ratio": "string (optional)", 
  "duration": "number (optional)",
  "image": "string (optional)",
  "video": "string (optional)",
  "audio": "string (optional)"
}
```

**Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|----------|
| `prompt` | string | Custom system prompt for the agent | `"You are a friendly AI assistant"` |
| `image` | string | Image URL or base64 data | `"https://example.com/image.jpg"` |
| `video` | string | Video URL or base64 data | `"https://example.com/video.mp4"` |
| `audio` | string | Audio URL or base64 data | `"https://example.com/audio.mp3"` |

**Response:**
```json
{
  "success": true,
  "message": "Agent generation started",
  "agent_id": "A91XMB7113",
  "status": "processing"
}
```

**Example Request:**
```python
import requests

url = "https://public.api.bithuman.ai/v1/agent/generate"
headers = {
    "Content-Type": "application/json",
    "api-secret": "YOUR_API_SECRET"
}
payload = {
    "prompt": "You are a professional video content creator who helps with social media content."
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

**Example with Media:**
```python
payload = {
    "prompt": "You are an art critic who analyzes visual artworks.",
    "image": "https://example.com/artwork.jpg"
}

response = requests.post(url, headers=headers, json=payload)
```

---

#### Get Agent Status

**`GET /v1/agent/status/{agent_id}`**

Retrieve the current status and details of a specific agent.

**Headers:**
```http
api-secret: YOUR_API_SECRET
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | string | The unique identifier of the agent |

**Response:**
```json
{
  "success": true,
  "data": {
    "agent_id": "agent id",
    "event_type": "lip_created",
    "status": "ready",
    "error_message": null,
    "created_at": "2025-08-01T13:58:51.907177+00:00",
    "updated_at": "2025-08-01T09:59:15.159901+00:00",
    "system_prompt": "your agent prompt",
    "image_url": "your_image_url",
    "video_url": "your_video_url",
    "name": "agent name",
    "model_url": "your model url"
  }
}
```

**Status Values:**
- `processing` - Agent is currently being generated
- `ready` - Agent generation completed successfully
- `failed` - Agent generation failed

**Example Request:**
```python
import requests

agent_id = "A81FMS8296"
url = f"https://public.api.bithuman.ai/v1/agent/status/{agent_id}"
headers = {
    "api-secret": "YOUR_API_SECRET"
}

response = requests.get(url, headers=headers)
print(response.json())
```

**Complete Example:**
```python
import requests
import time

# Step 1: Create agent
generate_url = "https://public.api.bithuman.ai/v1/agent/generate"
headers = {
    "Content-Type": "application/json",
    "api-secret": "YOUR_API_SECRET"
}

payload = {
    "prompt": "You are a friendly AI assistant that helps with creative writing."
}

# Generate agent
response = requests.post(generate_url, headers=headers, json=payload)
result = response.json()
agent_id = result["data"]["agent_id"]

print(f"Agent created: {agent_id}")

# Step 2: Poll for completion
status_url = f"https://public.api.bithuman.ai/v1/agent/status/{agent_id}"
status_headers = {"api-secret": "YOUR_API_SECRET"}

while True:
    status_response = requests.get(status_url, headers=status_headers)
    status_data = status_response.json()
    status = status_data["data"]["status"]
    
    if status == "ready":
        print(f"Agent ready: {status_data['data']['model_url']}")
        break
    elif status == "failed":
        print("Generation failed")
        break
    
    time.sleep(5)  # Wait 5 seconds before checking again
```

### 🔧 Error Handling

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API secret)
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "error": "Invalid API secret",
  "code": "UNAUTHORIZED",
  "details": "Please check your API secret from imaginex.bithuman.ai"
}
```

---

## 🏃‍♂️ Quick Start

### 🐳 **Fastest Way: Complete Docker Demo**

Get a **full end-to-end bitHuman + LiveKit app with web UI** running in minutes!

**What you get:** Complete visual agent with real-time conversation, web interface, and audio support.

📦 **[Full Example Repository →](https://github.com/bithuman-prod/public-docker-example)**

#### 1️⃣ Get Your Credentials
- 🔑 **Free API Secret** → [imaginex.bithuman.ai](https://imaginex.bithuman.ai)
  
  ![Free API Secret](assets/images/example-api-secret.jpg)

- 🤖 **Download Avatar** → [Community Models](https://imaginex.bithuman.ai/#community)
  
  ![Download Avatar](assets/images/example-download-button.jpg)

#### 2️⃣ Clone & Setup
```bash
# Clone the complete demo
git clone https://github.com/bithuman-prod/public-docker-example.git
cd public-docker-example

# Create environment file
echo "BITHUMAN_API_SECRET=your_api_secret_here" > .env
echo "OPENAI_API_KEY=your_openai_key_here" >> .env

# Add your .imx model files to models/ directory
mkdir -p models
# Copy your downloaded .imx files here
```

#### 3️⃣ Launch Complete App
```bash
# Start all services (LiveKit + Agent + Web UI + Redis)
docker compose up

# Open your browser to http://localhost:4202
# 🎉 Interactive avatar ready!
```

**🌟 That's it!** You now have a complete bitHuman application with:
- ✅ Real-time avatar animation
- ✅ Voice conversation capabilities  
- ✅ Professional web interface
- ✅ Full LiveKit integration

---

### 🛠️ **Alternative: SDK Integration**

For custom applications, integrate bitHuman directly:

#### Install & Setup
```bash
# Install SDK
pip install bithuman --upgrade

# Set environment
export BITHUMAN_API_SECRET="your_secret"
export BITHUMAN_MODEL_PATH="/path/to/model.imx"
```

#### Your First Avatar (3 lines!)
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

✅ **💻 CPU-Only Runtime** - No expensive GPUs needed, 10x lower costs  
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
