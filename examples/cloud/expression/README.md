# Cloud Expression - Advanced Avatar Examples

This directory contains advanced examples showcasing different ways to create expressive bitHuman avatars for LiveKit agents. Choose between using pre-configured avatar IDs or custom avatar images.

## 📁 Files Overview

- `agent_with_avatar_id.py` - Uses pre-configured avatar from bitHuman cloud
- `agent_with_avatar_image.py` - Uses custom avatar images (local files or URLs)
- `agent_with_custom_gpu_endpoint.py` - Uses self-hosted GPU worker (Docker, AWS, GCP)
- `custom_gpu_endpoint.env.example` - Environment configuration for custom GPU endpoint
- `avatar.jpg` - Sample avatar image (you can replace with your own)
- `README.md` - This documentation

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all required packages from requirements.txt
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in this directory:

```bash
# bitHuman API Configuration
BITHUMAN_API_SECRET=sk_bh_your_api_secret_here

# Avatar Configuration (choose one method)
BITHUMAN_AVATAR_ID=A05XGC2284                    # For avatar_id method
BITHUMAN_AVATAR_IMAGE=/path/to/your/image.jpg    # For avatar_image method (local file)
# BITHUMAN_AVATAR_IMAGE=https://example.com/avatar.jpg  # For avatar_image method (URL)

# OpenAI Configuration
OPENAI_API_KEY=sk-proj_your_openai_api_key_here
OPENAI_VOICE=coral                               # Options: alloy, echo, fable, onyx, nova, shimmer, coral

# Avatar Personality (optional)
AVATAR_PERSONALITY="You are a friendly and expressive virtual assistant..."

# LiveKit Configuration
LIVEKIT_API_KEY=APIyour_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

## 🎭 Example 1: Avatar with ID

Uses pre-configured avatars from the bitHuman platform.

### Features
- Pre-trained avatar models with optimized expressions
- Consistent quality and performance
- Easy to swap between different avatar personalities
- Enhanced expression controls

### Usage

```bash
python agent_with_avatar_id.py dev
```

### Configuration

Edit the avatar ID in the script or use environment variables:

```python
avatar_id=os.getenv("BITHUMAN_AVATAR_ID", "A05XGC2284")
```

**Finding Avatar IDs:**
1. Visit [imaginex.bithuman.ai/#community](https://imaginex.bithuman.ai/#community)
2. Browse available avatars
3. Copy the ID from your chosen model

## 🖼️ Example 2: Avatar with Custom Image

Uses your own images to create personalized avatars.

### Features
- Support for local image files (JPG, PNG, etc.)
- Support for image URLs
- Automatic face detection and cropping
- Custom expression scaling
- Flexible image sources

### Usage

```bash
python agent_with_avatar_image.py dev
```

### Image Sources

The script supports multiple image sources (in priority order):

1. **Environment variable** (`BITHUMAN_AVATAR_IMAGE`)
2. **Local file** (`avatar.jpg` in the same directory)
3. **Default URL** (fallback example image)

### Supported Image Formats

#### Local Files
```bash
# Set in .env file
BITHUMAN_AVATAR_IMAGE=/path/to/your/photo.jpg
BITHUMAN_AVATAR_IMAGE=./my_avatar.png
BITHUMAN_AVATAR_IMAGE=../images/portrait.jpeg
```

#### URLs
```bash
# Set in .env file
BITHUMAN_AVATAR_IMAGE=https://example.com/avatar.jpg
BITHUMAN_AVATAR_IMAGE=https://your-cdn.com/profile.png
```

#### Code Examples
```python
# Local file
avatar_image = Image.open(os.path.join(os.path.dirname(__file__), "avatar.jpg"))

# URL
avatar_image = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"

