# Bluetooth Device Scanner

A simple Bluetooth device scanner and connection manager for the GitHub Universe Badge.

## Features

- **Device Discovery**: Scans for nearby Bluetooth devices
- **Device List**: Displays discovered devices with signal strength (RSSI)
- **Device Selection**: Navigate through devices using UP/DOWN buttons
- **Connection Management**: Connect to and disconnect from devices using the B button
- **Status Feedback**: Visual indicators for connection status and scanning progress

## Controls

- **UP/DOWN**: Navigate through the list of discovered devices
- **A Button**: Rescan for devices (disconnects from any connected device)
- **B Button**: Connect to selected device / Disconnect from current device
- **C Button**: (Not used)
- **HOME Button**: Return to menu launcher

## Display

- **Header**: Shows "Bluetooth Devices" title
- **Device List**: Shows up to 5 devices at a time with scrolling
  - Device name
  - Signal strength (RSSI value in dBm)
  - Green dot indicator for connected device
- **Status Messages**: Temporary messages for scanning, connection, and errors
- **Footer**: Button hints showing available actions

## Technical Notes

### Implementation

This app demonstrates the structure for a Bluetooth scanner. The current implementation uses mock device data for demonstration purposes. On real hardware with Bluetooth support, you would:

1. Import the Bluetooth module:
   ```python
   import bluetooth
   # or
   import aioble
   ```

2. Initialize BLE:
   ```python
   ble = bluetooth.BLE()
   ble.active(True)
   ```

3. Scan for devices:
   ```python
   devices = ble.gap_scan(duration_ms=5000)
   # or with aioble
   async for device in aioble.scan():
       # process device
   ```

4. Connect to device:
   ```python
   connection = ble.gap_connect(device_addr)
   # or with aioble
   connection = await aioble.connect(device)
   ```

### State Persistence

The app saves connection state using the badgeware State management system. This allows the app to remember the last connected device across app restarts.

### Requirements

- MicroPython with Bluetooth support (RP2350 supports Bluetooth via external modules)
- For real Bluetooth functionality, the hardware needs a Bluetooth module or adapter
- The Tufty 2350 badge would need a compatible Bluetooth module connected via GPIO

## Future Enhancements

Possible improvements for real hardware implementation:

- Actual Bluetooth scanning using hardware BLE module
- Device pairing and authentication
- Service discovery (GATT services)
- Read/write characteristics
- Background connection monitoring
- Device name resolution
- Filter by device type or service UUID
- RSSI-based signal strength indicator (graphical)
- Connection history
