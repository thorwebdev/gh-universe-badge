# ElevenLabs Scribe - Audio Transcription App

A voice transcription app that records audio from a USB microphone and transcribes it using the ElevenLabs Scribe API.

## Features

- **Voice Recording**: Press button A to start recording, press again to stop
- **Real-time Status**: Visual indicators for recording, processing, and results
- **WiFi Integration**: Automatically connects to configured WiFi network
- **Transcription Display**: Shows the transcribed text on screen with text wrapping
- **Error Handling**: Clear error messages for troubleshooting

## Hardware Requirements

- Tufty 2350 badge
- USB microphone compatible with I2S interface
- WiFi connection for API access

## Setup

### 1. Configure WiFi and API Key

Edit `/secrets.py` on your badge and add:

```python
WIFI_SSID = "your_wifi_network"
WIFI_PASSWORD = "your_password"
ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
```

### 2. Get ElevenLabs API Key

1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Navigate to your API settings
3. Copy your API key
4. Add it to `secrets.py`

### 3. Connect USB Microphone

Connect a USB microphone to the badge. The app is configured to use I2S pins:
- Serial Clock (SCK): Pin 18
- Word Select (WS): Pin 19
- Serial Data (SD): Pin 20

**Note**: Pin configuration may need adjustment based on your specific USB microphone hardware.

## Usage

1. Launch the app from the menu
2. **Press A** to start recording
3. Speak into the microphone
4. **Press A again** to stop recording and send for transcription
5. Wait for the transcription to appear on screen
6. **Press C** to clear the transcript and start over

## UI Elements

- **Title Bar**: Shows "ElevenLabs Scribe"
- **Status Area**: 
  - Shows current state (Recording, Processing, or Transcript)
  - Displays error messages if something goes wrong
- **Footer Bar**: Shows available controls

## Troubleshooting

### "Missing WiFi/API config"
- Ensure `WIFI_SSID`, `WIFI_PASSWORD`, and `ELEVENLABS_API_KEY` are set in `/secrets.py`

### "WiFi error"
- Check that your WiFi credentials are correct
- Ensure you're in range of the WiFi network
- Verify the network is 2.4GHz (5GHz not supported)

### "Audio init error"
- Verify USB microphone is properly connected
- Check that the microphone is compatible with I2S interface
- Try reconnecting the microphone

### "API error"
- Verify your ElevenLabs API key is valid
- Check that you have API credits available
- Ensure you have internet connectivity

## Technical Details

### Audio Configuration
- **Sample Rate**: 16kHz (optimized for speech)
- **Bit Depth**: 16-bit
- **Format**: Mono PCM
- **Buffer Size**: 32KB (~2 seconds)

### API Integration
- Uses ElevenLabs Scribe API endpoint: `https://api.elevenlabs.io/v1/audio-to-text`
- Audio is sent as WAV format with proper headers
- Multipart form data submission
- Returns JSON with transcribed text

## Limitations

- Recording length is limited by buffer size (~2 seconds at 16kHz)
- Requires active internet connection
- API usage counts against your ElevenLabs quota
- USB microphone must be I2S compatible

## Development Notes

This app follows the standard badge app structure:
- Uses `badgeware` library for display and input
- Implements `init()`, `update()`, and `on_exit()` lifecycle methods
- Manages WiFi and I2S hardware resources
- Includes proper cleanup in `on_exit()`

## Credits

Built for the GitHub Universe 2025 Tufty Badge using the ElevenLabs Scribe API.
