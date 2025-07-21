# Real Time Visual Agent on Raspberry Pi

> Deploy bitHuman agents on Raspberry Pi for edge AI applications with optimized performance for ARM64 architecture.

## Overview

This example shows how to run bitHuman agents on Raspberry Pi devices, enabling edge AI deployments with real-time avatar generation. Perfect for IoT applications, kiosks, and edge computing scenarios.

## Prerequisites

- **Raspberry Pi 4B** (8GB RAM recommended)
- **Raspberry Pi OS 64-bit** (Bullseye or later)
- **Python 3.9+**
- **USB microphone and camera**
- **bitHuman API secret**
- **Avatar model file** (.imx)

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Model** | Pi 4B 4GB | Pi 4B 8GB |
| **Storage** | 32GB microSD | 64GB+ SSD |
| **Power** | 3A USB-C | Official PSU |
| **Cooling** | Passive heatsink | Active cooling |

## Installation

### System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    cmake \
    build-essential \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    libasound2-dev \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libopencv-dev

# Enable camera and audio
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_ssh 0
```

### Python Environment

```bash
# Create virtual environment
python3 -m venv bithuman-env
source bithuman-env/bin/activate

# Install optimized packages for ARM64
pip install --upgrade pip
pip install numpy==1.21.6  # ARM64 optimized version
pip install opencv-python-headless
pip install pyaudio
pip install asyncio
pip install psutil

# Install bitHuman SDK
pip install bithuman
```

## Project Structure

```
pi-agent/
├── main.py              # Main application
├── config.py            # Configuration
├── audio_capture.py     # Audio handling
├── video_processor.py   # Video processing
├── performance.py       # Performance monitoring
├── requirements.txt     # Dependencies
└── systemd/            # Service files
    └── bithuman-agent.service
```

## Core Implementation

### Configuration for Pi

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class PiConfig:
    # API Configuration
    bithuman_api_secret: str = os.getenv('BITHUMAN_API_SECRET')
    avatar_model_path: str = "/home/pi/models/avatar.imx"
    
    # Performance Settings (optimized for Pi)
    video_width: int = 256
    video_height: int = 256
    video_fps: int = 15
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    audio_chunk_size: int = 2048
    
    # Resource Limits
    max_cpu_usage: float = 85.0
    max_memory_mb: float = 2048
    
    # GPU Acceleration (if available)
    use_gpu: bool = False  # Limited on Pi
    
    # Network Settings
    enable_streaming: bool = True
    stream_port: int = 8080

config = PiConfig()
```

### Optimized Main Application

