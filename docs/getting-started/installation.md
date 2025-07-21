# Installation

Get the bitHuman SDK installed and configured in just a few minutes.

## Prerequisites

### System Requirements

- **Python**: 3.10, 3.11, 3.12, or 3.13
- **Operating System**: 
  - Linux (x86_64 or ARM64)
  - macOS 15+ (Apple Silicon)
  - Windows (coming soon)

### Check Your Python Version

```bash
python --version
# or
python3 --version
```

If you need to install Python, visit [python.org](https://www.python.org/downloads/).

## Step 1: Install bitHuman SDK

### Using pip (Recommended)

```bash
pip install bithuman
```

### Using pip with Python 3 explicitly

```bash
pip3 install bithuman
```

### Install in a Virtual Environment (Recommended)

```bash
# Create a virtual environment
python -m venv bithuman-env

# Activate it
source bithuman-env/bin/activate  # On Linux/macOS
# bithuman-env\Scripts\activate   # On Windows

# Install the SDK
pip install bithuman
```

## Step 2: Get Your API Secret

1. Visit [console.bithuman.io](https://console.bithuman.io)
2. Register for a free account
3. Navigate to the **SDK** section
4. Create a new API secret
5. Copy your API secret (keep it secure!)

## Step 3: Download an Avatar Model

You'll need a `.imx` model file to run bitHuman avatars:

1. Go to the [Community page](https://console.bithuman.io/#community)
2. Browse available avatar models
3. Click on any avatar to download the `.imx` file
4. Save it to a location you'll remember

## Step 4: Configure Environment Variables

### Option A: Environment Variables

```bash
export BITHUMAN_API_SECRET='your_api_secret_here'
export BITHUMAN_AVATAR_MODEL='/path/to/your/model.imx'
```

### Option B: .env File (Recommended for Development)

Create a `.env` file in your project directory:

```bash
# .env file
BITHUMAN_API_SECRET=your_api_secret_here
BITHUMAN_AVATAR_MODEL=/path/to/your/model.imx
```

Then install python-dotenv:

```bash
pip install python-dotenv
```

And load it in your Python code:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Step 5: Verify Installation

Create a simple test file to verify everything works:

```python
# test_installation.py
import asyncio
from bithuman.runtime import AsyncBithuman

async def test_installation():
    try:
        # Initialize runtime (this validates your API secret and model)
        runtime = await AsyncBithuman.create(
            api_secret="your_api_secret",  # or use environment variable
            model_path="/path/to/model.imx"  # or use environment variable
        )
        print("✅ bitHuman SDK installed and configured successfully!")
        await runtime.close()
    except Exception as e:
        print(f"❌ Installation test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_installation())
```

Run the test:

```bash
python test_installation.py
```

## Common Installation Issues

### Issue: Module Not Found

```
ImportError: No module named 'bithuman'
```

**Solution**: Make sure you're using the correct Python environment:

```bash
# Check which Python you're using
which python
which pip

# Make sure you installed in the right environment
pip list | grep bithuman
```

### Issue: API Secret Invalid

```
Exception: Invalid API secret
```

**Solution**: 
1. Double-check your API secret from the console
2. Make sure there are no extra spaces or quotes
3. Verify environment variables are set correctly

### Issue: Model File Not Found

```
Exception: Model file not found
```

**Solution**:
1. Check the file path is correct
2. Ensure the file has `.imx` extension
3. Verify file permissions

### Issue: Platform Not Supported

```
Exception: Platform not supported
```

**Solution**: Check our [supported platforms](#prerequisites). Contact support if you need Windows support.

## Advanced Installation Options

### Installing with Optional Dependencies

For specific integrations, you might need additional packages:

```bash
# For LiveKit integration
pip install "bithuman[livekit]"

# For development tools
pip install "bithuman[dev]"

# For all optional dependencies
pip install "bithuman[all]"
```

### Installing from Source (Advanced)

```bash
git clone https://github.com/bithuman-io/python-sdk.git
cd python-sdk
pip install -e .
```

## Docker Installation

### Using Pre-built Image

```dockerfile
FROM bithuman/python-sdk:latest

COPY . /app
WORKDIR /app

ENV BITHUMAN_API_SECRET=your_secret
ENV BITHUMAN_AVATAR_MODEL=/app/model.imx

CMD ["python", "your_app.py"]
```

### Building Your Own Image

```dockerfile
FROM python:3.11-slim

RUN pip install bithuman

# Copy your application
COPY . /app
WORKDIR /app

CMD ["python", "your_app.py"]
```

## Next Steps

Now that you have bitHuman SDK installed:

1. **[Validate your API secret](validate-api.md)** - Test your credentials
2. **[Run your first model](first-model.md)** - Create your first avatar
3. **[Browse examples](../examples/voice-driven-audio.md)** - See working code samples

## Getting Help

If you encounter any installation issues:

- Check our [troubleshooting guide](#common-installation-issues)
- Visit our [Community Hub](https://console.bithuman.io/#community)
- Ask questions on our Discord server
- Create an issue on GitHub

The installation should take less than 5 minutes. Let's move on to [validating your API secret](validate-api.md)! 