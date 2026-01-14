# Self-Hosted GPU Avatar Container

> **Preview Feature: Deploy GPU Avatar Workers on Your Infrastructure**
> Run production-grade GPU avatar generation on your own cloud infrastructure with full control over scaling, costs, and data privacy.
>
> **Pricing**: 2 credits per minute while using the GPU container.

## Overview

The self-hosted GPU avatar container (`docker.io/bithumanhubs/gpu-avatar-worker:latest`) enables you to deploy production-grade avatar generation on your own GPU infrastructure. This provides:

- **Full Control**: Complete control over deployment, scaling, and configuration
- **Cost Optimization**: Pay only for the GPU resources you use
- **Data Privacy**: Avatar images and audio never leave your infrastructure
- **Customization**: Extend the worker with custom logic and integrations

### Features

- **Real-time Avatar Generation**: Generate expressive talking avatars from single reference images
- **Natural Speech Synthesis**: Synchronized lip-sync and facial expressions driven by audio input
- **Emotion Recognition**: Automatic emotion detection from speech with 7 basic emotions supported
- **Smooth Motion**: Fluid, natural-looking animations optimized for real-time streaming
- **WebRTC Streaming**: Direct video streaming to browsers with low latency

## Quick Start

### Pull and Run

```bash
# Pull the latest image
docker pull docker.io/bithumanhubs/gpu-avatar-worker:latest

# Run with GPU support
docker run --gpus all -p 8089:8089 \
    -v /path/to/model-storage:/persistent-storage/avatar-model \
    -e AVATAR_MODEL_DIR=/persistent-storage/avatar-model \
    docker.io/bithumanhubs/gpu-avatar-worker:latest
```

### Verify Deployment

```bash
# Health check
curl http://localhost:8089/health

# Should return: {"status": "ok", "active_workers": 0}
```

## Container Architecture

### Components

The container includes:

- **Avatar Generation Engine**: High-quality talking avatar generation from reference images
- **Audio Processing Pipeline**: Audio feature extraction and emotion recognition
- **WebRTC Streaming Framework**: Real-time video streaming to browsers
- **HTTP API Server**: RESTful API for worker management and requests
- **Preset Avatar Cache**: Optional pre-encoded avatar storage for fast startup

## Storage Architecture

The container uses two storage directories with different purposes:

### AVATAR_MODEL_DIR (Required)

**Purpose**: Stores the avatar generation models required for all avatar processing.

**Key Points**:
- **Mandatory** - Required for all avatar generation (both preset and custom avatars)
- **Automatic download** - Models are downloaded automatically on first container startup
- **Persistent storage recommended** - Mount an external volume to avoid re-downloading on container restart
- **100% local processing** - All avatar generation happens locally; no cloud API calls after models are loaded

**Size**: Approximately 2-3 GB

### PRESET_AVATARS_DIR (Optional but Recommended)

**Purpose**: Stores pre-encoded avatar reference images for faster startup.

**Contents**:
```
/persistent-storage/preset-avatars/
├── avatar_001/
│   └── face.jpg          # Image file (avatar_001 is the avatar_id)
├── avatar_002/
│   └── portrait.png      # Image file (avatar_002 is the avatar_id)
└── avatar_003/
    └── avatar.webp       # Image file (avatar_003 is the avatar_id)
```

**Key Points**:
- **Optional** - Container works without it
- **Pre-encoded at startup** - Images are processed and cached in memory
- **Faster first frame** - ~4s vs ~6s for custom images
- **Best for frequently used avatars** - Add your main characters/support agents

### How They Work Together

