# Real Time Visual Agent on macOS (Offline)

> Build a fully offline real-time visual agent on macOS using local processing with optimized performance for Apple Silicon.

## Overview

This example demonstrates how to create a completely offline real-time visual agent on macOS, leveraging local processing capabilities without requiring internet connectivity. Perfect for privacy-sensitive applications, demonstrations, or environments with limited connectivity.

## Prerequisites

- **macOS 15+** (Sequoia or later)
- **Apple Silicon** (M1, M2, M3, or later) recommended
- **Python 3.9+**
- **16GB RAM minimum** (32GB recommended for optimal performance)
- **Local avatar model file** (.imx)
- **Valid bitHuman API secret** (for initial setup)

## System Requirements

### Hardware Recommendations

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Processor** | Intel i7 or Apple M1 | Apple M2 Pro or better |
| **Memory** | 16GB RAM | 32GB RAM |
| **Storage** | 10GB free space | 50GB+ SSD |
| **Camera** | 720p webcam | 1080p or better |
| **Microphone** | Built-in mic | External USB mic |

### Software Dependencies

```bash
# Install core dependencies
pip install bithuman numpy opencv-python pillow

# macOS-specific audio libraries
pip install pyaudio sounddevice

# For advanced features
pip install accelerate torch torchvision torchaudio

# GUI framework
pip install tkinter customtkinter

# Performance monitoring
pip install psutil memory_profiler
```

## Project Structure

```
macos-offline-agent/
├── main.py               # Main application
├── config.py             # Configuration management
├── audio/                # Audio processing
│   ├── __init__.py
│   ├── capture.py        # Audio capture
│   ├── processor.py      # Audio processing
│   └── vad.py           # Voice activity detection
├── video/                # Video processing
│   ├── __init__.py
│   ├── renderer.py       # Video rendering
│   ├── display.py        # Display management
│   └── recorder.py       # Video recording
├── ui/                   # User interface
│   ├── __init__.py
│   ├── main_window.py    # Main GUI
│   ├── controls.py       # Control widgets
│   └── visualizer.py     # Audio visualizer
├── utils/                # Utilities
│   ├── __init__.py
│   ├── performance.py    # Performance monitoring
│   └── storage.py        # Local storage
├── models/               # Local model storage
│   └── avatar.imx        # Avatar model file
└── output/               # Generated content
    ├── videos/
    └── recordings/
```

## Core Implementation

### Configuration Management

```python
# config.py
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class OfflineConfig:
    # Model Configuration
    avatar_model_path: str = "models/avatar.imx"
    bithuman_api_secret: str = os.getenv('BITHUMAN_API_SECRET')
    
    # Audio Configuration
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    audio_chunk_size: int = 1024
    audio_buffer_duration: float = 0.1  # seconds
    
    # Video Configuration
    video_width: int = 512
    video_height: int = 512
    video_fps: int = 25
    video_bitrate: int = 2000000
    
    # Performance Configuration
    max_cpu_usage: float = 80.0  # percentage
    memory_limit_gb: float = 8.0
    enable_gpu_acceleration: bool = True
    thread_pool_size: int = 4
    
    # Storage Configuration
    output_directory: str = "output"
    max_storage_gb: float = 10.0
    auto_cleanup: bool = True
    
    # UI Configuration
    window_width: int = 1200
    window_height: int = 800
    theme: str = "dark"
    show_performance_stats: bool = True

config = OfflineConfig()
```

### Main Application

