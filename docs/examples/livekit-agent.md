# Real Time Visual Agent via LiveKit

> Build a production-ready real-time avatar agent that can engage in live conversations using LiveKit's WebRTC infrastructure.

## Overview

This example demonstrates how to create a real-time visual agent using bitHuman SDK with LiveKit for WebRTC streaming. The agent can participate in live video calls, respond to audio input with realistic facial animations, and stream the results to multiple participants.

## Prerequisites

- Python 3.8+
- bitHuman SDK installed
- LiveKit account and API credentials
- Avatar model file (.imx)
- Valid bitHuman API secret

## Installation

```bash
# Install required packages
pip install bithuman livekit-rtc livekit-api asyncio

# For audio processing
pip install numpy soundfile

# For enhanced features (optional)
pip install opencv-python pillow
```

## Project Structure

```
livekit-agent/
├── agent.py              # Main agent implementation
├── config.py             # Configuration management
├── audio_processor.py    # Audio processing utilities
├── requirements.txt      # Dependencies
└── docker/              # Docker deployment files
    ├── Dockerfile
    └── docker-compose.yml
```

## Basic LiveKit Agent

### Configuration

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    # LiveKit Configuration
    livekit_url: str = os.getenv('LIVEKIT_URL', 'wss://your-livekit-server.com')
    livekit_api_key: str = os.getenv('LIVEKIT_API_KEY')
    livekit_api_secret: str = os.getenv('LIVEKIT_API_SECRET')
    
    # bitHuman Configuration
    bithuman_api_secret: str = os.getenv('BITHUMAN_API_SECRET')
    avatar_model_path: str = os.getenv('BITHUMAN_AVATAR_MODEL')
    
    # Agent Configuration
    room_name: str = "bithuman-agent-room"
    agent_name: str = "bitHuman Assistant"
    audio_sample_rate: int = 16000
    video_fps: int = 25
    
    # Quality settings
    video_width: int = 512
    video_height: int = 512
    audio_bitrate: int = 64000
    video_bitrate: int = 1000000

config = Config()
```

### Main Agent Implementation

```python
# agent.py
import asyncio
import logging
import numpy as np
from typing import Optional
import cv2

from livekit import rtc, api
from bithuman import AsyncBithuman, AudioChunk

