# LiveKit Integration

Integrate bitHuman avatars seamlessly with LiveKit for real-time video conferencing, streaming, and interactive applications. This guide covers setup, implementation, and best practices.

## Overview

LiveKit + bitHuman enables:
- **Real-time avatar conferencing** - Video calls with lifelike avatars
- **Interactive streaming** - Live streams with avatar hosts
- **Multi-participant experiences** - Multiple avatars in one session
- **WebRTC optimization** - Low-latency peer-to-peer connections
- **Scalable infrastructure** - Handle thousands of concurrent users

## Prerequisites

Before starting, ensure you have:
- ✅ [bitHuman SDK installed](../getting-started/installation.md)
- ✅ [Validated API credentials](../getting-started/validate-api.md)
- ✅ LiveKit server or LiveKit Cloud account
- ✅ Python 3.10+ environment

## Installation

### 1. Install Dependencies

```bash
# Install LiveKit Python SDK and bitHuman integration
pip install livekit bithuman[livekit]

# For advanced features
pip install livekit-agents livekit-api
```

### 2. Environment Setup

```bash
# LiveKit configuration
export LIVEKIT_URL='wss://your-livekit-server.com'
export LIVEKIT_API_KEY='your_livekit_api_key'
export LIVEKIT_API_SECRET='your_livekit_api_secret'

# bitHuman configuration  
export BITHUMAN_API_SECRET='your_bithuman_api_secret'
export BITHUMAN_AVATAR_MODEL='/path/to/avatar.imx'
```

## Basic Integration

### Simple Avatar Participant

```python
# basic_avatar_participant.py
import asyncio
import os
from livekit import Room, RoomOptions, VideoTrack, AudioTrack
from livekit.agents import JobContext, WorkerOptions, cli
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk
from bithuman.livekit import BitHumanVideoTrack, BitHumanAudioTrack

class AvatarParticipant:
    def __init__(self, room_name: str, participant_name: str):
        self.room_name = room_name
        self.participant_name = participant_name
        self.room = None
        self.bithuman_runtime = None
        self.video_track = None
        self.audio_track = None
        
    async def initialize(self):
        """Initialize bitHuman runtime and LiveKit room"""
        # Initialize bitHuman
        self.bithuman_runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        
        # Create custom video track for avatar
        self.video_track = BitHumanVideoTrack(self.bithuman_runtime)
        self.audio_track = BitHumanAudioTrack()
        
        # Connect to LiveKit room
        self.room = Room()
        
        # Set up event handlers
        self.room.on("participant_connected", self.on_participant_connected)
        self.room.on("track_subscribed", self.on_track_subscribed)
        
        # Connect to room
        await self.room.connect(
            url=os.getenv('LIVEKIT_URL'),
            token=self.generate_access_token(),
            options=RoomOptions(
                auto_subscribe=True,
                dynacast=True,
                adaptive_stream=True
            )
        )
        
        # Publish avatar tracks
        await self.room.local_participant.publish_track(
            self.video_track, 
            name="avatar_video"
        )
        await self.room.local_participant.publish_track(
            self.audio_track,
            name="avatar_audio"
        )
        
    def generate_access_token(self):
        """Generate LiveKit access token"""
        from livekit.api import AccessToken, VideoGrants
        
        token = AccessToken(
            api_key=os.getenv('LIVEKIT_API_KEY'),
            api_secret=os.getenv('LIVEKIT_API_SECRET')
        )
        
        token = token.with_identity(self.participant_name)
        token = token.with_grants(VideoGrants(
            room_join=True,
            room=self.room_name,
            can_publish=True,
            can_subscribe=True
        ))
        
        return token.to_jwt()
    
    async def on_participant_connected(self, participant):
        """Handle new participant joining"""
        print(f"Participant joined: {participant.identity}")
        
        # Send welcome message through avatar
        welcome_audio = f"Hello {participant.identity}, welcome to the room!"
        await self.speak_text(welcome_audio)
    
    async def on_track_subscribed(self, track, publication, participant):
        """Handle incoming audio/video tracks"""
        if track.kind == "audio":
            # Process incoming audio through avatar
            asyncio.create_task(self.process_incoming_audio(track))
    
    async def process_incoming_audio(self, audio_track):
        """Process incoming audio and generate avatar response"""
        async for audio_frame in audio_track:
            # Convert LiveKit audio frame to bitHuman AudioChunk
            audio_data = audio_frame.data
            audio_chunk = AudioChunk.from_bytes(audio_data, audio_frame.sample_rate)
            
            # Process through bitHuman to generate avatar animation
            async for video_frame in self.bithuman_runtime.process_audio_chunk(audio_chunk):
                # Send video frame to LiveKit
                await self.video_track.send_frame(video_frame)
                
                # Send corresponding audio
                await self.audio_track.send_audio(video_frame.audio_chunk)
    
    async def speak_text(self, text: str):
        """Make avatar speak given text (requires TTS integration)"""
        # Convert text to audio using your preferred TTS
        # This is a placeholder - implement with your TTS service
        tts_audio = await self.text_to_speech(text)
        
        # Process through bitHuman
        async for video_frame in self.bithuman_runtime.process_audio_chunk(tts_audio):
            await self.video_track.send_frame(video_frame)
            await self.audio_track.send_audio(video_frame.audio_chunk)
    
    async def text_to_speech(self, text: str) -> AudioChunk:
        """Convert text to speech (implement with your TTS service)"""
        # Placeholder implementation
        # In practice, integrate with services like:
        # - OpenAI TTS
        # - Azure Cognitive Services
        # - Google Text-to-Speech
        # - Amazon Polly
        pass
    
    async def cleanup(self):
        """Clean up resources"""
        if self.room:
            await self.room.disconnect()
        if self.bithuman_runtime:
            await self.bithuman_runtime.close()

# Usage
async def main():
    avatar = AvatarParticipant("my-room", "avatar-host")
    
    try:
        await avatar.initialize()
        print("Avatar participant connected to LiveKit room")
        
        # Keep running
        await asyncio.Future()
        
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await avatar.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Integration: AI Agent

### Conversational Avatar Agent

```python
# ai_avatar_agent.py
import asyncio
import logging
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.llm import LLM, ChatContext, ChatMessage
from livekit.agents.stt import STT
from livekit.agents.tts import TTS
from livekit.agents.voice_assistant import VoiceAssistant
from bithuman.runtime import AsyncBithuman
from bithuman.livekit import BitHumanVideoPlugin

