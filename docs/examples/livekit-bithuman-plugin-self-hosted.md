# 🚀 LiveKit bitHuman Plugin - Self-Hosted Mode

![Self-Hosted](https://img.shields.io/badge/Self--Hosted-FF6B6B?style=for-the-badge) ![LiveKit](https://img.shields.io/badge/LiveKit-00D4AA?style=for-the-badge&logo=livekit&logoColor=white)

> **bitHuman LiveKit Plugin Integration for Self-Hosted Deployment**

Use bitHuman agents in real-time applications with self-hosted deployment, featuring direct model file access and VideoControl-based gesture triggering.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd examples/self-hosted
pip install -r requirements.txt
```

### 2. Get API Credentials
- **API Secret**: [imaginex.bithuman.ai](https://imaginex.bithuman.ai/#developer)
- **Model File**: Download your `.imx` model file from the platform

### 3. Configure Environment

Create a `.env` file:

```env
# bitHuman Configuration
BITHUMAN_API_SECRET=your_api_secret_here
BITHUMAN_MODEL_PATH=/path/to/your/avatar_model.imx
BITHUMAN_AGENT_ID=A31KJC8622  # Optional: for fetching dynamics gestures

# OpenAI Configuration (for conversational AI)
OPENAI_API_KEY=your_openai_api_key_here

# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

### 4. Run Basic Agent

```bash
python agent.py dev
```

---

## 💡 Usage Examples

### **Basic Self-Hosted Agent**

For standard avatar interactions without dynamics:

```python
# See examples/self-hosted/agent.py
# Basic agent with native AsyncBithuman integration
```

**Key Features:**
- Direct model file access (`.imx` format)
- Native AsyncBithuman runtime integration
- High-performance streaming with VideoGenerator pattern
- Real-time audio/video processing

### **Self-Hosted Agent with Dynamics (RPC-based Gesture Triggers)**

For reactive avatar gestures triggered by user speech keywords:

**Step 1: Get Available Gesture Actions**

Before setting up keyword triggers, retrieve the list of available gesture actions for your agent. The available gestures are user-defined and generated based on your agent's dynamics configuration. See the [Get Dynamics endpoint](../preview/dynamics-api.md#get-dynamics) in the Dynamics API documentation for details.

```python
import requests

# Get available gestures for your agent
agent_id = "A31KJC8622"
url = f"https://public.api.bithuman.ai/v1/dynamics/{agent_id}"
headers = {"api-secret": "YOUR_API_SECRET"}

response = requests.get(url, headers=headers)
dynamics_data = response.json()

if dynamics_data.get("success"):
    # gestures is now a dictionary: {gesture_key: video_url}
    gestures_dict = dynamics_data["data"].get("gestures", {})
    available_gestures = list(gestures_dict.keys())
    print(f"Available gestures: {available_gestures}")
    # Example output: ["mini_wave_hello", "talk_head_nod_subtle", "blow_kiss_heart", "laugh_react"]
else:
    print("Failed to get dynamics or agent has no dynamics configured")
    available_gestures = []
```

> **Note:** The gesture actions are user-defined and vary based on your agent's dynamics generation. Always check the `gestures` dictionary from the API response to see what actions are available for your specific agent.

**Step 2: Set Up Keyword-to-Action Mapping**

Once you know the available gestures, create a keyword mapping. The `agent_with_dynamics.py` example automatically creates keyword mappings from the gestures dictionary, but you can customize them:

```python
from livekit.agents import AgentSession, JobContext, UserInputTranscribedEvent
from livekit.agents.voice.room_io import TextInputEvent
from livekit.plugins import bithuman
from bithuman.api import VideoControl
import asyncio
import os

# Keyword-to-action mapping (use gestures from Step 1)
KEYWORD_ACTION_MAP = {
    "laugh": "laugh_react",
    "laughing": "laugh_react",
    "haha": "laugh_react",
    "funny": "laugh_react",
    "hello": "mini_wave_hello",
    "hi": "mini_wave_hello",
    "hey": "mini_wave_hello",
    # Add more mappings based on available_gestures from Step 1
}

def detect_keyword_action(transcript: str, keyword_map: dict[str, str]) -> str | None:
    """Detect if transcript contains any keywords and return corresponding action."""
    transcript_lower = transcript.lower()
    for keyword, action in keyword_map.items():
        if keyword in transcript_lower:
            return action
    return None

async def entrypoint(ctx: JobContext):
    """Agent entrypoint with dynamics support"""
    await ctx.connect()
    await ctx.wait_for_participant()
    
    # Initialize bitHuman avatar session with model_path (self-hosted mode)
    bithuman_avatar = bithuman.AvatarSession(
        api_secret=os.getenv("BITHUMAN_API_SECRET"),
        model_path=os.getenv("BITHUMAN_MODEL_PATH"),  # Use model_path for self-hosted
    )
    
    # Configure and start session (see agent_with_dynamics.py for full implementation)
    session = AgentSession(...)
    await bithuman_avatar.start(session, room=ctx.room)
    
    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):
        """Detect keywords and trigger dynamics"""
        if not event.is_final:
            return
        
        transcript = event.transcript.lower()
        action = detect_keyword_action(transcript, KEYWORD_ACTION_MAP)
        
        if action:
            # Trigger gesture using VideoControl (self-hosted pattern)
            asyncio.create_task(
                bithuman_avatar.runtime.push(VideoControl(action=action))
            )
```

**How it works:**
1. **Get available gestures** - Call `GET /v1/dynamics/{agent_id}` to retrieve the dictionary of available gesture actions (keys are gesture names, values are video URLs)
2. **Extract gesture keys** - Get the list of gesture names from the `gestures` dictionary keys
3. **Map keywords to actions** - Create a keyword-to-action mapping using the gesture names from step 2
4. **Listen for user input** - Agent listens to user speech via `user_input_transcribed` events
5. **Detect keywords** - When keywords like "laugh" are detected, it triggers gestures via VideoControl
6. **Trigger gestures** - Avatar runtime receives `VideoControl(action=action)` and executes corresponding gestures
7. **Cooldown protection** - Gestures are triggered with cooldown protection to prevent spam

**Example Flow:**
1. Get dynamics status: `GET /v1/dynamics/A31KJC8622` → Returns `{"gestures": {"mini_wave_hello": "https://...", "laugh_react": "https://..."}}`
2. Extract gesture keys: `available_gestures = list(response["data"]["gestures"].keys())` → `["mini_wave_hello", "laugh_react"]`
3. User says "That's funny!" → Agent detects "funny" keyword
4. Agent calls `bithuman_avatar.runtime.push(VideoControl(action="laugh_react"))` → Avatar performs laughing gesture

**Important:** Always verify that the gesture action exists in the `gestures` dictionary keys before using it in your keyword mapping. Using a non-existent gesture will result in the gesture being ignored by the avatar runtime.

> **⏱️ Performance Note:** When using dynamics with self-hosted deployment, the avatar runtime model connection and loading typically takes approximately **20 seconds** on first initialization.

See [agent_with_dynamics.py](https://github.com/bithuman-prod/public-docs/tree/main/examples/self-hosted/agent_with_dynamics.py) for a complete working example.

---

## 🔧 Configuration Options

### **Agent Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model_path` | string | Yes | Path to the `.imx` model file |
| `api_secret` | string | Yes | Authentication secret from bitHuman platform |
| `api_token` | string | No | Optional API token for authentication |
| `agent_id` | string | No | Agent ID for fetching dynamics gestures from API |

### **Model Types**

**Self-Hosted Model:**
- Direct access to `.imx` model files
- Full control over model deployment
- No cloud dependencies for model loading
- Supports all gesture types configured in dynamics
- Higher memory requirements (typically 4-8GB RAM)

---

## 🌐 Self-Hosted Advantages

✅ **Full Control** - Complete control over model files and deployment  
✅ **Privacy** - Models stay on your infrastructure  
✅ **Customization** - Modify and extend agent behavior  
✅ **Performance** - Optimize for your specific hardware  
✅ **Offline Capable** - Works without internet after initial setup  

---

## 🛠️ Advanced Integration

### **Session Management**

```python
from livekit.plugins import bithuman
from bithuman.api import VideoControl

class SelfHostedAvatarManager:
    def __init__(self, model_path: str, api_secret: str):
        self.model_path = model_path
        self.api_secret = api_secret
        self.avatar_session: Optional[bithuman.AvatarSession] = None
    
    async def create_avatar_session(self):
        """Create BitHuman avatar session"""
        self.avatar_session = bithuman.AvatarSession(
            api_secret=self.api_secret,
            model_path=self.model_path,
        )
        return self.avatar_session
    
    async def trigger_gesture(self, action: str):
        """Trigger gesture using VideoControl"""
        if self.avatar_session:
            await self.avatar_session.runtime.push(VideoControl(action=action))
```

### **Error Handling**

```python
from livekit.plugins import bithuman

try:
    avatar_session = bithuman.AvatarSession(
        api_secret="your_api_secret",
        model_path="path/to/model.imx",
    )
    
    # Use avatar_session...
    
except FileNotFoundError:
    print("Model file not found. Check BITHUMAN_MODEL_PATH.")
    
except ValueError as e:
    print(f"Invalid configuration: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## 🔍 Monitoring & Debugging

### **Enable Logging**

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('bithuman-selfhosted')

# Runtime will log detailed information
```

### **Performance Metrics**

```python
import time

start_time = time.time()
# Initialize runtime...
init_time = time.time() - start_time
print(f"Runtime initialized in {init_time:.2f} seconds")
```

---

## 🚨 Common Issues

**Model Loading Errors:**
- Verify model file path is correct and accessible
- Check file permissions
- Ensure model file is not corrupted

**Memory Issues:**
- Increase available RAM (minimum 4GB, recommended 8GB+)
- Consider using a smaller model
- Monitor system resources

**Gesture Not Triggering:**
- Verify gesture name exists in dynamics API response
- Check VideoControl is being called correctly
- Ensure gesture cooldown has expired

**Connection Issues:**
- Verify LiveKit server URL and credentials
- Check network connectivity
- Ensure room exists or can be created

---

## 🎯 Perfect for

✅ **Enterprise Deployment** - Full control over infrastructure  
✅ **Privacy-Sensitive Applications** - Models stay on-premises  
✅ **Custom Integrations** - Extend and modify as needed  
✅ **High-Performance Requirements** - Optimize for your hardware  
✅ **Offline Applications** - Work without cloud dependencies  

---

## 📊 Model Requirements

**Supported Formats:**
- `.imx` files (bitHuman's optimized format)

**Hardware Requirements:**
- Minimum: 4GB RAM, CPU-only
- Recommended: 8GB+ RAM, GPU support
- Model Size: Typically 50MB - 500MB

**Performance:**
- Initialization: ~20 seconds
- Frame Rate: 25 FPS (configurable)
- Audio Sample Rate: 16kHz (configurable)

---

## ➡️ Next Steps

**Full Example:** [agent_with_dynamics.py](https://github.com/bithuman-prod/public-docs/tree/main/examples/self-hosted/agent_with_dynamics.py)  
**Basic Example:** [agent.py](https://github.com/bithuman-prod/public-docs/tree/main/examples/self-hosted/agent.py)  
**API Documentation:** [Dynamics API](../preview/dynamics-api.md)  
**Cloud Plugin:** [LiveKit Cloud Plugin](../preview/livekit-cloud-plugin.md)  
**Community Support:** [Discord](https://discord.gg/ES953n7bPA)  

---

*Self-hosted avatars with full control!* 🏠✨

