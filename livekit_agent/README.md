# bitHuman LiveKit Agent

This example demonstrates how to create an interactive AI agent with a bitHuman avatar that can be run locally or deployed to a LiveKit room.

## Overview

The example includes two main components:

1. **Local Agent (`agent_local.py`)**: Runs an interactive agent locally, processing audio input, generating responses, and rendering the avatar on your local machine.

2. **WebRTC Agent (`agent_webrtc.py`)**: Deploys the agent to a LiveKit room, making it accessible to multiple users via WebRTC.

## Prerequisites

- Python 3.10+
- bitHuman SDK installed
- OpenAI API key
- LiveKit server (for WebRTC example)
- LiveKit API key and secret (for WebRTC example)

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
# Bithuman Configuration
export BITHUMAN_AVATAR_MODEL="/path/to/model.imx"

# Authentication (only one required)
export BITHUMAN_RUNTIME_TOKEN=your-bithuman-token
# OR
export BITHUMAN_API_SECRET=your-api-secret

# OpenAI API
export OPENAI_API_KEY=your-openai-token

# LiveKit Configuration (for WebRTC example)
export LIVEKIT_URL=wss://your-livekit-server.com
export LIVEKIT_API_KEY=your-api-key
export LIVEKIT_API_SECRET=your-api-secret
```

## Running the Examples

### Local Agent

Run the agent locally, which will process audio input from your microphone and display the avatar on your screen:

```bash
python agent_local.py
```

### WebRTC Agent

Deploy the agent to a LiveKit room, making it accessible via WebRTC:

```bash
python agent_webrtc.py dev
```

## Customization

You can customize the agent's behavior by modifying:

- The LLM prompt and system instructions
- The avatar's appearance by using different models

## Troubleshooting

- If you encounter audio input issues, make sure your microphone is properly connected and set as the default input device.
- For LiveKit connection issues, verify your server URL, API key, and secret.
- If the avatar doesn't appear, check that your avatar model path is correct and the file exists.

## Resources

- [Bithuman Documentation](https://docs.bithuman.io)
- [LiveKit Agents](https://github.com/livekit/agents)