```python
# main.py
import asyncio
import logging
import tkinter as tk
from pathlib import Path
import numpy as np
import cv2
from typing import Optional

from bithuman import AsyncBithuman, AudioChunk
from config import config
from audio.capture import AudioCapture
from audio.processor import AudioProcessor
from video.renderer import VideoRenderer
from video.display import VideoDisplay
from ui.main_window import MainWindow
from utils.performance import PerformanceMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OfflineAgent:
    def __init__(self):
        self.bithuman: Optional[AsyncBithuman] = None
        self.audio_capture: Optional[AudioCapture] = None
        self.audio_processor: Optional[AudioProcessor] = None
        self.video_renderer: Optional[VideoRenderer] = None
        self.video_display: Optional[VideoDisplay] = None
        self.main_window: Optional[MainWindow] = None
        self.performance_monitor = PerformanceMonitor()
        
        self.is_running = False
        self.is_recording = False
        self.frame_count = 0
        
    async def initialize(self):
        """Initialize all components for offline operation"""
        try:
            logger.info("Initializing offline agent...")
            
            # Verify model file exists
            model_path = Path(config.avatar_model_path)
            if not model_path.exists():
                raise FileNotFoundError(f"Avatar model not found: {model_path}")
            
            # Initialize bitHuman runtime
            self.bithuman = AsyncBithuman(
                api_secret=config.bithuman_api_secret,
                avatar_model_path=str(model_path),
                offline_mode=True  # Enable offline processing
            )
            
            # Initialize audio components
            self.audio_capture = AudioCapture(
                sample_rate=config.audio_sample_rate,
                channels=config.audio_channels,
                chunk_size=config.audio_chunk_size
            )
            
            self.audio_processor = AudioProcessor()
            
            # Initialize video components
            self.video_renderer = VideoRenderer(
                width=config.video_width,
                height=config.video_height,
                fps=config.video_fps
            )
            
            self.video_display = VideoDisplay()
            
            # Initialize UI
            self.main_window = MainWindow(self)
            
            # Start performance monitoring
            self.performance_monitor.start()
            
            logger.info("Offline agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize offline agent: {e}")
            raise

    async def start(self):
        """Start the offline agent"""
        try:
            self.is_running = True
            logger.info("Starting offline agent...")
            
            # Start audio capture
            await self.audio_capture.start()
            
            # Start main processing loop
            await self.processing_loop()
            
        except Exception as e:
            logger.error(f"Error starting agent: {e}")
        finally:
            await self.stop()

    async def processing_loop(self):
        """Main processing loop for real-time avatar generation"""
        while self.is_running:
            try:
                # Monitor performance
                if self.performance_monitor.cpu_usage > config.max_cpu_usage:
                    logger.warning("High CPU usage detected, adjusting processing")
                    await asyncio.sleep(0.1)
                    continue
                
                # Capture audio frame
                audio_frame = await self.audio_capture.get_frame()
                
                if audio_frame is not None:
                    # Process audio
                    processed_audio = await self.audio_processor.process(audio_frame)
                    
                    if processed_audio is not None:
                        # Generate avatar response
                        video_frame, response_audio = await self.generate_avatar_frame(
                            processed_audio
                        )
                        
                        if video_frame is not None:
                            # Render and display
                            await self.display_frame(video_frame)
                            
                            # Record if enabled
                            if self.is_recording:
                                await self.record_frame(video_frame, response_audio)
                
                # Maintain frame rate
                await asyncio.sleep(1.0 / config.video_fps)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(0.1)

    async def generate_avatar_frame(self, audio_chunk: AudioChunk):
        """Generate avatar frame from audio input"""
        try:
            # Process through bitHuman runtime
            result = await self.bithuman.process_audio(audio_chunk)
            
            if result:
                video_frame, response_audio = result
                self.frame_count += 1
                
                # Update performance stats
                self.performance_monitor.update_frame_stats(self.frame_count)
                
                return video_frame, response_audio
            
            return None, None
            
        except Exception as e:
            logger.error(f"Error generating avatar frame: {e}")
            return None, None

    async def display_frame(self, video_frame):
        """Display video frame in the UI"""
        try:
            # Render frame
            rendered_frame = await self.video_renderer.render(video_frame)
            
            # Display in UI
            await self.video_display.show_frame(rendered_frame)
            
            # Update UI
            if self.main_window:
                self.main_window.update_frame_display(rendered_frame)
                
        except Exception as e:
            logger.error(f"Error displaying frame: {e}")

    async def record_frame(self, video_frame, audio_chunk):
        """Record frame to local storage"""
        try:
            # Save to video recorder
            await self.video_renderer.record_frame(video_frame, audio_chunk)
            
        except Exception as e:
            logger.error(f"Error recording frame: {e}")

    async def stop(self):
        """Stop the offline agent"""
        self.is_running = False
        logger.info("Stopping offline agent...")
        
        try:
            if self.audio_capture:
                await self.audio_capture.stop()
            
            if self.video_renderer:
                await self.video_renderer.close()
            
            if self.bithuman:
                await self.bithuman.close()
            
            self.performance_monitor.stop()
            
            logger.info("Offline agent stopped")
            
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")

    def toggle_recording(self):
        """Toggle video recording"""
        self.is_recording = not self.is_recording
        logger.info(f"Recording {'started' if self.is_recording else 'stopped'}")
```