```
┌─────────────────────────────────────────────────────────────┐
│                    Avatar Generation Flow                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Container Startup                                        │
│     ├─ Load models from AVATAR_MODEL_DIR (~30s, one-time)   │
│     └─ If PRESET_AVATARS_DIR: Pre-encode images             │
│                                                               │
│  2. Avatar Request (Preset Avatar)                           │
│     └─ avatar_id="avatar_001"                                │
│        ├─ Load pre-encoded features from memory (~4s)        │
│        └─ Generate frames using local models                 │
│           → NO cloud calls                                   │
│                                                               │
│  3. Avatar Request (Custom Image)                            │
│     └─ avatar_image=<custom image>                           │
│        ├─ Encode image using local models (~2s)              │
│        └─ Generate frames using local models                 │
│           → NO cloud calls                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Important**: Both preset and custom avatars use models from `AVATAR_MODEL_DIR`. The difference is only in whether the reference image is pre-encoded or encoded on-demand.

### Storage Recommendations

| Component | Size | Mount Type | Required |
|-----------|------|------------|----------|
| **AVATAR_MODEL_DIR** | ~2-3 GB | Persistent volume (EFS/GCS/NFS) | ✅ Yes |
| **PRESET_AVATARS_DIR** | Varies | Persistent volume (optional) | ⚪ Recommended |

**Why persistent storage for models?**
- Models are large (2-3 GB)
- Downloading takes time and costs bandwidth
- Persistent storage ensures instant availability on restart

**Why PRESET_AVATARS_DIR is recommended?**
- Faster first frame for frequently used avatars
- Better user experience with predictable performance
- Reduces GPU processing during peak traffic

## Performance Characteristics

### Startup Behavior

The container exhibits different startup times depending on configuration:

| Configuration | Time to First Frame | Description |
|---------------|---------------------|-------------|
| **Long-running + PRESET_AVATARS_DIR** | ~4 seconds | Avatar images pre-processed, minimal GPU initialization |
| **Long-running + No Cache** | ~6 seconds | Avatar processing on first request, GPU initialization |
| **Cold Start** | ~30-40 seconds | Full avatar engine initialization |

### Long-Running Containers

**Recommended for production deployments.** Containers stay running and handle multiple requests.

**With PRESET_AVATARS_DIR configured:**
- Avatar engine initialized at startup (~30s one-time)
- Avatar images pre-processed for instant loading
- First frame in ~4 seconds for preset avatars
- Subsequent frames at ~25 FPS

**Without PRESET_AVATARS_DIR:**
- Avatar engine initialized at startup (~30s one-time)
- Avatar processing on first request (~2s overhead)
- First frame in ~6 seconds
- Subsequent requests use in-memory cache

### Cold Start Containers

**Recommended for cost-optimized deployments.** Each request gets a fresh container.

**Characteristics:**
- Container starts from scratch (~30s initialization time)
- Container handles one request then terminates
- No persistent state between requests
- Higher latency per request, lower idle costs

## PRESET_AVATARS_DIR Configuration

### Directory Structure

The preset avatar directory stores avatar images for instant loading:

```
/persistent-storage/preset-avatars/
├── avatar_001/
│   └── face.jpg          # Image file (avatar_001 is the avatar_id)
├── avatar_002/
│   └── portrait.png      # Image file (avatar_002 is the avatar_id)
└── avatar_003/
    └── avatar.webp       # Image file (avatar_003 is the avatar_id)
```

**Key points:**
- Each subdirectory name becomes the `avatar_id` for that avatar
- Each subdirectory contains one image file (.jpg, .jpeg, .png, or .webp)
- The system automatically finds and uses the first image file in each directory
- Image features are pre-encoded and cached in memory at container startup

### Supported Image Formats

- `.jpg` / `.jpeg` - JPEG format (recommended)
- `.png` - PNG format
- `.webp` - WebP format

### Mounting Preset Directory

```bash
docker run --gpus all -p 8089:8089 \
    -v /path/to/model-storage:/persistent-storage/avatar-model \
    -v /path/to/preset-avatars:/persistent-storage/preset-avatars \
    -e AVATAR_MODEL_DIR=/persistent-storage/avatar-model \
    -e PRESET_AVATARS_DIR=/persistent-storage/preset-avatars \
    docker.io/bithumanhubs/gpu-avatar-worker:latest
