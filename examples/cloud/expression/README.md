# Cloud Expression - Advanced Avatar Examples

This directory contains advanced examples showcasing different ways to create expressive bitHuman avatars for LiveKit agents. Choose between using pre-configured avatar IDs or custom avatar images.

## 📁 Files Overview

- `agent_with_avatar_id.py` - Uses pre-configured avatar from bitHuman cloud
- `agent_with_avatar_image.py` - Uses custom avatar images (local files or URLs)
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

- Learn about [advanced LiveKit features](https://docs.livekit.io/agents)
- Explore [bitHuman avatar customization](https://docs.bithuman.ai)
- Try the [basic essence example](../essence/) for simpler setup
- Join our [Discord community](https://discord.gg/ES953n7bPA) for tips and tricks

## 🆘 Support

- 💬 [Discord Community](https://discord.gg/ES953n7bPA)
- 📖 [bitHuman Documentation](https://docs.bithuman.ai)
- 🔧 [LiveKit Documentation](https://docs.livekit.io/agents)
- 🎨 [Image Guidelines](https://docs.bithuman.ai/guides/image-preparation)
