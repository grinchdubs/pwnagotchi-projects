# APRS iGate Display

A repurposed Pwnagotchi that functions as an APRS iGate with local e-ink display for received packets, weather data, and station statistics.

## Hardware
- Raspberry Pi Zero W
- Waveshare e-ink display
- WiFi connection for APRS-IS

## Features
- APRS-IS gateway (iGate functionality)
- Real-time packet display on e-ink screen
- Station statistics and tracking
- Weather data display
- Message filtering and routing
- Local packet logging
- Web interface for configuration

## Architecture

```
RF → SDR/TNC → aprsc → Python Script → Display
                  ↓
              APRS-IS Network
```

## APRS-IS Connection
- Connects to APRS-IS servers (rotate.aprs2.net)
- Receives packets for configured filter
- Optional: transmit local packets to APRS-IS
- Callsign and passcode authentication

## Display Modes

### Mode 1: Recent Packets
Shows last 5-10 received packets with:
- Callsign
- Position or message
- Distance from station
- Time received

### Mode 2: Statistics
- Total packets received
- Unique stations heard
- Packets per hour
- Top stations by packet count

### Mode 3: Weather
- Local weather from APRS weather stations
- Temperature, pressure, wind
- Forecast integration

### Mode 4: Messages
- Display directed messages
- Message history
- Notification indicator

## Configuration

### Station Settings
- Callsign and SSID
- Station location (lat/lon)
- APRS-IS passcode
- Filter radius

### Display Settings
- Refresh interval
- Display rotation
- Auto-rotate modes
- Font size

### Filter Settings
- Geographic radius
- Packet types (position, weather, messages)
- Callsign whitelist/blacklist

## Installation

### Prerequisites
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil
sudo pip3 install aprslib pillow
```

### APRS Configuration
1. Obtain APRS-IS passcode for your callsign
2. Configure station location
3. Set up packet filters

### Running as Service
```bash
sudo cp aprs-igate.service /etc/systemd/system/
sudo systemctl enable aprs-igate
sudo systemctl start aprs-igate
```

## Usage

```bash
python3 main.py
```

### Web Interface
Access configuration at: `http://raspberrypi.local:8080`

## APRS Filter Examples

```python
# All traffic within 50km
"r/40.7128/-74.0060/50"

# Position reports only
"t/p"

# Weather stations
"t/w"

# Messages to your callsign
"b/YOURCALL"
```

## Development Roadmap

- [ ] APRS-IS client integration
- [ ] Packet parser
- [ ] E-ink display layouts
- [ ] Statistics tracking
- [ ] Web configuration interface
- [ ] Message handling
- [ ] Weather data integration
- [ ] GPS support for mobile operation
- [ ] Digipeater mode (with appropriate RF hardware)

## Amateur Radio License Requirement

⚠️ **Important**: Operating an APRS iGate requires a valid amateur radio license. Ensure you are compliant with your country's regulations before transmitting.

## Credits

Built by Grnch (callsign: [YOUR_CALL]) for APRS operations.
Uses aprslib for APRS-IS connectivity.