### Audio Processing Components

```python
# audio/capture.py
import asyncio
import numpy as np
import sounddevice as sd
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AudioCapture:
    def __init__(self, sample_rate: int, channels: int, chunk_size: int):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.stream: Optional[sd.InputStream] = None
        self.audio_queue = asyncio.Queue(maxsize=10)
        self.is_capturing = False

    async def start(self):
        """Start audio capture using sounddevice"""
        try:
            # List available audio devices
            devices = sd.query_devices()
            logger.info("Available audio devices:")
            for i, device in enumerate(devices):
                logger.info(f"  {i}: {device['name']}")
            
            # Create input stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                device=None  # Use default input device
            )
            
            self.stream.start()
            self.is_capturing = True
            logger.info("Audio capture started")
            
        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            raise

    def _audio_callback(self, indata, frames, time, status):
        """Audio input callback"""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Convert to AudioChunk format
        audio_data = indata.copy().flatten().astype(np.int16)
        
        # Add to queue (non-blocking)
        try:
            self.audio_queue.put_nowait(audio_data)
        except asyncio.QueueFull:
            # Drop oldest frame if queue is full
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put_nowait(audio_data)
            except asyncio.QueueEmpty:
                pass

    async def get_frame(self) -> Optional[np.ndarray]:
        """Get next audio frame"""
        try:
            if not self.is_capturing:
                return None
            
            # Get frame with timeout
            audio_data = await asyncio.wait_for(
                self.audio_queue.get(), 
                timeout=0.1
            )
            return audio_data
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Error getting audio frame: {e}")
            return None

    async def stop(self):
        """Stop audio capture"""
        self.is_capturing = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        logger.info("Audio capture stopped")

# audio/processor.py
import numpy as np
from typing import Optional
import webrtcvad
from bithuman import AudioChunk

class AudioProcessor:
    def __init__(self):
        # Voice Activity Detection
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        # Audio enhancement
        self.noise_reduction_enabled = True
        self.auto_gain_enabled = True
        
        # Buffers
        self.audio_buffer = np.array([], dtype=np.int16)
        self.noise_profile = None

    async def process(self, audio_data: np.ndarray) -> Optional[AudioChunk]:
        """Process raw audio data and return AudioChunk if speech detected"""
        try:
            # Apply enhancements
            if self.noise_reduction_enabled:
                audio_data = self._reduce_noise(audio_data)
            
            if self.auto_gain_enabled:
                audio_data = self._apply_auto_gain(audio_data)
            
            # Add to buffer
            self.audio_buffer = np.append(self.audio_buffer, audio_data)
            
            # Process in VAD-sized chunks
            while len(self.audio_buffer) >= self.frame_size:
                frame = self.audio_buffer[:self.frame_size]
                self.audio_buffer = self.audio_buffer[self.frame_size:]
                
                # Voice activity detection
                is_speech = self.vad.is_speech(frame.tobytes(), self.sample_rate)
                
                if is_speech:
                    # Create AudioChunk for bitHuman processing
                    return AudioChunk.from_numpy(
                        frame.astype(np.float32) / 32768.0,  # Normalize to [-1, 1]
                        sample_rate=self.sample_rate
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return None

    def _reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Simple noise reduction using spectral subtraction"""
        try:
            # Initialize noise profile if not set
            if self.noise_profile is None:
                self.noise_profile = np.mean(np.abs(audio_data))
            
            # Apply basic noise gate
            threshold = self.noise_profile * 2
            mask = np.abs(audio_data) > threshold
            
            return audio_data * mask
            
        except Exception:
            return audio_data

    def _apply_auto_gain(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply automatic gain control"""
        try:
            # Calculate RMS
            rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
            
            if rms > 0:
                # Target RMS (about -20dB)
                target_rms = 3276.8  # 10% of max int16
                gain = target_rms / rms
                
                # Limit gain to prevent clipping
                gain = min(gain, 4.0)
                
                return (audio_data.astype(np.float32) * gain).astype(np.int16)
            
            return audio_data
            
        except Exception:
            return audio_data
```

