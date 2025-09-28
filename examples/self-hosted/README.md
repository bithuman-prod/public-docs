# Self-Hosted bitHuman Agent with LiveKit

This example demonstrates how to run a self-hosted bitHuman agent using LiveKit with advanced features including custom gesture triggers, real-time conversation handling, and audio interruption management.

## Features

- **Self-hosted model deployment**: Run bitHuman avatars using your own model files
- **Custom gesture triggers**: Automatically trigger gestures based on conversation keywords
- **Real-time conversation handling**: Advanced speech recognition and response management
- **Audio interruption support**: Natural conversation flow with interruption handling
- **Periodic health monitoring**: Automatic status checks and maintenance tasks

## Prerequisites

1. **bitHuman API Secret**: Get your API secret from the [bitHuman platform](https://platform.bithuman.ai)
2. **bitHuman Model File**: Download your avatar model file (`.imx` format)
3. **OpenAI API Key**: Required for the conversational AI (GPT-4o-mini-realtime-preview)
4. **LiveKit Server**: Either use LiveKit Cloud or run your own LiveKit server

## Installation

1. **Clone the repository and navigate to this example**:
   ```bash
   cd examples/self-hosted
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment configuration**:
   ```bash
   cp .env.example .env
   ```

4. **Configure your environment variables** in `.env`:
   ```env
   # bitHuman Configuration
   BITHUMAN_API_SECRET=your_api_secret_here
   BITHUMAN_MODEL_PATH=/path/to/your/avatar_model.imx
   
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # LiveKit Configuration
   LIVEKIT_URL=wss://your-livekit-server.com
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   
   # Optional: Development mode
   DEV_MODE=false
   ```

## Usage

### Basic Usage

Run the agent with default settings:

```bash
python agent.py dev
```

### Advanced Usage

For production deployment with custom room configuration:

```bash
python agent.py start \
  --room my-avatar-room \
  --identity bithuman-agent \
  --log-level INFO
```

### Docker Deployment

Build and run using Docker:

```bash
# Build the Docker image
docker build -t bithuman-selfhosted-agent .

# Run the container
docker run -d \
  --name bithuman-agent \
  --env-file .env \
  -v /path/to/your/models:/app/models \
  bithuman-selfhosted-agent
```

## Configuration Options

### Gesture Triggers

The agent supports automatic gesture triggering based on conversation keywords:

- **mini_wave_hello**: Triggered by greetings ("hello", "hi", "hey", "goodbye")
- **thumbs_up_pulse**: Triggered by positive words ("good", "great", "awesome")
- **heart_hands**: Triggered by affectionate words ("love", "heart", "care")
- **celebration_jump**: Triggered by celebration words ("celebrate", "party", "congratulations")

### Audio Interruption Settings

Configure interruption sensitivity in the agent code:

```python
await self.bithuman_avatar.configure_interruptions(
    enabled=True,
    sensitivity=0.6,  # 0.0 (low) to 1.0 (high)
    min_interruption_duration=0.3,  # seconds
    grace_period=0.2,  # seconds
)
```

### Voice Activity Detection

Customize VAD settings for better conversation flow:

```python
vad=silero.VAD.load(
    min_speaking_duration=0.1,  # Minimum speech duration
    min_silence_duration=0.5,   # Minimum silence to end speech
    padding_duration=0.1,       # Padding around speech segments
)
```

## Model Requirements

### Supported Model Formats

- **IMX Files**: bitHuman's optimized model format
- **Model Size**: Typically 50MB - 500MB depending on quality
- **Hardware**: Minimum 4GB RAM, GPU recommended for real-time performance

### Model Placement

Place your model files in a accessible directory and update the `BITHUMAN_MODEL_PATH` environment variable:

```bash
# Example directory structure
/app/models/
├── avatar_v1.imx
├── avatar_v2.imx
└── backup/
    └── avatar_backup.imx
```

## Troubleshooting

### Common Issues

1. **Model Loading Errors**:
   ```
   Error: Failed to load model from path
   ```
   - Verify the model file path is correct
   - Ensure the model file is not corrupted
   - Check file permissions

2. **API Authentication Errors**:
   ```
   Error: Invalid API secret
   ```
   - Verify your `BITHUMAN_API_SECRET` is correct
   - Check if your API key has the necessary permissions

3. **LiveKit Connection Issues**:
   ```
   Error: Failed to connect to LiveKit room
   ```
   - Verify your LiveKit server URL and credentials
   - Check network connectivity
   - Ensure the room exists or can be created

4. **Memory Issues**:
   ```
   Warning: High memory usage detected
   ```
   - Increase the `job_memory_warn_mb` setting
   - Consider using a smaller model
   - Monitor system resources

### Performance Optimization

1. **GPU Acceleration**: Enable GPU support for faster model inference
2. **Model Caching**: Pre-load models to reduce startup time
3. **Resource Monitoring**: Use the built-in health checks to monitor performance
4. **Network Optimization**: Use a CDN for model distribution in production

## Development

### Running in Development Mode

Enable development mode for enhanced debugging:

```bash
export DEV_MODE=true
python agent.py dev --reload
```

### Custom Gesture Development

Add custom gestures by extending the `gesture_configs` in the agent code:

```python
gesture_configs.append({
    "gesture": "custom_wave",
    "keywords": ["custom", "special", "unique"],
    "description": "Custom gesture for special occasions"
})
```

### Event Handling

Extend conversation event handling:

```python
@self.session.on("custom_event")
async def on_custom_event(data):
    logger.info(f"Custom event received: {data}")
    # Handle custom logic here
```

## Support

For issues and questions:

1. Check the [bitHuman Documentation](https://docs.bithuman.ai)
2. Visit our [GitHub Issues](https://github.com/bithuman/issues)
3. Join our [Discord Community](https://discord.gg/bithuman)

## License

This example is provided under the MIT License. See the main repository for full license details.
