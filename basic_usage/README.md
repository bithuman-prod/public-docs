# Bithuman Runtime Example

This example demonstrates how to use the Bithuman Runtime to create an interactive avatar that responds to audio input.

## Installation

1. System requirements

   **Supported Python Versions:**
   - Python 3.10
   - Python 3.11
   - Python 3.12
   - Python 3.13

   **Supported Operating Systems:**
   - Linux (x86_64 and arm64)
   - macOS (Apple Silicon)


2. Install bithuman:
   ```bash
   pip install bithuman
   ```

3. Install the example dependencies for audio playing:
   ```bash
   pip install sounddevice
   ```

## Setup

### 1. Register and Get API Secret

1. Go to [https://console.bithuman.io](https://console.bithuman.io) and register for free
2. After registration, navigate to the **SDK** page to create a new API secret
3. Copy your API secret for use in the example

### 2. Download Avatar Model

You'll need a Bithuman avatar model (`.imx` file) to run the example. These models define the appearance and behavior of your virtual avatar.

1. Visit the [Community page](https://console.bithuman.io/#community)
2. Browse the available avatar models
3. Click on any agent card to download the `.imx` model file directly

## Running the Example

Run the example with the following command:

```bash
export BITHUMAN_API_SECRET='your_api_secret'
python example.py --audio-file <audio file> --model <model file>
```


## Example Controls

While the example is running, you can use the following keyboard controls:
- Press `1`: Play the specified audio file through the avatar
- Press `2`: Interrupt the current playback
- Press `q`: Exit the application

## How It Works

The example demonstrates:
1. Initializing the Bithuman Runtime with your API secret
2. Setting up audio and video players
3. Processing audio input and rendering the avatar's response
4. Handling user interactions

The avatar will animate in response to the audio input, creating a lifelike interactive experience.

## API Overview

The Bithuman Runtime API provides a powerful interface for creating interactive avatars:

### Core Components

1. **AsyncBithuman**: The main class that handles communication with the Bithuman service.
   - Initialize with your API secret: `runtime = AsyncBithuman(api_secret="your_api_secret")`
   - Set avatar model: `await runtime.set_avatar_model("path/to/model.imx")`
   - Process audio: Send audio data to animate the avatar
   - Interrupt: Cancel ongoing speech with `runtime.interrupt()`

2. **AudioChunk**: Represents audio data for processing.
   - Accepts 16kHz, mono, int16 format audio
   - Can be created from bytes or numpy arrays
   - Provides duration and format conversion utilities

3. **VideoFrame**: Contains the output from the runtime.
   - BGR image data (numpy array)
   - Synchronized audio chunks
   - Frame metadata (index, message ID)


### Input/Output Flow

1. **Input**:
   - Send audio data (16kHz, mono, int16 format) to the runtime
   - The runtime processes this input to generate appropriate avatar animations

2. **Processing**:
   - The runtime analyzes the audio to determine appropriate facial movements and expressions
   - Frames are generated at 25 FPS with synchronized audio

3. **Output**:
   - Each frame contains both visual data (BGR image) and the corresponding audio chunk
   - The example shows how to render these frames and play the audio in real-time