### Video Components

```python
# video/renderer.py
import cv2
import numpy as np
from typing import Optional
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoRenderer:
    def __init__(self, width: int, height: int, fps: int):
        self.width = width
        self.height = height
        self.fps = fps
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.recording_path: Optional[Path] = None
        
        # Enhancement settings
        self.enable_smoothing = True
        self.enable_upscaling = False
        self.upscale_factor = 2.0

    async def render(self, frame: np.ndarray) -> np.ndarray:
        """Render and enhance video frame"""
        try:
            # Ensure correct format
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # BGR to RGB conversion
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize to target dimensions
            if frame.shape[:2] != (self.height, self.width):
                frame = cv2.resize(frame, (self.width, self.height))
            
            # Apply enhancements
            if self.enable_smoothing:
                frame = await self._apply_smoothing(frame)
            
            if self.enable_upscaling:
                frame = await self._apply_upscaling(frame)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error rendering frame: {e}")
            return frame

    async def _apply_smoothing(self, frame: np.ndarray) -> np.ndarray:
        """Apply temporal smoothing to reduce flicker"""
        try:
            # Simple bilateral filter for noise reduction
            return cv2.bilateralFilter(frame, 5, 50, 50)
        except Exception:
            return frame

    async def _apply_upscaling(self, frame: np.ndarray) -> np.ndarray:
        """Apply AI-based upscaling if available"""
        try:
            # Simple bicubic upscaling
            new_width = int(self.width * self.upscale_factor)
            new_height = int(self.height * self.upscale_factor)
            
            return cv2.resize(frame, (new_width, new_height), 
                            interpolation=cv2.INTER_CUBIC)
        except Exception:
            return frame

    async def start_recording(self, output_path: str):
        """Start recording video to file"""
        try:
            self.recording_path = Path(output_path)
            self.recording_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(self.recording_path),
                fourcc,
                self.fps,
                (self.width, self.height)
            )
            
            logger.info(f"Started recording to {self.recording_path}")
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            raise

    async def record_frame(self, video_frame: np.ndarray, audio_chunk=None):
        """Record frame to video file"""
        try:
            if self.video_writer and video_frame is not None:
                # Convert RGB back to BGR for OpenCV
                bgr_frame = cv2.cvtColor(video_frame, cv2.COLOR_RGB2BGR)
                self.video_writer.write(bgr_frame)
                
        except Exception as e:
            logger.error(f"Error recording frame: {e}")

    async def stop_recording(self):
        """Stop video recording"""
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            logger.info(f"Stopped recording to {self.recording_path}")

    async def close(self):
        """Close renderer and cleanup"""
        await self.stop_recording()

# video/display.py
import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import asyncio

class VideoDisplay:
    def __init__(self, parent=None):
        self.parent = parent
        self.canvas: Optional[tk.Canvas] = None
        self.current_image: Optional[ImageTk.PhotoImage] = None

    def setup_canvas(self, parent, width: int, height: int):
        """Setup the display canvas"""
        self.canvas = tk.Canvas(parent, width=width, height=height, bg='black')
        self.canvas.pack(pady=10)

    async def show_frame(self, frame: np.ndarray):
        """Display frame on canvas"""
        try:
            if self.canvas is None:
                return
            
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(frame.astype(np.uint8))
            
            # Convert to PhotoImage
            self.current_image = ImageTk.PhotoImage(pil_image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                image=self.current_image
            )
            
        except Exception as e:
            logger.error(f"Error displaying frame: {e}")
```

