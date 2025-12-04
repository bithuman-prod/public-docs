# 🎭 Dynamics API

> **Agent Movement Generation Service**  
> Generate and manage dynamic movements and animations for bitHuman agents.

## 🔑 Authentication

Get your API secret from [imaginex.bithuman.ai](https://imaginex.bithuman.ai/#developer)

## 📡 Base URL
```
https://public.api.bithuman.ai
```

## 🚀 Endpoints

### Generate Dynamics

**`POST /v1/dynamics/generate`**

Generate dynamic movements and animations for an agent. This creates various motion patterns that can be triggered by keywords or used for idle animations.

**Headers:**
```http
Content-Type: application/json
api-secret: YOUR_API_SECRET
```

**Request Body:**
```json
{
  "agent_id": "string (required)",
  "image_url": "string (optional)",
  "duration": "number (optional)",
  "model": "string (optional)"
}
```

**Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|----------|
| `agent_id` | string | Agent ID to generate dynamics for | `"A91XMB7113"` |
| `image_url` | string | Agent image URL (will fetch from agent data if not provided) | `"https://example.com/image.jpg"` |
| `duration` | number | Duration of each motion in seconds | `5` |
| `model` | string | Model to use for generation | `"seedance"` |

**Response:**
```json
{
  "success": true,
  "message": "Dynamics generation started",
  "agent_id": "A91XMB7113",
  "status": "processing"
}
```

> **Note:** This endpoint returns immediately with a "processing" status. Use the GET dynamics endpoint to check completion status.

**Example Request:**
```python
import requests

url = "https://public.api.bithuman.ai/v1/dynamics/generate"
headers = {
    "Content-Type": "application/json",
    "api-secret": "YOUR_API_SECRET"
}
payload = {
    "agent_id": "A91XMB7113",
    "image_url": "https://example.com/agent-image.jpg",  # Optional
    "duration": 5,
    "model": "seedance"
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

### Get Dynamics

**`GET /v1/dynamics/{agent_id}`**

Retrieve the current dynamics configuration and status for a specific agent.

**Headers:**
```http
api-secret: YOUR_API_SECRET
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | string | Agent ID to get dynamics for |

**Response (when dynamics are generated):**
```json
{
  "success": true,
  "data": {
    "url": "https://storage.supabase.co/dynamics-model.imx",
    "status": "ready",
    "agent_id": "A91XMB7113",
    "gestures": {
      "mini_wave_hello": "https://storage.supabase.co/mini_wave_hello.mp4",
      "talk_head_nod_subtle": "https://storage.supabase.co/talk_head_nod_subtle.mp4",
      "blow_kiss_heart": "https://storage.supabase.co/blow_kiss_heart.mp4"
    }
  }
}
```

**Response (when dynamics are not generated yet):**
```json
{
  "success": true,
  "data": {
    "url": null,
    "status": "ready",
    "agent_id": "A91XMB7113",
    "gestures": {}
  }
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `url` | string \| null | URL to the dynamics model file (.imx file), or null if not generated |
| `status` | string | Current status of dynamics generation (see Status Values below) |
| `agent_id` | string | The agent ID |
| `gestures` | object | Dictionary of available gestures, where keys are gesture action names and values are video URLs |
| `gestures[gesture_name]` | string \| null | URL to the gesture video file for the specified gesture name |

**Status Values:**
- `"generating"` - Dynamics are currently being generated
- `"ready"` - Dynamics generation is complete and ready to use

**Example Request:**
```python
agent_id = "A91XMB7113"
url = f"https://public.api.bithuman.ai/v1/dynamics/{agent_id}"
headers = {"api-secret": "YOUR_API_SECRET"}

response = requests.get(url, headers=headers)
print(response.json())
```

### Update Dynamics

**`PUT /v1/dynamics/{agent_id}`**

Update dynamics configuration for an agent. This allows enabling/disabling dynamics, updating video results, and managing the dynamics model configuration.

**Headers:**
```http
Content-Type: application/json
api-secret: YOUR_API_SECRET
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | string | Agent ID to update dynamics for |

**Request Body:**
```json
{
  "dynamics": {
    "enabled": true,
    "batch_results": {
      "wave": {
        "video_url": "https://storage.supabase.co/wave.mp4",
        "status": "success"
      }
    },
    "result": {
      "model_path": "https://storage.supabase.co/dynamics-model.bin",
      "model_hash": "abc123def456"
    },
    "talking": {
      "model_path": "https://storage.supabase.co/talking-model.bin",
      "model_hash": "def456ghi789"
    }
  },
  "toggle_enabled": true
}
```

**Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|----------|
| `dynamics` | object | Dynamics configuration object | See above |
| `toggle_enabled` | boolean | Signal for enable/disable toggle | `true` |

**Response:**
```json
{
  "success": true,
  "message": "Dynamics updated successfully",
  "data": {
    "agent_id": "A91XMB7113",
    "updated_at": "2025-01-15T10:30:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Dynamics updated successfully and movements regeneration started",
  "agent_id": "A91XMB7113",
  "regeneration_status": "started"
}
```

**Regeneration Status:**
- `"started"` - Movements regeneration has been triggered successfully
- `"failed"` - Movements regeneration failed to start (check `regeneration_error` field)

**Example Request:**
```python
agent_id = "A91XMB7113"
url = f"https://public.api.bithuman.ai/v1/dynamics/{agent_id}"
headers = {
    "Content-Type": "application/json",
    "api-secret": "YOUR_API_SECRET"
}
payload = {
    "dynamics": {
        "enabled": True,
        "batch_results": {
            "wave": {
                "video_url": "https://storage.supabase.co/wave.mp4",
                "status": "success"
            }
        }
    },
    "toggle_enabled": True
}

response = requests.put(url, headers=headers, json=payload)
print(response.json())
```

## 🎯 Motion Types

| Motion | Description | Use Case |
|--------|-------------|----------|
| `wave` | Hand waving gesture | Greeting, goodbye |
| `nod` | Head nodding | Agreement, acknowledgment |
| `smile` | Facial expression change | Happiness, friendliness |
| `idle` | Subtle idle animation | Background movement |
| `talking` | Speech-synchronized motion | Conversation |

## ⚙️ Configuration Options

**Duration Settings:**
- `1-3 seconds`: Quick gestures
- `3-5 seconds`: Standard motions
- `5-10 seconds`: Extended animations

**Model Options:**
- `seedance`: High-quality motion generation
- `kling`: Alternative motion model
- `auto`: Automatic model selection

## 🔧 Error Handling

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API secret)
- `404` - Agent not found
- `402` - Insufficient credits
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "error": "Dynamics generation failed",
  "code": "INTERNAL_ERROR",
  "details": "Agent not found or insufficient credits"
}
```

## 💡 Use Cases

- **Interactive Agents**: Add natural movements to conversational agents
- **Presentation Avatars**: Create engaging presentation assistants
- **Customer Service**: Enhance virtual customer service representatives
- **Educational Content**: Make learning experiences more engaging

## 🔗 Related APIs

- [Agent Generation API](./agent-generation-api.md) - Create agents with dynamic capabilities
- [File Upload API](./file-upload-api.md) - Upload media assets for agent customization

## 📊 Integration Example

```python
import requests
import time

# Step 1: Create an agent
agent_url = "https://public.api.bithuman.ai/v1/agent/generate"
headers = {"Content-Type": "application/json", "api-secret": "YOUR_API_SECRET"}

agent_payload = {
    "prompt": "You are a friendly customer service representative."
}

agent_response = requests.post(agent_url, headers=headers, json=agent_payload)
agent_data = agent_response.json()
agent_id = agent_data["agent_id"]

print(f"Agent created: {agent_id}")

# Step 2: Wait for agent to be ready
status_url = f"https://public.api.bithuman.ai/v1/agent/status/{agent_id}"
while True:
    status_response = requests.get(status_url, headers={"api-secret": "YOUR_API_SECRET"})
    status_data = status_response.json()
    
    if status_data["data"]["status"] == "ready":
        break
    time.sleep(5)

# Step 3: Generate dynamics
dynamics_url = "https://public.api.bithuman.ai/v1/dynamics/generate"
dynamics_payload = {
    "agent_id": agent_id,
    "motion_prompts": ["wave", "nod", "smile"],
    "duration": 3
}

dynamics_response = requests.post(dynamics_url, headers=headers, json=dynamics_payload)
print("Dynamics generated:", dynamics_response.json())
```
