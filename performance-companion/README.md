# Live Performance Companion

A repurposed Pwnagotchi that displays real-time performance data from Ableton Live and TouchDesigner during A/V performances. Perfect for glanceable information without disrupting your creative flow.

## Hardware
- Raspberry Pi Zero W
- Waveshare e-ink display
- WiFi connection to performance computer

## Features
- Real-time BPM display from Ableton Live
- Current scene/track information
- Audio level meters (visual representation)
- TouchDesigner parameter display
- Custom performance notes/cues
- Set timer and elapsed time
- MIDI CC value monitoring
- OSC message display

## Architecture

```
Ableton Live → MIDI/OSC → Performance Computer → MQTT/OSC → Pi Zero W → Display
TouchDesigner → OSC → Performance Computer → MQTT/OSC → Pi Zero W → Display
```

## Display Modes

### Mode 1: Ableton Overview
- Current BPM
- Active scene name
- Track status (playing/stopped)
- Elapsed time
- Next cue point

### Mode 2: Audio Levels
- Master output level (visual bar)
- Individual track levels
- Clip status indicators

### Mode 3: TouchDesigner Parameters
- Active composition name
- Key parameter values
- Frame rate
- Custom operator values

### Mode 4: Performance Notes
- Set list progress
- Upcoming sections
- Technical reminders
- Custom text notes

### Mode 5: MIDI Monitor
- Recent MIDI CC messages
- Controller values
- Channel information

## Integration Methods

### MIDI Integration (via rtmidi)
- Monitor MIDI clock for BPM
- Track MIDI CC messages
- Scene launch detection

### OSC Integration (recommended)
- Ableton Live via LiveOSC or Connection Kit
- TouchDesigner native OSC output
- Flexible parameter mapping

### MQTT Integration
- Bridge OSC to MQTT
- Multi-device synchronization
- Network resilience

## TouchDesigner Setup

1. Add OSC Out CHOP to your project
2. Configure to send to Pi Zero W IP
3. Map parameters to OSC addresses:
   - `/td/fps` - Frame rate
   - `/td/param/[name]` - Custom parameters
   - `/td/scene` - Active composition

## Ableton Live Setup

### Option 1: LiveOSC (Legacy)
Install LiveOSC for Ableton 9-11

### Option 2: Connection Kit (Ableton 11+)
Use native OSC support in Ableton 11+

### Option 3: MIDI Bridge
Use MIDI clock and CC messages via Max for Live device

## Configuration

```json
{
  "sources": {
    "ableton": {
      "enabled": true,
      "method": "osc",
      "address": "0.0.0.0",
      "port": 9000
    },
    "touchdesigner": {
      "enabled": true,
      "method": "osc",
      "address": "0.0.0.0",
      "port": 9001
    },
    "mqtt": {
      "enabled": true,
      "broker": "localhost",
      "topics": ["performance/#"]
    }
  },
  "display": {
    "default_mode": 0,
    "auto_rotate": false,
    "refresh_rate": 2
  }
}
```

## Installation

### Prerequisites
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil
sudo pip3 install python-osc paho-mqtt pillow python-rtmidi
```

### Max for Live Device (Optional)
Included in `max4live/` directory:
- Performance Monitor.amxd - Send Ableton data via OSC

### TouchDesigner Component (Optional)
Included in `touchdesigner/` directory:
- PerformanceMonitor.tox - Component for sending data

## Usage

```bash
# Start the performance companion
python3 main.py

# Change display mode via OSC
# /companion/mode [0-4]

# Send custom note via OSC
# /companion/note "Check cables after this song"
```

## OSC Address Map

### Incoming (from Ableton/TD)
- `/live/tempo` - BPM (float)
- `/live/scene` - Scene name (string)
- `/live/track/[n]/volume` - Track volume (float 0-1)
- `/td/fps` - Frame rate (float)
- `/td/param/*` - Custom parameters
- `/companion/mode` - Change display mode (int)
- `/companion/note` - Display custom note (string)

### Outgoing (status)
- `/companion/status` - Device status
- `/companion/display_mode` - Current mode

## Advanced Features

### Set List Integration
Load set list from JSON:
```json
{
  "set_list": [
    {
      "song": "Opening Track",
      "bpm": 128,
      "duration": 240,
      "notes": "Check visual sync"
    }
  ]
}
```

### Wireless Setup
Configure Pi Zero W as WiFi client or create hotspot for isolated performance network.

### Multiple Displays
Run multiple instances for different information displays around your setup.

## Development Roadmap

- [ ] OSC server implementation
- [ ] MIDI input handling
- [ ] MQTT client integration
- [ ] Display rendering for all modes
- [ ] TouchDesigner .tox component
- [ ] Max for Live device
- [ ] Set list manager
- [ ] Web configuration interface
- [ ] Recording/streaming status indicators
- [ ] DMX light cue display

## Performance Tips

- Use wired network connection when possible for lowest latency
- Keep refresh rate at 2-5 seconds to preserve e-ink display
- Use OSC over MQTT for real-time parameters
- Pre-load set lists before performance
- Test all connections during soundcheck

## Credits

Built by Grnch for live A/V performances with Ableton and TouchDesigner.
Perfect companion for interactive installations and live coding sets.