logger = logging.getLogger("avatar-agent")

class BitHumanAvatarAgent:
    def __init__(self, ctx: JobContext):
        self.ctx = ctx
        self.bithuman_runtime = None
        self.chat_context = ChatContext()
        
        # Configure personality
        self.chat_context.messages.append(
            ChatMessage(
                role="system",
                content="""You are Alex, a friendly and knowledgeable customer service representative. 
                You speak naturally and conversationally, helping users with their questions and concerns.
                Keep responses concise but helpful."""
            )
        )
    
    async def entrypoint(self):
        """Main entry point for the agent"""
        logger.info("Starting bitHuman Avatar Agent")
        
        # Initialize bitHuman runtime
        self.bithuman_runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        
        # Create avatar video plugin
        avatar_plugin = BitHumanVideoPlugin(self.bithuman_runtime)
        
        # Configure AI services (use your preferred providers)
        llm = LLM()  # Configure with OpenAI, Anthropic, etc.
        stt = STT()  # Configure speech-to-text
        tts = TTS()  # Configure text-to-speech
        
        # Create voice assistant with avatar integration
        assistant = VoiceAssistant(
            llm=llm,
            stt=stt,
            tts=tts,
            chat_ctx=self.chat_context,
            video_plugin=avatar_plugin,  # Avatar integration
            fnc_ctx=None,  # Function calling context if needed
        )
        
        # Connect to room and start assistant
        await self.ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        assistant.start(self.ctx.room)
        
        # Greet users when they join
        await asyncio.sleep(1)
        await assistant.say("Hello! I'm Alex, your virtual assistant. How can I help you today?")
        
        # Keep agent running
        await assistant.aclose()

# Agent configuration
async def entrypoint(ctx: JobContext):
    agent = BitHumanAvatarAgent(ctx)
    await agent.entrypoint()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=None,  # Optional prewarming
        ),
    )
```

### Multi-Avatar Conference

```python
# multi_avatar_conference.py
import asyncio
import logging
from typing import Dict, List
from livekit import Room, Participant, VideoTrack
from livekit.agents import JobContext, WorkerOptions
from bithuman.runtime import AsyncBithuman
from bithuman.livekit import BitHumanVideoTrack