```

### Using Preset Avatars

Preset avatars are automatically pre-processed at container startup for instant loading.

**To set up preset avatars:**

1. **Organize avatar images** in the preset directory structure:
   ```
   /persistent-storage/preset-avatars/
   ├── avatar_001/
   │   └── face.jpg
   ├── avatar_002/
   │   └── portrait.png
   └── avatar_003/
       └── avatar.webp
   ```

2. **Mount the directory** when starting the container:
   ```bash
   -v /path/to/preset-avatars:/persistent-storage/preset-avatars \
   -e PRESET_AVATARS_DIR=/persistent-storage/preset-avatars
   ```

3. **Use avatar IDs** in your requests:
   - Specify `avatar_id: "avatar_001"` to use that preset avatar
   - The container will load the pre-encoded features instantly

**Benefits of preset avatars:**
- ~4s startup time vs ~6s for on-demand encoding
- Consistent performance across requests
- Reduced GPU utilization during runtime
- Ideal for frequently used avatar designs

**Image requirements:**
- High-quality portrait images (512x512 recommended)
- Front-facing photos with visible faces
- Good lighting and neutral expression
- File size under 10MB for optimal performance

## Cloud Deployment Guides

### Cerebrium

Cerebrium provides pay-per-second computing with automatic scaling and GPU support, making it ideal for production deployments with flexible request handling.

**Key Advantages:**
- ✅ **Pay-per-second billing** - Only pay when code is running, no idle costs
- ✅ **Automatic scaling** - Scales up/down based on concurrency utilization
- ✅ **Async API support** - Use `?async=true` URL parameter for non-blocking requests
- ✅ **GPU support** - Full GPU acceleration available (NVIDIA A10/A100)
- ✅ **Cost-efficient** - Perfect for variable workloads

**Reference:** [Cerebrium Documentation](https://docs.cerebrium.ai/)

#### Prerequisites

- Cerebrium account ([Sign up here](https://www.cerebrium.ai/))
- Cerebrium API key
- Understanding of Cerebrium deployment concepts

**Note:** No code changes or Docker image building required. The pre-built Docker image is available at `docker.io/bithumanhubs/gpu-avatar-worker:latest` and can be deployed directly.

#### Step 1: Prepare Configuration Files

Create the following files in your project directory:

**`Dockerfile.public`:**
```dockerfile
# Dockerfile for deploying from public Docker Hub image
# This file is used by Cerebrium to deploy the pre-built image

FROM docker.io/bithumanhubs/gpu-avatar-worker:latest

# Override ENTRYPOINT and CMD to prevent Cerebrium's uvicorn auto-detection
# Use shell form which is harder for Cerebrium to override
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["sh", "-c", "cd /app && python dispatcher_run.py --host 0.0.0.0 --port 8089"]
```

**`cerebrium.docker.toml`:**
```toml
# Cerebrium deployment configuration using public Docker image
#
# This configuration deploys GPU Avatar Worker using the pre-built public Docker
# image from Docker Hub, without building from source.
#
# Usage:
#   uv run cerebrium deploy --config-file cerebrium.docker.toml --disable-syntax-check

[cerebrium.deployment]
name = "gpu-avatar-worker"
# Only need the Dockerfile - all code is in the pre-built Docker image
include = [
    "Dockerfile.public"
]

[cerebrium.hardware]
# Hardware requirements for FLOAT model inference
cpu = 8                    # 8 CPU cores for audio/video processing
memory = 12.0             # 12GB RAM for model and buffers
compute = "AMPERE_A10"    # NVIDIA A10 GPU for fast inference
# Alternative options:
# compute = "AMPERE_A100"  # A100 for better performance
# compute = "VOLTA_A100G"  # A100 80GB for large batch sizes
region = "us-east-1"

[cerebrium.scaling]
min_replicas = 1          # Keep at least 1 replica warm (or 0 to scale to zero)
max_replicas = 30         # Maximum concurrent instances (platform limit: 30)
cooldown = 300            # 5 minutes before scaling down
replica_concurrency = 1   # One request per replica (GPU intensive)
response_grace_period = 43200  # 12 hours max request duration
scaling_target = 100
scaling_metric = "concurrency_utilization"

[cerebrium.runtime.custom]
port = 8089
healthcheck_endpoint = "/health"
# Use Dockerfile.public which pulls the pre-built image
dockerfile_path = "./Dockerfile.public"
# Use container command explicitly (WORKDIR is already /app)
container_command = "python dispatcher_run.py --host 0.0.0.0 --port 8089"
```

#### Step 2: Deploy to Cerebrium

**Using Cerebrium CLI:**
```bash
# Install Cerebrium CLI (if not already installed)
pip install cerebrium

# Set API key
export CEREBRIUM_API_KEY="your-api-key"

