# Real Time Avatar Driven by Microphone

Create a real-time avatar that responds to live microphone input. This example demonstrates low-latency audio processing and real-time avatar animation.

## Overview

This example shows how to:
- Capture live microphone audio
- Process audio in real-time with minimal latency
- Generate synchronized avatar animations
- Handle audio buffering and streaming
- Implement voice activity detection
- Optimize for real-time performance

## Prerequisites

- ✅ [bitHuman SDK installed](../getting-started/installation.md)
- ✅ [API credentials configured](../getting-started/validate-api.md)
- ✅ Avatar model (.imx file) downloaded
- ✅ Microphone access permissions
- ✅ Audio drivers properly configured

## Basic Implementation

### Simple Real-time Avatar

```python
# realtime_microphone_avatar.py
import asyncio
import os
import cv2
import numpy as np
import pyaudio
import threading
from collections import deque
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk

class RealTimeMicrophoneAvatar:
    def __init__(self):
        self.runtime = None
        self.audio_stream = None
        self.audio_buffer = deque(maxlen=100)  # Buffer for audio chunks
        self.is_recording = False
        self.processing_lock = threading.Lock()
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_duration = 0.5  # 500ms chunks for low latency
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # PyAudio instance
        self.audio = pyaudio.PyAudio()
        
    async def initialize(self):
        """Initialize bitHuman runtime and audio system"""
        print("🎤 Initializing real-time microphone avatar...")
        
        # Initialize bitHuman
        self.runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        
        # Setup audio stream
        self.setup_audio_stream()
        
        print("✅ Real-time avatar initialized")
    
    def setup_audio_stream(self):
        """Setup PyAudio stream for microphone input"""
        try:
            self.audio_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.audio_callback,
                start=False
            )
            print("🎵 Audio stream configured")
            
        except Exception as e:
            print(f"❌ Audio setup failed: {e}")
            self.list_audio_devices()
            raise
    
    def list_audio_devices(self):
        """List available audio input devices"""
        print("\n🎤 Available audio input devices:")
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"   {i}: {device_info['name']} - {device_info['maxInputChannels']} channels")
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream"""
        if status:
            print(f"⚠️ Audio status: {status}")
        
        # Convert audio data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Add to buffer for processing
        self.audio_buffer.append(audio_data)
        
        return (None, pyaudio.paContinue)
    
    def get_audio_level(self, audio_data: np.ndarray) -> float:
        """Calculate audio level for visualization"""
        return np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
    
    def has_voice_activity(self, audio_data: np.ndarray, threshold: float = 0.01) -> bool:
        """Simple voice activity detection"""
        level = self.get_audio_level(audio_data)
        return level > threshold
    
    async def start_real_time_processing(self):
        """Start real-time audio processing and avatar animation"""
        print("🚀 Starting real-time processing...")
        print("Press 'q' to quit, 's' to toggle speech detection")
        
        # Setup video display
        cv2.namedWindow('Real-time Avatar', cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow('Real-time Avatar', 512, 512)
        
        # Start audio recording
        self.is_recording = True
        self.audio_stream.start_stream()
        
        # Processing variables
        frame_count = 0
        last_processing_time = asyncio.get_event_loop().time()
        use_voice_detection = True
        
        try:
            while self.is_recording:
                # Check for audio data
                if self.audio_buffer:
                    with self.processing_lock:
                        audio_data = self.audio_buffer.popleft()
                    
                    # Voice activity detection
                    if use_voice_detection and not self.has_voice_activity(audio_data):
                        # Show idle frame if no voice activity
                        await self.show_idle_frame()
                    else:
                        # Process audio through bitHuman
                        await self.process_audio_chunk(audio_data)
                    
                    frame_count += 1
                    
                    # Performance monitoring
                    if frame_count % 10 == 0:
                        current_time = asyncio.get_event_loop().time()
                        processing_fps = 10 / (current_time - last_processing_time)
                        last_processing_time = current_time
                        
                        print(f"📊 Processing FPS: {processing_fps:.1f}")
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    use_voice_detection = not use_voice_detection
                    status = "enabled" if use_voice_detection else "disabled"
                    print(f"🎙️ Voice detection {status}")
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("⏹️ Stopped by user")
        
        finally:
            await self.cleanup()
    
    async def process_audio_chunk(self, audio_data: np.ndarray):
        """Process audio chunk and display avatar frame"""
        try:
            # Create AudioChunk
            audio_chunk = AudioChunk.from_numpy(audio_data, self.sample_rate)
            
            # Process through bitHuman (get first frame for real-time)
            async for video_frame in self.runtime.process_audio_chunk(audio_chunk):
                # Display frame
                cv2.imshow('Real-time Avatar', video_frame.image)
                break  # Only show first frame for real-time response
                
        except Exception as e:
            print(f"❌ Processing error: {e}")
    
    async def show_idle_frame(self):
        """Show idle avatar frame when no voice activity"""
        # Create silent audio chunk
        silent_audio = np.zeros(self.chunk_size, dtype=np.int16)
        audio_chunk = AudioChunk.from_numpy(silent_audio, self.sample_rate)
        
        # Process silent audio to get idle frame
        async for video_frame in self.runtime.process_audio_chunk(audio_chunk):
            cv2.imshow('Real-time Avatar', video_frame.image)
            break
    
    async def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        
        self.is_recording = False
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        if self.runtime:
            await self.runtime.close()
        
        cv2.destroyAllWindows()
        print("✅ Cleanup complete")

# Main execution
async def main():
    avatar = RealTimeMicrophoneAvatar()
    
    try:
        await avatar.initialize()
        await avatar.start_real_time_processing()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await avatar.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### Enhanced Real-time Avatar with Features

```python
# enhanced_realtime_avatar.py
import asyncio
import os
import cv2
import numpy as np
import pyaudio
import webrtcvad
import collections
import threading
from dataclasses import dataclass
from typing import Optional, Deque
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk

