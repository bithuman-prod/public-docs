# bitHuman GPU Cloud

Experience lightning-fast avatar processing with our high-performance GPU cloud infrastructure. Optimized for real-time interactions and demanding production workloads.

## Overview

bitHuman GPU Cloud delivers:
- **Ultra-low latency** - Sub-100ms processing times
- **Real-time performance** - Optimized for live interactions
- **Premium quality** - Highest fidelity avatar rendering
- **Auto-scaling** - Handle traffic spikes effortlessly
- **Enterprise-grade** - Built for production workloads

## When to Use GPU Cloud

### ✅ Perfect For:
- **Real-time video calls and streaming**
- **Live customer service interactions**
- **Gaming and interactive entertainment**
- **High-frequency API usage**
- **Premium user experiences**
- **Production applications requiring <100ms latency**

### ⚡ Performance Benefits:
- **5-10x faster** than CPU cloud processing
- **Consistent low latency** regardless of load
- **Higher quality** avatar rendering
- **Better frame consistency** for smooth animations

## Getting Started

### 1. Enable GPU Cloud Access

1. Log into [bitHuman Console](https://console.bithuman.io)
2. Navigate to **Cloud Services** > **GPU Cloud**
3. Request GPU Cloud access (approval required)
4. Complete billing setup for GPU tier
5. Generate GPU Cloud API credentials

### 2. Quick Start Example

```python
# gpu_cloud_quickstart.py
import asyncio
import os
from bithuman.cloud import GPUCloudRuntime
from bithuman.audio import AudioChunk

async def gpu_cloud_example():
    # Initialize GPU Cloud runtime
    runtime = await GPUCloudRuntime.create(
        api_secret=os.getenv('BITHUMAN_API_SECRET'),
        gpu_token=os.getenv('BITHUMAN_GPU_TOKEN'),
        model_id='your_model_id',
        region='us-east-1',
        instance_type='gpu-v100'  # or 'gpu-a100' for maximum performance
    )
    
    print("Connected to bitHuman GPU Cloud")
    
    # Load audio data
    audio_chunk = AudioChunk.from_file('sample_audio.wav')
    
    # Process with ultra-low latency
    start_time = asyncio.get_event_loop().time()
    frame_count = 0
    
    async for video_frame in runtime.process_audio_chunk(audio_chunk):
        frame_count += 1
        if frame_count == 1:
            first_frame_time = asyncio.get_event_loop().time() - start_time
            print(f"First frame latency: {first_frame_time*1000:.1f}ms")
    
    total_time = asyncio.get_event_loop().time() - start_time
    fps = frame_count / total_time
    print(f"Average FPS: {fps:.1f}")
    
    await runtime.close()

if __name__ == "__main__":
    asyncio.run(gpu_cloud_example())
```

### 3. Environment Setup

```bash
# GPU Cloud environment variables
export BITHUMAN_API_SECRET='your_api_secret'
export BITHUMAN_GPU_TOKEN='your_gpu_cloud_token'
export BITHUMAN_GPU_REGION='us-east-1'
export BITHUMAN_GPU_INSTANCE='gpu-v100'  # or gpu-a100
export BITHUMAN_GPU_PRIORITY='high'      # standard, high, critical
```

## Pricing & Instance Types

### GPU Instance Types

#### V100 Instances (Balanced Performance)
| Metric | Specification | Cost |
|--------|---------------|------|
| **GPU** | NVIDIA V100 (16GB) | $0.50/hour |
| **Processing** | $0.15/minute | Real processing time |
| **Latency** | 50-100ms | Typical response time |
| **Throughput** | 30-50 FPS | Sustained performance |
| **Best For** | Most production applications | Standard real-time use |

#### A100 Instances (Maximum Performance)
| Metric | Specification | Cost |
|--------|---------------|------|
| **GPU** | NVIDIA A100 (40GB) | $0.80/hour |
| **Processing** | $0.25/minute | Real processing time |
| **Latency** | 20-50ms | Ultra-low response time |
| **Throughput** | 50-75 FPS | Peak performance |
| **Best For** | Demanding applications | Critical real-time systems |

### Priority Tiers

#### Standard Priority
- **Cost**: Base rates
- **Availability**: Best effort
- **Use Case**: Development and testing

#### High Priority
- **Cost**: +50% of base rates
- **Availability**: Guaranteed resources
- **Use Case**: Production applications

#### Critical Priority
- **Cost**: +100% of base rates
- **Availability**: Dedicated resources
- **Use Case**: Mission-critical systems

### Cost Calculator

```python
# gpu_cost_calculator.py
class GPUCloudCostCalculator:
    def __init__(self, instance_type='gpu-v100', priority='standard'):
        self.rates = {
            'gpu-v100': {
                'hourly': 0.50,
                'processing': 0.15,
                'data_transfer': 0.005
            },
            'gpu-a100': {
                'hourly': 0.80,
                'processing': 0.25,
                'data_transfer': 0.005
            }
        }[instance_type]
        
        self.priority_multipliers = {
            'standard': 1.0,
            'high': 1.5,
            'critical': 2.0
        }
        
        self.multiplier = self.priority_multipliers[priority]
    
    def calculate_hourly_cost(self, 
                            active_hours_per_month,
                            processing_minutes_per_month,
                            data_transfer_gb_per_month):
        
        instance_cost = active_hours_per_month * self.rates['hourly'] * self.multiplier
        processing_cost = processing_minutes_per_month * self.rates['processing'] * self.multiplier
        transfer_cost = data_transfer_gb_per_month * self.rates['data_transfer']
        
        total = instance_cost + processing_cost + transfer_cost
        
        return {
            'instance_hours': instance_cost,
            'processing': processing_cost,
            'data_transfer': transfer_cost,
            'total_monthly': total,
            'cost_per_hour': total / active_hours_per_month if active_hours_per_month > 0 else 0
        }

# Example usage
calculator = GPUCloudCostCalculator('gpu-v100', 'high')
costs = calculator.calculate_hourly_cost(
    active_hours_per_month=200,      # 8 hours/day for 25 days
    processing_minutes_per_month=5000, # ~25 minutes/hour average
    data_transfer_gb_per_month=100
)

print(f"Monthly cost estimate: ${costs['total_monthly']:.2f}")
print(f"Cost per active hour: ${costs['cost_per_hour']:.2f}")
```

## Performance Optimization

### Real-time Streaming Setup

```python
# realtime_streaming.py
import asyncio
import websockets
import json
from bithuman.cloud import GPUCloudRuntime
from bithuman.audio import AudioChunk

class RealTimeAvatarStreamer:
    def __init__(self, instance_type='gpu-v100'):
        self.runtime = None
        self.instance_type = instance_type
        self.active_sessions = {}
        
    async def initialize(self):
        """Initialize GPU cloud runtime with optimizations"""
        self.runtime = await GPUCloudRuntime.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            gpu_token=os.getenv('BITHUMAN_GPU_TOKEN'),
            model_id=os.getenv('BITHUMAN_MODEL_ID'),
            region='us-east-1',
            instance_type=self.instance_type,
            # Real-time optimizations
            low_latency_mode=True,
            frame_buffer_size=2,      # Minimal buffering
            prediction_lookahead=3,   # Predict next frames
            quality_preset='realtime', # Favor speed over quality
            enable_frame_skipping=True # Skip frames if falling behind
        )
    
    async def handle_client(self, websocket, path):
        """Handle real-time client connection"""
        session_id = path.split('/')[-1]
        self.active_sessions[session_id] = websocket
        
        print(f"New real-time session: {session_id}")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'audio_chunk':
                    await self.process_realtime_audio(session_id, data['audio'])
                elif data['type'] == 'interrupt':
                    self.runtime.interrupt()
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.active_sessions.pop(session_id, None)
            print(f"Session ended: {session_id}")
    
    async def process_realtime_audio(self, session_id, audio_data):
        """Process audio with minimal latency"""
        try:
            # Convert audio data
            audio_bytes = bytes.fromhex(audio_data)
            audio_chunk = AudioChunk.from_bytes(audio_bytes, 16000)
            
            websocket = self.active_sessions.get(session_id)
            if not websocket:
                return
            
            # Process with real-time streaming
            async for video_frame in self.runtime.process_audio_chunk_realtime(audio_chunk):
                # Send frame immediately
                response = {
                    'type': 'video_frame',
                    'frame_index': video_frame.frame_index,
                    'timestamp': video_frame.timestamp,
                    'image_data': video_frame.image.tobytes().hex(),
                    'latency_ms': video_frame.processing_latency_ms
                }
                
                await websocket.send(json.dumps(response))
                
        except Exception as e:
            print(f"Error in real-time processing: {e}")

    async def start_server(self, host='0.0.0.0', port=8765):
        """Start WebSocket server for real-time streaming"""
        await self.initialize()
        
        print(f"Starting real-time avatar server on {host}:{port}")
        print(f"Using {self.instance_type} GPU instances")
        
        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()  # Run forever

# Usage
if __name__ == "__main__":
    streamer = RealTimeAvatarStreamer('gpu-a100')  # Use A100 for best performance
    asyncio.run(streamer.start_server())
```

### Latency Optimization Techniques

```python
# latency_optimizer.py
import asyncio
import time
from bithuman.cloud import GPUCloudRuntime
from bithuman.audio import AudioChunk

class LatencyOptimizer:
    def __init__(self):
        self.runtime = None
        self.latency_history = []
        
    async def initialize_optimized_runtime(self):
        """Initialize runtime with all latency optimizations"""
        self.runtime = await GPUCloudRuntime.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            gpu_token=os.getenv('BITHUMAN_GPU_TOKEN'),
            model_id=os.getenv('BITHUMAN_MODEL_ID'),
            region='us-east-1',
            instance_type='gpu-a100',
            
            # Latency optimizations
            priority='critical',           # Dedicated resources
            low_latency_mode=True,        # Minimize processing delays
            preload_models=True,          # Keep models in GPU memory
            connection_pooling=True,      # Reuse connections
            frame_prediction=True,        # Predict next frames
            adaptive_quality=True,        # Adjust quality for speed
            
            # Network optimizations
            compression_level=1,          # Light compression
            tcp_nodelay=True,            # Disable Nagle's algorithm
            socket_buffer_size=65536,    # Larger buffers
            
            # GPU optimizations
            gpu_memory_fraction=0.9,     # Use most GPU memory
            mixed_precision=True,        # FP16 for speed
            tensorrt_optimization=True,  # Optimize inference
        )
    
    async def measure_latency(self, audio_chunk):
        """Measure end-to-end latency"""
        start_time = time.time()
        
        first_frame_received = False
        total_frames = 0
        
        async for video_frame in self.runtime.process_audio_chunk(audio_chunk):
            if not first_frame_received:
                first_frame_latency = (time.time() - start_time) * 1000
                self.latency_history.append(first_frame_latency)
                first_frame_received = True
                print(f"First frame latency: {first_frame_latency:.1f}ms")
            
            total_frames += 1
        
        total_time = (time.time() - start_time) * 1000
        avg_frame_time = total_time / total_frames if total_frames > 0 else 0
        
        return {
            'first_frame_ms': first_frame_latency,
            'total_time_ms': total_time,
            'avg_frame_time_ms': avg_frame_time,
            'total_frames': total_frames
        }
    
    def get_latency_stats(self):
        """Get latency statistics"""
        if not self.latency_history:
            return None
            
        return {
            'avg_latency_ms': sum(self.latency_history) / len(self.latency_history),
            'min_latency_ms': min(self.latency_history),
            'max_latency_ms': max(self.latency_history),
            'p95_latency_ms': sorted(self.latency_history)[int(len(self.latency_history) * 0.95)],
            'sample_count': len(self.latency_history)
        }

# Usage example
async def run_latency_tests():
    optimizer = LatencyOptimizer()
    await optimizer.initialize_optimized_runtime()
    
    # Test with various audio lengths
    test_durations = [1, 3, 5, 10]  # seconds
    
    for duration in test_durations:
        print(f"\nTesting {duration}s audio...")
        
        # Generate test audio
        sample_rate = 16000
        audio_data = np.random.randint(-1000, 1000, duration * sample_rate, dtype=np.int16)
        audio_chunk = AudioChunk.from_numpy(audio_data, sample_rate)
        
        # Measure latency
        results = await optimizer.measure_latency(audio_chunk)
        print(f"Results: {results}")
    
    # Print overall statistics
    stats = optimizer.get_latency_stats()
    print(f"\nOverall latency stats: {stats}")

if __name__ == "__main__":
    asyncio.run(run_latency_tests())
```

## Enterprise Integration

### High Availability Setup

```python
# ha_gpu_cloud.py
import asyncio
import random
from typing import List, Optional
from bithuman.cloud import GPUCloudRuntime, CloudError

class HighAvailabilityGPUCloud:
    def __init__(self, regions: List[str], instance_type='gpu-v100'):
        self.regions = regions
        self.instance_type = instance_type
        self.runtimes = {}
        self.region_health = {}
        self.current_region = None
        
    async def initialize_multi_region(self):
        """Initialize runtimes in multiple regions"""
        for region in self.regions:
            try:
                runtime = await GPUCloudRuntime.create(
                    api_secret=os.getenv('BITHUMAN_API_SECRET'),
                    gpu_token=os.getenv('BITHUMAN_GPU_TOKEN'),
                    model_id=os.getenv('BITHUMAN_MODEL_ID'),
                    region=region,
                    instance_type=self.instance_type,
                    priority='high'
                )
                
                self.runtimes[region] = runtime
                self.region_health[region] = True
                print(f"Initialized runtime in {region}")
                
            except Exception as e:
                print(f"Failed to initialize runtime in {region}: {e}")
                self.region_health[region] = False
        
        # Set primary region
        healthy_regions = [r for r, h in self.region_health.items() if h]
        if healthy_regions:
            self.current_region = healthy_regions[0]
    
    async def process_with_failover(self, audio_chunk, max_retries=3):
        """Process audio with automatic failover"""
        for attempt in range(max_retries):
            try:
                # Select best available region
                region = await self.select_best_region()
                if not region:
                    raise CloudError("No healthy regions available")
                
                runtime = self.runtimes[region]
                
                # Process audio
                frames = []
                async for frame in runtime.process_audio_chunk(audio_chunk):
                    frames.append(frame)
                
                # Mark region as healthy
                self.region_health[region] = True
                return frames
                
            except CloudError as e:
                print(f"Region {region} failed (attempt {attempt + 1}): {e}")
                
                # Mark region as unhealthy
                if region:
                    self.region_health[region] = False
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (2 ** attempt))  # Exponential backoff
                else:
                    raise
    
    async def select_best_region(self) -> Optional[str]:
        """Select the best available region"""
        healthy_regions = [r for r, h in self.region_health.items() if h]
        
        if not healthy_regions:
            # Try to recover one region
            await self.health_check_all_regions()
            healthy_regions = [r for r, h in self.region_health.items() if h]
        
        if not healthy_regions:
            return None
        
        # For now, just return a random healthy region
        # In production, you might consider latency, load, etc.
        return random.choice(healthy_regions)
    
    async def health_check_all_regions(self):
        """Check health of all regions"""
        for region in self.regions:
            try:
                runtime = self.runtimes.get(region)
                if runtime:
                    # Simple health check
                    await runtime.health_check()
                    self.region_health[region] = True
                else:
                    # Try to reinitialize
                    runtime = await GPUCloudRuntime.create(
                        api_secret=os.getenv('BITHUMAN_API_SECRET'),
                        gpu_token=os.getenv('BITHUMAN_GPU_TOKEN'),
                        model_id=os.getenv('BITHUMAN_MODEL_ID'),
                        region=region,
                        instance_type=self.instance_type
                    )
                    self.runtimes[region] = runtime
                    self.region_health[region] = True
                    
            except Exception:
                self.region_health[region] = False

# Usage
async def main():
    ha_cloud = HighAvailabilityGPUCloud(['us-east-1', 'us-west-2', 'eu-west-1'])
    await ha_cloud.initialize_multi_region()
    
    # Process audio with automatic failover
    audio_chunk = AudioChunk.from_file('test_audio.wav')
    try:
        frames = await ha_cloud.process_with_failover(audio_chunk)
        print(f"Successfully processed {len(frames)} frames")
    except Exception as e:
        print(f"Failed to process audio: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Auto-scaling Configuration

```python
# autoscaling_gpu.py
import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List
from bithuman.cloud import GPUCloudRuntime

@dataclass
class ScalingMetrics:
    active_requests: int
    avg_latency_ms: float
    queue_depth: int
    cpu_utilization: float
    timestamp: float

class AutoScalingGPUCloud:
    def __init__(self):
        self.instances: Dict[str, GPUCloudRuntime] = {}
        self.metrics_history: List[ScalingMetrics] = []
        self.target_latency_ms = 100
        self.max_instances = 10
        self.min_instances = 2
        
    async def initialize(self):
        """Initialize with minimum instances"""
        for i in range(self.min_instances):
            await self.add_instance(f"instance-{i}")
    
    async def add_instance(self, instance_id: str):
        """Add a new GPU instance"""
        try:
            runtime = await GPUCloudRuntime.create(
                api_secret=os.getenv('BITHUMAN_API_SECRET'),
                gpu_token=os.getenv('BITHUMAN_GPU_TOKEN'),
                model_id=os.getenv('BITHUMAN_MODEL_ID'),
                region='us-east-1',
                instance_type='gpu-v100',
                priority='high'
            )
            
            self.instances[instance_id] = runtime
            print(f"Added instance: {instance_id}")
            
        except Exception as e:
            print(f"Failed to add instance {instance_id}: {e}")
    
    async def remove_instance(self, instance_id: str):
        """Remove a GPU instance"""
        if instance_id in self.instances:
            try:
                await self.instances[instance_id].close()
                del self.instances[instance_id]
                print(f"Removed instance: {instance_id}")
            except Exception as e:
                print(f"Error removing instance {instance_id}: {e}")
    
    async def collect_metrics(self) -> ScalingMetrics:
        """Collect current scaling metrics"""
        # In a real implementation, these would come from monitoring systems
        active_requests = len(self.instances)  # Simplified
        avg_latency_ms = 75.0  # Would be measured
        queue_depth = 0  # Would be tracked
        cpu_utilization = 45.0  # Would be monitored
        
        return ScalingMetrics(
            active_requests=active_requests,
            avg_latency_ms=avg_latency_ms,
            queue_depth=queue_depth,
            cpu_utilization=cpu_utilization,
            timestamp=time.time()
        )
    
    async def evaluate_scaling(self, metrics: ScalingMetrics):
        """Evaluate if scaling is needed"""
        current_instances = len(self.instances)
        
        # Scale up conditions
        should_scale_up = (
            metrics.avg_latency_ms > self.target_latency_ms * 1.5 or
            metrics.queue_depth > 5 or
            metrics.cpu_utilization > 80
        )
        
        # Scale down conditions
        should_scale_down = (
            metrics.avg_latency_ms < self.target_latency_ms * 0.5 and
            metrics.queue_depth == 0 and
            metrics.cpu_utilization < 30 and
            current_instances > self.min_instances
        )
        
        if should_scale_up and current_instances < self.max_instances:
            new_instance_id = f"instance-{int(time.time())}"
            await self.add_instance(new_instance_id)
            
        elif should_scale_down:
            # Remove oldest instance
            if self.instances:
                oldest_instance = list(self.instances.keys())[0]
                await self.remove_instance(oldest_instance)
    
    async def auto_scaling_loop(self):
        """Main auto-scaling loop"""
        while True:
            try:
                metrics = await self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last hour of metrics
                cutoff_time = time.time() - 3600
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                await self.evaluate_scaling(metrics)
                
                print(f"Instances: {len(self.instances)}, "
                      f"Latency: {metrics.avg_latency_ms:.1f}ms, "
                      f"CPU: {metrics.cpu_utilization:.1f}%")
                
            except Exception as e:
                print(f"Error in auto-scaling loop: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds

# Usage
async def main():
    scaler = AutoScalingGPUCloud()
    await scaler.initialize()
    
    # Start auto-scaling in background
    asyncio.create_task(scaler.auto_scaling_loop())
    
    # Simulate workload
    await asyncio.sleep(300)  # Run for 5 minutes

if __name__ == "__main__":
    asyncio.run(main())
```

## Monitoring and Analytics

### Performance Dashboard

```python
# gpu_dashboard.py
import asyncio
import time
import json
from datetime import datetime, timedelta
from bithuman.cloud import GPUCloudRuntime

class GPUPerformanceDashboard:
    def __init__(self):
        self.metrics = {
            'latency_ms': [],
            'throughput_fps': [],
            'gpu_utilization': [],
            'memory_usage': [],
            'error_rate': [],
            'cost_per_hour': []
        }
        self.start_time = time.time()
        
    async def collect_gpu_metrics(self, runtime):
        """Collect GPU-specific metrics"""
        try:
            # Get GPU metrics from runtime
            gpu_stats = await runtime.get_gpu_stats()
            
            current_metrics = {
                'timestamp': datetime.now().isoformat(),
                'latency_ms': gpu_stats.get('avg_latency_ms', 0),
                'throughput_fps': gpu_stats.get('current_fps', 0),
                'gpu_utilization': gpu_stats.get('gpu_utilization_percent', 0),
                'memory_usage': gpu_stats.get('gpu_memory_used_percent', 0),
                'active_sessions': gpu_stats.get('active_sessions', 0),
                'queue_depth': gpu_stats.get('queue_depth', 0)
            }
            
            # Store metrics
            for key, value in current_metrics.items():
                if key != 'timestamp' and key in self.metrics:
                    self.metrics[key].append(value)
            
            return current_metrics
            
        except Exception as e:
            print(f"Error collecting GPU metrics: {e}")
            return None
    
    def calculate_performance_summary(self, window_minutes=60):
        """Calculate performance summary for the last N minutes"""
        cutoff_time = time.time() - (window_minutes * 60)
        
        # In a real implementation, you'd filter by timestamp
        recent_latency = self.metrics['latency_ms'][-100:] if self.metrics['latency_ms'] else []
        recent_fps = self.metrics['throughput_fps'][-100:] if self.metrics['throughput_fps'] else []
        
        if not recent_latency:
            return None
        
        return {
            'avg_latency_ms': sum(recent_latency) / len(recent_latency),
            'p95_latency_ms': sorted(recent_latency)[int(len(recent_latency) * 0.95)] if recent_latency else 0,
            'p99_latency_ms': sorted(recent_latency)[int(len(recent_latency) * 0.99)] if recent_latency else 0,
            'avg_fps': sum(recent_fps) / len(recent_fps) if recent_fps else 0,
            'min_latency_ms': min(recent_latency),
            'max_latency_ms': max(recent_latency),
            'sample_count': len(recent_latency),
            'uptime_hours': (time.time() - self.start_time) / 3600
        }
    
    def export_metrics(self, filename='gpu_metrics.json'):
        """Export metrics to JSON file"""
        summary = self.calculate_performance_summary()
        
        export_data = {
            'summary': summary,
            'raw_metrics': self.metrics,
            'export_time': datetime.now().isoformat(),
            'total_uptime_hours': (time.time() - self.start_time) / 3600
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Metrics exported to {filename}")

# Usage with monitoring
async def monitor_gpu_performance():
    dashboard = GPUPerformanceDashboard()
    
    runtime = await GPUCloudRuntime.create(
        api_secret=os.getenv('BITHUMAN_API_SECRET'),
        gpu_token=os.getenv('BITHUMAN_GPU_TOKEN'),
        model_id=os.getenv('BITHUMAN_MODEL_ID'),
        region='us-east-1',
        instance_type='gpu-a100'
    )
    
    print("Starting GPU performance monitoring...")
    
    try:
        while True:
            metrics = await dashboard.collect_gpu_metrics(runtime)
            if metrics:
                print(f"GPU Metrics: {metrics}")
            
            # Print summary every 10 minutes
            if int(time.time()) % 600 == 0:
                summary = dashboard.calculate_performance_summary()
                if summary:
                    print(f"Performance Summary: {summary}")
            
            await asyncio.sleep(30)  # Collect every 30 seconds
            
    except KeyboardInterrupt:
        print("Stopping monitoring...")
        dashboard.export_metrics()
    finally:
        await runtime.close()

if __name__ == "__main__":
    asyncio.run(monitor_gpu_performance())
```

## Best Practices

### 1. Instance Selection

```python
# Choose the right instance type based on your needs
performance_requirements = {
    'development': 'gpu-v100',      # Cost-effective for testing
    'production': 'gpu-a100',       # Best performance for live apps
    'batch_processing': 'gpu-v100', # Balanced for non-real-time work
    'real_time_critical': 'gpu-a100' # Maximum performance for critical apps
}
```

### 2. Region Strategy

```python
# Multi-region deployment for global applications
region_strategy = {
    'americas': 'us-east-1',        # Primary for Americas
    'europe': 'eu-west-1',          # Primary for Europe
    'asia_pacific': 'ap-northeast-1' # Primary for Asia
}

# Use closest region to your users for best latency
```

### 3. Cost Optimization

```python
# Optimize costs while maintaining performance
cost_optimization_tips = {
    'right_sizing': 'Use V100 unless you need A100 performance',
    'priority_selection': 'Use standard priority for non-critical workloads',
    'auto_scaling': 'Scale down during low usage periods',
    'batch_processing': 'Combine multiple requests when possible',
    'monitoring': 'Track usage patterns and optimize accordingly'
}
```

## Troubleshooting

### Common Issues

#### High Latency
```python
# Diagnose and fix high latency issues
async def diagnose_latency():
    # Check network latency to region
    latency = await test_region_latency('us-east-1')
    if latency > 50:
        print("High network latency - consider closer region")
    
    # Check instance type
    if instance_type == 'gpu-v100' and required_latency < 50:
        print("Consider upgrading to gpu-a100")
    
    # Check priority setting
    if priority == 'standard':
        print("Consider high or critical priority for guaranteed performance")
```

#### Resource Limits
```python
# Handle resource limit errors
try:
    runtime = await GPUCloudRuntime.create(...)
except ResourceLimitError as e:
    print(f"Resource limit reached: {e}")
    print("Consider:")
    print("- Upgrading your GPU Cloud plan")
    print("- Using auto-scaling to manage load")
    print("- Implementing request queuing")
```

## Next Steps

To maximize your GPU Cloud deployment:

1. **[Compare with Self-hosted](self-hosted.md)** - Understand trade-offs
2. **[Integrate with Applications](../integrations/livekit.md)** - Connect to your systems
3. **[Monitor Performance](../examples/livekit-agent.md)** - Track metrics and optimize
4. **[Scale Globally](#multi-region-deployment)** - Deploy across regions

## Support

For GPU Cloud support:
- **Premium Support**: Priority technical assistance
- **Dedicated Account Manager**: For enterprise customers
- **24/7 Monitoring**: Proactive issue detection
- **SLA Guarantees**: 99.9% uptime commitment

GPU Cloud delivers the ultimate in avatar performance - perfect for demanding applications that require the absolute best user experience! 