# Environment variable
avatar_image = os.getenv("BITHUMAN_AVATAR_IMAGE")
```

## 🖥️ Example 3: Custom GPU Endpoint

Use a self-hosted or cloud-deployed GPU avatar worker for maximum control and customization.

> **Preview Feature**: This example requires a special version of the `livekit-plugins-bithuman` package. See [Plugin Installation](#plugin-installation) below.

### Features
- **Self-hosted GPU workers** - Deploy on your own infrastructure (AWS, GCP, Azure)
- **Cost optimization** - Pay only for the GPU resources you use
- **Data privacy** - Avatar images and audio never leave your infrastructure
- **Preset avatar caching** - Pre-encode avatars for ~4s startup time
- **Full control** - Extend with custom logic and integrations

### Supported Deployments

| Platform | Deployment Mode | Scaling Strategy |
|----------|----------------|------------------|
| **Cerebrium** | Serverless GPU | 0-30 replicas, scale-to-zero |
| **AWS ECS** | Fargate with GPU | 1-10 tasks, auto-scaling |
| **Google Cloud Run** | GPU containers | 0-100 instances, scale-to-zero |
| **Self-hosted** | Docker with GPU | Manual or external orchestration |

### Usage

```bash
python agent_with_custom_gpu_endpoint.py dev
```

### Configuration

Create a `.env` file from the example:

```bash
cp custom_gpu_endpoint.env.example .env
```

**Required Environment Variables:**

```bash
# BitHuman API secret for authorization and authentication (required)
BITHUMAN_API_SECRET=sk_bh_your_api_secret_here

# Your custom GPU worker endpoint
CUSTOM_GPU_URL=https://your-gpu-worker.com/launch

# API token for Bearer authentication with custom GPU endpoint (required)
CUSTOM_GPU_TOKEN=your_api_token_here

# LiveKit configuration
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# OpenAI for voice
OPENAI_API_KEY=sk-your-openai-api-key
```

**Optional: Custom Avatar Image**

```bash
# Use a custom avatar image
BITHUMAN_AVATAR_IMAGE=/path/to/your/avatar.jpg
# or
BITHUMAN_AVATAR_IMAGE=https://example.com/avatar.jpg
```

### Endpoint URL Formats

**Cerebrium:**
```
https://api.aws.us-east-1.cerebrium.ai/v4/p-xxxxx/gpu-avatar-worker/launch
```

**AWS ECS (with Load Balancer):**
```
https://gpu-worker-elb.us-east-1.elb.amazonaws.com/launch
```

**Google Cloud Run:**
```
https://gpu-avatar-worker-xxxxx.a.run.app/launch
```

**Local Development:**
```
http://localhost:8089/launch
```

### Plugin Installation

> **Important**: This example requires a special version of the `livekit-plugins-bithuman` package with custom GPU endpoint support.

**Install the required version:**

```bash
# Install from the feature branch
pip install "livekit-plugins-bithuman @ git+https://github.com/CathyL0/agents.git@feat/add-custom-bithuman-gpu-avatar-endpoint#subdirectory=livekit-plugins/livekit-plugins-bithuman"
```

**Add to your `requirements.txt`:**

```txt
# Custom GPU endpoint support (preview feature)
livekit-plugins-bithuman @ git+https://github.com/CathyL0/agents.git@feat/add-custom-bithuman-gpu-avatar-endpoint#subdirectory=livekit-plugins/livekit-plugins-bithuman
```

### Deployment Guides

#### Quick Deploy with Docker

```bash
# Pull the official image
docker pull docker.io/bithumanhubs/gpu-avatar-worker:latest

# Run with GPU support
docker run --gpus all -p 8089:8089 \
    -v /path/to/model-storage:/persistent-storage/avatar-model \
    docker.io/bithumanhubs/gpu-avatar-worker:latest

# Test the endpoint
curl http://localhost:8089/health
# Should return: {"status": "ok", "active_workers": 0}
```

#### Deploy on AWS ECS

For production deployment on AWS with auto-scaling, see the [Self-Hosted GPU Container](../../../docs/preview/self-hosted-gpu-container.md) guide which includes:

- Complete ECS task definition with GPU support
- Auto-scaling policies (long-running vs cold start)
- Recommended GPU instance types (g4dn, g5, p3)
- Cost estimation and optimization strategies
- Security and networking configuration

### Performance Comparison

| Configuration | First Frame | Notes |
|---------------|-------------|-------|
| **Long-running + Preset Cache** | ~4s | Avatar images pre-encoded, fastest startup |
| **Long-running + No Cache** | ~6s | Avatar encoding on first request |
| **Cold Start** | ~30-40s | Full avatar engine initialization |

### Preset Avatar Directory

For optimal performance with long-running containers, configure `PRESET_AVATARS_DIR`:

```bash
docker run --gpus all -p 8089:8089 \
    -v /path/to/model-storage:/persistent-storage/avatar-model \
    -v /path/to/preset-avatars:/persistent-storage/preset-avatars \
    -e AVATAR_MODEL_DIR=/persistent-storage/avatar-model \
    -e PRESET_AVATARS_DIR=/persistent-storage/preset-avatars \
    docker.io/bithumanhubs/gpu-avatar-worker:latest
