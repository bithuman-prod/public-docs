# Avatar Echo Example

This example demonstrates how to capture audio from your microphone, process it with the bitHuman SDK, and display the animated avatar in a local window.

## Prerequisites

- Python 3.10+
- bitHuman SDK installed
- Audio input device (microphone)

## Installation

Install the required dependencies:

```bash
pip install bithuman
pip install sounddevice  # For audio playback
```

## Configuration

Set your Bithuman token and avatar model path as environment variables:

```bash
export BITHUMAN_API_SECRET='your_api_secret'
export BITHUMAN_AVATAR_MODEL='/path/to/model/avatar.imx'
```

## Running the Example

Run the example with:

```bash
python echo.py
```

## How It Works

The example demonstrates:

1. Initializing the bitHuman Runtime with your API token
2. Setting up audio input from your microphone
3. Processing audio input and rendering the avatar's response in real-time
4. Displaying the avatar in a local window


## Code Structure

- `echo.py`: Main example script that initializes the Bithuman Runtime and processes audio input

## Troubleshooting

- If you encounter audio input issues, make sure your microphone is properly connected and set as the default input device.
- If the avatar doesn't appear, check that your avatar model path is correct and the file exists.
- For token-related errors, verify that your **bitHuman** API token is valid and properly set in the environment variable. 