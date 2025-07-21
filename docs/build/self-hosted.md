# Self-hosted Model

Deploy bitHuman SDK on your own infrastructure for maximum control, security, and customization. This guide covers setup, configuration, and optimization for self-hosted deployments.

## Overview

Self-hosted deployment offers:
- **Complete control** over your data and infrastructure
- **Custom configuration** tailored to your needs
- **Enhanced security** with no data leaving your environment
- **Cost optimization** for high-volume applications
- **Low latency** with local processing

## System Requirements

### Minimum Requirements

| Component | Specification | Notes |
|-----------|---------------|-------|
| **CPU** | 8 cores, 3.0 GHz+ | Intel/AMD x86_64 or ARM64 |
| **RAM** | 16 GB | 32 GB recommended for better performance |
| **Storage** | 100 GB SSD | Fast storage for model loading |
| **GPU** | Optional | NVIDIA GPU with 8GB+ VRAM for acceleration |
| **Network** | 1 Gbps | For model downloads and updates |
| **OS** | Linux Ubuntu 20.04+ | CentOS, RHEL also supported |

### Recommended Production Setup

| Component | Specification | Notes |
|-----------|---------------|-------|
| **CPU** | 16+ cores, 3.5 GHz+ | More cores = better concurrent performance |
| **RAM** | 64 GB+ | Enables model caching and multiple instances |
| **Storage** | 500 GB NVMe SSD | Fast model loading and caching |
| **GPU** | NVIDIA RTX 4090 or A100 | Significant performance improvement |
| **Network** | 10 Gbps | For high-throughput applications |
| **OS** | Linux Ubuntu 22.04 LTS | Latest stable with security updates |

## Installation

### 1. System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required dependencies
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    build-essential \
    curl \
    wget \
    git \
    htop \
    nvidia-driver-525  # If using GPU

# Install Docker (optional but recommended)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Environment Setup

```bash
# Create dedicated user for bitHuman
sudo useradd -m -s /bin/bash bithuman
sudo su - bithuman

# Create virtual environment
python3.10 -m venv bithuman-env
source bithuman-env/bin/activate

# Install bitHuman SDK
pip install bithuman[all]

# Verify installation
python -c "import bithuman; print('Installation successful')"
```

### 3. Configuration

#### Environment Variables

```bash
# Create configuration file
cat > ~/.bithuman_config << EOF
# API Configuration
BITHUMAN_API_SECRET=your_api_secret_here
BITHUMAN_LOG_LEVEL=INFO

# Model Configuration
BITHUMAN_MODEL_CACHE_DIR=/opt/bithuman/models
BITHUMAN_MODEL_MEMORY_LIMIT=8GB

# Performance Configuration
BITHUMAN_MAX_CONCURRENT_SESSIONS=10
BITHUMAN_ENABLE_GPU=true
BITHUMAN_GPU_MEMORY_FRACTION=0.8

# Network Configuration
BITHUMAN_BIND_HOST=0.0.0.0
BITHUMAN_BIND_PORT=8080
BITHUMAN_WORKER_PROCESSES=4

# Security Configuration
BITHUMAN_ENABLE_RATE_LIMITING=true
BITHUMAN_MAX_REQUESTS_PER_MINUTE=100
EOF

# Source configuration
source ~/.bithuman_config
```

#### System Service Configuration

```bash
# Create systemd service
sudo tee /etc/systemd/system/bithuman.service << EOF
[Unit]
Description=bitHuman Avatar Service
After=network.target

[Service]
Type=forking
User=bithuman
Group=bithuman
WorkingDirectory=/home/bithuman
Environment=PATH=/home/bithuman/bithuman-env/bin
EnvironmentFile=/home/bithuman/.bithuman_config
ExecStart=/home/bithuman/bithuman-env/bin/python -m bithuman.server
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable bithuman
sudo systemctl start bithuman
```

## Basic Server Implementation

### Python Server Example

