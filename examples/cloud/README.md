# Cloud Examples - bitHuman Avatar Agents

This directory contains cloud-based LiveKit agent examples using bitHuman avatars. These examples demonstrate different approaches to creating interactive avatar agents with varying complexity levels.

## 📁 Directory Structure

```
cloud/
├── essence/                 # Basic avatar setup with avatar_id
│   ├── agent.py            # Simple cloud avatar agent
│   └── README.md           # Setup and usage instructions
├── expression/             # Advanced avatar customization
│   ├── agent_with_avatar_id.py     # Enhanced avatar_id setup
│   ├── agent_with_avatar_image.py  # Custom image avatar setup
│   ├── avatar.jpg          # Sample avatar image
│   └── README.md           # Advanced setup instructions
└── README.md               # This overview file
```

## 🎯 Choose Your Starting Point

### 🌟 **New to bitHuman?** → Start with [Essence](./essence/)
- Simple setup with minimal configuration
- Uses pre-configured avatar models
- Perfect for learning the basics
- 5-minute setup time

### 🎨 **Want Customization?** → Try [Expression](./expression/)
- Advanced avatar customization options
- Support for custom images and URLs
- Enhanced expression controls
- Multiple configuration examples

## 🚀 Quick Comparison

| Feature | Essence | Expression |
|---------|---------|------------|
| **Complexity** | Beginner | Intermediate |
| **Setup Time** | 5 minutes | 10-15 minutes |
| **Avatar Source** | Pre-configured ID | ID + Custom Images |
| **Customization** | Basic | Advanced |
| **Dependencies** | Minimal | + PIL/Pillow |
| **Use Cases** | Learning, prototyping | Production, branding |

## 🛠️ Common Prerequisites

All cloud examples require:

### 1. Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Navigate to your chosen example directory
cd essence/          # OR cd expression/

# Install from requirements.txt
pip install -r requirements.txt
```

### 3. API Credentials

Create a `.env` file with:
```bash
# bitHuman API
BITHUMAN_API_SECRET=sk_bh_your_secret_here

# OpenAI API
OPENAI_API_KEY=sk-proj_your_key_here

# LiveKit API
LIVEKIT_API_KEY=APIyour_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

## 🔗 Getting Credentials

### bitHuman API Secret
1. Visit [imaginex.bithuman.ai](https://imaginex.bithuman.ai/#developer)
2. Create account and navigate to Developer section
3. Generate API secret (starts with `sk_bh_`)

### OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com/api-keys)
2. Create API key (starts with `sk-proj_`)
3. Ensure Realtime API access

### LiveKit Credentials
1. Sign up at [livekit.io](https://livekit.io)
2. Create new project
3. Copy API keys and project URL

## 🎮 Running Examples

Each example supports three modes:

```bash
# Development mode with web interface (recommended)
python agent.py dev

# Production deployment mode
python agent.py start

# Console mode for testing (no web UI)
python agent.py console
```

## 🌐 Testing Your Agents

### 🎮 LiveKit Playground (Recommended)

1. **Start your agent**:
   ```bash
   python agent.py dev
   ```
   Wait for: "Agent is ready and waiting for participants"

2. **Open Playground**: Visit [agents-playground.livekit.io](https://agents-playground.livekit.io)

3. **Connect with your credentials**:
   - Click "Continue with LiveKit Cloud"
   - Use the **same credentials** from your `.env` file:
     - API Key: `LIVEKIT_API_KEY`
     - API Secret: `LIVEKIT_API_SECRET` 
     - URL: `LIVEKIT_URL`

4. **Join and test**:
   - Click "Connect" to join the room
   - **⏱️ Connection times**:
     - **Essence examples**: ~30 seconds
     - **Expression examples**: ~1 minute (image processing)
   - Grant microphone permissions
   - Start conversations with your avatar!

### 🖥️ Local Web Interface (Alternative)

1. Run agent in `dev` mode and note the local URL
2. Open the provided URL in your browser  
3. Grant microphone/camera permissions
4. Test your avatar locally

## 🎨 Customization Guide

### Avatar Personalities
Customize your avatar's behavior by modifying the agent instructions:

```python
agent=Agent(
    instructions=(
        "You are a [ROLE]. "
        "Your personality is [TRAITS]. "
        "Respond in a [STYLE] manner."
    )
)
```

**Example personalities:**
- **Customer Service**: Professional, helpful, patient
- **Educational**: Encouraging, clear, informative  
- **Entertainment**: Energetic, funny, engaging
- **Healthcare**: Caring, empathetic, reassuring

### Voice Options
Change the OpenAI voice model:

```python
voice="coral"  # Options: alloy, echo, fable, onyx, nova, shimmer, coral
```

### Expression Controls
For enhanced expression (Expression examples):

```python
avatar_motion_scale=1.5,      # Motion intensity (0.0-2.0)
avatar_expression_scale=1.2,  # Expression intensity (0.0-2.0)
```

## 🔧 Troubleshooting

### Common Issues

1. **Module import errors**
   ```bash
   pip install --upgrade livekit-agents livekit-plugins-bithuman
   ```

2. **API authentication failures**
   - Verify API keys are correct and active
   - Check `.env` file formatting
   - Ensure no extra spaces or quotes

3. **Avatar not appearing**
   - Check avatar_id exists (for Essence)
   - Verify image file/URL accessibility (for Expression)
   - Monitor console for error messages

4. **Audio/video issues**
   - Grant browser microphone/camera permissions
   - Check LiveKit room connection
   - Verify VAD (Voice Activity Detection) is working

### Debug Mode
Enable detailed logging in any example:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance Tips

1. **Memory optimization**: Monitor memory usage with `job_memory_warn_mb`
2. **Network optimization**: Use local files instead of URLs when possible
3. **Process management**: Adjust `num_idle_processes` based on your server capacity
4. **Timeout settings**: Increase `initialize_process_timeout` for complex setups

## 🚀 Production Deployment

### Resource Requirements
- **Minimum**: 2 CPU cores, 4GB RAM
- **Recommended**: 4 CPU cores, 8GB RAM
- **Network**: Stable internet connection for API calls

### Scaling Considerations
- Use load balancers for multiple agent instances
- Monitor API rate limits (OpenAI, bitHuman)
- Implement error handling and fallback mechanisms
- Set up logging and monitoring

## 📚 Next Steps

1. **Start with [Essence](./essence/)** if you're new to bitHuman
2. **Move to [Expression](./expression/)** for advanced features
3. **Explore [LiveKit documentation](https://docs.livekit.io/agents)** for platform details
4. **Join [Discord community](https://discord.gg/ES953n7bPA)** for support and discussions

## 🆘 Support & Resources

- 💬 **Community**: [Discord](https://discord.gg/ES953n7bPA)
- 📖 **Documentation**: [bitHuman Docs](https://docs.bithuman.ai)
- 🔧 **LiveKit Docs**: [agents.livekit.io](https://docs.livekit.io/agents)
- 🌟 **Avatar Models**: [Community Gallery](https://imaginex.bithuman.ai/#community)
- 🛠️ **API Reference**: [Developer Portal](https://imaginex.bithuman.ai/#developer)
