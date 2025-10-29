import sys
import os

sys.path.insert(0, "/system/apps/scribe")
os.chdir("/system/apps/scribe")

from badgeware import screen, PixelFont, brushes, shapes, run, io, State
import machine
import network
from urllib.urequest import urlopen, Request
import json
import gc

# UI Colors
BACKGROUND = brushes.color(20, 20, 30)
TEXT_COLOR = brushes.color(255, 255, 255)
RECORDING_COLOR = brushes.color(255, 50, 50)
PROCESSING_COLOR = brushes.color(255, 200, 50)
SUCCESS_COLOR = brushes.color(50, 255, 100)
ERROR_COLOR = brushes.color(255, 100, 100)

# Load fonts
small_font = PixelFont.load("/system/assets/fonts/ark.ppf")
large_font = PixelFont.load("/system/assets/fonts/absolute.ppf")

# State management
state = {
    "recording": False,
    "processing": False,
    "transcript": "",
    "error": None,
    "audio_buffer": None,
    "connected": False,
    "api_key": None,
}

# Audio configuration for I2S microphone
SAMPLE_RATE = 16000  # 16kHz sample rate for speech
BITS_PER_SAMPLE = 16
BUFFER_SIZE = 32000  # ~2 seconds at 16kHz

# WiFi and API configuration
WIFI_SSID = None
WIFI_PASSWORD = None
ELEVENLABS_API_KEY = None
SCRIBE_API_URL = "https://api.elevenlabs.io/v1/audio-to-text"

wlan = None
i2s = None


def load_secrets():
    """Load WiFi credentials and ElevenLabs API key from secrets.py"""
    global WIFI_SSID, WIFI_PASSWORD, ELEVENLABS_API_KEY
    
    try:
        sys.path.insert(0, "/")
        from secrets import WIFI_SSID as ssid, WIFI_PASSWORD as pwd
        sys.path.pop(0)
        WIFI_SSID = ssid
        WIFI_PASSWORD = pwd
    except (ImportError, AttributeError):
        WIFI_SSID = None
        WIFI_PASSWORD = None
    
    # Try to load ElevenLabs API key
    try:
        sys.path.insert(0, "/")
        from secrets import ELEVENLABS_API_KEY as key
        sys.path.pop(0)
        ELEVENLABS_API_KEY = key
    except (ImportError, AttributeError):
        ELEVENLABS_API_KEY = None
    
    return WIFI_SSID is not None and ELEVENLABS_API_KEY is not None


def connect_wifi():
    """Connect to WiFi network"""
    global wlan, state
    
    if state["connected"]:
        return True
    
    if not load_secrets():
        state["error"] = "Missing WiFi/API config"
        return False
    
    try:
        if wlan is None:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
        
        if wlan.isconnected():
            state["connected"] = True
            return True
        
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection (with timeout)
        timeout = 30
        while not wlan.isconnected() and timeout > 0:
            timeout -= 1
            # Brief delay handled by main loop
        
        state["connected"] = wlan.isconnected()
        return state["connected"]
    
    except Exception as e:
        state["error"] = f"WiFi error: {str(e)}"
        return False


def init_audio():
    """Initialize I2S audio input"""
    global i2s
    
    try:
        # Initialize I2S for audio input from digital microphone (e.g., INMP441, ICS-43434)
        # Pin configuration for I2S digital microphone
        # Standard pins: SCK=18, WS=19, SD=20
        i2s = machine.I2S(
            0,
            sck=machine.Pin(18),   # Serial clock
            ws=machine.Pin(19),    # Word select (left/right)
            sd=machine.Pin(20),    # Serial data
            mode=machine.I2S.RX,
            bits=BITS_PER_SAMPLE,
            format=machine.I2S.MONO,
            rate=SAMPLE_RATE,
            ibuf=BUFFER_SIZE
        )
        return True
    except Exception as e:
        state["error"] = f"Audio init error: {str(e)}"
        return False


def start_recording():
    """Start audio recording"""
    global state
    
    if not init_audio():
        return False
    
    # Create audio buffer
    state["audio_buffer"] = bytearray(BUFFER_SIZE)
    state["recording"] = True
    state["error"] = None
    return True


def stop_recording():
    """Stop audio recording and return audio data"""
    global state, i2s
    
    if not state["recording"]:
        return None
    
    state["recording"] = False
    
    try:
        # Read from I2S buffer
        if i2s and state["audio_buffer"]:
            bytes_read = i2s.readinto(state["audio_buffer"])
            # Return the audio data that was actually read
            audio_data = bytes(state["audio_buffer"][:bytes_read])
            
            # Clean up I2S
            i2s.deinit()
            i2s = None
            
            return audio_data
    except Exception as e:
        state["error"] = f"Recording error: {str(e)}"
    
    return None