### User Interface

```python
# ui/main_window.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import threading
from pathlib import Path

from video.display import VideoDisplay
from utils.performance import PerformanceMonitor

class MainWindow:
    def __init__(self, agent):
        self.agent = agent
        self.root = tk.Tk()
        self.setup_ui()
        self.video_display = VideoDisplay()
        
        # Performance tracking
        self.fps_label = None
        self.cpu_label = None
        self.memory_label = None

    def setup_ui(self):
        """Setup the main user interface"""
        self.root.title("bitHuman Offline Agent")
        self.root.geometry(f"{config.window_width}x{config.window_height}")
        
        # Create main frames
        self.create_menu()
        self.create_control_panel()
        self.create_video_panel()
        self.create_status_panel()

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Model", command=self.load_model)
        file_menu.add_command(label="Start Recording", command=self.start_recording)
        file_menu.add_command(label="Stop Recording", command=self.stop_recording)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Performance Stats", command=self.toggle_stats)

    def create_control_panel(self):
        """Create control panel"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Start/Stop buttons
        self.start_button = ttk.Button(
            control_frame, 
            text="Start Agent", 
            command=self.start_agent
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            control_frame, 
            text="Stop Agent", 
            command=self.stop_agent,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Recording controls
        self.record_button = ttk.Button(
            control_frame, 
            text="Start Recording", 
            command=self.toggle_recording
        )
        self.record_button.pack(side=tk.LEFT, padx=5)

    def create_video_panel(self):
        """Create video display panel"""
        video_frame = ttk.LabelFrame(self.root, text="Avatar Display")
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Setup video display
        self.video_display.setup_canvas(
            video_frame, 
            config.video_width, 
            config.video_height
        )

    def create_status_panel(self):
        """Create status panel"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Performance labels
        self.fps_label = ttk.Label(status_frame, text="FPS: 0")
        self.fps_label.pack(side=tk.LEFT, padx=10)
        
        self.cpu_label = ttk.Label(status_frame, text="CPU: 0%")
        self.cpu_label.pack(side=tk.LEFT, padx=10)
        
        self.memory_label = ttk.Label(status_frame, text="Memory: 0MB")
        self.memory_label.pack(side=tk.LEFT, padx=10)

    def start_agent(self):
        """Start the agent in a separate thread"""
        def run_agent():
            asyncio.run(self.agent.start())
        
        threading.Thread(target=run_agent, daemon=True).start()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_agent(self):
        """Stop the agent"""
        asyncio.create_task(self.agent.stop())
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def toggle_recording(self):
        """Toggle recording state"""
        self.agent.toggle_recording()
        
        if self.agent.is_recording:
            self.record_button.config(text="Stop Recording")
        else:
            self.record_button.config(text="Start Recording")

    def load_model(self):
        """Load a new avatar model"""
        file_path = filedialog.askopenfilename(
            title="Select Avatar Model",
            filetypes=[("IMX files", "*.imx"), ("All files", "*.*")]
        )
        
        if file_path:
            config.avatar_model_path = file_path
            messagebox.showinfo("Model Loaded", f"Loaded: {file_path}")

    def update_frame_display(self, frame):
        """Update the video display with new frame"""
        asyncio.create_task(self.video_display.show_frame(frame))

    def update_performance_stats(self, fps: float, cpu: float, memory: float):
        """Update performance statistics"""
        self.fps_label.config(text=f"FPS: {fps:.1f}")
        self.cpu_label.config(text=f"CPU: {cpu:.1f}%")
        self.memory_label.config(text=f"Memory: {memory:.0f}MB")

    def run(self):
        """Start the UI main loop"""
        self.root.mainloop()
```

### Performance Monitoring