class MultiAvatarConference:
    def __init__(self):
        self.avatars: Dict[str, AsyncBithuman] = {}
        self.video_tracks: Dict[str, BitHumanVideoTrack] = {}
        self.room = None
        
    async def initialize_avatars(self, avatar_configs: List[Dict]):
        """Initialize multiple avatars with different models/personalities"""
        for config in avatar_configs:
            avatar_id = config['id']
            
            # Initialize bitHuman runtime for this avatar
            runtime = await AsyncBithuman.create(
                api_secret=os.getenv('BITHUMAN_API_SECRET'),
                model_path=config['model_path']
            )
            
            self.avatars[avatar_id] = runtime
            
            # Create video track for this avatar
            video_track = BitHumanVideoTrack(
                runtime, 
                participant_name=config['name']
            )
            self.video_tracks[avatar_id] = video_track
    
    async def connect_to_room(self, room_url: str, room_token: str):
        """Connect all avatars to LiveKit room"""
        self.room = Room()
        
        await self.room.connect(room_url, room_token)
        
        # Publish all avatar video tracks
        for avatar_id, track in self.video_tracks.items():
            await self.room.local_participant.publish_track(
                track, 
                name=f"avatar_{avatar_id}"
            )
    
    async def orchestrate_conversation(self, conversation_script: List[Dict]):
        """Orchestrate a scripted conversation between avatars"""
        for step in conversation_script:
            avatar_id = step['avatar']
            text = step['text']
            
            if avatar_id in self.avatars:
                await self.make_avatar_speak(avatar_id, text)
                await asyncio.sleep(step.get('pause', 1))
    
    async def make_avatar_speak(self, avatar_id: str, text: str):
        """Make specific avatar speak"""
        if avatar_id not in self.avatars:
            return
            
        runtime = self.avatars[avatar_id]
        video_track = self.video_tracks[avatar_id]
        
        # Convert text to audio (implement TTS)
        audio_chunk = await self.text_to_speech(text)
        
        # Process through bitHuman
        async for video_frame in runtime.process_audio_chunk(audio_chunk):
            await video_track.send_frame(video_frame)

# Example usage
avatar_configs = [
    {
        'id': 'host',
        'name': 'Sarah',
        'model_path': '/path/to/host_avatar.imx'
    },
    {
        'id': 'expert',
        'name': 'Dr. Johnson',
        'model_path': '/path/to/expert_avatar.imx'
    }
]

conversation_script = [
    {'avatar': 'host', 'text': "Welcome to today's expert session!", 'pause': 2},
    {'avatar': 'expert', 'text': "Thank you Sarah. I'm excited to share some insights.", 'pause': 2},
    {'avatar': 'host', 'text': "Let's start with your latest research findings.", 'pause': 1}
]

async def run_conference():
    conference = MultiAvatarConference()
    await conference.initialize_avatars(avatar_configs)
    await conference.connect_to_room(room_url, room_token)
    await conference.orchestrate_conversation(conversation_script)

if __name__ == "__main__":
    asyncio.run(run_conference())
```

## Production Deployment

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV LIVEKIT_LOG_LEVEL=info

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run agent
CMD ["python", "-m", "livekit.agents", "start", "avatar_agent.py"]
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bithuman-livekit-agent
  labels:
    app: bithuman-avatar
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bithuman-avatar
  template:
    metadata:
      labels:
        app: bithuman-avatar
    spec:
      containers:
      - name: avatar-agent
        image: your-registry/bithuman-livekit:latest
        ports:
        - containerPort: 8080
        env:
        - name: LIVEKIT_URL
          valueFrom:
            secretKeyRef:
              name: livekit-secrets
              key: url
        - name: LIVEKIT_API_KEY
          valueFrom:
            secretKeyRef:
              name: livekit-secrets
              key: api-key
        - name: LIVEKIT_API_SECRET
          valueFrom:
            secretKeyRef:
              name: livekit-secrets
              key: api-secret
        - name: BITHUMAN_API_SECRET
          valueFrom:
            secretKeyRef:
              name: bithuman-secrets
              key: api-secret
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: bithuman-livekit-service
spec:
  selector:
    app: bithuman-avatar
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

## Client-Side Integration

### React Web Client

```tsx
// AvatarRoom.tsx
import React, { useEffect, useRef, useState } from 'react';
import { 
  Room, 
  RoomEvent, 
  Track,
  RemoteTrack,
  RemoteVideoTrack,
  RemoteAudioTrack
} from 'livekit-client';