```python
# server.py
import asyncio
import os
import logging
from aiohttp import web, WSMsgType
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BitHumanServer:
    def __init__(self):
        self.runtime = None
        self.sessions = {}
        
    async def initialize(self):
        """Initialize the bitHuman runtime"""
        try:
            self.runtime = await AsyncBithuman.create(
                api_secret=os.getenv('BITHUMAN_API_SECRET'),
                model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
            )
            logger.info("bitHuman runtime initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize runtime: {e}")
            raise

    async def handle_websocket(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        session_id = request.headers.get('Session-ID', 'default')
        self.sessions[session_id] = ws
        
        logger.info(f"New WebSocket connection: {session_id}")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.BINARY:
                    await self.process_audio(session_id, msg.data)
                elif msg.type == WSMsgType.TEXT:
                    await self.handle_command(session_id, msg.data)
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    break
        except Exception as e:
            logger.error(f"Error in WebSocket handler: {e}")
        finally:
            self.sessions.pop(session_id, None)
            logger.info(f"WebSocket connection closed: {session_id}")
        
        return ws

    async def process_audio(self, session_id, audio_data):
        """Process audio data and return video frames"""
        try:
            # Create audio chunk
            audio_chunk = AudioChunk.from_bytes(audio_data, 16000)
            
            # Process with bitHuman
            async for video_frame in self.runtime.process_audio_chunk(audio_chunk):
                # Send video frame to client
                response = {
                    'type': 'video_frame',
                    'frame_index': video_frame.frame_index,
                    'message_id': video_frame.message_id,
                    'image_data': video_frame.image.tobytes().hex()
                }
                
                ws = self.sessions.get(session_id)
                if ws:
                    await ws.send_str(json.dumps(response))
                    
        except Exception as e:
            logger.error(f"Error processing audio: {e}")

    async def handle_command(self, session_id, command_data):
        """Handle text commands"""
        try:
            command = json.loads(command_data)
            
            if command['type'] == 'interrupt':
                self.runtime.interrupt()
                logger.info(f"Interrupted session: {session_id}")
                
        except Exception as e:
            logger.error(f"Error handling command: {e}")

    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'sessions': len(self.sessions),
            'runtime': 'active' if self.runtime else 'inactive'
        })

async def create_app():
    """Create and configure the web application"""
    server = BitHumanServer()
    await server.initialize()
    
    app = web.Application()
    app.router.add_get('/ws', server.handle_websocket)
    app.router.add_get('/health', server.health_check)
    
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8080)
```

### Docker Deployment

#### Dockerfile

```dockerfile
FROM nvidia/cuda:11.8-runtime-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    build-essential \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -m -s /bin/bash bithuman
USER bithuman
WORKDIR /home/bithuman

# Create virtual environment
RUN python3.10 -m venv bithuman-env
ENV PATH="/home/bithuman/bithuman-env/bin:$PATH"

# Install bitHuman SDK
RUN pip install --upgrade pip
RUN pip install bithuman[all]

# Copy application code
COPY --chown=bithuman:bithuman server.py .
COPY --chown=bithuman:bithuman requirements.txt .

# Install additional dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start application
CMD ["python", "server.py"]
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  bithuman:
    build: .
    ports:
      - "8080:8080"
    environment:
      - BITHUMAN_API_SECRET=${BITHUMAN_API_SECRET}
      - BITHUMAN_AVATAR_MODEL=/app/models/avatar.imx
    volumes:
      - ./models:/app/models:ro
      - ./logs:/app/logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - bithuman
    restart: unless-stopped
```

## Performance Optimization

### Model Caching

```python
# model_cache.py
import os
import hashlib
from pathlib import Path

class ModelCache:
    def __init__(self, cache_dir="/opt/bithuman/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get_model_hash(self, model_path):
        """Generate hash for model file"""
        with open(model_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    
    def cache_model(self, model_path):
        """Cache model for faster loading"""
        model_hash = self.get_model_hash(model_path)
        cache_path = self.cache_dir / f"{model_hash}.cache"
        
        if not cache_path.exists():
            # Preprocess and cache model
            # Implementation depends on bitHuman SDK caching API
            pass
            
        return cache_path
```

### Load Balancing

```python
# load_balancer.py
import asyncio
import random
from typing import List, Optional

class LoadBalancer:
    def __init__(self, max_instances: int = 4):
        self.instances = []
        self.max_instances = max_instances
        self.current_loads = {}
        
    async def initialize_instances(self):
        """Initialize multiple bitHuman instances"""
        for i in range(self.max_instances):
            instance = await AsyncBithuman.create(
                api_secret=os.getenv('BITHUMAN_API_SECRET'),
                model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
            )
            self.instances.append(instance)
            self.current_loads[i] = 0
    
    def get_least_loaded_instance(self) -> Optional[int]:
        """Get instance with lowest current load"""
        if not self.instances:
            return None
            
        min_load = min(self.current_loads.values())
        candidates = [i for i, load in self.current_loads.items() 
                     if load == min_load]
        return random.choice(candidates)
    
    async def process_request(self, audio_chunk):
        """Process request on least loaded instance"""
        instance_id = self.get_least_loaded_instance()
        if instance_id is None:
            raise RuntimeError("No available instances")
        
        self.current_loads[instance_id] += 1
        try:
            instance = self.instances[instance_id]
            async for frame in instance.process_audio_chunk(audio_chunk):
                yield frame
        finally:
            self.current_loads[instance_id] -= 1
```