```

**Directory Structure:**
```
/persistent-storage/preset-avatars/
├── avatar_001/
│   └── face.jpg          # Image file (avatar_001 is the avatar_id)
├── avatar_002/
│   └── portrait.png      # Image file (avatar_002 is the avatar_id)
└── avatar_003/
    └── avatar.webp       # Image file (avatar_003 is the avatar_id)
```

Each subdirectory name becomes the `avatar_id` for that preset. The container automatically pre-encodes these images at startup for instant loading.

See the [Self-Hosted GPU Container](../../../docs/preview/self-hosted-gpu-container.md) guide for more details.

### Worker Options

The agent is configured with optimized settings for GPU avatar processing:

```python
WorkerOptions(
    entrypoint_fnc=entrypoint,
    worker_type=WorkerType.ROOM,
    # Higher memory limit for GPU avatar processing
    job_memory_warn_mb=3000,
    num_idle_processes=1,
    # Longer timeout for GPU model initialization
    initialize_process_timeout=240,
)
```

### API Reference

**Launch Endpoint:**

```http
POST /launch
Content-Type: multipart/form-data

livekit_url: wss://your-livekit-server
livekit_token: <jwt_token>
room_name: my-room
avatar_image: <file>  # or avatar_image_url: https://...
```

**Response:**
```json
{
  "status": "launched",
  "worker_id": "worker_abc123"
}
```

### Troubleshooting

**Connection fails:**
```bash
# Verify endpoint is accessible
curl http://your-gpu-worker:8089/health

# Check authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://your-gpu-worker:8089/health
```

**High first frame latency:**
- Verify PRESET_AVATARS_DIR is configured (for ~4s startup)
- Use long-running containers instead of cold start
- Check GPU utilization: `nvidia-smi`

**Plugin not found:**
```bash
# Verify installation
pip show livekit-plugins-bithuman

# Reinstall if needed
pip install --force-reinstall \
  "livekit-plugins-bithuman @ git+https://github.com/CathyL0/agents.git@feat/add-custom-bithuman-gpu-avatar-endpoint#subdirectory=livekit-plugins/livekit-plugins-bithuman"
```

## 🧪 Testing Your Avatars

### Option A: LiveKit Playground (Recommended) 🎮

1. **Start your chosen agent**:
   ```bash
   # For avatar_id example
   python agent_with_avatar_id.py dev
   
   # OR for avatar_image example  
   python agent_with_avatar_image.py dev
   ```
   Wait for the message: "Agent is ready and waiting for participants"

2. **Open LiveKit Playground**: Visit [agents-playground.livekit.io](https://agents-playground.livekit.io)

3. **Connect to your project**:
   - Click "Continue with LiveKit Cloud"
   - Use the **same LiveKit credentials** from your `.env` file:
     - **API Key**: Your `LIVEKIT_API_KEY` 
     - **API Secret**: Your `LIVEKIT_API_SECRET`
     - **URL**: Your `LIVEKIT_URL`

4. **Join and test**:
   - Click "Connect" to join the room
   - **⏱️ Connection time**: 
     - **Avatar ID**: ~30-45 seconds for initialization
     - **Avatar Image**: ~1 minute for image processing and initialization
   - Grant microphone permissions when prompted
   - Start talking to your avatar!

### Option B: Local Web Interface

1. Run your agent in dev mode and note the local web interface URL
2. Open the provided URL in your browser
3. Grant microphone/camera permissions and test

### 🔄 Testing Different Configurations

**Quick Avatar ID Switch**:
```bash
# Test different avatars quickly
BITHUMAN_AVATAR_ID="A05XGC2284" python agent_with_avatar_id.py dev
BITHUMAN_AVATAR_ID="ANOTHER_ID" python agent_with_avatar_id.py dev
```

**Quick Image Switch**:
```bash
# Test with URL
BITHUMAN_AVATAR_IMAGE="https://example.com/avatar.jpg" python agent_with_avatar_image.py dev