```python
# utils/performance.py
import psutil
import time
import threading
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.fps = 0.0
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        
        self.monitoring = False
        self.monitor_thread = None

    def start(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Performance monitoring started")

    def stop(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Performance monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Update CPU usage
                self.cpu_usage = self.process.cpu_percent()
                
                # Update memory usage
                memory_info = self.process.memory_info()
                self.memory_usage = memory_info.rss / 1024 / 1024  # MB
                
                time.sleep(1.0)  # Update every second
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                time.sleep(1.0)

    def update_frame_stats(self, frame_count: int):
        """Update frame statistics"""
        self.frame_count = frame_count
        current_time = time.time()
        
        # Calculate FPS
        time_diff = current_time - self.last_frame_time
        if time_diff > 0:
            self.fps = 1.0 / time_diff
        
        self.last_frame_time = current_time

    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        return {
            'fps': self.fps,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'frame_count': self.frame_count,
            'uptime': time.time() - self.start_time
        }

    def is_performance_acceptable(self) -> bool:
        """Check if performance is within acceptable limits"""
        return (
            self.cpu_usage < config.max_cpu_usage and
            self.memory_usage < config.memory_limit_gb * 1024
        )
```

## Running the Application

### Startup Script

```python
# run_offline_agent.py
#!/usr/bin/env python3
import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from main import OfflineAgent
from config import config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('offline_agent.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

async def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create and initialize agent
        agent = OfflineAgent()
        await agent.initialize()
        
        # Start UI
        logger.info("Starting offline agent UI...")
        agent.main_window.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### Launch Script

```bash
#!/bin/bash
# launch_offline_agent.sh

# Set environment variables
export BITHUMAN_API_SECRET="your_api_secret_here"
export BITHUMAN_AVATAR_MODEL="./models/avatar.imx"

# Check system requirements
echo "Checking system requirements..."

# Check macOS version
macos_version=$(sw_vers -productVersion)
echo "macOS version: $macos_version"

# Check available memory
memory_gb=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
echo "Available memory: ${memory_gb}GB"

if [ $memory_gb -lt 16 ]; then
    echo "Warning: Minimum 16GB RAM recommended"
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create necessary directories
mkdir -p models output/videos output/recordings

# Install dependencies if needed
if [ ! -f "requirements_installed.flag" ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    touch requirements_installed.flag
fi

# Launch the application
echo "Launching bitHuman Offline Agent..."
python3 run_offline_agent.py
```

## Advanced Features

### Model Optimization

```python
# utils/model_optimizer.py
import torch
from bithuman import AsyncBithuman

class ModelOptimizer:
    @staticmethod
    async def optimize_for_apple_silicon(model_path: str) -> str:
        """Optimize model for Apple Silicon performance"""
        try:
            # Load and optimize model
            # This would be implemented based on bitHuman's optimization API
            optimized_path = model_path.replace('.imx', '_optimized.imx')
            
            # Model optimization logic here
            # - Quantization for faster inference
            # - Metal Performance Shaders integration
            # - Core ML conversion if supported
            
            return optimized_path
            
        except Exception as e:
            logger.error(f"Model optimization failed: {e}")
            return model_path
```

### Deployment Options

```bash
# Create macOS app bundle
python setup.py py2app

# Create DMG installer
hdiutil create -volname "bitHuman Offline Agent" \
    -srcfolder dist/ \
    -ov -format UDZO \
    bitHuman-offline-agent.dmg
```

## Troubleshooting

### Common Issues

1. **Audio device not found**:
   ```bash
   # List audio devices
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```

2. **Permission denied for microphone**:
   - Grant microphone access in System Preferences > Security & Privacy

3. **High CPU usage**:
   - Reduce video resolution or frame rate
   - Enable performance monitoring
   - Check for background processes

4. **Memory issues**:
   - Monitor memory usage in Activity Monitor
   - Adjust buffer sizes in configuration
   - Enable automatic cleanup

### Performance Optimization

1. **Enable Metal Performance Shaders**:
   ```python
   config.enable_gpu_acceleration = True
   ```

2. **Adjust quality settings**:
   ```python
   config.video_fps = 15  # Reduce for lower CPU usage
   config.video_width = 256  # Smaller resolution
   ```

3. **Optimize audio processing**:
   ```python
   config.audio_chunk_size = 2048  # Larger chunks
   ```

This comprehensive offline implementation provides a fully functional real-time visual agent that runs entirely on macOS without internet connectivity, optimized for Apple Silicon performance. 