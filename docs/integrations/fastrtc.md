# FastRTC Integration

Integrate bitHuman avatars with FastRTC for simplified WebRTC implementation. FastRTC provides an easier alternative to LiveKit with streamlined setup and deployment.

## Overview

FastRTC + bitHuman offers:
- **Simplified WebRTC** - Easy peer-to-peer connections
- **Lightweight integration** - Minimal overhead and dependencies
- **Direct streaming** - Avatar video/audio directly to browsers
- **Self-contained solution** - No external infrastructure required
- **Cost-effective** - Reduced complexity and hosting costs

## Prerequisites

- ✅ [bitHuman SDK installed](../getting-started/installation.md)
- ✅ [Validated API credentials](../getting-started/validate-api.md)
- ✅ Python 3.10+ environment
- ✅ Modern web browser with WebRTC support

## Installation

```bash
# Install FastRTC and bitHuman integration
pip install fastrtc bithuman[fastrtc]

# For development dependencies
pip install fastrtc[dev] uvicorn websockets
```

## Basic Implementation

### Simple Avatar Streamer

```python
# fastrtc_avatar.py
import asyncio
import logging
from fastrtc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from fastrtc.contrib.media import MediaPlayer, MediaRecorder
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk
from bithuman.fastrtc import BitHumanVideoTrack, BitHumanAudioTrack

logger = logging.getLogger(__name__)

class AvatarStreamer:
    def __init__(self):
        self.bithuman_runtime = None
        self.peer_connections = set()
        self.video_track = None
        self.audio_track = None
        
    async def initialize(self):
        """Initialize bitHuman runtime and media tracks"""
        # Initialize bitHuman
        self.bithuman_runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        
        # Create custom media tracks
        self.video_track = BitHumanVideoTrack(self.bithuman_runtime)
        self.audio_track = BitHumanAudioTrack()
        
        logger.info("Avatar streamer initialized")
    
    async def create_peer_connection(self):
        """Create new WebRTC peer connection"""
        pc = RTCPeerConnection()
        self.peer_connections.add(pc)
        
        # Add avatar tracks
        pc.addTrack(self.video_track)
        pc.addTrack(self.audio_track)
        
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f"Connection state: {pc.connectionState}")
            if pc.connectionState == "failed":
                await pc.close()
                self.peer_connections.discard(pc)
        
        @pc.on("datachannel")
        def on_datachannel(channel):
            @channel.on("message")
            def on_message(message):
                # Handle incoming messages (e.g., chat, commands)
                asyncio.create_task(self.handle_message(message))
        
        return pc
    
    async def handle_offer(self, offer_sdp: str):
        """Handle WebRTC offer from client"""
        pc = await self.create_peer_connection()
        
        # Set remote description
        await pc.setRemoteDescription(RTCSessionDescription(
            sdp=offer_sdp,
            type="offer"
        ))
        
        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        return answer.sdp
    
    async def handle_message(self, message: str):
        """Handle messages from client"""
        try:
            import json
            data = json.loads(message)
            
            if data.get('type') == 'speak':
                text = data.get('text', '')
                await self.make_avatar_speak(text)
            elif data.get('type') == 'audio'):
                audio_data = data.get('data', '')
                await self.process_audio_input(audio_data)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def make_avatar_speak(self, text: str):
        """Make avatar speak given text"""
        # Convert text to audio using TTS
        audio_chunk = await self.text_to_speech(text)
        
        # Process through bitHuman
        async for video_frame in self.bithuman_runtime.process_audio_chunk(audio_chunk):
            # Send frames to all connected peers
            await self.video_track.send_frame(video_frame)
            await self.audio_track.send_audio(video_frame.audio_chunk)
    
    async def process_audio_input(self, audio_data: str):
        """Process audio input from user"""
        try:
            # Convert base64 audio to AudioChunk
            import base64
            audio_bytes = base64.b64decode(audio_data)
            audio_chunk = AudioChunk.from_bytes(audio_bytes, 16000)
            
            # Process through bitHuman
            async for video_frame in self.bithuman_runtime.process_audio_chunk(audio_chunk):
                await self.video_track.send_frame(video_frame)
                await self.audio_track.send_audio(video_frame.audio_chunk)
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
    
    async def text_to_speech(self, text: str) -> AudioChunk:
        """Convert text to speech (implement with your TTS service)"""
        # Placeholder - integrate with your preferred TTS
        # Examples: OpenAI TTS, Azure Speech, Google TTS
        pass
    
    async def cleanup(self):
        """Clean up resources"""
        for pc in self.peer_connections:
            await pc.close()
        self.peer_connections.clear()
        
        if self.bithuman_runtime:
            await self.bithuman_runtime.close()

# WebRTC signaling server
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import json

app = FastAPI()
avatar_streamer = AvatarStreamer()

@app.on_event("startup")
async def startup():
    await avatar_streamer.initialize()

@app.on_event("shutdown") 
async def shutdown():
    await avatar_streamer.cleanup()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'offer':
                answer_sdp = await avatar_streamer.handle_offer(message['sdp'])
                await websocket.send_text(json.dumps({
                    'type': 'answer',
                    'sdp': answer_sdp
                }))
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Client-Side Implementation

```html
<!-- static/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>bitHuman Avatar with FastRTC</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        #avatar-video {
            width: 100%;
            max-width: 512px;
            height: 512px;
            background: #000;
            border-radius: 10px;
            margin: 20px auto;
            display: block;
        }
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        #chat-input {
            width: 70%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>bitHuman Avatar Demo</h1>
        
        <video id="avatar-video" autoplay playsinline muted="false"></video>
        
        <div class="controls">
            <button id="connect-btn">Connect</button>
            <button id="disconnect-btn" disabled>Disconnect</button>
        </div>
        
        <div class="controls">
            <input type="text" id="chat-input" placeholder="Type something for the avatar to say...">
            <button id="speak-btn" disabled>Make Avatar Speak</button>
        </div>
        
        <div class="controls">
            <button id="mic-btn" disabled>🎤 Talk to Avatar</button>
        </div>
    </div>

    <script>
        class AvatarClient {
            constructor() {
                this.pc = null;
                this.ws = null;
                this.dataChannel = null;
                this.isRecording = false;
                this.mediaRecorder = null;
            }

            async connect() {
                try {
                    // Create WebSocket connection
                    this.ws = new WebSocket(`ws://${window.location.host}/ws`);
                    
                    this.ws.onopen = () => {
                        console.log('WebSocket connected');
                        this.initWebRTC();
                    };
                    
                    this.ws.onmessage = (event) => {
                        const message = JSON.parse(event.data);
                        this.handleSignalingMessage(message);
                    };
                    
                } catch (error) {
                    console.error('Connection failed:', error);
                }
            }

            async initWebRTC() {
                // Create peer connection
                this.pc = new RTCPeerConnection({
                    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
                });

                // Handle incoming streams
                this.pc.ontrack = (event) => {
                    const video = document.getElementById('avatar-video');
                    if (event.streams && event.streams[0]) {
                        video.srcObject = event.streams[0];
                    }
                };

                // Create data channel for messaging
                this.dataChannel = this.pc.createDataChannel('messages');
                this.dataChannel.onopen = () => {
                    console.log('Data channel opened');
                    this.updateUI(true);
                };

                // Create offer
                const offer = await this.pc.createOffer();
                await this.pc.setLocalDescription(offer);

                // Send offer via WebSocket
                this.ws.send(JSON.stringify({
                    type: 'offer',
                    sdp: offer.sdp
                }));
            }

            async handleSignalingMessage(message) {
                if (message.type === 'answer') {
                    await this.pc.setRemoteDescription(new RTCSessionDescription({
                        type: 'answer',
                        sdp: message.sdp
                    }));
                }
            }

            async makeAvatarSpeak(text) {
                if (this.dataChannel && this.dataChannel.readyState === 'open') {
                    this.dataChannel.send(JSON.stringify({
                        type: 'speak',
                        text: text
                    }));
                }
            }

            async startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    this.mediaRecorder = new MediaRecorder(stream);
                    
                    const audioChunks = [];
                    this.mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    this.mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks);
                        const arrayBuffer = await audioBlob.arrayBuffer();
                        const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
                        
                        if (this.dataChannel && this.dataChannel.readyState === 'open') {
                            this.dataChannel.send(JSON.stringify({
                                type: 'audio',
                                data: base64Audio
                            }));
                        }
                    };
                    
                    this.mediaRecorder.start();
                    this.isRecording = true;
                    this.updateMicButton();
                    
                } catch (error) {
                    console.error('Failed to access microphone:', error);
                }
            }

            stopRecording() {
                if (this.mediaRecorder && this.isRecording) {
                    this.mediaRecorder.stop();
                    this.isRecording = false;
                    this.updateMicButton();
                }
            }

            disconnect() {
                if (this.pc) {
                    this.pc.close();
                    this.pc = null;
                }
                if (this.ws) {
                    this.ws.close();
                    this.ws = null;
                }
                this.updateUI(false);
            }

            updateUI(connected) {
                document.getElementById('connect-btn').disabled = connected;
                document.getElementById('disconnect-btn').disabled = !connected;
                document.getElementById('speak-btn').disabled = !connected;
                document.getElementById('mic-btn').disabled = !connected;
            }

            updateMicButton() {
                const micBtn = document.getElementById('mic-btn');
                micBtn.textContent = this.isRecording ? '🔴 Stop Recording' : '🎤 Talk to Avatar';
            }
        }

        // Initialize client
        const client = new AvatarClient();

        // Event listeners
        document.getElementById('connect-btn').onclick = () => client.connect();
        document.getElementById('disconnect-btn').onclick = () => client.disconnect();
        
        document.getElementById('speak-btn').onclick = () => {
            const text = document.getElementById('chat-input').value;
            if (text.trim()) {
                client.makeAvatarSpeak(text);
                document.getElementById('chat-input').value = '';
            }
        };

        document.getElementById('mic-btn').onclick = () => {
            if (client.isRecording) {
                client.stopRecording();
            } else {
                client.startRecording();
            }
        };

        // Enter key to speak
        document.getElementById('chat-input').onkeypress = (e) => {
            if (e.key === 'Enter') {
                document.getElementById('speak-btn').click();
            }
        };
    </script>