```python
# main.py
import asyncio
import logging
import numpy as np
from typing import Optional
import cv2
import time

from bithuman import AsyncBithuman, AudioChunk
from config import config
from audio_capture import PiAudioCapture
from video_processor import PiVideoProcessor
from performance import PerformanceMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PiAgent:
    def __init__(self):
        self.bithuman: Optional[AsyncBithuman] = None
        self.audio_capture = PiAudioCapture()
        self.video_processor = PiVideoProcessor()
        self.performance_monitor = PerformanceMonitor()
        self.is_running = False
        
    async def initialize(self):
        """Initialize components with Pi optimizations"""
        try:
            # Initialize bitHuman with reduced settings
            self.bithuman = AsyncBithuman(
                api_secret=config.bithuman_api_secret,
                avatar_model_path=config.avatar_model_path,
                max_concurrent_requests=1,  # Limit for Pi
                enable_optimizations=True
            )
            
            await self.audio_capture.initialize()
            await self.video_processor.initialize()
            self.performance_monitor.start()
            
            logger.info("Pi agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise

    async def run(self):
        """Main processing loop optimized for Pi"""
        self.is_running = True
        frame_interval = 1.0 / config.video_fps
        
        while self.is_running:
            start_time = time.time()
            
            try:
                # Check system resources
                if not self.performance_monitor.can_process():
                    await asyncio.sleep(0.1)
                    continue
                
                # Capture audio
                audio_data = await self.audio_capture.get_audio()
                
                if audio_data is not None:
                    # Process with bitHuman
                    video_frame, audio_response = await self.process_audio(audio_data)
                    
                    if video_frame is not None:
                        # Process video
                        await self.video_processor.display_frame(video_frame)
                
                # Maintain frame rate
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Processing error: {e}")
                await asyncio.sleep(0.1)

    async def process_audio(self, audio_data: np.ndarray):
        """Process audio with error handling"""
        try:
            audio_chunk = AudioChunk.from_numpy(
                audio_data.astype(np.float32) / 32768.0,
                sample_rate=config.audio_sample_rate
            )
            
            return await self.bithuman.process_audio(audio_chunk)
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return None, None

    async def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        
        if self.bithuman:
            await self.bithuman.close()
        
        await self.audio_capture.cleanup()
        await self.video_processor.cleanup()
        self.performance_monitor.stop()

# Audio capture optimized for Pi
# audio_capture.py
import pyaudio
import numpy as np
import asyncio
from typing import Optional

class PiAudioCapture:
    def __init__(self):
        self.stream = None
        self.audio_queue = asyncio.Queue(maxsize=5)
        
    async def initialize(self):
        """Initialize audio capture"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Find USB microphone
            device_index = self._find_usb_mic()
            
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=config.audio_channels,
                rate=config.audio_sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=config.audio_chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.stream.start_stream()
            logger.info("Audio capture initialized")
            
        except Exception as e:
            logger.error(f"Audio initialization failed: {e}")
            raise

    def _find_usb_mic(self):
        """Find USB microphone device"""
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if "USB" in info["name"] and info["maxInputChannels"] > 0:
                return i
        return None  # Use default

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio callback"""
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        try:
            self.audio_queue.put_nowait(audio_data)
        except asyncio.QueueFull:
            pass  # Drop frame if queue full
        
        return (None, pyaudio.paContinue)

    async def get_audio(self) -> Optional[np.ndarray]:
        """Get audio data"""
        try:
            return await asyncio.wait_for(
                self.audio_queue.get(), 
                timeout=0.1
            )
        except asyncio.TimeoutError:
            return None

    async def cleanup(self):
        """Cleanup audio resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if hasattr(self, 'audio'):
            self.audio.terminate()

# Video processing for Pi
# video_processor.py
import cv2
import numpy as np
from typing import Optional

class PiVideoProcessor:
    def __init__(self):
        self.display = None
        self.window_name = "bitHuman Agent"
        
    async def initialize(self):
        """Initialize video display"""
        try:
            # Check if display is available
            if os.environ.get('DISPLAY'):
                cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
                self.display = True
            else:
                logger.info("No display available, running headless")
                self.display = False
                
        except Exception as e:
            logger.warning(f"Display initialization failed: {e}")
            self.display = False

    async def display_frame(self, frame: np.ndarray):
        """Display video frame"""
        try:
            if self.display:
                # Resize for Pi display
                display_frame = cv2.resize(frame, (512, 512))
                cv2.imshow(self.window_name, display_frame)
                cv2.waitKey(1)
            
        except Exception as e:
            logger.error(f"Display error: {e}")

    async def cleanup(self):
        """Cleanup video resources"""
        if self.display:
            cv2.destroyAllWindows()

# Performance monitoring for Pi
# performance.py
import psutil
import time

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.temperature = 0.0
        
    def start(self):
        """Start monitoring"""
        logger.info("Performance monitoring started")
        
    def can_process(self) -> bool:
        """Check if system can handle processing"""
        self.update_stats()
        
        return (
            self.cpu_usage < config.max_cpu_usage and
            self.memory_usage < config.max_memory_mb and
            self.temperature < 80.0  # Thermal throttling
        )
    
    def update_stats(self):
        """Update system statistics"""
        self.cpu_usage = psutil.cpu_percent()
        self.memory_usage = psutil.virtual_memory().used / 1024 / 1024
        self.temperature = self._get_cpu_temperature()
    
    def _get_cpu_temperature(self) -> float:
        """Get CPU temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return float(f.read()) / 1000.0
        except:
            return 0.0
    
    def stop(self):
        """Stop monitoring"""
        logger.info("Performance monitoring stopped")

# Main execution
async def main():
    """Main entry point"""
    agent = PiAgent()
    
    try:
        await agent.initialize()
        logger.info("Starting Pi agent...")
        await agent.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Deployment

### Systemd Service

```ini
# systemd/bithuman-agent.service
[Unit]
Description=bitHuman Agent for Raspberry Pi
After=network.target sound.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/pi-agent
Environment=BITHUMAN_API_SECRET=your_secret_here
Environment=BITHUMAN_AVATAR_MODEL=/home/pi/models/avatar.imx
ExecStart=/home/pi/pi-agent/bithuman-env/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Install and enable service
sudo cp systemd/bithuman-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bithuman-agent
sudo systemctl start bithuman-agent
```

### Performance Optimization

```bash
# Increase GPU memory split
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt

# Optimize CPU performance
echo 'arm_freq=1800' | sudo tee -a /boot/config.txt
echo 'over_voltage=2' | sudo tee -a /boot/config.txt

# Improve I/O performance
echo 'dtparam=sd_overclock=100' | sudo tee -a /boot/config.txt

# Enable performance governor
echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

## Troubleshooting

### Common Issues

1. **Audio device not found**:
   ```bash
   # List audio devices
   arecord -l
   
   # Test microphone
   arecord -d 5 test.wav
   ```

2. **High CPU usage**:
   - Reduce video resolution and FPS
   - Enable hardware acceleration if available
   - Monitor with `htop`

3. **Memory issues**:
   ```bash
   # Check memory usage
   free -h
   
   # Increase swap if needed
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=2048
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

4. **Thermal throttling**:
   ```bash
   # Monitor temperature
   vcgencmd measure_temp
   
   # Check throttling status
   vcgencmd get_throttled
   ```

## Advanced Features

### Web Interface

```python
# Add to main.py for web streaming
from aiohttp import web
import aiohttp_cors

async def setup_web_server():
    """Setup web interface for remote access"""
    app = web.Application()
    
    # CORS setup
    cors = aiohttp_cors.setup(app)
    
    # Routes
    app.router.add_get('/status', get_status)
    app.router.add_get('/stream', get_video_stream)
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', config.stream_port)
    await site.start()

async def get_status(request):
    """Get agent status"""
    return web.json_response({
        'status': 'running',
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'temperature': agent.performance_monitor.temperature
    })
```

### IoT Integration

```python
# MQTT integration for IoT
import asyncio_mqtt as mqtt

async def mqtt_handler():
    """Handle MQTT messages for IoT control"""
    async with mqtt.Client("bithuman-pi") as client:
        await client.subscribe("bithuman/commands")
        
        async with client.unfiltered_messages() as messages:
            async for message in messages:
                command = message.payload.decode()
                
                if command == "start":
                    await agent.start()
                elif command == "stop":
                    await agent.stop()
```

This implementation provides a production-ready foundation for running bitHuman agents on Raspberry Pi with optimizations for ARM64 architecture and limited resources. 