def send_to_elevenlabs(audio_data):
    """Send audio data to ElevenLabs Scribe API for transcription"""
    global state
    
    if not audio_data:
        state["error"] = "No audio data"
        return None
    
    state["processing"] = True
    
    try:
        # Prepare the audio data as WAV format
        # Simple WAV header for PCM audio
        wav_data = create_wav_header(audio_data, SAMPLE_RATE, BITS_PER_SAMPLE) + audio_data
        
        # Create HTTP request with multipart form data
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="audio"; filename="recording.wav"\r\n'
            f'Content-Type: audio/wav\r\n\r\n'
        ).encode() + wav_data + f"\r\n--{boundary}--\r\n".encode()
        
        headers = {
            'xi-api-key': ELEVENLABS_API_KEY,
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        }
        
        # Make the request
        req = Request(SCRIBE_API_URL, data=body, headers=headers, method='POST')
        response = urlopen(req)
        
        # Parse JSON response
        result = json.loads(response.read().decode())
        
        state["processing"] = False
        
        if 'text' in result:
            return result['text']
        else:
            state["error"] = "No transcript in response"
            return None
    
    except Exception as e:
        state["processing"] = False
        state["error"] = f"API error: {str(e)}"
        return None


def create_wav_header(audio_data, sample_rate, bits_per_sample):
    """Create a simple WAV file header"""
    import struct
    
    channels = 1  # Mono
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(audio_data)
    
    header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,
        b'WAVE',
        b'fmt ',
        16,  # fmt chunk size
        1,   # PCM format
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size
    )
    
    return header


def wrap_text(text, max_width):
    """Wrap text to fit within max_width pixels"""
    if not text:
        return []
    
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        width, _ = screen.measure_text(test_line)
        
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines


def draw_ui():
    """Draw the main UI"""
    # Clear screen
    screen.brush = BACKGROUND
    screen.clear()
    
    # Draw header
    screen.brush = brushes.color(100, 100, 120)
    screen.draw(shapes.rectangle(0, 0, 160, 18))
    
    screen.font = large_font
    screen.brush = TEXT_COLOR
    title = "ElevenLabs Scribe"
    tw, th = screen.measure_text(title)
    screen.text(title, 80 - tw // 2, 3)
    
    # Draw status
    screen.font = small_font
    y_pos = 25
    
    if state["error"]:
        screen.brush = ERROR_COLOR
        error_lines = wrap_text(state["error"], 150)
        for line in error_lines[:3]:  # Show max 3 lines
            screen.text(line, 5, y_pos)
            y_pos += 10
    elif state["processing"]:
        screen.brush = PROCESSING_COLOR
        screen.text("Processing...", 5, y_pos)
    elif state["recording"]:
        screen.brush = RECORDING_COLOR
        screen.text("Recording...", 5, y_pos)
        screen.text("Press A to stop", 5, y_pos + 10)
    elif state["transcript"]:
        screen.brush = SUCCESS_COLOR
        screen.text("Transcript:", 5, y_pos)
        y_pos += 12
        
        screen.brush = TEXT_COLOR
        transcript_lines = wrap_text(state["transcript"], 150)
        for line in transcript_lines[:6]:  # Show max 6 lines
            screen.text(line, 5, y_pos)
            y_pos += 10
    else:
        screen.brush = TEXT_COLOR
        screen.text("Press A to record", 5, y_pos)
    
    # Draw footer with instructions
    screen.brush = brushes.color(100, 100, 120)
    screen.draw(shapes.rectangle(0, 102, 160, 18))
    
    screen.font = small_font
    screen.brush = TEXT_COLOR
    if not state["recording"] and not state["processing"]:
        screen.text("A: Record  C: Clear", 5, 106)
    elif state["recording"]:
        screen.text("A: Stop recording", 5, 106)


def update():
    """Main update loop"""
    global state
    
    # Handle button inputs
    if io.BUTTON_A in io.pressed:
        if state["recording"]:
            # Stop recording and transcribe
            audio_data = stop_recording()
            
            if audio_data:
                # Connect to WiFi if needed
                if not state["connected"]:
                    if not connect_wifi():
                        # Error already set in connect_wifi
                        pass
                    else:
                        # Send to ElevenLabs
                        transcript = send_to_elevenlabs(audio_data)
                        if transcript:
                            state["transcript"] = transcript
                            state["error"] = None
                else:
                    # Already connected
                    transcript = send_to_elevenlabs(audio_data)
                    if transcript:
                        state["transcript"] = transcript
                        state["error"] = None
                
                # Clean up audio buffer
                state["audio_buffer"] = None
                gc.collect()
        else:
            # Start recording
            if start_recording():
                state["transcript"] = ""
                state["error"] = None
    
    if io.BUTTON_C in io.pressed:
        if not state["recording"] and not state["processing"]:
            # Clear transcript and errors
            state["transcript"] = ""
            state["error"] = None
    
    # Draw UI
    draw_ui()


def init():
    """Initialize app state"""
    # Load any saved state if needed
    pass


def on_exit():
    """Clean up on exit"""
    global i2s, wlan
    
    # Clean up I2S
    if i2s:
        try:
            i2s.deinit()
        except:
            pass
    
    # Disconnect WiFi
    if wlan:
        try:
            wlan.disconnect()
            wlan.active(False)
        except:
            pass


if __name__ == "__main__":
    run(update, init=init, on_exit=on_exit)
