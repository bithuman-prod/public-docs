# Run Your First Model

Let's create your first animated avatar with bitHuman SDK! This tutorial will walk you through a simple example that loads an avatar and makes it speak.

## Prerequisites

Before starting, make sure you have:

- ✅ [Installed bitHuman SDK](installation.md)
- ✅ [Validated your API secret](validate-api.md)
- ✅ Downloaded an avatar model (.imx file)

## Basic Example: Text-to-Speech Avatar

Create your first speaking avatar with this simple example:

```python
# first_avatar.py
import asyncio
import os
import cv2
import numpy as np
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk

async def first_avatar_example():
    # Load configuration
    api_secret = os.getenv('BITHUMAN_API_SECRET')
    model_path = os.getenv('BITHUMAN_AVATAR_MODEL')
    
    print("🚀 Starting your first bitHuman avatar...")
    
    # Initialize the runtime
    runtime = await AsyncBithuman.create(
        api_secret=api_secret,
        model_path=model_path
    )
    
    print("✅ Avatar loaded successfully!")
    
    # Create sample audio data (you can replace this with real audio)
    sample_rate = 16000
    duration = 3.0  # 3 seconds
    
    # Generate a simple tone (replace with real audio or TTS)
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440  # A4 note
    audio_data = (np.sin(2 * np.pi * frequency * t) * 0.3 * 32767).astype(np.int16)
    
    # Create audio chunk
    audio_chunk = AudioChunk.from_numpy(audio_data, sample_rate)
    
    print("🎤 Processing audio...")
    
    # Process audio and display avatar frames
    cv2.namedWindow('bitHuman Avatar', cv2.WINDOW_AUTOSIZE)
    
    frame_count = 0
    async for video_frame in runtime.process_audio_chunk(audio_chunk):
        # Convert BGR to RGB for display
        frame_rgb = cv2.cvtColor(video_frame.image, cv2.COLOR_BGR2RGB)
        
        # Display the frame
        cv2.imshow('bitHuman Avatar', frame_rgb)
        
        frame_count += 1
        print(f"Frame {frame_count}: {video_frame.image.shape}")
        
        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    print(f"✅ Generated {frame_count} frames")
    
    # Cleanup
    cv2.destroyAllWindows()
    await runtime.close()
    
    print("🎉 Your first avatar is complete!")

if __name__ == "__main__":
    asyncio.run(first_avatar_example())
```

## Run the Example

Install the required dependency:

```bash
pip install opencv-python
```

Run your first avatar:

```bash
python first_avatar.py
```

You should see:
1. A window opens showing your avatar
2. The avatar animates based on the audio
3. Frame information printed to console

Press 'q' to close the window.

## Enhanced Example: Audio File Input

Here's a more practical example using an audio file:

```python
# audio_file_avatar.py
import asyncio
import os
import cv2
import wave
import numpy as np
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk

async def audio_file_avatar(audio_file_path):
    # Load configuration
    api_secret = os.getenv('BITHUMAN_API_SECRET')
    model_path = os.getenv('BITHUMAN_AVATAR_MODEL')
    
    print(f"🚀 Loading avatar with audio file: {audio_file_path}")
    
    # Initialize runtime
    runtime = await AsyncBithuman.create(
        api_secret=api_secret,
        model_path=model_path
    )
    
    # Load audio file
    try:
        with wave.open(audio_file_path, 'rb') as wav_file:
            # Check audio format
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            
            print(f"📁 Audio file info:")
            print(f"   Sample rate: {sample_rate} Hz")
            print(f"   Channels: {channels}")
            print(f"   Sample width: {sample_width} bytes")
            
            # Read audio data
            audio_data = wav_file.readframes(wav_file.getnframes())
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Convert to mono if stereo
            if channels == 2:
                audio_array = audio_array.reshape(-1, 2).mean(axis=1).astype(np.int16)
                print("   Converted stereo to mono")
            
            # Resample if necessary (bitHuman requires 16kHz)
            if sample_rate != 16000:
                # Simple resampling (for production, use proper resampling)
                target_length = int(len(audio_array) * 16000 / sample_rate)
                audio_array = np.interp(
                    np.linspace(0, len(audio_array), target_length),
                    np.arange(len(audio_array)),
                    audio_array
                ).astype(np.int16)
                print(f"   Resampled from {sample_rate}Hz to 16kHz")
    
    except Exception as e:
        print(f"❌ Error loading audio file: {e}")
        await runtime.close()
        return
    
    # Create audio chunk
    audio_chunk = AudioChunk.from_numpy(audio_array, 16000)
    
    print("🎭 Generating avatar animation...")
    
    # Setup video display
    cv2.namedWindow('bitHuman Avatar', cv2.WINDOW_AUTOSIZE)
    
    frame_count = 0
    start_time = asyncio.get_event_loop().time()
    
    async for video_frame in runtime.process_audio_chunk(audio_chunk):
        # Display frame
        cv2.imshow('bitHuman Avatar', video_frame.image)
        
        frame_count += 1
        
        # Maintain ~25 FPS display rate
        target_time = start_time + (frame_count / 25.0)
        current_time = asyncio.get_event_loop().time()
        
        if current_time < target_time:
            await asyncio.sleep(target_time - current_time)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    elapsed_time = asyncio.get_event_loop().time() - start_time
    fps = frame_count / elapsed_time if elapsed_time > 0 else 0
    
    print(f"✅ Generated {frame_count} frames in {elapsed_time:.2f}s ({fps:.1f} FPS)")
    
    # Cleanup
    cv2.destroyAllWindows()
    await runtime.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python audio_file_avatar.py <audio_file.wav>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        sys.exit(1)
    
    asyncio.run(audio_file_avatar(audio_file))
```

