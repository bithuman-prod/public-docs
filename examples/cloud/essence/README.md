# Cloud Essence - Basic Avatar Agent

This example demonstrates the simplest cloud-based bitHuman avatar setup using a pre-configured avatar ID. Perfect for getting started with LiveKit agents and bitHuman avatars.

## ✨ What This Example Does

- Creates a conversational AI agent using OpenAI's Realtime API
- Uses a pre-configured bitHuman avatar (via `avatar_id`)
- Provides real-time video avatar with synchronized speech
- Handles voice activity detection for natural conversations

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all required packages from requirements.txt
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in this directory:

```bash
# bitHuman API Configuration
BITHUMAN_API_SECRET=sk_bh_your_api_secret_here

# OpenAI Configuration
OPENAI_API_KEY=sk-proj_your_openai_api_key_here

# LiveKit Configuration
LIVEKIT_API_KEY=APIyour_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

### 3. Get Your Credentials

#### bitHuman API Secret
1. Visit [imaginex.bithuman.ai](https://imaginex.bithuman.ai/#developer)
2. Sign up/login and navigate to Developer section
3. Create an API secret (starts with `sk_bh_`)

#### OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com/api-keys)
2. Create a new API key (starts with `sk-proj_`)
3. Ensure you have access to the Realtime API

#### LiveKit Credentials
1. Sign up at [livekit.io](https://livekit.io)
2. Create a new project
3. Get your API keys and project URL from the dashboard

### 4. Customize Avatar

Replace the `avatar_id` in `agent.py`:

```python
bithuman_avatar = bithuman.AvatarSession(
    api_secret=os.getenv("BITHUMAN_API_SECRET"),
    avatar_id="YOUR_AVATAR_ID_HERE",  # Get this from bitHuman community page
)
```

To find avatar IDs:
1. Visit [imaginex.bithuman.ai/#community](https://imaginex.bithuman.ai/#community)
2. Browse available avatars
3. Copy the avatar ID from your chosen model

### 5. Test Your Setup (Recommended)

Before running the agent, use the diagnostic tool to check your configuration:

```bash
# Run diagnostics to verify your setup
python diagnose.py
```

This will check:
- ✅ All required packages are installed
- ✅ API keys are properly configured
- ✅ BitHuman API is accessible
- ✅ Avatar ID is valid

### 6. Run the Agent

```bash
# Development mode with web interface
python agent.py dev

# Production mode
python agent.py start

# Console mode for testing
python agent.py console
```

### 7. Test Your Avatar

#### Option A: LiveKit Playground (Recommended) 🎮

1. **Start your agent in development mode**:
   ```bash
   python agent.py dev
   ```
   Wait for the message: "Agent is ready and waiting for participants"

2. **Open LiveKit Playground**: Visit [agents-playground.livekit.io](https://agents-playground.livekit.io)

3. **Connect to your project**:
   - Click "Continue with LiveKit Cloud"
   - Use the **same LiveKit credentials** from your `.env` file:
     - **API Key**: Your `LIVEKIT_API_KEY` 
     - **API Secret**: Your `LIVEKIT_API_SECRET`
     - **URL**: Your `LIVEKIT_URL`

4. **Join and test**:
   - Click "Connect" to join the room
   - **Connection time**: ~30 seconds for avatar initialization
   - Grant microphone permissions when prompted
   - Start talking to your avatar!

#### Option B: Local Web Interface

1. Run agent in dev mode and look for the local web interface URL
2. Open the provided URL in your browser
3. Grant microphone/camera permissions and test

## 🎛️ Customization Options

### Modify AI Instructions

Update the agent instructions in `agent.py`:

```python
agent=Agent(
    instructions=(
        "You are a customer service representative. "
        "Be helpful, professional, and respond clearly."
    )
)
```

### Change Voice Settings

Modify the OpenAI voice configuration:

```python
llm=openai.realtime.RealtimeModel(
    voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer, coral
    model="gpt-4o-mini-realtime-preview",
)
```

## 🔧 Troubleshooting

### Quick Diagnosis

**First, run the diagnostic tool:**
```bash
python diagnose.py
```

This will automatically check for common issues and provide specific guidance.

### Common Issues

1. **"Avatar session failed" errors**: 
   - Try a different avatar ID from [community gallery](https://imaginex.bithuman.ai/#community)
   - Check if your account has access to the avatar
   - Verify BitHuman service status

2. **"Module not found" errors**: 
   ```bash
   pip install -r requirements.txt
   ```

3. **API authentication failures**: 
   - Verify your API keys are correct and active
   - Check `.env` file formatting (no extra spaces/quotes)
   - Ensure BITHUMAN_API_SECRET starts with `sk_bh_`

4. **Avatar not loading**: 
   - Run `python diagnose.py` to test avatar ID validity
   - Try the default avatar ID or browse alternatives
   - Check network connectivity to BitHuman API

5. **No audio/video**: 
   - Grant browser microphone/camera permissions
   - Check LiveKit room connection
   - Verify VAD (Voice Activity Detection) is working

### Debug Mode

Enable more detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Advanced Troubleshooting

If the diagnostic tool shows all checks pass but you still have issues:

1. **Check BitHuman service status**: Visit [status page](https://status.bithuman.ai) (if available)
2. **Try different avatar**: Use a different avatar ID from the community gallery
3. **Network issues**: Test from a different network/location
4. **Resource constraints**: Ensure sufficient CPU/memory for avatar processing

## 📚 Next Steps

- Try the [Expression examples](../expression/) for custom avatar images
- Learn about [advanced agent features](https://docs.livekit.io/agents)
- Explore [bitHuman documentation](https://docs.bithuman.ai)

## 🆘 Support

- 💬 [Discord Community](https://discord.gg/ES953n7bPA)
- 📖 [bitHuman Docs](https://docs.bithuman.ai)
- 🔧 [LiveKit Docs](https://docs.livekit.io/agents)
