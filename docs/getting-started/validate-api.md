# Validate Your API Secret

Before building with bitHuman SDK, let's make sure your API secret is working correctly.

## Quick Validation Test

Create a simple script to test your API secret:

```python
# validate_api.py
import asyncio
import os
from bithuman.runtime import AsyncBithuman

async def validate_api_secret():
    try:
        # Get API secret from environment or replace with your secret
        api_secret = os.getenv('BITHUMAN_API_SECRET', 'your_api_secret_here')
        model_path = os.getenv('BITHUMAN_AVATAR_MODEL', '/path/to/model.imx')
        
        print("🔍 Validating API secret...")
        
        # Initialize runtime - this validates your API secret
        runtime = await AsyncBithuman.create(
            api_secret=api_secret,
            model_path=model_path
        )
        
        print("✅ API secret is valid!")
        print("✅ Model loaded successfully!")
        print("🎉 You're ready to build with bitHuman SDK!")
        
        # Clean up
        await runtime.close()
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        print("🔧 Check the troubleshooting section below")

if __name__ == "__main__":
    asyncio.run(validate_api_secret())
```

Run the validation:

```bash
python validate_api.py
```

## Expected Output

### ✅ Success
```
🔍 Validating API secret...
✅ API secret is valid!
✅ Model loaded successfully!
🎉 You're ready to build with bitHuman SDK!
```

### ❌ Common Errors

#### Invalid API Secret
```
❌ Validation failed: Invalid API secret
```

**Causes:**
- Wrong API secret
- Extra spaces or characters
- API secret not set in environment

**Solutions:**
1. Double-check your API secret from [console.bithuman.io](https://console.bithuman.io)
2. Make sure you copied it completely
3. Check for trailing spaces

#### Model File Not Found
```
❌ Validation failed: Model file not found: /path/to/model.imx
```

**Solutions:**
1. Verify the model file path is correct
2. Download a model from the [Community page](https://console.bithuman.io/#community)
3. Check file permissions

#### Network Issues
```
❌ Validation failed: Connection timeout
```

**Solutions:**
1. Check your internet connection
2. Verify firewall settings allow HTTPS traffic
3. Try again in a few minutes

## Detailed Validation Script

For more thorough testing, use this enhanced validation script:

```python
# detailed_validation.py
import asyncio
import os
import sys
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk
import numpy as np

async def detailed_validation():
    api_secret = os.getenv('BITHUMAN_API_SECRET')
    model_path = os.getenv('BITHUMAN_AVATAR_MODEL')
    
    # Check environment variables
    print("🔍 Checking environment setup...")
    
    if not api_secret:
        print("❌ BITHUMAN_API_SECRET not set")
        print("   Set it with: export BITHUMAN_API_SECRET='your_secret'")
        return False
    
    if not model_path:
        print("❌ BITHUMAN_AVATAR_MODEL not set")
        print("   Set it with: export BITHUMAN_AVATAR_MODEL='/path/to/model.imx'")
        return False
    
    print(f"✅ API secret: {api_secret[:8]}...")
    print(f"✅ Model path: {model_path}")
    
    # Test model file access
    print("\n🔍 Checking model file...")
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return False
    
    print(f"✅ Model file exists: {os.path.getsize(model_path)} bytes")
    
    # Test API connection and model loading
    print("\n🔍 Testing API connection...")
    try:
        runtime = await AsyncBithuman.create(
            api_secret=api_secret,
            model_path=model_path
        )
        print("✅ API connection successful")
        print("✅ Model loaded successfully")
        
        # Test basic audio processing
        print("\n🔍 Testing audio processing...")
        
        # Create test audio (1 second of silence)
        sample_rate = 16000
        duration = 1.0
        test_audio = np.zeros(int(sample_rate * duration), dtype=np.int16)
        audio_chunk = AudioChunk.from_numpy(test_audio, sample_rate)
        
        # Process audio
        async for video_frame in runtime.process_audio_chunk(audio_chunk):
            print(f"✅ Received video frame: {video_frame.image.shape}")
            break  # Just test one frame
        
        print("✅ Audio processing successful")
        print("\n🎉 Full validation completed successfully!")
        print("   You're ready to build amazing applications with bitHuman SDK!")
        
        await runtime.close()
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(detailed_validation())
    sys.exit(0 if success else 1)
```

## Environment Variable Verification

### Check Current Settings

```bash
# Check if environment variables are set
echo "API Secret: ${BITHUMAN_API_SECRET:0:8}..."
echo "Model Path: $BITHUMAN_AVATAR_MODEL"
```

### Set Environment Variables

#### Linux/macOS
```bash
export BITHUMAN_API_SECRET='your_api_secret_here'
export BITHUMAN_AVATAR_MODEL='/path/to/your/model.imx'
```

#### Windows (PowerShell)
```powershell
$env:BITHUMAN_API_SECRET='your_api_secret_here'
$env:BITHUMAN_AVATAR_MODEL='C:\path\to\your\model.imx'
```

#### Windows (Command Prompt)
```cmd
set BITHUMAN_API_SECRET=your_api_secret_here
set BITHUMAN_AVATAR_MODEL=C:\path\to\your\model.imx
```

## Using .env Files

For development, create a `.env` file:

```bash
# .env
BITHUMAN_API_SECRET=your_api_secret_here
BITHUMAN_AVATAR_MODEL=/path/to/your/model.imx

# Optional: Set log level
BITHUMAN_LOG_LEVEL=INFO
```

Then load it in your script:

```python
from dotenv import load_dotenv
load_dotenv()

# Now environment variables are available
api_secret = os.getenv('BITHUMAN_API_SECRET')
```

## API Secret Management Best Practices

### ✅ Do:
- Store API secrets in environment variables
- Use `.env` files for development
- Keep API secrets out of version control
- Rotate API secrets regularly
- Use different secrets for different environments

### ❌ Don't:
- Hard-code API secrets in source code
- Share API secrets in chat or email
- Commit API secrets to git repositories
- Use production secrets in development

## Getting New API Secrets

If you need to create additional API secrets:

1. Go to [console.bithuman.io](https://console.bithuman.io)
2. Navigate to **SDK** section
3. Click **Create New Secret**
4. Give it a descriptive name
5. Copy the secret immediately (you won't see it again)

## Troubleshooting

### API Secret Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid API secret` | Wrong or expired secret | Get new secret from console |
| `API secret not found` | Environment variable not set | Set `BITHUMAN_API_SECRET` |
| `Authentication failed` | Network/server issue | Try again in a few minutes |

### Model File Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `Model file not found` | Wrong path | Check file path and existence |
| `Invalid model format` | Wrong file type | Ensure file has `.imx` extension |
| `Model loading failed` | Corrupted file | Re-download model |

## Next Steps

Once your API secret is validated:

1. **[Run your first model](first-model.md)** - Create your first animated avatar
2. **[Explore examples](../examples/voice-driven-audio.md)** - See working applications
3. **[Learn about integrations](../integrations/livekit.md)** - Add avatars to existing apps

## Getting Help

If validation continues to fail:

- Check our [installation guide](installation.md) again
- Visit our [Community Hub](https://console.bithuman.io/#community)
- Join our Discord for real-time help
- Contact support through the console

Your API secret is the key to unlocking bitHuman's capabilities. Let's move on to [running your first model](first-model.md)! 