</body>
</html>
```

## Advanced Features

### Multi-User Avatar Chat

```python
# multi_user_chat.py
import asyncio
import json
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastrtc import RTCPeerConnection
from bithuman.runtime import AsyncBithuman
from bithuman.fastrtc import BitHumanVideoTrack

class MultiUserAvatarChat:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.peer_connections: Dict[str, RTCPeerConnection] = {}
        self.avatar_runtime = None
        self.video_track = None
        
    async def initialize(self):
        """Initialize shared avatar runtime"""
        self.avatar_runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        self.video_track = BitHumanVideoTrack(self.avatar_runtime)
    
    async def add_user(self, user_id: str, websocket: WebSocket):
        """Add new user to chat"""
        self.connections[user_id] = websocket
        
        # Create peer connection for this user
        pc = RTCPeerConnection()
        pc.addTrack(self.video_track)
        self.peer_connections[user_id] = pc
        
        # Notify other users
        await self.broadcast_message({
            'type': 'user_joined',
            'user_id': user_id
        }, exclude=user_id)
    
    async def remove_user(self, user_id: str):
        """Remove user from chat"""
        if user_id in self.connections:
            del self.connections[user_id]
        
        if user_id in self.peer_connections:
            await self.peer_connections[user_id].close()
            del self.peer_connections[user_id]
        
        # Notify other users
        await self.broadcast_message({
            'type': 'user_left',
            'user_id': user_id
        }, exclude=user_id)
    
    async def handle_message(self, user_id: str, message: dict):
        """Handle message from user"""
        if message['type'] == 'chat':
            # Make avatar speak the message
            text = f"{user_id} says: {message['text']}"
            await self.make_avatar_speak(text)
            
            # Broadcast to all users
            await self.broadcast_message({
                'type': 'chat',
                'user_id': user_id,
                'text': message['text']
            })
        
        elif message['type'] == 'offer':
            # Handle WebRTC offer
            pc = self.peer_connections.get(user_id)
            if pc:
                answer_sdp = await self.handle_webrtc_offer(pc, message['sdp'])
                await self.send_to_user(user_id, {
                    'type': 'answer',
                    'sdp': answer_sdp
                })
    
    async def make_avatar_speak(self, text: str):
        """Make avatar speak for all users"""
        # Convert text to audio (implement TTS)
        audio_chunk = await self.text_to_speech(text)
        
        # Process through bitHuman
        async for video_frame in self.avatar_runtime.process_audio_chunk(audio_chunk):
            await self.video_track.send_frame(video_frame)
    
    async def broadcast_message(self, message: dict, exclude: str = None):
        """Broadcast message to all connected users"""
        for user_id, websocket in self.connections.items():
            if user_id != exclude:
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    # Connection closed, remove user
                    asyncio.create_task(self.remove_user(user_id))
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user"""
        websocket = self.connections.get(user_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                await self.remove_user(user_id)

# FastAPI integration
app = FastAPI()
chat_room = MultiUserAvatarChat()

@app.on_event("startup")
async def startup():
    await chat_room.initialize()

@app.websocket("/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    await chat_room.add_user(user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await chat_room.handle_message(user_id, message)
            
    except WebSocketDisconnect:
        await chat_room.remove_user(user_id)
```

### Screen Sharing Integration

```python
# screen_sharing.py
from fastrtc import RTCPeerConnection, MediaStreamTrack
from fastrtc.contrib.media import MediaPlayer
from bithuman.fastrtc import BitHumanVideoTrack

class ScreenSharingAvatar:
    def __init__(self):
        self.avatar_runtime = None
        self.screen_track = None
        self.avatar_track = None
        self.composite_track = None
        
    async def initialize(self):
        """Initialize avatar and screen sharing"""
        self.avatar_runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        
        self.avatar_track = BitHumanVideoTrack(self.avatar_runtime)
        self.composite_track = CompositeVideoTrack()
    
    async def start_screen_sharing(self, screen_source):
        """Start sharing screen with avatar overlay"""
        # Create screen capture track
        player = MediaPlayer(screen_source)
        self.screen_track = player.video
        
        # Composite avatar over screen
        await self.composite_track.add_background(self.screen_track)
        await self.composite_track.add_overlay(self.avatar_track, position='bottom-right')
    
    def add_to_peer_connection(self, pc: RTCPeerConnection):
        """Add composite track to peer connection"""
        pc.addTrack(self.composite_track)

class CompositeVideoTrack(MediaStreamTrack):
    """Composite video track that overlays avatar on screen"""
    
    def __init__(self):
        super().__init__()
        self.kind = "video"
        self.background_track = None
        self.overlay_track = None
        self.overlay_position = 'bottom-right'
    
    async def add_background(self, track):
        self.background_track = track
    
    async def add_overlay(self, track, position='bottom-right'):
        self.overlay_track = track
        self.overlay_position = position
    
    async def recv(self):
        """Receive and composite video frames"""
        if not self.background_track or not self.overlay_track:
            return
        
        # Get frames from both tracks
        bg_frame = await self.background_track.recv()
        overlay_frame = await self.overlay_track.recv()
        
        # Composite frames (implementation depends on your video processing library)
        composite_frame = await self.composite_frames(bg_frame, overlay_frame)
        
        return composite_frame
    
    async def composite_frames(self, background, overlay):
        """Composite overlay frame onto background"""
        # Implement frame composition logic
        # This would typically use OpenCV or similar library
        pass
```

## Production Deployment

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Load Balancing

```python
# load_balancer.py
import asyncio
import random
from typing import List, Dict
from fastrtc import RTCPeerConnection

class FastRTCLoadBalancer:
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.server_loads: Dict[str, int] = {server: 0 for server in servers}
        self.max_connections_per_server = 100
    
    def get_least_loaded_server(self) -> str:
        """Get server with lowest current load"""
        available_servers = [
            server for server, load in self.server_loads.items()
            if load < self.max_connections_per_server
        ]
        
        if not available_servers:
            raise Exception("No available servers")
        
        return min(available_servers, key=lambda s: self.server_loads[s])
    
    async def create_connection(self, user_id: str) -> tuple[str, RTCPeerConnection]:
        """Create connection on least loaded server"""
        server = self.get_least_loaded_server()
        
        # Create peer connection to selected server
        pc = RTCPeerConnection()
        
        # Track connection
        self.server_loads[server] += 1
        
        @pc.on("connectionstatechange")
        async def on_state_change():
            if pc.connectionState in ["closed", "failed"]:
                self.server_loads[server] -= 1
        
        return server, pc
    
    def get_server_stats(self) -> Dict[str, int]:
        """Get current server load statistics"""
        return self.server_loads.copy()
```

## Performance Optimization

### Bandwidth Management

```python
# bandwidth_manager.py
import asyncio
from fastrtc import RTCPeerConnection

class BandwidthManager:
    def __init__(self):
        self.quality_presets = {
            'low': {'width': 320, 'height': 320, 'fps': 15, 'bitrate': 300_000},
            'medium': {'width': 480, 'height': 480, 'fps': 20, 'bitrate': 800_000},
            'high': {'width': 720, 'height': 720, 'fps': 25, 'bitrate': 1_500_000}
        }
        
    async def adapt_quality(self, pc: RTCPeerConnection, track):
        """Adapt video quality based on connection stats"""
        while pc.connectionState == "connected":
            try:
                # Get WebRTC statistics
                stats = await pc.getStats()
                
                # Analyze connection quality
                packet_loss = self.calculate_packet_loss(stats)
                available_bandwidth = self.estimate_bandwidth(stats)
                
                # Adjust quality based on metrics
                if packet_loss > 0.05:  # 5% packet loss
                    await self.reduce_quality(track)
                elif available_bandwidth > 2_000_000:  # 2 Mbps available
                    await self.increase_quality(track)
                
            except Exception as e:
                print(f"Error adapting quality: {e}")
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    def calculate_packet_loss(self, stats) -> float:
        """Calculate packet loss rate from WebRTC stats"""
        # Implementation depends on stats format
        return 0.0
    
    def estimate_bandwidth(self, stats) -> int:
        """Estimate available bandwidth from WebRTC stats"""
        # Implementation depends on stats format
        return 1_000_000
    
    async def reduce_quality(self, track):
        """Reduce video quality"""
        current_bitrate = getattr(track, 'bitrate', 800_000)
        new_bitrate = int(current_bitrate * 0.8)
        await track.set_bitrate(new_bitrate)
    
    async def increase_quality(self, track):
        """Increase video quality"""
        current_bitrate = getattr(track, 'bitrate', 800_000)
        new_bitrate = int(current_bitrate * 1.2)
        await track.set_bitrate(min(new_bitrate, 2_000_000))
```

## Monitoring and Analytics

```python
# fastrtc_monitor.py
import time
import asyncio
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ConnectionMetrics:
    user_id: str
    connection_time: float
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_lost: int = 0
    avg_latency_ms: float = 0.0

class FastRTCMonitor:
    def __init__(self):
        self.connections: Dict[str, ConnectionMetrics] = {}
        self.global_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'total_bytes_transferred': 0,
            'avg_session_duration': 0.0
        }
    
    def track_connection(self, user_id: str):
        """Start tracking a new connection"""
        self.connections[user_id] = ConnectionMetrics(
            user_id=user_id,
            connection_time=time.time()
        )
        self.global_stats['total_connections'] += 1
        self.global_stats['active_connections'] += 1
    
    def track_disconnection(self, user_id: str):
        """Track connection ending"""
        if user_id in self.connections:
            metrics = self.connections[user_id]
            session_duration = time.time() - metrics.connection_time
            
            # Update global stats
            self.global_stats['active_connections'] -= 1
            self.global_stats['total_bytes_transferred'] += (
                metrics.bytes_sent + metrics.bytes_received
            )
            
            # Update average session duration
            total_sessions = self.global_stats['total_connections']
            current_avg = self.global_stats['avg_session_duration']
            new_avg = ((current_avg * (total_sessions - 1)) + session_duration) / total_sessions
            self.global_stats['avg_session_duration'] = new_avg
            
            del self.connections[user_id]
    
    async def collect_stats(self, user_id: str, pc):
        """Collect WebRTC statistics"""
        try:
            stats = await pc.getStats()
            metrics = self.connections.get(user_id)
            
            if metrics and stats:
                # Update metrics from WebRTC stats
                metrics.bytes_sent = getattr(stats, 'bytesSent', 0)
                metrics.bytes_received = getattr(stats, 'bytesReceived', 0)
                metrics.packets_lost = getattr(stats, 'packetsLost', 0)
                metrics.avg_latency_ms = getattr(stats, 'roundTripTime', 0) * 1000
                
        except Exception as e:
            print(f"Error collecting stats for {user_id}: {e}")
    
    def get_summary(self) -> dict:
        """Get monitoring summary"""
        return {
            'global_stats': self.global_stats,
            'active_connections': len(self.connections),
            'connection_details': [
                {
                    'user_id': metrics.user_id,
                    'duration_seconds': time.time() - metrics.connection_time,
                    'bytes_transferred': metrics.bytes_sent + metrics.bytes_received,
                    'latency_ms': metrics.avg_latency_ms
                }
                for metrics in self.connections.values()
            ]
        }
```

## Best Practices

### 1. Connection Management
- Implement proper connection cleanup on disconnect
- Use connection pooling for high-traffic scenarios
- Monitor connection states and handle failures gracefully

### 2. Media Quality
- Start with lower quality and adapt based on connection
- Implement frame dropping for poor connections
- Use efficient codecs (H.264, VP8)

### 3. Error Handling
- Implement exponential backoff for reconnections
- Handle ICE connection failures
- Provide fallback mechanisms for unsupported browsers

### 4. Security
- Validate all incoming messages
- Implement rate limiting for WebSocket connections
- Use HTTPS/WSS in production

## Troubleshooting

### Common Issues

#### WebRTC Connection Failures
```python
# Debug connection issues
async def debug_webrtc(pc):
    @pc.on("icegatheringstatechange")
    def on_ice_gathering():
        print(f"ICE gathering state: {pc.iceGatheringState}")
    
    @pc.on("iceconnectionstatechange") 
    def on_ice_connection():
        print(f"ICE connection state: {pc.iceConnectionState}")
        
    @pc.on("connectionstatechange")
    def on_connection():
        print(f"Connection state: {pc.connectionState}")
```

#### Audio/Video Sync Issues
```python
# Fix sync problems
async def fix_av_sync(video_track, audio_track):
    # Ensure consistent timing
    await video_track.sync_with_audio(audio_track)
    
    # Monitor sync offset
    while True:
        offset = await video_track.get_sync_offset()
        if abs(offset) > 40:  # 40ms threshold
            await video_track.adjust_timing(-offset)
        await asyncio.sleep(1)
```

## Next Steps

To enhance your FastRTC integration:

1. **[Compare with LiveKit](livekit.md)** - Understand differences
2. **[Explore Examples](../examples/voice-driven-audio.md)** - See complete implementations  
3. **[Optimize Performance](../build/gpu-cloud.md)** - Use GPU cloud for better performance
4. **[Deploy to Production](../build/self-hosted.md)** - Set up monitoring and scaling

## Resources

- **[FastRTC Documentation](https://github.com/aiortc/aiortc)** - Complete FastRTC guides
- **[WebRTC Standards](https://webrtc.org/)** - WebRTC specifications
- **[MDN WebRTC Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)** - Browser WebRTC APIs
- **[Community Examples](https://console.bithuman.io/#community)** - More integration examples

FastRTC provides a lightweight, flexible approach to WebRTC integration with bitHuman avatars. Perfect for custom applications requiring direct control over the WebRTC pipeline! 