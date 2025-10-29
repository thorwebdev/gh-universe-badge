import sys
import os

sys.path.insert(0, "/system/apps/bluetooth")
os.chdir("/system/apps/bluetooth")

from badgeware import screen, PixelFont, Image, shapes, brushes, run, io, State

# Load font
screen.font = PixelFont.load("/system/assets/fonts/ark.ppf")
screen.antialias = Image.X2

# Color definitions
BACKGROUND = brushes.color(20, 20, 40)
HEADER_BG = brushes.color(0, 120, 255)
TEXT_COLOR = brushes.color(255, 255, 255)
HIGHLIGHT_COLOR = brushes.color(0, 180, 255)
GRAY_TEXT = brushes.color(180, 180, 180)
SUCCESS_COLOR = brushes.color(0, 255, 100)
ERROR_COLOR = brushes.color(255, 80, 80)

# State management
state = {
    "scanning": False,
    "selected_index": 0,
    "connected_device": None,
    "status_message": "",
    "status_time": 0,
}

# Mock device list (since we're running MicroPython without actual BLE library access)
# In a real implementation, this would use aioble or bluetooth module
devices = []
scan_attempts = 0

def init():
    """Initialize the app and load saved state"""
    State.load("bluetooth", state)
    start_scan()

def start_scan():
    """Start Bluetooth scanning for devices"""
    global devices, scan_attempts
    state["scanning"] = True
    state["status_message"] = "Scanning..."
    state["status_time"] = io.ticks
    scan_attempts = 0
    
    # Simulate device discovery
    # In real implementation, use: aioble.scan() or bluetooth.BLE().gap_scan()
    try:
        # Try to import Bluetooth module
        try:
            import bluetooth
            ble = bluetooth.BLE()
            # This would trigger actual scanning in real hardware
            # For now, we'll use mock data
        except (ImportError, AttributeError):
            pass
        
        # Mock discovered devices for demonstration
        devices = [
            {"name": "Phone", "addr": "AA:BB:CC:DD:EE:01", "rssi": -45},
            {"name": "Laptop", "addr": "AA:BB:CC:DD:EE:02", "rssi": -52},
            {"name": "Headphones", "addr": "AA:BB:CC:DD:EE:03", "rssi": -38},
            {"name": "Speaker", "addr": "AA:BB:CC:DD:EE:04", "rssi": -60},
            {"name": "Watch", "addr": "AA:BB:CC:DD:EE:05", "rssi": -55},
        ]
    except Exception as e:
        state["status_message"] = f"Error: {str(e)}"
        state["status_time"] = io.ticks

def connect_to_device(device):
    """Attempt to connect to selected Bluetooth device"""
    state["status_message"] = f"Connecting to {device['name']}..."
    state["status_time"] = io.ticks
    
    try:
        # In real implementation:
        # connection = await aioble.connect(device)
        # Or: ble.gap_connect(device['addr'])
        
        # Simulate connection success
        state["connected_device"] = device
        state["status_message"] = f"Connected to {device['name']}"
        state["status_time"] = io.ticks
    except Exception as e:
        state["status_message"] = f"Failed: {str(e)}"
        state["status_time"] = io.ticks
        state["connected_device"] = None

def disconnect_device():
    """Disconnect from current device"""
    if state["connected_device"]:
        device_name = state["connected_device"]["name"]
        state["status_message"] = f"Disconnected from {device_name}"
        state["status_time"] = io.ticks
        state["connected_device"] = None

def draw_header():
    """Draw the app header"""
    screen.brush = HEADER_BG
    screen.draw(shapes.rounded_rectangle(0, 0, 160, 18, 0))
    
    screen.brush = TEXT_COLOR
    title = "Bluetooth Devices"
    w, _ = screen.measure_text(title)
    screen.text(title, 80 - (w / 2), 3)

