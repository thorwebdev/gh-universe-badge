# ElevenLabs Scribe - Audio Transcription App

A voice transcription app that records audio from an I2S digital microphone and transcribes it using the ElevenLabs Scribe API.

## Features

- **Voice Recording**: Press button A to start recording, press again to stop
- **Real-time Status**: Visual indicators for recording, processing, and results
- **WiFi Integration**: Automatically connects to configured WiFi network
- **Transcription Display**: Shows the transcribed text on screen with text wrapping
- **Error Handling**: Clear error messages for troubleshooting

## Hardware Requirements

- Tufty 2350 badge
- I2S digital microphone (e.g., INMP441, ICS-43434, or similar)
- WiFi connection for API access

**Note**: This app requires an I2S digital microphone, not a USB microphone. The microphone must be connected to the badge's I2S pins.

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

### 3. Connect I2S Microphone

Connect an I2S digital microphone (such as INMP441 or ICS-43434) to the badge using these pins:
- Serial Clock (SCK): Pin 18
- Word Select (WS): Pin 19  
- Serial Data (SD): Pin 20
- Ground (GND): Connect to badge ground
- VCC: Connect to 3.3V power

**Important**: This app requires an I2S digital microphone module, not a standard USB or analog microphone. I2S microphones are small breakout boards available from electronics suppliers.

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
- Verify I2S microphone is properly connected to pins 18, 19, 20
- Check power (3.3V) and ground connections
- Ensure you're using a compatible I2S digital microphone (INMP441, ICS-43434, etc.)
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
- Requires I2S digital microphone hardware (not standard USB or analog microphones)

## Development Notes

This app follows the standard badge app structure:
- Uses `badgeware` library for display and input
- Implements `init()`, `update()`, and `on_exit()` lifecycle methods
- Manages WiFi and I2S hardware resources
- Includes proper cleanup in `on_exit()`

## Credits

Built for the GitHub Universe 2025 Tufty Badge using the ElevenLabs Scribe API.
