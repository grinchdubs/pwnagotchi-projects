# APRS iGate Display - Development Guide

## Project Overview

A Raspberry Pi Zero W + e-ink display system that functions as an APRS iGate, receiving amateur radio packets from APRS-IS and displaying them locally with statistics and weather information.

**IMPORTANT**: This project is for licensed amateur radio operators. Operating an APRS iGate requires a valid amateur radio license.

## Technical Stack

- **Hardware**: Raspberry Pi Zero W, Waveshare e-ink display
- **Language**: Python 3
- **Key Libraries**:
  - `aprslib` - APRS-IS client and packet parsing
  - `Pillow` (PIL) - Display rendering
  - Waveshare e-Paper library - Display driver
- **Network**: WiFi connection to APRS-IS servers

## Architecture

```
APRS-IS Network (rotate.aprs2.net:14580)
           ↓
    Python aprslib Client
           ↓
    Packet Parser/Filter
           ↓
    Statistics Engine
           ↓
    Display Renderer → e-ink Display
```

### Data Flow
1. Connect to APRS-IS server with callsign and passcode
2. Apply geographic/content filters to receive relevant packets
3. Parse incoming APRS packets
4. Update statistics (packet counts, unique stations, etc.)
5. Render information to e-ink display
6. Cycle through display modes

## File Structure

```
aprs-igate-display/
├── main.py                 # Main application entry point
├── config.example.json     # Example configuration
├── requirements.txt        # Python dependencies
├── README.md              # User documentation
├── claude.md              # This file - development guide
└── .gitignore             # Git ignore rules
```

## Configuration

The `config.json` file (created from `config.example.json`) should contain:

```json
{
  "station": {
    "callsign": "N0CALL",
    "ssid": 10,
    "passcode": 12345,
    "latitude": 40.7128,
    "longitude": -74.0060,
    "comment": "Pwnagotchi iGate"
  },
  "aprs_is": {
    "server": "rotate.aprs2.net",
    "port": 14580,
    "filter": "r/40.7128/-74.0060/50"
  },
  "display": {
    "model": "epd2in13_V2",
    "rotation": 0,
    "refresh_interval": 30,
    "mode_rotation_interval": 60,
    "default_mode": 0
  }
}
```

### APRS-IS Passcode

Generate your passcode at: https://apps.magicbug.co.uk/passcode/

**Never commit your actual passcode to git!**

## Development Guidelines

### Setting Up Development Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Key Components to Implement

#### APRS-IS Client
- Connect to APRS-IS with callsign authentication
- Handle reconnection on network failures
- Apply server-side filters for efficiency

```python
import aprslib

def callback(packet):
    """Process each received packet"""
    print(packet)

AIS = aprslib.IS(callsign, passwd=passcode, port=14580)
AIS.set_filter(filter_string)
AIS.connect()
AIS.consumer(callback, raw=False)
```

#### Packet Parser
Parse different APRS packet types:
- **Position reports**: Lat/lon, altitude, course, speed
- **Weather reports**: Temperature, pressure, wind, rain
- **Messages**: Directed messages to/from stations
- **Status**: Station status updates
- **Telemetry**: Sensor data

```python
# aprslib automatically parses most fields
if 'latitude' in packet:
    # Position report
    lat = packet['latitude']
    lon = packet['longitude']
```

#### Statistics Tracking
- Total packets received
- Unique stations heard
- Packets per hour/day
- Top stations by packet count
- Distance calculations from home station

#### Display Modes

**Mode 1: Recent Packets**
```
Last 5 Packets:
─────────────────
N0CALL-9  12:34
  Pos: 2.3mi NE
W1ABC    12:33
  Msg: Hello!
```

**Mode 2: Statistics**
```
Station Stats:
─────────────────
Packets: 1,234
Stations: 89
Pkts/hr: 42
Uptime: 3d 4h
```

**Mode 3: Weather**
```
Weather (W1WX):
─────────────────
Temp: 72°F
Wind: 5mph NE
Press: 30.12"
Rain: 0.0" today
```

**Mode 4: Messages**
```
Messages:
─────────────────
From: W1ABC
12:34:56
Hello, testing!
─────────────────
```

### APRS Filter Syntax

Configure server-side filters in APRS-IS connection:

```python
# Radius filter: packets within 50km of lat/lon
filter = "r/40.7128/-74.0060/50"

# Type filters
filter = "t/p"     # Position reports only
filter = "t/w"     # Weather reports only
filter = "t/m"     # Messages only

# Callsign filter
filter = "b/N0CALL"  # Messages to N0CALL

# Combined filters (space-separated)
filter = "r/40.7128/-74.0060/50 t/pw"  # Positions & weather in radius
```

### Distance Calculations