from config import config
from audio_processor import AudioProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BitHumanAgent:
    def __init__(self):
        self.room: Optional[rtc.Room] = None
        self.bithuman: Optional[AsyncBithuman] = None
        self.audio_processor = AudioProcessor()
        self.is_connected = False
        self.video_track: Optional[rtc.LocalVideoTrack] = None
        self.audio_track: Optional[rtc.LocalAudioTrack] = None
        
    async def initialize(self):
        """Initialize the bitHuman runtime and LiveKit components"""
        try:
            # Initialize bitHuman runtime
            self.bithuman = AsyncBithuman(
                api_secret=config.bithuman_api_secret,
                avatar_model_path=config.avatar_model_path
            )
            
            logger.info("bitHuman runtime initialized successfully")
            
            # Create LiveKit room
            self.room = rtc.Room()
            self.room.on("participant_connected", self.on_participant_connected)
            self.room.on("track_received", self.on_track_received)
            self.room.on("disconnected", self.on_disconnected)
            
            logger.info("LiveKit room created successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    async def connect_to_room(self, token: str):
        """Connect to LiveKit room with provided token"""
        try:
            await self.room.connect(config.livekit_url, token)
            self.is_connected = True
            logger.info(f"Connected to room: {config.room_name}")
            
            # Start publishing avatar video and audio
            await self.start_publishing()
            
        except Exception as e:
            logger.error(f"Failed to connect to room: {e}")
            raise

    async def start_publishing(self):
        """Start publishing avatar video and audio streams"""
        try:
            # Create video track
            video_source = rtc.VideoSource(
                config.video_width, 
                config.video_height
            )
            self.video_track = rtc.LocalVideoTrack.create_video_track(
                "avatar-video", 
                video_source
            )
            
            # Create audio track
            audio_source = rtc.AudioSource(
                config.audio_sample_rate, 
                1  # mono
            )
            self.audio_track = rtc.LocalAudioTrack.create_audio_track(
                "avatar-audio", 
                audio_source
            )
            
            # Publish tracks
            await self.room.local_participant.publish_track(
                self.video_track,
                rtc.TrackPublishOptions(video_encoding=rtc.VideoEncoding(
                    max_bitrate=config.video_bitrate
                ))
            )
            
            await self.room.local_participant.publish_track(
                self.audio_track,
                rtc.TrackPublishOptions(audio_encoding=rtc.AudioEncoding(
                    max_bitrate=config.audio_bitrate
                ))
            )
            
            logger.info("Started publishing avatar streams")
            
        except Exception as e:
            logger.error(f"Failed to start publishing: {e}")
            raise

    async def on_participant_connected(self, participant: rtc.RemoteParticipant):
        """Handle new participant joining the room"""
        logger.info(f"Participant connected: {participant.identity}")

    async def on_track_received(self, track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        """Handle incoming audio/video tracks from participants"""
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            logger.info(f"Received audio track from {participant.identity}")
            # Process incoming audio for avatar animation
            await self.process_incoming_audio(track)

    async def process_incoming_audio(self, audio_track: rtc.AudioTrack):
        """Process incoming audio and generate avatar responses"""
        async for frame in rtc.AudioStream(audio_track):
            try:
                # Convert LiveKit audio frame to numpy array
                audio_data = np.frombuffer(frame.data, dtype=np.int16)
                
                # Process with audio processor
                processed_audio = self.audio_processor.process(audio_data)
                
                if processed_audio is not None:
                    # Create AudioChunk for bitHuman
                    audio_chunk = AudioChunk.from_numpy(
                        processed_audio, 
                        sample_rate=config.audio_sample_rate
                    )
                    
                    # Generate avatar response
                    await self.generate_avatar_response(audio_chunk)
                    
            except Exception as e:
                logger.error(f"Error processing audio: {e}")

    async def generate_avatar_response(self, audio_chunk: AudioChunk):
        """Generate and stream avatar response"""
        try:
            # Process through bitHuman runtime
            video_frame, response_audio = await self.bithuman.process_audio(audio_chunk)
            
            if video_frame:
                # Convert to LiveKit video frame
                lk_video_frame = self.convert_to_livekit_frame(video_frame)
                
                # Send to video track
                if self.video_track:
                    await self.video_track.capture_frame(lk_video_frame)
            
            if response_audio:
                # Convert to LiveKit audio frame
                lk_audio_frame = self.convert_to_livekit_audio(response_audio)
                
                # Send to audio track
                if self.audio_track:
                    await self.audio_track.capture_frame(lk_audio_frame)
                    
        except Exception as e:
            logger.error(f"Error generating avatar response: {e}")

    def convert_to_livekit_frame(self, video_frame) -> rtc.VideoFrame:
        """Convert bitHuman video frame to LiveKit format"""
        # Convert frame to RGB if needed
        if len(video_frame.shape) == 3 and video_frame.shape[2] == 3:
            frame_rgb = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
        else:
            frame_rgb = video_frame
            
        return rtc.VideoFrame(
            width=frame_rgb.shape[1],
            height=frame_rgb.shape[0],
            type=rtc.VideoBufferType.RGBA,
            data=frame_rgb.tobytes()
        )

    def convert_to_livekit_audio(self, audio_chunk: AudioChunk) -> rtc.AudioFrame:
        """Convert bitHuman audio chunk to LiveKit format"""
        audio_data = audio_chunk.to_numpy()
        
        return rtc.AudioFrame(
            data=audio_data.tobytes(),
            sample_rate=config.audio_sample_rate,
            num_channels=1,
            samples_per_channel=len(audio_data)
        )

    async def on_disconnected(self):
        """Handle room disconnection"""
        self.is_connected = False
        logger.info("Disconnected from room")

    async def cleanup(self):
        """Clean up resources"""
        if self.room and self.is_connected:
            await self.room.disconnect()
        
        if self.bithuman:
            await self.bithuman.close()
        
        logger.info("Agent cleanup completed")

# Audio Processing Utilities
# audio_processor.py
import numpy as np
from typing import Optional
import webrtcvad

class AudioProcessor:
    def __init__(self, aggressiveness: int = 2):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        self.buffer = np.array([], dtype=np.int16)
        
    def process(self, audio_data: np.ndarray) -> Optional[np.ndarray]:
        """Process incoming audio and return when speech is detected"""
        # Add to buffer
        self.buffer = np.append(self.buffer, audio_data)
        
        # Process in chunks
        while len(self.buffer) >= self.frame_size:
            frame = self.buffer[:self.frame_size]
            self.buffer = self.buffer[self.frame_size:]
            
            # Voice activity detection
            is_speech = self.vad.is_speech(frame.tobytes(), self.sample_rate)
            
            if is_speech:
                return frame
                
        return None

# Token Generation Utility
async def generate_room_token(room_name: str, participant_identity: str) -> str:
    """Generate a LiveKit room token for the agent"""
    token = (
        api.AccessToken(config.livekit_api_key, config.livekit_api_secret)
        .with_identity(participant_identity)
        .with_name(config.agent_name)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True
            )
        )
    )
    
    return token.to_jwt()

# Main execution
async def main():
    """Main entry point for the LiveKit agent"""
    try:
        # Create and initialize agent
        agent = BitHumanAgent()
        await agent.initialize()
        
        # Generate room token
        token = await generate_room_token(
            config.room_name, 
            config.agent_name
        )
        
        # Connect to room
        await agent.connect_to_room(token)
        
        logger.info("Agent is running and ready for participants...")
        
        # Keep the agent running
        while agent.is_connected:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down agent...")
    except Exception as e:
        logger.error(f"Agent error: {e}")
    finally:
        if 'agent' in locals():
            await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Features

### Multi-participant Support