# Test with local file
BITHUMAN_AVATAR_IMAGE="./my_photo.jpg" python agent_with_avatar_image.py dev
```

## 🎨 Customization Options

### Expression Settings

Both examples support enhanced expression controls:

```python
bithuman_avatar = bithuman.AvatarSession(
    api_secret=os.getenv("BITHUMAN_API_SECRET"),
    avatar_id="YOUR_ID",  # or avatar_image=your_image
    
    # Expression customization
    avatar_motion_scale=1.0,      # Motion intensity (0.0-2.0)
    avatar_expression_scale=1.5,  # Expression intensity (0.0-2.0)
    
    # Image processing (for avatar_image only)
    enable_face_detection=True,   # Auto-detect face
    crop_to_face=True,           # Auto-crop to face region
)
```

### Voice Customization

Configure different OpenAI voices:

```python
llm=openai.realtime.RealtimeModel(
    voice="nova",  # Available: alloy, echo, fable, onyx, nova, shimmer, coral
    model="gpt-4o-mini-realtime-preview",
)
```

### Personality Customization

Set custom personalities via environment variables or directly in code:

```bash
# In .env
AVATAR_PERSONALITY="You are a professional customer service representative with a warm personality..."
```

## 📷 Preparing Your Avatar Images

### Image Requirements
- **Format**: JPG, PNG, WebP
- **Size**: Minimum 256x256, recommended 512x512 or higher
- **Aspect ratio**: Square (1:1) works best
- **Quality**: Clear, well-lit face photo
- **Background**: Any (will be automatically processed)

### Best Practices
1. **Face visibility**: Ensure the face is clearly visible and well-lit
2. **Expression**: Use a neutral or slightly positive expression
3. **Angle**: Front-facing photos work best
4. **Resolution**: Higher resolution = better avatar quality
5. **File size**: Keep under 10MB for faster processing

### Image Sources
- Personal photos
- Stock photography
- AI-generated portraits
- Professional headshots
- Webcam captures

## 🔧 Troubleshooting

### Common Issues

1. **Image loading errors**
   ```bash
   # Check file path
   ls -la /path/to/your/image.jpg
   
   # Check URL accessibility
   curl -I https://your-image-url.jpg
   ```

2. **Face detection failures**
   - Ensure the face is clearly visible
   - Try images with better lighting
   - Use front-facing photos

3. **Memory issues**
   - Reduce image size before processing
   - Use compressed image formats
   - Increase `job_memory_warn_mb` in WorkerOptions

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Performance Tips

1. **Image optimization**: Resize images to 512x512 for optimal performance
2. **Local files**: Use local files instead of URLs for faster loading
3. **Memory management**: Monitor memory usage with large images
4. **Caching**: The system caches processed avatars for better performance

## 📚 Next Steps

- [Self-Hosted GPU Container Guide](../../../docs/preview/self-hosted-gpu-container.md) - Deploy GPU workers on AWS, GCP, or your own infrastructure
- Learn about [advanced LiveKit features](https://docs.livekit.io/agents)
- Explore [bitHuman avatar customization](https://docs.bithuman.ai)
- Try the [basic essence example](../essence/) for simpler setup
- Join our [Discord community](https://discord.gg/ES953n7bPA) for tips and tricks

## 🆘 Support

- 💬 [Discord Community](https://discord.gg/ES953n7bPA)
- 📖 [bitHuman Documentation](https://docs.bithuman.ai)
- 🔧 [LiveKit Documentation](https://docs.livekit.io/agents)
- 🎨 [Image Guidelines](https://docs.bithuman.ai/guides/image-preparation)