### Resource Monitoring

```python
# monitoring.py
import psutil
import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    gpu_memory_used: float
    active_sessions: int
    requests_per_second: float

class ResourceMonitor:
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.metrics_history = []
        self.request_counter = 0
        self.logger = logging.getLogger(__name__)
        
    async def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU metrics (requires nvidia-ml-py)
        gpu_memory = 0.0
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_memory = gpu_info.used / gpu_info.total * 100
        except:
            pass
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            gpu_memory_used=gpu_memory,
            active_sessions=len(self.active_sessions),
            requests_per_second=self.calculate_rps()
        )
    
    def calculate_rps(self) -> float:
        """Calculate requests per second"""
        # Implementation depends on request tracking
        return 0.0
    
    async def monitor_loop(self):
        """Continuous monitoring loop"""
        while True:
            try:
                metrics = await self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last hour of metrics
                if len(self.metrics_history) > 120:
                    self.metrics_history.pop(0)
                
                # Log warnings for high resource usage
                if metrics.cpu_percent > 80:
                    self.logger.warning(f"High CPU usage: {metrics.cpu_percent}%")
                
                if metrics.memory_percent > 85:
                    self.logger.warning(f"High memory usage: {metrics.memory_percent}%")
                    
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
            
            await asyncio.sleep(self.check_interval)
```

## Security Configuration

### SSL/TLS Setup

```bash
# Generate SSL certificates (use Let's Encrypt for production)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Or create self-signed certificates for development
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream bithuman_backend {
        server bithuman:8080;
        # Add more servers for load balancing
        # server bithuman2:8080;
        # server bithuman3:8080;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

        # WebSocket support
        location /ws {
            proxy_pass http://bithuman_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API endpoints
        location /api {
            proxy_pass http://bithuman_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
        limit_req zone=api burst=20 nodelay;
    }
}
```

### Firewall Configuration

```bash
# UFW firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# For internal services only
sudo ufw allow from 10.0.0.0/8 to any port 8080
```

## Monitoring and Logging

### Prometheus Metrics

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
REQUEST_COUNT = Counter('bithuman_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('bithuman_request_duration_seconds', 'Request duration')
ACTIVE_SESSIONS = Gauge('bithuman_active_sessions', 'Active sessions')
GPU_MEMORY = Gauge('bithuman_gpu_memory_percent', 'GPU memory usage')

class MetricsCollector:
    def __init__(self, port=9090):
        start_http_server(port)
        
    def record_request(self, method, endpoint, duration):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        REQUEST_DURATION.observe(duration)
    
    def update_sessions(self, count):
        ACTIVE_SESSIONS.set(count)
    
    def update_gpu_memory(self, percent):
        GPU_MEMORY.set(percent)
```

### Log Configuration

```python
# logging_config.py
import logging
import logging.handlers
import os

def setup_logging():
    # Create logs directory
    os.makedirs('/var/log/bithuman', exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        '/var/log/bithuman/app.log',
        maxBytes=50*1024*1024,  # 50MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        '/var/log/bithuman/error.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    
    # Formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
```

## Troubleshooting

### Common Issues

#### Out of Memory Errors
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Solution: Increase memory limits
export BITHUMAN_MODEL_MEMORY_LIMIT=4GB
export BITHUMAN_MAX_CONCURRENT_SESSIONS=5
```

#### Slow Model Loading
```bash
# Check disk I/O
iostat -x 1

# Solution: Use faster storage
# Move models to NVMe SSD
sudo mv /home/bithuman/models /nvme/bithuman/models
ln -s /nvme/bithuman/models /home/bithuman/models
```

#### GPU Not Detected
```bash
# Check GPU status
nvidia-smi

# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Solution: Install proper drivers
sudo apt install nvidia-driver-525
sudo reboot
```

### Performance Tuning

```bash
# System optimization
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'net.core.rmem_max=134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max=134217728' >> /etc/sysctl.conf

# Apply changes
sysctl -p

# CPU governor for performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

## Next Steps

Once your self-hosted deployment is running:

1. **[Monitor Performance](../integrations/livekit.md)** - Set up comprehensive monitoring
2. **[Scale Horizontally](cpu-cloud.md)** - Consider cloud options for scaling
3. **[Optimize Costs](gpu-cloud.md)** - Balance performance and costs
4. **[Test Integrations](../integrations/livekit.md)** - Connect with your applications

## Support

For self-hosted deployment support:
- **Documentation**: Complete setup guides
- **Community**: Discord server for troubleshooting
- **Enterprise Support**: Available for production deployments
- **Professional Services**: Custom deployment assistance

Self-hosting gives you complete control over your bitHuman deployment while ensuring optimal performance and security! 