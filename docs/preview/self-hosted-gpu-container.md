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