Calculate distance and bearing to received stations:

```python
from math import radians, cos, sin, asin, sqrt, atan2, degrees

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in miles between two points"""
    R = 3959  # Earth radius in miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing in degrees"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1

    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    bearing = atan2(x, y)
    return (degrees(bearing) + 360) % 360
```

### Code Organization Best Practices

```python
class APRSClient:
    """Handles APRS-IS connection and packet reception"""

class PacketDatabase:
    """Stores and queries received packets"""

class StatisticsEngine:
    """Calculates statistics from packet database"""

class DisplayController:
    """Renders current mode to e-ink display"""

class ModeManager:
    """Manages display mode rotation"""
```

### Testing Without Hardware

**Test APRS-IS Connection**:
```python
import aprslib

def test_callback(packet):
    print(f"From: {packet.get('from')}")
    print(f"Type: {packet.get('format')}")
    print(f"Data: {packet}")
    print("---")

AIS = aprslib.IS("N0CALL", passwd=-1)  # -1 for read-only
AIS.set_filter("r/40.7128/-74.0060/25")
AIS.connect()
AIS.consumer(test_callback, raw=False)
```

**Simulate Display Output**:
```python
# Instead of writing to e-ink, write to console or image file
def render_to_console(lines):
    print("\n" + "="*30)
    for line in lines:
        print(line)
    print("="*30 + "\n")
```

### Common Issues

1. **Invalid Passcode**: Generate correct passcode for your callsign
2. **No Packets Received**: Check filter syntax, try broader filter
3. **Connection Timeout**: Verify internet connectivity, try different APRS-IS server
4. **Parsing Errors**: Some packets may have non-standard formats, handle exceptions
5. **Display Artifacts**: Perform full refresh periodically to clear ghosting

### APRS Packet Types

Understanding packet formats helps with parsing:

```
Position (uncompressed):
N0CALL-9>APRS,WIDE1-1:!4903.50N/07201.75W-Comment

Position (compressed):
N0CALL-9>APRS,WIDE1-1:!/5L!!<*e7>7P[

Weather:
W1WX>APRS:@092345z4903.50N/07201.75W_220/004g005t077r000p000

Message:
N0CALL>APRS::N0CALL-9 :Hello{001

Status:
N0CALL>APRS:>Station is operational
```

### Performance Optimization

- Use packet filters to reduce processing load
- Limit packet history (e.g., last 1000 packets)
- Update display only when mode changes or new data arrives
- Use partial refresh when possible
- Consider SQLite for persistent packet storage

### Legal and Regulatory Considerations

**FCC Regulations (US)**:
- Must have valid amateur radio license
- Callsign must be transmitted properly
- Follow Part 97 rules for amateur radio
- iGate operation is considered automatic control

**International**:
- Check local amateur radio regulations
- Some countries have different rules for automated stations

### APRS-IS Etiquette

- Use appropriate filters to reduce server load
- Don't reconnect too frequently
- Implement exponential backoff on connection failures
- Use read-only connection (passcode -1) for receive-only

### Future Enhancement Ideas

- **Transmit capability**: With TNC/radio, transmit local packets to RF
- **Digipeater mode**: Repeat packets (requires RF hardware)
- **GPS integration**: Mobile iGate with GPS for position updates
- **Web interface**: Real-time web dashboard
- **Alert system**: Email/push notifications for specific stations
- **Packet logging**: Store all packets to database
- **APRS messaging**: Send/receive messages via display
- **Integration with aprs.fi**: Display map overlays

## Deployment

### Production Checklist

- [ ] Configure correct callsign and passcode
- [ ] Set home station coordinates
- [ ] Configure appropriate APRS-IS filter
- [ ] Set up systemd service for auto-start
- [ ] Configure static IP or mDNS
- [ ] Set up logging
- [ ] Test reconnection on network failure
- [ ] Verify display refresh cycles
- [ ] Document station setup

### Monitoring

Monitor logs for:
- Connection failures
- Packet parsing errors
- Display errors
- Memory usage (important on Pi Zero)

## Contributing

When contributing:
- Follow PEP 8 style guidelines
- Test with real APRS-IS connection
- Handle malformed packets gracefully
- Update README.md for user-facing changes
- Respect amateur radio regulations

## Resources

- **APRS Specification**: http://www.aprs.org/doc/APRS101.PDF
- **aprslib Documentation**: https://github.com/rossengeorgiev/aprs-python
- **APRS-IS Servers**: http://www.aprs-is.net/
- **APRS.fi**: https://aprs.fi/ (Live tracking)
- **FCC Part 97**: https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97

## License

MIT License - See README.md for details

**Note**: While the software is MIT licensed, operating APRS stations requires appropriate amateur radio licensing per your local regulations.
