# bitHuman CPU Cloud

Deploy bitHuman avatars using our managed CPU cloud infrastructure for cost-effective, scalable avatar processing without the complexity of self-hosting.

## Overview

bitHuman CPU Cloud provides:
- **Managed infrastructure** - No server setup or maintenance
- **Pay-per-use pricing** - Only pay for what you consume
- **Global availability** - Low-latency endpoints worldwide
- **Auto-scaling** - Automatic capacity management
- **Cost-effective** - Optimized for budget-conscious applications

## When to Use CPU Cloud

### ✅ Ideal For:
- **Development and prototyping**
- **Low to moderate traffic applications**
- **Cost-sensitive projects**
- **Applications with flexible latency requirements**
- **Getting started with bitHuman**

### ❌ Consider GPU Cloud For:
- High-frequency, real-time interactions
- Applications requiring < 100ms latency
- High-volume production workloads
- Premium user experiences

## Getting Started

### 1. Enable CPU Cloud Access

1. Log into [bitHuman Console](https://console.bithuman.io)
2. Navigate to **Cloud Services**
3. Enable **CPU Cloud** access
4. Configure your billing preferences
5. Copy your Cloud API credentials

### 2. Basic Setup

```python
# cpu_cloud_example.py
import asyncio
import os
from bithuman.cloud import CPUCloudRuntime
from bithuman.audio import AudioChunk

async def cpu_cloud_example():
    # Initialize CPU Cloud runtime
    runtime = await CPUCloudRuntime.create(
        api_secret=os.getenv('BITHUMAN_API_SECRET'),
        cloud_token=os.getenv('BITHUMAN_CLOUD_TOKEN'),
        model_id='your_model_id',  # From bitHuman Console
        region='us-east-1'  # Choose closest region
    )
    
    print("Connected to bitHuman CPU Cloud")
    
    # Load audio data
    audio_chunk = AudioChunk.from_file('sample_audio.wav')
    
    # Process with cloud
    async for video_frame in runtime.process_audio_chunk(audio_chunk):
        print(f"Received frame {video_frame.frame_index}")
        # Process video frame...
    
    await runtime.close()

if __name__ == "__main__":
    asyncio.run(cpu_cloud_example())
```

### 3. Environment Configuration

```bash
# Set environment variables
export BITHUMAN_API_SECRET='your_api_secret'
export BITHUMAN_CLOUD_TOKEN='your_cloud_token'
export BITHUMAN_CLOUD_REGION='us-east-1'
export BITHUMAN_CLOUD_TIER='standard'  # standard, premium
```

## Pricing Model

### Standard Tier

| Metric | Rate | Notes |
|--------|------|-------|
| **Processing Time** | $0.05/minute | Actual processing time |
| **Data Transfer** | $0.01/GB | Audio upload + video download |
| **Model Storage** | $0.10/GB/month | Custom model hosting |
| **API Requests** | $0.001/request | Authentication and setup |

### Premium Tier

| Metric | Rate | Notes |
|--------|------|-------|
| **Processing Time** | $0.08/minute | Priority processing |
| **Data Transfer** | $0.005/GB | Reduced transfer costs |
| **Model Storage** | $0.15/GB/month | Enhanced model hosting |
| **SLA** | 99.9% uptime | Service level guarantee |

### Cost Calculator

```python
# cost_calculator.py
class CPUCloudCostCalculator:
    def __init__(self, tier='standard'):
        self.rates = {
            'standard': {
                'processing': 0.05,  # per minute
                'transfer': 0.01,    # per GB
                'storage': 0.10,     # per GB/month
                'requests': 0.001    # per request
            },
            'premium': {
                'processing': 0.08,
                'transfer': 0.005,
                'storage': 0.15,
                'requests': 0.001
            }
        }[tier]
    
    def calculate_monthly_cost(self, 
                             processing_minutes_per_month,
                             data_transfer_gb_per_month,
                             model_storage_gb,
                             api_requests_per_month):
        
        processing_cost = processing_minutes_per_month * self.rates['processing']
        transfer_cost = data_transfer_gb_per_month * self.rates['transfer']
        storage_cost = model_storage_gb * self.rates['storage']
        request_cost = api_requests_per_month * self.rates['requests']
        
        total = processing_cost + transfer_cost + storage_cost + request_cost
        
        return {
            'processing': processing_cost,
            'transfer': transfer_cost,
            'storage': storage_cost,
            'requests': request_cost,
            'total': total
        }

# Example usage
calculator = CPUCloudCostCalculator('standard')
costs = calculator.calculate_monthly_cost(
    processing_minutes_per_month=1000,
    data_transfer_gb_per_month=50,
    model_storage_gb=2,
    api_requests_per_month=10000
)

print(f"Monthly cost estimate: ${costs['total']:.2f}")
```

## Regional Deployment

### Available Regions

| Region | Location | Latency (typical) |
|--------|----------|-------------------|
| **us-east-1** | N. Virginia | 20-50ms (US East) |
| **us-west-2** | Oregon | 20-50ms (US West) |
| **eu-west-1** | Ireland | 30-60ms (Europe) |
| **ap-southeast-1** | Singapore | 40-80ms (Asia Pacific) |
| **ap-northeast-1** | Tokyo | 30-70ms (Asia Pacific) |

### Region Selection

```python
# region_selector.py
import asyncio
import time
from bithuman.cloud import CPUCloudRuntime

async def test_region_latency(region):
    """Test latency to a specific region"""
    try:
        start_time = time.time()
        
        runtime = await CPUCloudRuntime.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            cloud_token=os.getenv('BITHUMAN_CLOUD_TOKEN'),
            model_id='test_model',
            region=region,
            test_mode=True  # Don't actually process
        )
        
        connection_time = (time.time() - start_time) * 1000
        await runtime.close()
        
        return connection_time
    except Exception as e:
        return float('inf')

async def find_best_region():
    """Find the region with lowest latency"""
    regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
    results = {}
    
    for region in regions:
        latency = await test_region_latency(region)
        results[region] = latency
        print(f"{region}: {latency:.0f}ms")
    
    best_region = min(results, key=results.get)
    print(f"\nBest region: {best_region} ({results[best_region]:.0f}ms)")
    return best_region

# Usage
if __name__ == "__main__":
    asyncio.run(find_best_region())
```

## Advanced Configuration

### Performance Optimization

```python
# optimized_cpu_client.py
import asyncio
from bithuman.cloud import CPUCloudRuntime
from bithuman.audio import AudioChunk

class OptimizedCPUClient:
    def __init__(self, region='auto'):
        self.region = region
        self.runtime = None
        self.connection_pool_size = 3
        
    async def initialize(self):
        """Initialize optimized client"""
        self.runtime = await CPUCloudRuntime.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            cloud_token=os.getenv('BITHUMAN_CLOUD_TOKEN'),
            model_id=os.getenv('BITHUMAN_MODEL_ID'),
            region=self.region,
            # Performance optimizations
            connection_pool_size=self.connection_pool_size,
            enable_compression=True,
            chunk_size=4096,  # Optimal chunk size for CPU processing
            timeout=30,
            retry_attempts=2
        )
    
    async def process_audio_optimized(self, audio_data):
        """Process audio with optimizations"""
        # Split large audio files for better parallelization
        chunk_size = 30  # 30 seconds per chunk
        chunks = self.split_audio(audio_data, chunk_size)
        
        # Process chunks in parallel (limited by connection pool)
        results = []
        semaphore = asyncio.Semaphore(self.connection_pool_size)
        
        async def process_chunk(chunk):
            async with semaphore:
                frames = []
                async for frame in self.runtime.process_audio_chunk(chunk):
                    frames.append(frame)
                return frames
        
        tasks = [process_chunk(chunk) for chunk in chunks]
        chunk_results = await asyncio.gather(*tasks)
        
        # Combine results
        for chunk_frames in chunk_results:
            results.extend(chunk_frames)
        
        return results
    
    def split_audio(self, audio_data, chunk_duration_seconds):
        """Split audio into chunks for parallel processing"""
        # Implementation depends on audio format
        pass
```

### Error Handling and Retry Logic

```python
# robust_client.py
import asyncio
import logging
from typing import AsyncGenerator
from bithuman.cloud import CPUCloudRuntime, CloudError
from bithuman.audio import AudioChunk

class RobustCPUClient:
    def __init__(self, max_retries=3, retry_delay=1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        
    async def process_with_retry(self, audio_chunk: AudioChunk) -> AsyncGenerator:
        """Process audio with automatic retry on failures"""
        for attempt in range(self.max_retries + 1):
            try:
                runtime = await CPUCloudRuntime.create(
                    api_secret=os.getenv('BITHUMAN_API_SECRET'),
                    cloud_token=os.getenv('BITHUMAN_CLOUD_TOKEN'),
                    model_id=os.getenv('BITHUMAN_MODEL_ID'),
                    region=os.getenv('BITHUMAN_CLOUD_REGION', 'us-east-1')
                )
                
                async for frame in runtime.process_audio_chunk(audio_chunk):
                    yield frame
                    
                await runtime.close()
                return  # Success, exit retry loop
                
            except CloudError as e:
                self.logger.warning(f"Cloud error (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    raise  # Max retries exceeded
                    
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                raise
```

## Integration Examples

### Web Application Integration

```python
# web_app.py
from flask import Flask, request, jsonify
import asyncio
import base64
from bithuman.cloud import CPUCloudRuntime
from bithuman.audio import AudioChunk

app = Flask(__name__)

class WebAppHandler:
    def __init__(self):
        self.runtime = None
        
    async def initialize(self):
        self.runtime = await CPUCloudRuntime.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            cloud_token=os.getenv('BITHUMAN_CLOUD_TOKEN'),
            model_id=os.getenv('BITHUMAN_MODEL_ID'),
            region='us-east-1'
        )

handler = WebAppHandler()

@app.route('/process-audio', methods=['POST'])
def process_audio():
    """Process audio via CPU cloud"""
    try:
        # Get audio data from request
        audio_data = request.files['audio'].read()
        
        # Process with CPU cloud
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        audio_chunk = AudioChunk.from_bytes(audio_data, 16000)
        frames = []
        
        async def process():
            async for frame in handler.runtime.process_audio_chunk(audio_chunk):
                # Convert frame to base64 for JSON response
                frame_data = base64.b64encode(frame.image.tobytes()).decode()
                frames.append({
                    'index': frame.frame_index,
                    'data': frame_data
                })
        
        loop.run_until_complete(process())
        loop.close()
        
        return jsonify({
            'success': True,
            'frames': frames,
            'frame_count': len(frames)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Initialize handler
    loop = asyncio.get_event_loop()
    loop.run_until_complete(handler.initialize())
    
    app.run(host='0.0.0.0', port=5000)
```

### Batch Processing

```python
# batch_processor.py
import asyncio
import os
import glob
from bithuman.cloud import CPUCloudRuntime
from bithuman.audio import AudioChunk

class BatchProcessor:
    def __init__(self, concurrent_jobs=3):
        self.concurrent_jobs = concurrent_jobs
        self.runtime = None
        
    async def initialize(self):
        self.runtime = await CPUCloudRuntime.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            cloud_token=os.getenv('BITHUMAN_CLOUD_TOKEN'),
            model_id=os.getenv('BITHUMAN_MODEL_ID'),
            region='us-east-1'
        )
    
    async def process_file(self, audio_file_path, output_dir):
        """Process a single audio file"""
        try:
            print(f"Processing: {audio_file_path}")
            
            # Load audio
            audio_chunk = AudioChunk.from_file(audio_file_path)
            
            # Process frames
            output_frames = []
            async for frame in self.runtime.process_audio_chunk(audio_chunk):
                output_frames.append(frame)
            
            # Save results
            base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_avatar.mp4")
            
            # Save video (implementation depends on your video saving method)
            self.save_video(output_frames, output_path)
            
            print(f"Completed: {audio_file_path} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"Error processing {audio_file_path}: {e}")
            return False
    
    async def process_directory(self, input_dir, output_dir):
        """Process all audio files in a directory"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all audio files
        audio_files = []
        for ext in ['*.wav', '*.mp3', '*.m4a']:
            audio_files.extend(glob.glob(os.path.join(input_dir, ext)))
        
        print(f"Found {len(audio_files)} audio files to process")
        
        # Process files with limited concurrency
        semaphore = asyncio.Semaphore(self.concurrent_jobs)
        
        async def process_with_semaphore(file_path):
            async with semaphore:
                return await self.process_file(file_path, output_dir)
        
        tasks = [process_with_semaphore(f) for f in audio_files]
        results = await asyncio.gather(*tasks)
        
        successful = sum(results)
        print(f"Batch processing complete: {successful}/{len(audio_files)} successful")

# Usage
async def main():
    processor = BatchProcessor(concurrent_jobs=3)
    await processor.initialize()
    await processor.process_directory('input_audio/', 'output_videos/')

if __name__ == "__main__":
    asyncio.run(main())
```

## Monitoring and Analytics

### Usage Tracking

```python
# usage_tracker.py
import asyncio
import time
import json
from datetime import datetime, timedelta
from bithuman.cloud import CPUCloudRuntime

class UsageTracker:
    def __init__(self):
        self.session_data = []
        self.start_time = None
        
    async def track_session(self, audio_chunk):
        """Track a processing session"""
        session_start = time.time()
        frame_count = 0
        data_processed = len(audio_chunk.data)
        
        # Process audio
        runtime = await CPUCloudRuntime.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            cloud_token=os.getenv('BITHUMAN_CLOUD_TOKEN'),
            model_id=os.getenv('BITHUMAN_MODEL_ID'),
            region='us-east-1'
        )
        
        async for frame in runtime.process_audio_chunk(audio_chunk):
            frame_count += 1
            
        session_duration = time.time() - session_start
        
        # Record session data
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': session_duration,
            'frames_generated': frame_count,
            'data_size_bytes': data_processed,
            'region': 'us-east-1'
        }
        
        self.session_data.append(session_data)
        await runtime.close()
        
        return session_data
    
    def get_usage_summary(self, days=30):
        """Get usage summary for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_sessions = [
            s for s in self.session_data 
            if datetime.fromisoformat(s['timestamp']) > cutoff_date
        ]
        
        total_duration = sum(s['duration_seconds'] for s in recent_sessions)
        total_frames = sum(s['frames_generated'] for s in recent_sessions)
        total_data = sum(s['data_size_bytes'] for s in recent_sessions)
        
        return {
            'period_days': days,
            'total_sessions': len(recent_sessions),
            'total_processing_minutes': total_duration / 60,
            'total_frames_generated': total_frames,
            'total_data_gb': total_data / (1024**3),
            'avg_session_duration': total_duration / len(recent_sessions) if recent_sessions else 0
        }
```

## Performance Optimization Tips

### 1. Audio Preprocessing

```python
# Optimize audio before sending to cloud
def optimize_audio(audio_chunk):
    """Optimize audio for CPU cloud processing"""
    # Ensure optimal format
    audio_chunk = audio_chunk.resample(16000)  # Standard sample rate
    audio_chunk = audio_chunk.to_mono()        # Single channel
    audio_chunk = audio_chunk.normalize()      # Consistent levels
    
    # Compress for faster upload
    audio_chunk = audio_chunk.compress(quality=0.8)
    
    return audio_chunk
```

### 2. Chunk Size Optimization

```python
# Find optimal chunk size for your use case
async def test_chunk_sizes():
    chunk_sizes = [10, 20, 30, 45, 60]  # seconds
    
    for size in chunk_sizes:
        start_time = time.time()
        # Process chunk of given size
        duration = time.time() - start_time
        
        print(f"Chunk size {size}s: {duration:.2f}s processing time")
```

### 3. Connection Pooling

```python
# Reuse connections for better performance
class ConnectionPool:
    def __init__(self, pool_size=3):
        self.pool = asyncio.Queue(maxsize=pool_size)
        self.pool_size = pool_size
        
    async def initialize(self):
        for _ in range(self.pool_size):
            runtime = await CPUCloudRuntime.create(...)
            await self.pool.put(runtime)
    
    async def get_runtime(self):
        return await self.pool.get()
    
    async def return_runtime(self, runtime):
        await self.pool.put(runtime)
```

## Cost Optimization Strategies

### 1. Smart Region Selection
- Test latency to all regions
- Choose closest region for your users
- Consider data residency requirements

### 2. Efficient Batching
- Combine multiple short requests
- Process longer audio chunks when possible
- Use connection pooling

### 3. Model Optimization
- Use smaller, optimized models when possible
- Cache frequently used models
- Consider model compression techniques

### 4. Monitoring and Alerts
- Set up cost monitoring
- Alert on unexpected usage spikes
- Regular usage reviews

## Next Steps

To optimize your CPU Cloud deployment:

1. **[Try GPU Cloud](gpu-cloud.md)** - Compare performance and costs
2. **[Explore Integrations](../integrations/livekit.md)** - Connect with your applications
3. **[Review Examples](../examples/voice-driven-audio.md)** - See implementation patterns
4. **Monitor Usage** - Track costs and performance

## Support

For CPU Cloud support:
- **Documentation**: Complete API reference
- **Console Dashboard**: Usage monitoring and billing
- **Community**: Discord server for questions
- **Technical Support**: Available for all customers

CPU Cloud provides an excellent balance of cost, performance, and ease of use for most bitHuman applications! 