## Usage with Audio File

```bash
# Download a sample audio file or use your own
python audio_file_avatar.py sample_speech.wav
```

## Save Avatar Video

Want to save the avatar animation as a video file? Here's how:

```python
# save_avatar_video.py
import asyncio
import os
import cv2
import numpy as np
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk

async def save_avatar_video(audio_file_path, output_video_path):
    # Initialize runtime
    runtime = await AsyncBithuman.create(
        api_secret=os.getenv('BITHUMAN_API_SECRET'),
        model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
    )
    
    # Load and process audio (similar to previous example)
    # ... audio loading code ...
    
    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 25
    frame_size = (512, 512)  # Adjust based on your avatar model
    
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, frame_size)
    
    print(f"💾 Saving avatar video to: {output_video_path}")
    
    frame_count = 0
    async for video_frame in runtime.process_audio_chunk(audio_chunk):
        # Resize frame if necessary
        if video_frame.image.shape[:2] != frame_size[::-1]:
            frame = cv2.resize(video_frame.image, frame_size)
        else:
            frame = video_frame.image
        
        # Write frame to video
        video_writer.write(frame)
        frame_count += 1
        
        if frame_count % 25 == 0:
            print(f"   Processed {frame_count} frames...")
    
    # Cleanup
    video_writer.release()
    await runtime.close()
    
    print(f"✅ Video saved: {frame_count} frames")

# Usage
if __name__ == "__main__":
    asyncio.run(save_avatar_video("input.wav", "avatar_output.mp4"))
```

## Understanding the Output

### VideoFrame Object

Each frame contains:

```python
video_frame.image        # numpy array (H, W, 3) - BGR format
video_frame.audio_chunk  # synchronized audio data
video_frame.frame_index  # frame number
video_frame.message_id   # unique identifier
```

### Audio Synchronization

- Video frames are generated at 25 FPS
- Each frame includes corresponding audio chunk
- Audio and video are automatically synchronized

## Common Issues and Solutions

### Issue: No Window Appears

```python
# Make sure you have display support
import cv2
print("OpenCV version:", cv2.__version__)

# For headless servers, save to file instead
```

### Issue: Audio Format Errors

```python
# Always ensure 16kHz, mono, int16 format
audio_array = audio_array.astype(np.int16)  # Convert data type
sample_rate = 16000  # Required sample rate
```

### Issue: Model Loading Slow

The first model load may take 30-60 seconds. Subsequent loads are faster.

## Performance Tips

### Optimize for Real-time

```python
# Use smaller audio chunks for lower latency
chunk_size = 0.1  # 100ms chunks
# Split large audio into smaller chunks
```

### Batch Processing

```python
# For multiple files, reuse the runtime
runtime = await AsyncBithuman.create(...)

for audio_file in audio_files:
    async for frame in runtime.process_audio_chunk(chunk):
        # process frame
    
await runtime.close()  # Close once at the end
```

## Next Steps

Congratulations! You've created your first bitHuman avatar. Now you can:

1. **[Explore Examples](../examples/voice-driven-audio.md)** - See more complex implementations
2. **[Learn about Integrations](../integrations/livekit.md)** - Add avatars to existing applications
3. **[Create Custom Agents](../generate-agent/prompt-guidelines.md)** - Build your own avatar models
4. **[Deploy to Production](../build/self-hosted.md)** - Scale your avatar applications

## Getting Help

- 📖 **[Documentation](/)** - Complete API reference
- 🌟 **[Community Hub](https://console.bithuman.io/#community)** - Models and examples
- 💬 **Discord** - Get help from other developers
- 🐛 **GitHub Issues** - Report bugs or request features

You're now ready to build amazing applications with bitHuman SDK! 🎉 