# bitHuman SDK Examples

Interactive avatar examples using the bitHuman SDK for real-time conversational AI.

## Installation

```bash
# 1. Create conda environment
conda create -n bithuman python=3.11
conda activate bithuman

# 2. Install dependencies
pip install -r requirements.txt
pip install bithuman --upgrade [Note: this is important!]
```

## Setup Environment

Create `.env` file in the root directory:
```bash
BITHUMAN_API_SECRET=your_api_secret
BITHUMAN_AVATAR_MODEL=/path/to/model.imx
```

Get your API secret at [console.bithuman.io](https://console.bithuman.io) and download avatar models from the [Community page](https://console.bithuman.io/#community).

## Examples

### Local Display (OpenCV Window)

**1. Audio Clip Playback**
```bash
python examples/avatar-with-audio-clip.py --model /path/to/model.imx --audio-file /path/to/audio.wav
```

**2. Live Microphone Input**
```bash
python examples/avatar-with-microphone.py --model /path/to/model.imx
```

### LiveKit Agents (Web UI)

For examples 3-4, use [LiveKit's Agents Playground](https://github.com/livekit/agents-playground/) for the best experience.

**Setup LiveKit Playground:**

1. **Register free LiveKit account** at [livekit.io](https://livekit.io)

2. **Add LiveKit credentials to `.env`:**
   ```bash
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   LIVEKIT_URL=wss://your-project.livekit.cloud
   ```

3. **Download & setup playground:**
   ```bash
   git clone https://github.com/livekit/agents-playground.git
   cd agents-playground
   npm install
   ```

4. **Configure playground** (create a separate `.env` in the agents-playground repo):
   ```bash
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud
   ```

5. **Start playground:**
   ```bash
   npm run dev
   ```

6. **Run agents** (in separate terminal):
   ```bash
   # OpenAI conversational agent
   python examples/agent-livekit-openai.py console dev
   
   # Apple local agent
   python examples/agent-livekit-apple-local.py console dev
   ```

7. **Connect:** Open `http://localhost:3000` and join a room to chat with your avatar!

## Requirements

- Python 3.11
- macOS (Apple Silicon) or Linux
- OpenAI API key (for OpenAI agent example)
- LiveKit account (for web UI examples)

## Support
- [bitHuman Documentation](https://docs.bithuman.io)
- [bitHuman Discord](https://discord.gg/yM7wRRqu)
- [LiveKit Agents Docs](https://docs.livekit.io/agents)
- [Community](https://console.bithuman.io/#community)
