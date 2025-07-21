# bitHuman FastRTC Example

This example demonstrates how to use the bitHuman SDK with FastRTC WebRTC implementation to create an interactive avatar that can be streamed over WebRTC.

## Overview

The FastRTC example provides a simpler WebRTC solution compared to LiveKit, with similar capabilities. It demonstrates how to:

1. Initialize the bitHuman Runtime and avatar
2. Set up WebRTC connections using FastRTC
3. Stream the avatar's video and audio to WebRTC peers
4. Process audio input to control the avatar's speech

## Prerequisites

- Python 3.10+
- bitHuman SDK installed

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Set your bitHuman API secret key and avatar model path as environment variables:

```bash
export BITHUMAN_API_SECRET='your_api_secret'
export BITHUMAN_AVATAR_MODEL='/path/to/model/avatar.imx'
```

## Running the Example

Run the example with:

```bash
python fastrtc_example.py
```

## How It Works

The example demonstrates:

1. Initializing the bitHuman Runtime with your API secret key
2. Setting up FastRTC WebRTC connections
3. Capturing audio input from participants
4. Processing audio input with bitHuman Runtime
5. Rendering the avatar's response and streaming it over WebRTC

## Troubleshooting

- For WebRTC connection issues, check network connectivity and firewall settings
- If the avatar doesn't appear, verify your avatar model path
- For API-related errors, check that your Bithuman API secret key is valid

## Resources

- [bitHuman Documentation](https://docs.bithuman.io)
- [FastRTC Documentation](https://fastrtc.org) 