@dataclass
class AudioSettings:
    sample_rate: int = 16000
    chunk_duration_ms: int = 30  # 30ms chunks for WebRTC VAD
    channels: int = 1
    format: int = pyaudio.paInt16
    
    @property
    def chunk_size(self) -> int:
        return int(self.sample_rate * self.chunk_duration_ms / 1000)

class EnhancedVoiceActivityDetector:
    def __init__(self, aggressiveness: int = 2):
        """
        Initialize VAD with WebRTC
        aggressiveness: 0-3, higher = more aggressive filtering
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = 16000
        self.frame_duration_ms = 30
        
    def is_speech(self, audio_data: bytes) -> bool:
        """Detect if audio contains speech"""
        try:
            return self.vad.is_speech(audio_data, self.sample_rate)
        except Exception:
            return False

class AudioBuffer:
    def __init__(self, max_size: int = 50):
        self.buffer: Deque[np.ndarray] = collections.deque(maxlen=max_size)
        self.lock = threading.Lock()
        
    def add(self, audio_data: np.ndarray):
        with self.lock:
            self.buffer.append(audio_data)
    
    def get_all(self) -> Optional[np.ndarray]:
        with self.lock:
            if not self.buffer:
                return None
            
            # Concatenate all buffered audio
            combined = np.concatenate(list(self.buffer))
            self.buffer.clear()
            return combined
    
    def is_empty(self) -> bool:
        with self.lock:
            return len(self.buffer) == 0

class EnhancedRealTimeAvatar:
    def __init__(self, audio_settings: Optional[AudioSettings] = None):
        self.audio_settings = audio_settings or AudioSettings()
        self.runtime = None
        self.audio_stream = None
        self.audio_buffer = AudioBuffer()
        self.vad = EnhancedVoiceActivityDetector()
        self.is_running = False
        
        # Performance metrics
        self.frame_count = 0
        self.processing_times = collections.deque(maxlen=100)
        
        # Audio system
        self.audio = pyaudio.PyAudio()
        
        # State management
        self.is_speaking = False
        self.silence_frames = 0
        self.speech_frames = 0
        self.min_speech_frames = 10  # Minimum frames to consider as speech
        self.max_silence_frames = 20  # Maximum silence before stopping
        
    async def initialize(self):
        """Initialize the enhanced real-time avatar"""
        print("🚀 Initializing Enhanced Real-time Avatar...")
        
        # Initialize bitHuman runtime
        self.runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        
        # Setup audio input
        self.setup_audio_input()
        
        print("✅ Enhanced avatar initialized")
        self.print_controls()
    
    def print_controls(self):
        """Print control instructions"""
        print("\n🎮 Controls:")
        print("   Q - Quit")
        print("   S - Toggle speech detection")
        print("   M - Mute/unmute microphone") 
        print("   R - Reset avatar to idle")
        print("   I - Show performance info")
        print("")
    
    def setup_audio_input(self):
        """Setup audio input stream"""
        try:
            # List and select audio device
            self.list_audio_devices()
            
            self.audio_stream = self.audio.open(
                format=self.audio_settings.format,
                channels=self.audio_settings.channels,
                rate=self.audio_settings.sample_rate,
                input=True,
                frames_per_buffer=self.audio_settings.chunk_size,
                stream_callback=self.audio_callback,
                start=False
            )
            
            print(f"🎤 Audio configured: {self.audio_settings.sample_rate}Hz, {self.audio_settings.chunk_duration_ms}ms chunks")
            
        except Exception as e:
            print(f"❌ Audio setup failed: {e}")
            raise
    
    def list_audio_devices(self):
        """List available audio devices"""
        print("🎤 Available input devices:")
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"   {i}: {device_info['name']}")
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback"""
        if status:
            print(f"⚠️ Audio status: {status}")
        
        # Convert to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Voice activity detection
        is_speech = self.vad.is_speech(in_data)
        
        if is_speech:
            self.speech_frames += 1
            self.silence_frames = 0
            
            # Add to buffer if we have enough speech frames
            if self.speech_frames >= self.min_speech_frames:
                self.audio_buffer.add(audio_data)
                self.is_speaking = True
        else:
            self.silence_frames += 1
            self.speech_frames = max(0, self.speech_frames - 1)
            
            # Stop speaking if too much silence
            if self.silence_frames >= self.max_silence_frames:
                self.is_speaking = False
        
        return (None, pyaudio.paContinue)
    
    async def start_processing(self):
        """Start the main processing loop"""
        print("🎬 Starting enhanced real-time processing...")
        
        # Setup display
        cv2.namedWindow('Enhanced Real-time Avatar', cv2.WINDOW_AUTOSIZE)
        self.setup_display_layout()
        
        # Start audio stream
        self.is_running = True
        self.audio_stream.start_stream()
        
        # Processing loop
        last_frame_time = asyncio.get_event_loop().time()
        
        try:
            while self.is_running:
                current_time = asyncio.get_event_loop().time()
                
                # Process audio if available
                if not self.audio_buffer.is_empty():
                    audio_data = self.audio_buffer.get_all()
                    if audio_data is not None:
                        processing_start = asyncio.get_event_loop().time()
                        await self.process_audio_data(audio_data)
                        processing_time = asyncio.get_event_loop().time() - processing_start
                        self.processing_times.append(processing_time)
                        
                elif not self.is_speaking:
                    # Show idle avatar when not speaking
                    await self.show_idle_avatar()
                
                # Handle user input
                key = cv2.waitKey(1) & 0xFF
                if not await self.handle_keyboard_input(key):
                    break
                
                # Update display info
                if current_time - last_frame_time > 1.0:  # Update every second
                    self.update_display_info()
                    last_frame_time = current_time
                
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("⏹️ Interrupted by user")
        finally:
            await self.cleanup()
    
    def setup_display_layout(self):
        """Setup the display layout with information panels"""
        self.info_panel_height = 100
        self.avatar_size = 512
        
    async def process_audio_data(self, audio_data: np.ndarray):
        """Process audio data through bitHuman"""
        try:
            # Create audio chunk
            audio_chunk = AudioChunk.from_numpy(audio_data, self.audio_settings.sample_rate)
            
            # Process through bitHuman
            async for video_frame in self.runtime.process_audio_chunk(audio_chunk):
                # Create enhanced display
                enhanced_frame = self.create_enhanced_display(video_frame.image)
                cv2.imshow('Enhanced Real-time Avatar', enhanced_frame)
                
                self.frame_count += 1
                break  # Show first frame for real-time response
                
        except Exception as e:
            print(f"❌ Processing error: {e}")
    
    async def show_idle_avatar(self):
        """Show idle avatar animation"""
        # Create very short silent audio for idle animation
        silent_duration = 0.1  # 100ms
        silent_samples = int(self.audio_settings.sample_rate * silent_duration)
        silent_audio = np.zeros(silent_samples, dtype=np.int16)
        
        audio_chunk = AudioChunk.from_numpy(silent_audio, self.audio_settings.sample_rate)
        
        async for video_frame in self.runtime.process_audio_chunk(audio_chunk):
            enhanced_frame = self.create_enhanced_display(video_frame.image, is_idle=True)
            cv2.imshow('Enhanced Real-time Avatar', enhanced_frame)
            break
    
    def create_enhanced_display(self, avatar_frame: np.ndarray, is_idle: bool = False) -> np.ndarray:
        """Create enhanced display with information overlay"""
        # Resize avatar frame if needed
        if avatar_frame.shape[:2] != (self.avatar_size, self.avatar_size):
            avatar_frame = cv2.resize(avatar_frame, (self.avatar_size, self.avatar_size))
        
        # Create info panel
        info_panel = np.zeros((self.info_panel_height, self.avatar_size, 3), dtype=np.uint8)
        
        # Add status information
        status_text = "IDLE" if is_idle else "SPEAKING"
        status_color = (0, 255, 255) if is_idle else (0, 255, 0)
        cv2.putText(info_panel, f"Status: {status_text}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Add performance metrics
        if self.processing_times:
            avg_processing_time = np.mean(list(self.processing_times)) * 1000  # ms
            cv2.putText(info_panel, f"Avg Processing: {avg_processing_time:.1f}ms", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add frame count
        cv2.putText(info_panel, f"Frames: {self.frame_count}", 
                   (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Voice activity indicator
        vad_color = (0, 255, 0) if self.is_speaking else (0, 0, 255)
        cv2.circle(info_panel, (450, 25), 10, vad_color, -1)
        cv2.putText(info_panel, "MIC", (470, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Combine avatar and info panel
        combined_frame = np.vstack([info_panel, avatar_frame])
        
        return combined_frame
    
    async def handle_keyboard_input(self, key: int) -> bool:
        """Handle keyboard input"""
        if key == ord('q'):
            print("👋 Quitting...")
            return False
        
        elif key == ord('s'):
            # Toggle speech detection sensitivity
            current_aggressiveness = self.vad.vad.mode
            new_aggressiveness = (current_aggressiveness + 1) % 4
            self.vad = EnhancedVoiceActivityDetector(new_aggressiveness)
            print(f"🎙️ VAD aggressiveness: {new_aggressiveness}")
        
        elif key == ord('m'):
            # Toggle mute
            if self.audio_stream.is_active():
                self.audio_stream.stop_stream()
                print("🔇 Microphone muted")
            else:
                self.audio_stream.start_stream()
                print("🎤 Microphone active")
        
        elif key == ord('r'):
            # Reset to idle
            self.is_speaking = False
            self.speech_frames = 0
            self.silence_frames = 0
            print("🔄 Reset to idle")
        
        elif key == ord('i'):
            # Show performance info
            self.show_performance_info()
        
        return True
    
    def update_display_info(self):
        """Update performance information"""
        if self.processing_times:
            avg_time = np.mean(list(self.processing_times)) * 1000
            max_time = np.max(list(self.processing_times)) * 1000
            print(f"📊 Processing: avg={avg_time:.1f}ms, max={max_time:.1f}ms, frames={self.frame_count}")
    
    def show_performance_info(self):
        """Show detailed performance information"""
        print("\n📈 Performance Information:")
        print(f"   Total frames processed: {self.frame_count}")
        
        if self.processing_times:
            times_ms = [t * 1000 for t in self.processing_times]
            print(f"   Average processing time: {np.mean(times_ms):.2f}ms")
            print(f"   Max processing time: {np.max(times_ms):.2f}ms")
            print(f"   Min processing time: {np.min(times_ms):.2f}ms")
        
        print(f"   Current VAD aggressiveness: {self.vad.vad.mode}")
        print(f"   Speech frames: {self.speech_frames}")
        print(f"   Silence frames: {self.silence_frames}")
        print("")
    
    async def cleanup(self):
        """Clean up all resources"""
        print("🧹 Cleaning up enhanced avatar...")
        
        self.is_running = False
        
        if self.audio_stream and self.audio_stream.is_active():
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        if self.runtime:
            await self.runtime.close()
        
        cv2.destroyAllWindows()
        print("✅ Enhanced cleanup complete")

# Main execution
async def main():
    # Configure audio settings for optimal performance
    audio_settings = AudioSettings(
        sample_rate=16000,
        chunk_duration_ms=30,  # Small chunks for low latency
        channels=1
    )
    
    avatar = EnhancedRealTimeAvatar(audio_settings)
    
    try:
        await avatar.initialize()
        await avatar.start_processing()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await avatar.cleanup()

if __name__ == "__main__":
    # Install required dependencies
    try:
        import webrtcvad
    except ImportError:
        print("❌ webrtcvad not installed. Run: pip install webrtcvad")
        exit(1)
    
    asyncio.run(main())
```

## Advanced Features

### Audio Quality Enhancement

```python
# audio_enhancement.py
import numpy as np
import scipy.signal
from typing import Tuple

class AudioEnhancer:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.setup_filters()
    
    def setup_filters(self):
        """Setup audio processing filters"""
        # High-pass filter to remove low-frequency noise
        self.hp_filter = scipy.signal.butter(4, 80, btype='high', fs=self.sample_rate)
        
        # Low-pass filter to remove high-frequency noise
        self.lp_filter = scipy.signal.butter(4, 8000, btype='low', fs=self.sample_rate)
        
        # Notch filter for 50/60Hz power line noise
        self.notch_filter = scipy.signal.iirnotch(50, 30, fs=self.sample_rate)
    
    def enhance_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply audio enhancements"""
        enhanced = audio_data.astype(np.float32)
        
        # Apply filters
        enhanced = scipy.signal.filtfilt(*self.hp_filter, enhanced)
        enhanced = scipy.signal.filtfilt(*self.lp_filter, enhanced)
        enhanced = scipy.signal.filtfilt(*self.notch_filter, enhanced)
        
        # Normalize
        enhanced = self.normalize_audio(enhanced)
        
        # Convert back to int16
        return (enhanced * 32767).astype(np.int16)
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio levels"""
        # Remove DC offset
        audio_data = audio_data - np.mean(audio_data)
        
        # RMS normalization
        rms = np.sqrt(np.mean(audio_data ** 2))
        if rms > 0:
            target_rms = 0.1  # Target RMS level
            audio_data = audio_data * (target_rms / rms)
        
        # Prevent clipping
        max_val = np.max(np.abs(audio_data))
        if max_val > 0.95:
            audio_data = audio_data * 0.95 / max_val
        
        return audio_data
    
    def apply_noise_gate(self, audio_data: np.ndarray, threshold: float = 0.02) -> np.ndarray:
        """Apply noise gate to reduce background noise"""
        audio_float = audio_data.astype(np.float32) / 32767.0
        
        # Calculate envelope
        envelope = np.abs(audio_float)
        
        # Apply smoothing
        alpha = 0.01
        smoothed_envelope = np.zeros_like(envelope)
        smoothed_envelope[0] = envelope[0]
        
        for i in range(1, len(envelope)):
            smoothed_envelope[i] = alpha * envelope[i] + (1 - alpha) * smoothed_envelope[i-1]
        
        # Apply gate
        gate_mask = smoothed_envelope > threshold
        gated_audio = audio_float * gate_mask
        
        return (gated_audio * 32767).astype(np.int16)
```

### Latency Optimization

```python
# latency_optimizer.py
import time
import asyncio
from collections import deque
from typing import Dict, List

class LatencyOptimizer:
    def __init__(self):
        self.latency_measurements = deque(maxlen=100)
        self.processing_times = deque(maxlen=100)
        self.target_latency_ms = 100  # Target 100ms end-to-end latency
        
    def measure_latency(self, audio_received_time: float, frame_displayed_time: float):
        """Measure end-to-end latency"""
        latency_ms = (frame_displayed_time - audio_received_time) * 1000
        self.latency_measurements.append(latency_ms)
        
        return latency_ms
    
    def get_latency_stats(self) -> Dict[str, float]:
        """Get latency statistics"""
        if not self.latency_measurements:
            return {}
        
        latencies = list(self.latency_measurements)
        return {
            'avg_latency_ms': np.mean(latencies),
            'min_latency_ms': np.min(latencies),
            'max_latency_ms': np.max(latencies),
            'p95_latency_ms': np.percentile(latencies, 95),
            'target_latency_ms': self.target_latency_ms
        }
    
    def optimize_chunk_size(self, current_latency: float) -> int:
        """Dynamically optimize audio chunk size based on latency"""
        if current_latency > self.target_latency_ms:
            # Reduce chunk size to decrease latency
            return max(480, int(16000 * 0.02))  # Min 20ms chunks
        else:
            # Can afford slightly larger chunks for better quality
            return min(1600, int(16000 * 0.05))  # Max 50ms chunks
    
    def should_skip_frame(self, processing_queue_size: int) -> bool:
        """Determine if we should skip frames to catch up"""
        # Skip frames if processing queue is backing up
        return processing_queue_size > 3

class OptimizedRealTimeAvatar:
    def __init__(self):
        self.latency_optimizer = LatencyOptimizer()
        self.audio_enhancer = AudioEnhancer()
        self.adaptive_chunk_size = 800  # Start with 50ms chunks
        
    async def process_optimized_audio(self, audio_data: np.ndarray, receive_time: float):
        """Process audio with latency optimization"""
        processing_start = time.time()
        
        # Enhance audio quality
        enhanced_audio = self.audio_enhancer.enhance_audio(audio_data)
        
        # Create audio chunk
        audio_chunk = AudioChunk.from_numpy(enhanced_audio, 16000)
        
        # Process through bitHuman
        async for video_frame in self.runtime.process_audio_chunk(audio_chunk):
            display_time = time.time()
            
            # Measure latency
            latency = self.latency_optimizer.measure_latency(receive_time, display_time)
            
            # Display frame
            cv2.imshow('Optimized Avatar', video_frame.image)
            
            # Optimize for next iteration
            self.adaptive_chunk_size = self.latency_optimizer.optimize_chunk_size(latency)
            
            break  # Show first frame only for real-time
        
        processing_time = time.time() - processing_start
        self.latency_optimizer.processing_times.append(processing_time)
```

### Multi-threaded Processing

```python
# threaded_processor.py
import threading
import queue
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class AudioFrame:
    data: np.ndarray
    timestamp: float
    frame_id: int

class ThreadedAudioProcessor:
    def __init__(self, max_queue_size: int = 10):
        self.audio_queue = queue.Queue(maxsize=max_queue_size)
        self.result_queue = queue.Queue(maxsize=max_queue_size)
        self.processing_thread = None
        self.is_running = False
        self.frame_counter = 0
        
    def start_processing_thread(self, runtime):
        """Start audio processing in separate thread"""
        self.is_running = True
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            args=(runtime,)
        )
        self.processing_thread.start()
        print("🧵 Processing thread started")
    
    def _processing_loop(self, runtime):
        """Main processing loop running in separate thread"""
        while self.is_running:
            try:
                # Get audio frame from queue (blocking with timeout)
                audio_frame = self.audio_queue.get(timeout=1.0)
                
                # Process through bitHuman
                asyncio.set_event_loop(asyncio.new_event_loop())
                loop = asyncio.get_event_loop()
                
                video_frames = []
                async def process_frame():
                    audio_chunk = AudioChunk.from_numpy(audio_frame.data, 16000)
                    async for video_frame in runtime.process_audio_chunk(audio_chunk):
                        video_frames.append(video_frame)
                        break  # Get first frame only
                
                loop.run_until_complete(process_frame())
                
                # Put result in result queue
                if video_frames:
                    self.result_queue.put({
                        'video_frame': video_frames[0],
                        'frame_id': audio_frame.frame_id,
                        'processing_time': time.time() - audio_frame.timestamp
                    })
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Processing thread error: {e}")
    
    def add_audio_frame(self, audio_data: np.ndarray) -> bool:
        """Add audio frame to processing queue"""
        try:
            audio_frame = AudioFrame(
                data=audio_data,
                timestamp=time.time(),
                frame_id=self.frame_counter
            )
            self.frame_counter += 1
            
            self.audio_queue.put_nowait(audio_frame)
            return True
            
        except queue.Full:
            # Queue is full, skip this frame to maintain real-time performance
            print("⚠️ Audio queue full, skipping frame")
            return False
    
    def get_processed_frame(self) -> Optional[dict]:
        """Get processed video frame"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop_processing(self):
        """Stop the processing thread"""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
            print("🧵 Processing thread stopped")
```

## Performance Monitoring

### Real-time Performance Dashboard

```python
# performance_dashboard.py
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque

class RealTimePerformanceDashboard:
    def __init__(self, max_points: int = 100):
        self.max_points = max_points
        
        # Data storage
        self.timestamps = deque(maxlen=max_points)
        self.latencies = deque(maxlen=max_points)
        self.processing_times = deque(maxlen=max_points)
        self.frame_rates = deque(maxlen=max_points)
        self.audio_levels = deque(maxlen=max_points)
        
        # Setup plots
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('Real-time Avatar Performance Dashboard')
        
        # Initialize plots
        self.setup_plots()
        
        # Animation
        self.animation = FuncAnimation(
            self.fig, self.update_plots, interval=100, blit=False
        )
    
    def setup_plots(self):
        """Setup the performance plots"""
        # Latency plot
        self.axes[0, 0].set_title('End-to-End Latency')
        self.axes[0, 0].set_ylabel('Latency (ms)')
        self.axes[0, 0].set_ylim(0, 500)
        self.axes[0, 0].axhline(y=100, color='r', linestyle='--', label='Target')
        self.axes[0, 0].legend()
        
        # Processing time plot
        self.axes[0, 1].set_title('Processing Time')
        self.axes[0, 1].set_ylabel('Time (ms)')
        self.axes[0, 1].set_ylim(0, 200)
        
        # Frame rate plot
        self.axes[1, 0].set_title('Frame Rate')
        self.axes[1, 0].set_ylabel('FPS')
        self.axes[1, 0].set_ylim(0, 30)
        self.axes[1, 0].axhline(y=25, color='g', linestyle='--', label='Target')
        self.axes[1, 0].legend()
        
        # Audio level plot
        self.axes[1, 1].set_title('Audio Input Level')
        self.axes[1, 1].set_ylabel('Level')
        self.axes[1, 1].set_ylim(0, 1)
    
    def add_data_point(self, latency_ms: float, processing_time_ms: float, 
                      frame_rate: float, audio_level: float):
        """Add new data point"""
        current_time = time.time()
        
        self.timestamps.append(current_time)
        self.latencies.append(latency_ms)
        self.processing_times.append(processing_time_ms)
        self.frame_rates.append(frame_rate)
        self.audio_levels.append(audio_level)
    
    def update_plots(self, frame):
        """Update all plots with current data"""
        if len(self.timestamps) < 2:
            return
        
        # Convert to numpy arrays for plotting
        times = np.array(self.timestamps)
        times = times - times[0]  # Relative time
        
        # Clear and update each plot
        for ax in self.axes.flat:
            ax.clear()
        
        self.setup_plots()
        
        # Plot data
        self.axes[0, 0].plot(times, list(self.latencies), 'b-')
        self.axes[0, 1].plot(times, list(self.processing_times), 'r-')
        self.axes[1, 0].plot(times, list(self.frame_rates), 'g-')
        self.axes[1, 1].plot(times, list(self.audio_levels), 'm-')
        
        # Update x-axis labels
        for ax in self.axes.flat:
            ax.set_xlabel('Time (s)')
        
        plt.tight_layout()
    
    def show_dashboard(self):
        """Show the dashboard"""
        plt.show()
    
    def save_performance_report(self, filename: str):
        """Save performance data to file"""
        if not self.timestamps:
            print("No data to save")
            return
        
        data = {
            'timestamps': list(self.timestamps),
            'latencies_ms': list(self.latencies),
            'processing_times_ms': list(self.processing_times),
            'frame_rates_fps': list(self.frame_rates),
            'audio_levels': list(self.audio_levels)
        }
        
        import json
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📊 Performance report saved to {filename}")
```

## Integration Examples

### WebRTC Integration

```python
# webrtc_realtime.py
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaRelay
import asyncio

class BitHumanWebRTCTrack(MediaStreamTrack):
    """Custom WebRTC track for bitHuman avatar"""
    
    kind = "video"
    
    def __init__(self, avatar_processor):
        super().__init__()
        self.avatar_processor = avatar_processor
        
    async def recv(self):
        """Receive video frames from avatar processor"""
        # Get latest frame from avatar processor
        frame = await self.avatar_processor.get_next_frame()
        return frame

class WebRTCRealTimeAvatar:
    def __init__(self):
        self.avatar_processor = EnhancedRealTimeAvatar()
        self.peer_connections = set()
        
    async def create_peer_connection(self):
        """Create WebRTC peer connection"""
        pc = RTCPeerConnection()
        self.peer_connections.add(pc)
        
        # Add avatar video track
        avatar_track = BitHumanWebRTCTrack(self.avatar_processor)
        pc.addTrack(avatar_track)
        
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"Connection state: {pc.connectionState}")
            if pc.connectionState == "failed":
                await pc.close()
                self.peer_connections.discard(pc)
        
        return pc
```

### Mobile App Integration

```python
# mobile_integration.py
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import base64
import asyncio

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class MobileAvatarServer:
    def __init__(self):
        self.avatar_processor = None
        self.connected_clients = set()
    
    async def initialize(self):
        """Initialize avatar processor"""
        self.avatar_processor = EnhancedRealTimeAvatar()
        await self.avatar_processor.initialize()
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f"Client connected: {request.sid}")
        self.connected_clients.add(request.sid)
        emit('status', {'message': 'Connected to avatar server'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f"Client disconnected: {request.sid}")
        self.connected_clients.discard(request.sid)
    
    @socketio.on('audio_data')
    async def handle_audio_data(data):
        """Handle incoming audio data from mobile client"""
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(data['audio'])
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Process through avatar
            video_frames = await self.avatar_processor.process_audio_data(audio_array)
            
            if video_frames:
                # Encode video frame as base64
                frame_bytes = cv2.imencode('.jpg', video_frames[0])[1].tobytes()
                frame_b64 = base64.b64encode(frame_bytes).decode('utf-8')
                
                # Send back to client
                emit('video_frame', {'frame': frame_b64})
                
        except Exception as e:
            emit('error', {'message': str(e)})

# Run server
if __name__ == '__main__':
    mobile_server = MobileAvatarServer()
    asyncio.run(mobile_server.initialize())
    socketio.run(app, host='0.0.0.0', port=5000)
```

## Troubleshooting

### Common Audio Issues

```python
# audio_troubleshooting.py
import pyaudio
import numpy as np

def diagnose_audio_setup():
    """Diagnose common audio setup issues"""
    print("🔍 Diagnosing audio setup...")
    
    audio = pyaudio.PyAudio()
    
    # Check available devices
    print("\n📱 Available audio devices:")
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"   {i}: {device_info['name']}")
            print(f"      Max channels: {device_info['maxInputChannels']}")
            print(f"      Default sample rate: {device_info['defaultSampleRate']}")
    
    # Test audio input
    try:
        test_stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        
        print("\n🎤 Testing audio input...")
        audio_data = test_stream.read(1024 * 10)  # 10 chunks
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Analyze audio
        rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
        max_val = np.max(np.abs(audio_array))
        
        print(f"   RMS level: {rms:.4f}")
        print(f"   Peak level: {max_val}")
        
        if rms < 0.001:
            print("⚠️  Warning: Very low audio levels detected")
        elif rms > 0.5:
            print("⚠️  Warning: Audio levels may be too high")
        else:
            print("✅ Audio levels look good")
        
        test_stream.close()
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
    
    audio.terminate()

def fix_common_issues():
    """Provide solutions for common issues"""
    print("\n🔧 Common solutions:")
    print("1. Check microphone permissions")
    print("2. Try different audio device indices")
    print("3. Adjust microphone levels in system settings")
    print("4. Install/update audio drivers")
    print("5. Check for conflicting audio applications")

if __name__ == "__main__":
    diagnose_audio_setup()
    fix_common_issues()
```

## Usage Examples

### Command Line Usage

```bash
# Basic real-time avatar
python realtime_microphone_avatar.py

# Enhanced version with VAD
python enhanced_realtime_avatar.py

# With performance monitoring
python enhanced_realtime_avatar.py --enable-dashboard

# Custom audio settings
python enhanced_realtime_avatar.py --sample-rate 16000 --chunk-size 30
```

### Configuration File

```yaml
# config.yaml
audio:
  sample_rate: 16000
  chunk_duration_ms: 30
  channels: 1
  device_index: -1  # Default device

processing:
  enable_vad: true
  vad_aggressiveness: 2
  enable_audio_enhancement: true
  target_latency_ms: 100

display:
  window_size: 512
  show_performance_info: true
  enable_recording: false

performance:
  enable_dashboard: false
  max_processing_threads: 1
  enable_latency_optimization: true
```

## Next Steps

After mastering real-time microphone avatars:

1. **[LiveKit Agent Integration](livekit-agent.md)** - Add AI conversation capabilities
2. **[WebRTC Streaming](../integrations/fastrtc.md)** - Stream to multiple clients
3. **[Production Deployment](../build/self-hosted.md)** - Deploy for real users
4. **[GPU Acceleration](../build/gpu-cloud.md)** - Reduce latency further

## Resources

- **[Audio Processing Guide](../generate-agent/voice-guidelines.md)** - Optimize audio quality
- **[Performance Optimization](../build/gpu-cloud.md)** - Achieve better real-time performance
- **[WebRTC Integration](../integrations/fastrtc.md)** - Stream avatars over the internet
- **[Community Examples](https://console.bithuman.io/#community)** - More real-time avatar examples

Real-time microphone avatars open up endless possibilities for interactive applications. Start building engaging, responsive avatar experiences today! 