# bitHuman SDK Examples

This repository contains comprehensive examples demonstrating how to build interactive agents using the bitHuman SDK. These examples showcase various use cases, from simple audio playback to real-time conversational AI agents with visual avatars.

## Quick Start

1. **Get your API credentials** at [console.bithuman.io](https://console.bithuman.io)
2. **Download an avatar model** from the [Community page](https://console.bithuman.io/#community)
3. **Install the SDK**: `pip install bithuman`
4. **Set environment variables**:
   ```bash
   export BITHUMAN_API_SECRET='your_api_secret'
   export BITHUMAN_AVATAR_MODEL='/path/to/model/avatar.imx'
   ```

For detailed setup instructions, see [📖 Getting Started Guide](docs/getting-started/overview.md).

## Repository Structure

```
public-sdk-examples/
├── 📁 basic_usage/          # Simple keyboard-controlled example
├── 📁 avatar/               # Real-time microphone input with local display
├── 📁 livekit_agent/        # AI conversational agents with OpenAI integration
├── 📁 livekit_webrtc/       # WebRTC streaming to LiveKit rooms
├── 📁 fastrtc/              # Simplified WebRTC implementation
└── 📁 docs/                 # 📖 Complete documentation and guides
    ├── getting-started/     # Installation and first steps
    ├── examples/            # Detailed example tutorials
    ├── generate-agent/      # Agent creation guidelines
    └── integrations/        # Platform integration guides
```

## Examples Overview

| Example | Description | Use Case |
|---------|-------------|----------|
| **basic_usage** | Audio file playback with keyboard controls | Learning SDK basics |
| **avatar** | Real-time microphone echo with local avatar | Testing audio processing |
| **livekit_agent** | AI conversational agent with OpenAI | Voice-to-voice AI assistants |
| **livekit_webrtc** | WebRTC streaming with WebSocket control | Multi-user avatar streaming |
| **fastrtc** | Alternative WebRTC implementation | Simplified streaming setup |

## Documentation

📖 **[Complete Documentation](docs/README.md)** - Start here for comprehensive guides

**Quick Links:**
- [Installation Guide](docs/getting-started/installation.md)
- [Your First Model](docs/getting-started/first-model.md) 
- [Example Tutorials](docs/examples/overview.md)
- [Integration Guides](docs/integrations/overview.md)
- [Agent Creation Guidelines](docs/generate-agent/overview.md)

## Requirements

- **Python**: 3.10 - 3.13
- **OS**: Linux (x86_64/arm64), macOS (Apple Silicon, macOS ≥ 15)
- **Hardware**: GPU recommended for optimal performance

## Support

- [bitHuman Documentation](https://docs.bithuman.io)
- [bitHuman Console](https://console.bithuman.io)
- [Community Page](https://console.bithuman.io/#community)

---

⚡ **Ready to build?** Choose an example from the folders above or dive into the [📖 documentation](docs/README.md) to get started!