def draw_device_list():
    """Draw the list of discovered Bluetooth devices"""
    start_y = 22
    item_height = 15
    visible_items = 5
    
    if not devices:
        screen.brush = GRAY_TEXT
        msg = "No devices found"
        w, _ = screen.measure_text(msg)
        screen.text(msg, 80 - (w / 2), 50)
        return
    
    # Calculate scroll offset to keep selected item visible
    scroll_offset = 0
    if state["selected_index"] >= visible_items:
        scroll_offset = state["selected_index"] - visible_items + 1
    
    # Draw visible devices
    for i in range(len(devices)):
        if i < scroll_offset:
            continue
        if i >= scroll_offset + visible_items:
            break
        
        device = devices[i]
        y = start_y + (i - scroll_offset) * item_height
        is_selected = (i == state["selected_index"])
        is_connected = (state["connected_device"] and 
                       state["connected_device"]["addr"] == device["addr"])
        
        # Draw selection highlight
        if is_selected:
            screen.brush = HIGHLIGHT_COLOR
            screen.draw(shapes.rectangle(2, y - 1, 156, item_height - 2))
        
        # Draw device name
        screen.brush = TEXT_COLOR if is_selected else GRAY_TEXT
        device_name = device["name"][:18]  # Truncate long names
        screen.text(device_name, 5, y + 1)
        
        # Draw connection indicator
        if is_connected:
            screen.brush = SUCCESS_COLOR
            screen.draw(shapes.rectangle(150, y + 2, 6, 6))
        
        # Draw signal strength (RSSI)
        rssi_text = f"{device['rssi']}"
        w, _ = screen.measure_text(rssi_text)
        screen.brush = TEXT_COLOR if is_selected else GRAY_TEXT
        screen.text(rssi_text, 145 - w, y + 1)

def draw_footer():
    """Draw the footer with button hints"""
    screen.brush = brushes.color(40, 40, 60)
    screen.draw(shapes.rectangle(0, 102, 160, 18))
    
    screen.brush = TEXT_COLOR
    screen.font = PixelFont.load("/system/assets/fonts/ark.ppf")
    
    if state["connected_device"]:
        footer_text = "A:Rescan B:Disconnect C:Select"
    else:
        footer_text = "A:Rescan B:Connect ↕:Navigate"
    
    w, _ = screen.measure_text(footer_text)
    # Scale text to fit if needed
    if w > 155:
        screen.text(footer_text, 2, 106)
    else:
        screen.text(footer_text, 80 - (w / 2), 106)

def draw_status():
    """Draw status message if recent"""
    if not state["status_message"]:
        return
    
    # Show status for 3 seconds
    if io.ticks - state["status_time"] < 3000:
        msg = state["status_message"]
        w, h = screen.measure_text(msg)
        
        # Determine background color based on message type
        if "Connected" in msg:
            bg_color = SUCCESS_COLOR
        elif "Error" in msg or "Failed" in msg:
            bg_color = ERROR_COLOR
        else:
            bg_color = HIGHLIGHT_COLOR
        
        # Draw status box
        box_width = min(w + 16, 150)
        screen.brush = bg_color
        screen.draw(shapes.rounded_rectangle(
            80 - (box_width / 2), 85, box_width, h + 8, 4))
        
        screen.brush = TEXT_COLOR
        screen.text(msg[:22], 80 - (w / 2), 88)

def update():
    """Main update loop called every frame"""
    global scan_attempts
    
    # Handle button input for navigation
    if io.BUTTON_UP in io.pressed:
        if devices:
            state["selected_index"] = (state["selected_index"] - 1) % len(devices)
    
    if io.BUTTON_DOWN in io.pressed:
        if devices:
            state["selected_index"] = (state["selected_index"] + 1) % len(devices)
    
    # Handle B button for connect/disconnect
    if io.BUTTON_B in io.pressed:
        if devices and state["selected_index"] < len(devices):
            selected_device = devices[state["selected_index"]]
            
            # Toggle connection
            if (state["connected_device"] and 
                state["connected_device"]["addr"] == selected_device["addr"]):
                disconnect_device()
            else:
                connect_to_device(selected_device)
    
    # Handle A button for rescan
    if io.BUTTON_A in io.pressed:
        disconnect_device()
        start_scan()
        state["selected_index"] = 0
    
    # Simulate scanning progress
    if state["scanning"] and scan_attempts < 30:
        scan_attempts += 1
        if scan_attempts >= 30:
            state["scanning"] = False
            state["status_message"] = f"Found {len(devices)} devices"
            state["status_time"] = io.ticks
    
    # Clear screen
    screen.brush = BACKGROUND
    screen.clear()
    
    # Draw UI components
    draw_header()
    draw_device_list()
    draw_footer()
    draw_status()
    
    return None

def on_exit():
    """Called when app exits - save state"""
    # Disconnect if connected
    if state["connected_device"]:
        disconnect_device()
    
    # Save state
    State.save("bluetooth", state)

if __name__ == "__main__":
    run(update, init=init, on_exit=on_exit)