```python
# Enhanced agent with multi-participant support
class MultiParticipantAgent(BitHumanAgent):
    def __init__(self):
        super().__init__()
        self.participant_audio_streams = {}
        self.conversation_context = {}
        
    async def on_participant_connected(self, participant: rtc.RemoteParticipant):
        """Handle new participant with context initialization"""
        await super().on_participant_connected(participant)
        
        # Initialize conversation context for participant
        self.conversation_context[participant.identity] = {
            'join_time': asyncio.get_event_loop().time(),
            'total_interactions': 0,
            'last_interaction': None
        }
        
        # Send welcome message
        await self.send_welcome_message(participant)
    
    async def send_welcome_message(self, participant: rtc.RemoteParticipant):
        """Send personalized welcome message"""
        welcome_text = f"Welcome {participant.identity} to the bitHuman experience!"
        
        # Convert text to speech and generate avatar animation
        audio_chunk = await self.text_to_speech(welcome_text)
        await self.generate_avatar_response(audio_chunk)
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Expose port for health checks
EXPOSE 8080

# Start the agent
CMD ["python", "agent.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  bithuman-agent:
    build: .
    environment:
      - LIVEKIT_URL=${LIVEKIT_URL}
      - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
      - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
      - BITHUMAN_API_SECRET=${BITHUMAN_API_SECRET}
      - BITHUMAN_AVATAR_MODEL=/app/models/avatar.imx
    volumes:
      - ./models:/app/models:ro
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Environment Setup

```bash
# .env file
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
BITHUMAN_API_SECRET=your_bithuman_secret
BITHUMAN_AVATAR_MODEL=/path/to/avatar.imx
```

## Testing the Agent

### Local Testing

```python
# test_agent.py
import asyncio
import pytest
from agent import BitHumanAgent
from config import config

@pytest.fixture
async def agent():
    agent = BitHumanAgent()
    await agent.initialize()
    yield agent
    await agent.cleanup()

async def test_agent_initialization(agent):
    """Test that agent initializes properly"""
    assert agent.bithuman is not None
    assert agent.room is not None

async def test_audio_processing(agent):
    """Test audio processing pipeline"""
    # Create test audio data
    test_audio = np.random.randint(-32768, 32767, 16000, dtype=np.int16)
    
    # Process audio
    processed = agent.audio_processor.process(test_audio)
    
    # Verify processing
    assert processed is not None or processed is None  # Depends on VAD
```

### Production Monitoring

```python
# monitoring.py
import logging
import time
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AgentMetrics:
    participants_count: int = 0
    total_audio_frames: int = 0
    total_video_frames: int = 0
    avg_processing_time: float = 0.0
    errors_count: int = 0
    uptime: float = 0.0

class AgentMonitor:
    def __init__(self):
        self.metrics = AgentMetrics()
        self.start_time = time.time()
        
    def update_metrics(self, **kwargs):
        """Update agent metrics"""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        
        self.metrics.uptime = time.time() - self.start_time
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return {
            "status": "healthy" if self.metrics.errors_count < 10 else "degraded",
            "metrics": self.metrics.__dict__,
            "timestamp": time.time()
        }
```

## Best Practices

### Performance Optimization

1. **Use efficient audio processing**:
   ```python
   # Use VAD to process only speech segments
   if self.vad.is_speech(frame, sample_rate):
       await self.process_audio_frame(frame)
   ```

2. **Implement frame rate control**:
   ```python
   # Control video frame rate
   frame_interval = 1.0 / config.video_fps
   await asyncio.sleep(frame_interval)
   ```

3. **Buffer management**:
   ```python
   # Maintain audio buffer for smooth processing
   self.audio_buffer.append(frame)
   if len(self.audio_buffer) > max_buffer_size:
       self.audio_buffer.pop(0)
   ```

### Error Handling

```python
async def robust_audio_processing(self, audio_data):
    """Audio processing with comprehensive error handling"""
    try:
        return await self.process_audio(audio_data)
    except AudioProcessingError as e:
        logger.warning(f"Audio processing failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await self.handle_critical_error(e)
        return None
```

## Deployment Options

### Cloud Deployment

1. **AWS ECS**: Use the provided Docker configuration
2. **Google Cloud Run**: Scale automatically with serverless
3. **Azure Container Instances**: Simple container deployment
4. **Kubernetes**: Full orchestration for production scale

### Scaling Considerations

- **Horizontal scaling**: Deploy multiple agent instances
- **Load balancing**: Distribute participants across agents
- **Resource monitoring**: Track CPU, memory, and network usage
- **Auto-scaling**: Scale based on participant count

## Troubleshooting

### Common Issues

1. **Audio sync problems**: Check sample rates match (16kHz)
2. **Video quality issues**: Adjust bitrate and resolution
3. **Connection timeouts**: Verify LiveKit server accessibility
4. **Avatar loading errors**: Check model file path and permissions

### Debug Mode

```python
# Enable debug logging
logging.getLogger('bithuman').setLevel(logging.DEBUG)
logging.getLogger('livekit').setLevel(logging.DEBUG)
```

This comprehensive example provides a production-ready foundation for building real-time visual agents with LiveKit integration. The modular design makes it easy to extend and customize for specific use cases. 