# Deploy using the configuration file
uv run cerebrium deploy --config-file cerebrium.docker.toml --disable-syntax-check
```

**Using Cerebrium Python SDK:**
```python
from cerebrium import Cerebrium

# Initialize Cerebrium client
cerebrium = Cerebrium(api_key="your-api-key")

# Deploy using configuration file
deployment = cerebrium.deploy_from_config(
    config_file="cerebrium.docker.toml",
    disable_syntax_check=True
)

print(f"Deployment ID: {deployment['id']}")
print(f"Endpoint URL: {deployment['endpoint_url']}")
```

#### Step 3: Verify Deployment

Once deployed, verify it's working:

```bash
# Get deployment status
cerebrium get deployment gpu-avatar-worker

# Test health endpoint
curl https://api.aws.us-east-1.cerebrium.ai/v4/{project}/gpu-avatar-worker/health

# Should return: {"status": "ok", "active_workers": 0, "available_slots": 1}
```

The endpoint is now ready to accept requests. No additional code or configuration is needed - the pre-built image contains everything required.

#### Scaling Configuration

Cerebrium scaling is based on `concurrency_utilization` metric. When all replicas are busy (each handling 1 request), Cerebrium automatically launches new replicas. Scaling decisions are made automatically by Cerebrium based on concurrency metrics.

**Key Configuration Parameters:**

| Parameter | Description | Recommended Value |
|-----------|-------------|-------------------|
| **min_replicas** | Minimum replicas to keep running | 0 (scale to zero) or 1 (always warm) |
| **max_replicas** | Maximum concurrent instances | 30 (platform limit: 30) |
| **cooldown** | Seconds before scaling down | 300 (5 minutes) |
| **replica_concurrency** | Requests per replica | 1 (GPU intensive) |
| **scaling_target** | Target concurrency utilization | 100 |
| **scaling_metric** | Metric for scaling decisions | `concurrency_utilization` |

**Important:** Cerebrium platform supports a maximum of **30 replicas** per deployment. This is a platform limitation and cannot be exceeded.

#### Cost-Optimized Configuration (Scale to Zero)

**Best for:** Variable workloads, cost optimization

```toml
[cerebrium.scaling]
min_replicas = 0          # Scale to zero when idle
max_replicas = 30         # Platform limit: 30
cooldown = 300            # 5 minutes
replica_concurrency = 1
scaling_target = 100
scaling_metric = "concurrency_utilization"
```

**Behavior:**
- Replicas scale to zero when no requests
- New replicas start on first request (~30-40s cold start)
- Replicas scale down after 5 minutes of idle time
- **Cost:** Only pay for actual compute time

**Trade-offs:**
- ✅ Lowest cost (no idle charges)
- ❌ Cold start latency (~30-40 seconds)
- ❌ First request slower

#### Fast Response Configuration (Always Warm)

**Best for:** Production with consistent traffic

```toml
[cerebrium.scaling]
min_replicas = 1          # Always keep 1 replica running
max_replicas = 30         # Platform limit: 30
cooldown = 600            # 10 minutes (longer for warm replicas)
replica_concurrency = 1
scaling_target = 100
scaling_metric = "concurrency_utilization"
```

**Behavior:**
- At least 1 replica always running
- New replicas start when existing replicas are busy
- Replicas scale down after 10 minutes of idle (if count > min)
- **Cost:** Pay for at least 1 replica continuously

**Trade-offs:**
- ✅ Fast response (~4-6 seconds)
- ✅ No cold start for first request
- ❌ Higher cost (always paying for 1 replica)

#### Hybrid Configuration (Recommended)

**Best for:** Production with variable traffic

```toml
[cerebrium.scaling]
min_replicas = 1          # Keep 1 warm during business hours
max_replicas = 30         # Platform limit: 30
cooldown = 300            # 5 minutes
replica_concurrency = 1
scaling_target = 100
scaling_metric = "concurrency_utilization"
```

**Behavior:**
- 1 replica always running (fast first response)
- Additional replicas scale based on demand
- Extra replicas scale down after 5 minutes idle
- **Cost:** Moderate (pay for 1 replica + actual usage)

#### Resource Requirements

**Per Replica:**
- **CPU:** 8 vCPU cores (recommended for model loading and I/O operations)
- **Memory:** 12 GB RAM (sufficient for model caching and preset avatar features)
- **GPU:** 1 GPU (A10 or A100 recommended)
- **VRAM:** 16 GB minimum (A10), 24 GB recommended (A100)

**Resource Usage Analysis:**

When using prewarm (recommended), avatar loading is **primarily memory-intensive**:

- **GPU VRAM:** ~6 GB (model weights loaded during prewarm, stays in GPU)
- **CPU Memory:**
  - Model file cache: ~2-3 GB (if using shared model state)
  - Preset avatar features: ~50-100 MB per avatar (encoded features cached in CPU memory)
  - Runtime buffers: ~1-2 GB
  - Python runtime: ~500 MB-1 GB
  - **Total: ~4-6 GB for base + ~100 MB per preset avatar**

- **CPU Usage:**
  - Model loading (one-time at startup): Moderate CPU usage for I/O and initialization
  - Avatar loading (with prewarm): Low CPU usage (mainly memory reads)
  - Inference: Low CPU usage (GPU handles computation, CPU handles data transfer)

**Why 8 CPU cores?**
- Faster model loading at startup (parallel I/O operations)
- Better handling of concurrent operations (model loading, avatar encoding, data preprocessing)
- Sufficient headroom for system processes and overhead

**Why 12 GB Memory?**
- Sufficient for model caching (~2-3 GB)
- Room for preset avatar features (~100 MB per avatar, scales with number of avatars)
- Runtime buffers and Python overhead (~2-3 GB)
- Safety margin for peak usage

#### Best Practices

1. **Use Async Requests for Long-Running Tasks**
   - All requests should use `?async=true` parameter for non-blocking behavior
   - API returns immediately with `task_id` for status tracking

2. **Configure Appropriate Cooldown**
   - Set `cooldown` based on your traffic patterns
   - High traffic, consistent load: `cooldown = 600` (10 minutes)
   - Variable traffic: `cooldown = 300` (5 minutes)
   - Low traffic, cost-sensitive: `cooldown = 180` (3 minutes)

3. **Monitor Replica Health**
   - Regularly check `/health` endpoint
   - Monitor concurrency utilization metrics
   - Track replica count and cold start frequency

4. **Handle Rate Limits**
   - Implement retry logic for rate-limited requests
   - Use exponential backoff for retries

### Other Cloud Platforms

> **Note:** Integration guides for other cloud platforms (AWS ECS, Google Cloud Run, Azure Container Instances, etc.) will be added in future updates. Please check back for additional deployment options.

## Troubleshooting

### Container won't start

**Symptom:** Container exits immediately

**Solutions:**
1. Check GPU availability: `nvidia-smi`
2. Verify storage volume mount
3. Check logs: `docker logs <container-id>`

### High first frame latency

**Symptom:** First frame takes >10 seconds

**Solutions:**
1. Configure PRESET_AVATARS_DIR for pre-processed avatars
2. Use long-running containers instead of cold start
3. Increase GPU memory allocation
4. Check avatar engine initialization in logs

### Out of memory errors

**Symptom:** GPU out of memory errors

**Solutions:**
1. Increase container memory limit
2. Reduce audio buffer configuration
3. Use larger GPU instance
4. Limit concurrent requests per container

### Slow encoding performance

**Symptom:** Avatar processing takes >2 seconds

**Solutions:**
1. Pre-process avatars into PRESET_AVATARS_DIR
2. Use GPU with more compute cores
3. Optimize image size before upload
4. Check GPU utilization with `nvidia-smi`

## Next Steps

- **Integration Guide**: See [Custom GPU Endpoint Integration](https://github.com/bithuman-prod/public-docs/tree/main/examples/cloud/expression#%EF%B8%8F-example-3-custom-gpu-endpoint)
- **LiveKit Plugins**: Install required `livekit-plugins-bithuman` package
- **Monitoring**: Set up monitoring dashboards and alerts for your deployment
- **Scaling**: Configure auto-scaling policies based on traffic patterns

## Additional Resources

- [Docker Hub Image](https://hub.docker.com/r/bithumanhubs/gpu-avatar-worker)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [Cerebrium Documentation](https://docs.cerebrium.ai/)
