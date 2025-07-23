# 🎵 Audio Clip Avatar

> **Play audio files with avatar animation**

Perfect first example - simple and works every time.

---

## 🚀 Quick Start

### 1. Install
```bash
pip install bithuman --upgrade opencv-python sounddevice
```

### 2. Set environment
```bash
export BITHUMAN_API_SECRET="your_secret"
export BITHUMAN_MODEL_PATH="/path/to/model.imx"
export BITHUMAN_AUDIO_PATH="/path/to/audio.wav"  # optional
```

### 3. Run
```bash
python examples/avatar-with-audio-clip.py
```

### 4. Controls
- **Press `1`** → Play audio with avatar
- **Press `2`** → Stop playback
- **Press `q`** → Quit

---

## 💡 What it does

1. Loads your audio file (WAV, MP3, M4A supported)
2. Creates synchronized avatar animation 
3. Shows real-time video in OpenCV window
4. Plays audio through speakers with sounddevice

**Key features:**
- Smooth audio playback with buffering
- Real-time video display at 25 FPS
- Keyboard controls for interaction
- Supports multiple audio formats

---

## 🔧 Command Line Options

You can also run with custom parameters:

```bash
# Use specific files
python examples/avatar-with-audio-clip.py \
  --model /path/to/model.imx \
  --audio-file /path/to/audio.wav \
  --api-secret your_secret

# Use JWT token instead of API secret
python examples/avatar-with-audio-clip.py \
  --token your_jwt_token \
  --model /path/to/model.imx
```

**Available options:**
- `--model`: Path to .imx model file
- `--audio-file`: Path to audio file  
- `--api-secret`: Your bitHuman API secret
- `--token`: JWT token (alternative to API secret)
- `--insecure`: Disable SSL verification (dev only)

---

## 🔧 Common Issues

**No audio playing?**
- Install sounddevice: `pip install sounddevice`
- Check audio file path in environment or command line
- Try WAV format for best compatibility

**Avatar not loading?**
- Verify `BITHUMAN_API_SECRET` is set correctly
- Check `BITHUMAN_MODEL_PATH` points to valid .imx file
- Ensure model file exists and is readable

**Video choppy or slow?**
- Close other applications using GPU/CPU
- Try smaller video window
- Check system resources with Activity Monitor

**Controls not working?**
- Click on the OpenCV window to focus it
- Use keyboard numbers (not numpad)
- Press keys while video window is active

---

## 🎯 Perfect for

✅ **Product demos and presentations**  
✅ **Testing new audio content**  
✅ **Learning bitHuman SDK basics**  
✅ **Creating voice-over videos**  
✅ **Batch processing audio files**

---

## 🔧 Technical Details

**Audio processing:**
- Sample rate: 16kHz (automatically converted)
- Channels: Mono (stereo converted automatically)
- Buffer size: Configurable for smooth playback
- Formats: WAV, MP3, M4A, FLAC

**Video output:**
- Resolution: 512x512 pixels
- Frame rate: 25 FPS
- Display: OpenCV window
- Format: RGB color

---

## ➡️ Next Steps

**Want real-time interaction?** → Try [Live Microphone Avatar](examples/avatar-with-microphone.md)

**Ready for web deployment?** → Try [OpenAI Agent](examples/livekit-openai-agent.md)

---

*Master this first example, then move to interactive demos!* 🚀 