interface AvatarRoomProps {
  roomUrl: string;
  token: string;
  onConnected?: () => void;
  onDisconnected?: () => void;
}

export const AvatarRoom: React.FC<AvatarRoomProps> = ({
  roomUrl,
  token,
  onConnected,
  onDisconnected
}) => {
  const [room, setRoom] = useState<Room | null>(null);
  const [avatarTracks, setAvatarTracks] = useState<Map<string, RemoteVideoTrack>>(new Map());
  const videoRefs = useRef<Map<string, HTMLVideoElement>>(new Map());

  useEffect(() => {
    const connectToRoom = async () => {
      const newRoom = new Room({
        adaptiveStream: true,
        dynacast: true,
        publishDefaults: {
          simulcast: false, // Disable for avatar streams
          videoCodec: 'h264' // Better for avatar content
        }
      });

      // Event handlers
      newRoom.on(RoomEvent.Connected, () => {
        console.log('Connected to LiveKit room');
        onConnected?.();
      });

      newRoom.on(RoomEvent.Disconnected, (reason) => {
        console.log('Disconnected from room:', reason);
        onDisconnected?.();
      });

      newRoom.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        if (track.kind === Track.Kind.Video && track.source === Track.Source.Camera) {
          const videoTrack = track as RemoteVideoTrack;
          
          // Check if this is an avatar track
          if (publication.name?.startsWith('avatar_')) {
            setAvatarTracks(prev => new Map(prev.set(participant.identity, videoTrack)));
            
            // Attach to video element
            const videoElement = videoRefs.current.get(participant.identity);
            if (videoElement) {
              videoTrack.attach(videoElement);
            }
          }
        }
      });

      newRoom.on(RoomEvent.TrackUnsubscribed, (track, publication, participant) => {
        if (track.kind === Track.Kind.Video) {
          setAvatarTracks(prev => {
            const newMap = new Map(prev);
            newMap.delete(participant.identity);
            return newMap;
          });
        }
      });

      // Connect to room
      try {
        await newRoom.connect(roomUrl, token);
        setRoom(newRoom);
      } catch (error) {
        console.error('Failed to connect to room:', error);
      }
    };

    connectToRoom();

    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [roomUrl, token]);

  const renderAvatarVideo = (participantId: string) => (
    <div key={participantId} className="avatar-container">
      <video
        ref={(el) => {
          if (el) {
            videoRefs.current.set(participantId, el);
            // Attach track if already available
            const track = avatarTracks.get(participantId);
            if (track) {
              track.attach(el);
            }
          }
        }}
        autoPlay
        playsInline
        muted={false}
        className="avatar-video"
      />
      <div className="participant-name">{participantId}</div>
    </div>
  );

  return (
    <div className="avatar-room">
      <h2>Avatar Conference</h2>
      <div className="avatars-grid">
        {Array.from(avatarTracks.keys()).map(renderAvatarVideo)}
      </div>
      
      {room && (
        <div className="room-controls">
          <button onClick={() => room.disconnect()}>
            Leave Room
          </button>
        </div>
      )}
    </div>
  );
};
```

### Mobile Client (React Native)

```tsx
// AvatarRoomMobile.tsx
import React, { useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { 
  Room, 
  VideoView,
  RoomEvent,
  Track
} from '@livekit/react-native';

interface AvatarRoomMobileProps {
  roomUrl: string;
  token: string;
}

export const AvatarRoomMobile: React.FC<AvatarRoomMobileProps> = ({
  roomUrl,
  token
}) => {
  const [room, setRoom] = useState<Room | null>(null);
  const [avatarParticipants, setAvatarParticipants] = useState<string[]>([]);

  useEffect(() => {
    const connectToRoom = async () => {
      const newRoom = new Room();

      newRoom.on(RoomEvent.Connected, () => {
        console.log('Connected to avatar room');
      });

      newRoom.on(RoomEvent.ParticipantConnected, (participant) => {
        // Check if this is an avatar participant
        if (participant.identity.startsWith('avatar-')) {
          setAvatarParticipants(prev => [...prev, participant.identity]);
        }
      });

      newRoom.on(RoomEvent.ParticipantDisconnected, (participant) => {
        setAvatarParticipants(prev => 
          prev.filter(id => id !== participant.identity)
        );
      });

      try {
        await newRoom.connect(roomUrl, token);
        setRoom(newRoom);
      } catch (error) {
        console.error('Connection failed:', error);
      }
    };

    connectToRoom();

    return () => {
      room?.disconnect();
    };
  }, [roomUrl, token]);

  return (
    <View style={styles.container}>
      {room && avatarParticipants.map(participantId => {
        const participant = room.participants.get(participantId);
        const videoTrack = participant?.videoTracks.values().next().value?.track;
        
        return videoTrack ? (
          <VideoView
            key={participantId}
            style={styles.avatarVideo}
            track={videoTrack}
            objectFit="cover"
          />
        ) : null;
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  avatarVideo: {
    flex: 1,
    margin: 4,
    borderRadius: 8,
  },
});
```

## Performance Optimization

### Bandwidth Optimization

```python
# bandwidth_optimizer.py
from livekit import VideoQuality, VideoCodec
from bithuman.livekit import BitHumanVideoTrack

class BandwidthOptimizer:
    def __init__(self):
        self.quality_presets = {
            'mobile': {
                'width': 480,
                'height': 480,
                'fps': 15,
                'bitrate': 500_000,  # 500 kbps
                'codec': VideoCodec.H264
            },
            'desktop': {
                'width': 720,
                'height': 720, 
                'fps': 25,
                'bitrate': 1_500_000,  # 1.5 Mbps
                'codec': VideoCodec.H264
            },
            'high_quality': {
                'width': 1080,
                'height': 1080,
                'fps': 30,
                'bitrate': 3_000_000,  # 3 Mbps
                'codec': VideoCodec.H264
            }
        }
    
    def create_optimized_track(self, quality_preset: str, runtime):
        """Create video track optimized for specific quality"""
        config = self.quality_presets[quality_preset]
        
        return BitHumanVideoTrack(
            runtime,
            width=config['width'],
            height=config['height'],
            fps=config['fps'],
            bitrate=config['bitrate'],
            codec=config['codec']
        )
    
    async def adaptive_quality(self, track, room):
        """Implement adaptive quality based on network conditions"""
        while True:
            # Monitor connection quality
            stats = await room.get_stats()
            
            # Adjust quality based on packet loss and bandwidth
            if stats.packet_loss > 0.05:  # 5% packet loss
                await self.reduce_quality(track)
            elif stats.available_bandwidth > 2_000_000:  # 2 Mbps available
                await self.increase_quality(track)
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    async def reduce_quality(self, track):
        """Reduce video quality to improve connection"""
        current_bitrate = await track.get_bitrate()
        new_bitrate = int(current_bitrate * 0.8)  # Reduce by 20%
        await track.set_bitrate(new_bitrate)
    
    async def increase_quality(self, track):
        """Increase video quality when connection allows"""
        current_bitrate = await track.get_bitrate()
        new_bitrate = int(current_bitrate * 1.2)  # Increase by 20%
        await track.set_bitrate(min(new_bitrate, 3_000_000))  # Cap at 3 Mbps
```

### Latency Reduction

```python
# latency_reducer.py
import asyncio
from bithuman.runtime import AsyncBithuman
from bithuman.livekit import BitHumanVideoTrack

class LatencyReducer:
    def __init__(self):
        self.frame_prediction_enabled = True
        self.adaptive_fps_enabled = True
        
    async def create_low_latency_track(self, runtime):
        """Create track optimized for minimum latency"""
        return BitHumanVideoTrack(
            runtime,
            # Latency optimizations
            buffer_size=1,           # Minimal buffering
            prediction_frames=3,     # Predict next frames
            adaptive_fps=True,       # Adjust FPS based on content
            low_latency_mode=True,   # Enable all low-latency optimizations
            frame_skipping=True,     # Skip frames if falling behind
            
            # Quality settings for speed
            width=512,
            height=512,
            fps=25,
            bitrate=1_000_000
        )
    
    async def monitor_latency(self, track, room):
        """Monitor and optimize latency in real-time"""
        while True:
            # Measure current latency
            latency = await self.measure_end_to_end_latency(room)
            
            if latency > 200:  # 200ms threshold
                await self.optimize_for_latency(track)
            
            await asyncio.sleep(1)
    
    async def measure_end_to_end_latency(self, room):
        """Measure end-to-end latency"""
        # Implementation depends on your monitoring setup
        # Could use WebRTC stats or custom timing
        return 150  # Placeholder
    
    async def optimize_for_latency(self, track):
        """Apply latency optimizations"""
        # Reduce frame prediction if latency is high
        await track.set_prediction_frames(1)
        
        # Enable aggressive frame skipping
        await track.enable_frame_skipping(True)
        
        # Reduce quality slightly for speed
        current_bitrate = await track.get_bitrate()
        await track.set_bitrate(int(current_bitrate * 0.9))
```

## Monitoring and Analytics

### Performance Metrics

```python
# livekit_metrics.py
import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List
from livekit import Room, RoomEvent

@dataclass
class LiveKitMetrics:
    room_id: str
    session_start: float = field(default_factory=time.time)
    participants_joined: int = 0
    participants_left: int = 0
    total_frames_sent: int = 0
    total_audio_sent: int = 0
    avg_latency_ms: float = 0.0
    packet_loss_rate: float = 0.0
    bandwidth_usage: Dict[str, float] = field(default_factory=dict)
    error_count: int = 0

class LiveKitMonitor:
    def __init__(self, room: Room):
        self.room = room
        self.metrics = LiveKitMetrics(room_id=room.name or "unknown")
        self.latency_samples: List[float] = []
        
    def start_monitoring(self):
        """Start monitoring LiveKit metrics"""
        # Set up event handlers
        self.room.on(RoomEvent.ParticipantConnected, self._on_participant_joined)
        self.room.on(RoomEvent.ParticipantDisconnected, self._on_participant_left)
        self.room.on(RoomEvent.TrackPublished, self._on_track_published)
        self.room.on(RoomEvent.ConnectionQualityChanged, self._on_quality_changed)
        
        # Start periodic monitoring
        asyncio.create_task(self._monitor_loop())
    
    def _on_participant_joined(self, participant):
        """Handle participant joining"""
        self.metrics.participants_joined += 1
        print(f"Participant joined: {participant.identity}")
    
    def _on_participant_left(self, participant):
        """Handle participant leaving"""
        self.metrics.participants_left += 1
        print(f"Participant left: {participant.identity}")
    
    def _on_track_published(self, publication, participant):
        """Handle track publication"""
        if publication.kind == "video":
            self.metrics.total_frames_sent += 1
        elif publication.kind == "audio":
            self.metrics.total_audio_sent += 1
    
    def _on_quality_changed(self, quality, participant):
        """Handle connection quality changes"""
        print(f"Quality changed for {participant.identity}: {quality}")
    
    async def _monitor_loop(self):
        """Periodic monitoring loop"""
        while True:
            try:
                # Collect WebRTC stats
                stats = await self.room.get_stats()
                
                if stats:
                    # Update latency
                    if stats.round_trip_time:
                        self.latency_samples.append(stats.round_trip_time * 1000)  # Convert to ms
                        
                        # Keep only last 100 samples
                        if len(self.latency_samples) > 100:
                            self.latency_samples.pop(0)
                        
                        self.metrics.avg_latency_ms = sum(self.latency_samples) / len(self.latency_samples)
                    
                    # Update packet loss
                    if stats.packets_lost and stats.packets_sent:
                        self.metrics.packet_loss_rate = stats.packets_lost / stats.packets_sent
                    
                    # Update bandwidth
                    if stats.bytes_sent and stats.bytes_received:
                        self.metrics.bandwidth_usage = {
                            'sent_mbps': (stats.bytes_sent * 8) / (1024 * 1024),
                            'received_mbps': (stats.bytes_received * 8) / (1024 * 1024)
                        }
                
                # Log metrics every minute
                if int(time.time()) % 60 == 0:
                    self._log_metrics()
                
            except Exception as e:
                self.metrics.error_count += 1
                print(f"Monitoring error: {e}")
            
            await asyncio.sleep(5)  # Monitor every 5 seconds
    
    def _log_metrics(self):
        """Log current metrics"""
        session_duration = (time.time() - self.metrics.session_start) / 60  # minutes
        
        print(f"""
        LiveKit Session Metrics:
        - Room: {self.metrics.room_id}
        - Duration: {session_duration:.1f} minutes
        - Participants: {self.metrics.participants_joined} joined, {self.metrics.participants_left} left
        - Frames sent: {self.metrics.total_frames_sent}
        - Average latency: {self.metrics.avg_latency_ms:.1f}ms
        - Packet loss: {self.metrics.packet_loss_rate:.2%}
        - Bandwidth: {self.metrics.bandwidth_usage}
        - Errors: {self.metrics.error_count}
        """)
    
    def get_session_summary(self):
        """Get complete session summary"""
        session_duration = (time.time() - self.metrics.session_start) / 60
        
        return {
            'room_id': self.metrics.room_id,
            'session_duration_minutes': session_duration,
            'participants_joined': self.metrics.participants_joined,
            'participants_left': self.metrics.participants_left,
            'total_frames_sent': self.metrics.total_frames_sent,
            'avg_latency_ms': self.metrics.avg_latency_ms,
            'packet_loss_rate': self.metrics.packet_loss_rate,
            'bandwidth_usage': self.metrics.bandwidth_usage,
            'error_count': self.metrics.error_count
        }
```

## Troubleshooting

### Common Issues

#### Connection Problems
```python
# Debug connection issues
async def debug_connection(room_url, token):
    try:
        room = Room()
        await room.connect(room_url, token)
        print("✅ Connection successful")
        await room.disconnect()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        
        # Check common issues
        if "authentication" in str(e).lower():
            print("Check your LiveKit API credentials")
        elif "network" in str(e).lower():
            print("Check network connectivity and firewall settings")
        elif "room" in str(e).lower():
            print("Check room name and permissions")
```

#### Audio/Video Sync Issues
```python
# Fix sync issues
async def fix_sync_issues(runtime, video_track, audio_track):
    # Ensure consistent timing
    await video_track.set_sync_mode('audio_master')
    
    # Adjust buffer sizes if needed
    await video_track.set_buffer_size(1)  # Minimal buffering
    await audio_track.set_buffer_size(1)
    
    # Monitor sync offset
    async def monitor_sync():
        while True:
            offset = await video_track.get_audio_sync_offset()
            if abs(offset) > 40:  # 40ms threshold
                await video_track.adjust_sync_offset(-offset)
            await asyncio.sleep(1)
    
    asyncio.create_task(monitor_sync())
```

#### Performance Issues
```python
# Diagnose performance problems
async def diagnose_performance(room):
    stats = await room.get_stats()
    
    if stats.frame_rate < 20:
        print("⚠️ Low frame rate - consider reducing quality")
    
    if stats.packet_loss > 0.02:
        print("⚠️ High packet loss - check network conditions")
    
    if stats.round_trip_time > 0.2:
        print("⚠️ High latency - consider closer server region")
```

## Best Practices

### 1. Resource Management
- Always clean up bitHuman runtimes and LiveKit connections
- Use connection pooling for multiple sessions
- Monitor memory usage with multiple avatars

### 2. Quality Configuration
- Choose appropriate video resolution for use case
- Implement adaptive bitrate based on network conditions
- Use efficient codecs (H.264 for compatibility, VP9 for quality)

### 3. Error Handling
- Implement reconnection logic for network issues
- Handle participant disconnections gracefully
- Monitor and alert on high error rates

### 4. Security
- Validate JWT tokens properly
- Use secure WebSocket connections (WSS)
- Implement rate limiting for API endpoints

## Next Steps

To enhance your LiveKit integration:

1. **[Explore Other Integrations](fastrtc.md)** - Compare with FastRTC
2. **[Review Examples](../examples/livekit-agent.md)** - See complete implementations
3. **[Optimize Performance](../build/gpu-cloud.md)** - Use GPU cloud for better performance
4. **[Monitor Production](../build/self-hosted.md)** - Set up comprehensive monitoring

## Resources

- **[LiveKit Documentation](https://docs.livekit.io/)** - Complete LiveKit guides
- **[LiveKit Agents](https://github.com/livekit/agents)** - AI agent framework
- **[WebRTC Best Practices](https://webrtc.org/)** - WebRTC optimization
- **[Community Examples](https://console.bithuman.io/#community)** - See other integrations

LiveKit integration opens up endless possibilities for real-time avatar experiences. Start building amazing interactive applications today! 