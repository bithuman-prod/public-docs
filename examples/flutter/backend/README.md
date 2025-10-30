# Flutter Integration Backend

This backend service provides a LiveKit agent with bitHuman avatar integration for the Flutter frontend application.

## 🏗️ Architecture

```
Flutter App ←→ LiveKit Room ←→ Python Agent ←→ bitHuman Avatar
     ↓              ↓              ↓              ↓
  Video/Audio   Real-time      AI Processing   Avatar Rendering
  Capture      Streaming       (OpenAI)        (Cloud)
```

## ✨ Features

- **LiveKit Agent**: Handles real-time communication
- **bitHuman Avatar**: AI-powered conversational avatar
- **OpenAI Integration**: Natural language processing
- **Voice Activity Detection**: Smart conversation flow
- **Room Management**: Multi-participant support

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:

```bash
# bitHuman API Configuration
BITHUMAN_API_SECRET=sk_bh_your_api_secret_here
BITHUMAN_AVATAR_ID=A33NZN6384  # Optional: Use specific avatar

# OpenAI Configuration
OPENAI_API_KEY=sk-proj_your_openai_api_key_here

# LiveKit Configuration
LIVEKIT_API_KEY=APIyour_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

### 3. Get Credentials

#### bitHuman API Secret
1. Visit [imaginex.bithuman.ai](https://imaginex.bithuman.ai/#developer)
2. Sign up/login → Developer section
3. Create API secret (starts with `sk_bh_`)

#### OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com/api-keys)
2. Create API key (starts with `sk-proj_`)
3. Ensure Realtime API access

#### LiveKit Credentials
1. Sign up at [livekit.io](https://livekit.io)
2. Create project → Get API keys from dashboard

### 4. Run the Agent

```bash
# Development mode with web interface
python agent.py dev

# Production mode
python agent.py start

# Console mode for testing
python agent.py console
```

## 🔧 Configuration

### Avatar Selection

Edit `agent.py` to change avatar:

```python
# Use specific avatar ID
avatar_id = os.getenv("BITHUMAN_AVATAR_ID", "A33NZN6384")

# Or use custom avatar image
bithuman_avatar = bithuman.AvatarSession(
    api_secret=api_secret,
    avatar_image="path/to/your/image.jpg"  # Instead of avatar_id
)
```

### AI Personality

Customize the AI instructions:

```python
agent=Agent(
    instructions=(
        "You are a helpful customer service representative. "
        "Be friendly, professional, and concise in your responses. "
        "Help users with their questions and provide accurate information."
    )
)
```

### Voice Settings

Modify OpenAI voice configuration:

```python
llm=openai.realtime.RealtimeModel(
    voice="coral",  # Options: alloy, echo, fable, onyx, nova, shimmer, coral
    model="gpt-4o-mini-realtime-preview",
)
```

## 🧪 Testing

### 1. Diagnostic Check

```bash
python diagnose.py
```

This will verify:
- ✅ All packages installed
- ✅ API keys configured
- ✅ BitHuman API accessible
- ✅ Avatar ID valid

### 2. LiveKit Playground Test

1. Start agent in dev mode: `python agent.py dev`
2. Visit [agents-playground.livekit.io](https://agents-playground.livekit.io)
3. Use your LiveKit credentials from `.env`
4. Connect and test the avatar

### 3. Flutter App Test

1. Ensure agent is running
2. Update Flutter app with correct LiveKit URL
3. Run Flutter app and connect to room

## 🔍 Troubleshooting

### Common Issues

1. **"Avatar session failed"**
   - Try different avatar ID from [community gallery](https://imaginex.bithuman.ai/#community)
   - Check account access to avatar
   - Verify BitHuman service status

2. **"Module not found"**
   ```bash
   pip install -r requirements.txt
   ```

3. **API authentication failures**
   - Verify API keys are correct and active
   - Check `.env` file formatting (no extra spaces)
   - Ensure BITHUMAN_API_SECRET starts with `sk_bh_`

4. **No audio/video in Flutter**
   - Check LiveKit room connection
   - Verify microphone/camera permissions
   - Ensure agent is running and connected

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

For better performance:

```python
# In agent.py
WorkerOptions(
    job_memory_warn_mb=2000,  # Increase memory limit
    num_idle_processes=2,     # More idle processes
    initialize_process_timeout=180,  # Longer timeout
)
```

## 📊 Monitoring

### Health Checks

The agent provides several health check endpoints:

- `/health` - Basic health status
- `/metrics` - Performance metrics
- `/status` - Detailed status information

### Logs

Monitor logs for:
- Connection status
- Avatar initialization
- Error messages
- Performance metrics

## 🚀 Deployment

### Production Setup

1. **Environment Variables**: Set all required env vars
2. **Resource Limits**: Ensure sufficient CPU/memory
3. **Monitoring**: Set up logging and metrics
4. **Security**: Use secure API keys and tokens

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "agent.py", "start"]
```

### Cloud Deployment

Compatible with:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Heroku
- Railway

## 📚 API Reference

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BITHUMAN_API_SECRET` | ✅ | bitHuman API secret key |
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `LIVEKIT_API_KEY` | ✅ | LiveKit API key |
| `LIVEKIT_API_SECRET` | ✅ | LiveKit API secret |
| `LIVEKIT_URL` | ✅ | LiveKit server URL |
| `BITHUMAN_AVATAR_ID` | ❌ | Specific avatar ID to use |

### Agent Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `voice` | "coral" | OpenAI voice selection |
| `model` | "gpt-4o-mini-realtime-preview" | OpenAI model |
| `avatar_id` | "A33NZN6384" | bitHuman avatar ID |
| `instructions` | Default helpful assistant | AI personality |

## 🔗 Integration Points

### With Flutter Frontend

- **Room Connection**: Flutter connects to same LiveKit room
- **Token Generation**: Backend can generate access tokens
- **Media Streaming**: Real-time video/audio exchange
- **Event Handling**: Room events and participant management

### With bitHuman Cloud

- **Avatar Rendering**: Cloud-based avatar generation
- **API Authentication**: Secure API key validation
- **Model Management**: Avatar model loading and caching
- **Performance Monitoring**: Usage tracking and optimization

## 🆘 Support

- 💬 [Discord Community](https://discord.gg/ES953n7bPA)
- 📖 [bitHuman Docs](https://docs.bithuman.ai)
- 🔧 [LiveKit Docs](https://docs.livekit.io/agents)
- 🐛 [Report Issues](https://github.com/bithuman/sdk/issues)

---

**Next**: Check out the [Frontend README](../frontend/README.md) to set up the Flutter application!
