# Live Performance Companion - Development Guide

## Project Overview

A Raspberry Pi Zero W + e-ink display system that shows real-time performance data from Ableton Live and TouchDesigner during live A/V performances. Provides glanceable information without disrupting creative flow.

## Technical Stack

- **Hardware**: Raspberry Pi Zero W, Waveshare e-ink display
- **Language**: Python 3
- **Key Libraries**:
  - `python-osc` - OSC (Open Sound Control) server
  - `paho-mqtt` - MQTT client for alternate integration
  - `python-rtmidi` - MIDI input handling
  - `Pillow` (PIL) - Display rendering
  - Waveshare e-Paper library - Display driver
- **Protocols**: OSC (primary), MQTT (optional), MIDI (optional)

## Architecture

```
Ableton Live ──OSC/MIDI──┐
                         ├──→ Performance Computer ──→ Network ──→ Pi Zero W ──→ e-ink Display
TouchDesigner ──OSC──────┘
```

### Integration Methods

**OSC (Recommended)**:
- Low latency
- Flexible parameter mapping
- Native support in TouchDesigner
- Available in Ableton via Connection Kit or LiveOSC

**MQTT (Optional)**:
- Persistent connections
- Multiple subscribers
- Network resilience
- Requires bridge from OSC

**MIDI**:
- Direct MIDI device connection
- Clock/BPM monitoring
- CC value tracking
- Requires USB MIDI interface

## File Structure

```
performance-companion/
├── main.py                 # Main application entry point
├── config.example.json     # Example configuration
├── setlist.example.json    # Example set list
├── requirements.txt        # Python dependencies
├── README.md              # User documentation
├── claude.md              # This file - development guide
└── .gitignore             # Git ignore rules
```

## Configuration

The `config.json` file (created from `config.example.json`) should contain:

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
      "enabled": false,
      "broker": "localhost",
      "port": 1883,
      "topics": ["performance/#"]
    }
  },
  "display": {
    "model": "epd2in13_V2",
    "rotation": 0,
    "default_mode": 0,
    "auto_rotate": false,
    "auto_rotate_interval": 10,
    "refresh_rate": 2
  },
  "performance": {
    "setlist_file": "setlist.json",
    "show_timer": true
  }
}
```

## Development Guidelines

### Setting Up Development Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Key Components to Implement

#### OSC Server

```python
from pythonosc import dispatcher
from pythonosc import osc_server

def tempo_handler(unused_addr, tempo):
    """Handle BPM updates from Ableton"""
    print(f"BPM: {tempo}")

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/live/tempo", tempo_handler)

server = osc_server.ThreadingOSCUDPServer(
    ("0.0.0.0", 9000), dispatcher)
server.serve_forever()
```

#### Data State Manager

Maintain current state of all tracked parameters:

```python
class PerformanceState:
    def __init__(self):
        self.bpm = 120.0
        self.current_scene = "Intro"
        self.track_volumes = {}
        self.td_fps = 0.0
        self.td_params = {}
        self.notes = []
        self.show_start_time = None

    def update_bpm(self, bpm):
        self.bpm = bpm
        # Trigger display update

    def update_scene(self, scene_name):
        self.current_scene = scene_name
        # Trigger display update
```

#### Display Mode Manager

Manage multiple display modes:

```python
class DisplayMode(Enum):
    ABLETON_OVERVIEW = 0
    AUDIO_LEVELS = 1
    TD_PARAMETERS = 2
    NOTES = 3
    MIDI_MONITOR = 4

class ModeManager:
    def __init__(self):
        self.current_mode = DisplayMode.ABLETON_OVERVIEW
        self.auto_rotate = False

    def next_mode(self):
        modes = list(DisplayMode)
        current_idx = modes.index(self.current_mode)
        self.current_mode = modes[(current_idx + 1) % len(modes)]
```

#### Display Renderers

Each mode has its own renderer:

```python
def render_ableton_overview(state):
    """Render Mode 1: Ableton Overview"""
    lines = [
        f"BPM: {state.bpm}",
        f"Scene: {state.current_scene}",
        f"Time: {state.elapsed_time}",
        "",
        "Next: Drop section"
    ]
    return render_to_display(lines)

def render_audio_levels(state):
    """Render Mode 2: Audio Levels"""
    # Draw visual bar graphs for track levels
    pass

def render_td_parameters(state):
    """Render Mode 3: TouchDesigner Parameters"""
    lines = [
        f"FPS: {state.td_fps:.1f}",
        f"Comp: {state.composition}",
        "",
        "Parameters:",
        f"  Blur: {state.td_params.get('blur', 0):.2f}",
        f"  Feedback: {state.td_params.get('feedback', 0):.2f}"
    ]
    return render_to_display(lines)
```

### OSC Address Map

#### From Ableton Live

**Using LiveOSC or Connection Kit**:
```
/live/tempo                  float    - Current BPM
/live/scene                  string   - Active scene name
/live/track/[n]/volume       float    - Track volume (0-1)
/live/track/[n]/name         string   - Track name
/live/track/[n]/mute         int      - Mute state (0/1)
/live/track/[n]/solo         int      - Solo state (0/1)
/live/track/[n]/arm          int      - Arm state (0/1)
/live/play                   int      - Transport playing (0/1)
/live/overdub                int      - Overdub state (0/1)
```

#### From TouchDesigner

**Custom OSC messages**:
```
/td/fps                      float    - Current FPS
/td/scene                    string   - Active composition
/td/param/[name]             float    - Custom parameter value
/td/beat                     int      - Beat count
/td/bar                      int      - Bar count
```

#### To Companion (Control)

```
/companion/mode              int      - Change display mode (0-4)
/companion/note              string   - Display custom note
/companion/clear_notes       -        - Clear all notes
/companion/reset_timer       -        - Reset show timer
```

#### From Companion (Status)

```
/companion/status            string   - Device status
/companion/display_mode      int      - Current mode
```

### Ableton Live Integration

#### Option 1: Connection Kit (Ableton 11.1+)

Native OSC support in Ableton Live 11.1+:
1. Preferences → Link/Tempo/MIDI → OSC
2. Enable OSC
3. Add output: Pi Zero W IP and port
4. Configure which parameters to send

#### Option 2: LiveOSC (Legacy)

For older Ableton versions:
1. Install LiveOSC MIDI Remote Script
2. Configure in Preferences → MIDI
3. Select LiveOSC as Control Surface

#### Option 3: Max for Live Device

Create custom M4L device to send OSC:

```javascript
// Max for Live patch
outlets = 2;

// Get BPM
var tempo = new LiveAPI("live_set tempo");
outlet(0, "/live/tempo", tempo);

// Get current scene
var scene_idx = new LiveAPI("live_set view selected_scene");
var scene = new LiveAPI("live_set scenes " + scene_idx);
outlet(0, "/live/scene", scene.get("name"));
```

### TouchDesigner Integration

#### OSC Out CHOP

1. Add OSC Out CHOP to network
2. Configure target IP (Pi Zero W) and port
3. Map CHOPs to OSC addresses:

```
FPS → /td/fps
custom_param1 → /td/param/blur
custom_param2 → /td/param/feedback
```

#### Python in TouchDesigner

```python
# Send OSC from TouchDesigner Python
import socket

def send_osc(address, value):
    # Implement OSC message formatting
    # Send via UDP socket
    pass

# In execute() or frameStart()
send_osc('/td/fps', me.time.rate)
```

### Set List Management

Load set list from JSON:

```json
{
  "show_name": "Summer Festival 2024",
  "set_list": [
    {
      "order": 1,
      "song": "Opening",
      "bpm": 128,
      "duration_seconds": 240,
      "scene_name": "1-Opening",
      "notes": "Check visual sync, activate feedback slowly",
      "td_composition": "intro.tox"
    },
    {
      "order": 2,
      "song": "Build Up",
      "bpm": 130,
      "duration_seconds": 300,
      "scene_name": "2-BuildUp",
      "notes": "Watch levels on drop",
      "td_composition": "buildup.tox"
    }
  ]
}
```

Load and track progress:

```python
class SetListManager:
    def __init__(self, setlist_file):
        with open(setlist_file) as f:
            data = json.load(f)
            self.set_list = data['set_list']
        self.current_song_idx = 0

    def next_song(self):
        self.current_song_idx += 1
        return self.get_current_song()

    def get_current_song(self):
        if self.current_song_idx < len(self.set_list):
            return self.set_list[self.current_song_idx]
        return None

    def get_next_song(self):
        next_idx = self.current_song_idx + 1
        if next_idx < len(self.set_list):
            return self.set_list[next_idx]
        return None
```

### MIDI Integration (Optional)

For MIDI clock and CC monitoring:

```python
import rtmidi

def midi_callback(message, data):
    status = message[0][0]

    # MIDI Clock (0xF8)
    if status == 0xF8:
        # Update BPM calculation
        pass

    # Control Change (0xB0)
    elif (status & 0xF0) == 0xB0:
        cc_num = message[0][1]
        cc_val = message[0][2]
        print(f"CC {cc_num}: {cc_val}")

midiin = rtmidi.MidiIn()
midiin.open_port(0)
midiin.set_callback(midi_callback)
```

### Display Rendering

#### Text-Based Layouts

```python
def render_to_display(lines, font_size=12):
    """Render text lines to e-ink display"""
    from PIL import Image, ImageDraw, ImageFont

    # Create image
    img = Image.new('1', (250, 122), 255)  # 2.13" display
    draw = ImageDraw.Draw(img)

    # Load font
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', font_size)

    y = 0
    for line in lines:
        draw.text((0, y), line, font=font, fill=0)
        y += font_size + 2

    # Send to display
    return img
```

#### Visual Elements

```python
def draw_level_meter(draw, x, y, width, height, level):
    """Draw audio level meter"""
    # Draw outline
    draw.rectangle([x, y, x+width, y+height], outline=0)

    # Fill based on level (0.0 to 1.0)
    fill_width = int(width * level)
    draw.rectangle([x, y, x+fill_width, y+height], fill=0)

def draw_progress_bar(draw, x, y, width, height, progress):
    """Draw progress bar for set timer"""
    # Similar to level meter
    pass
```

### Testing Without Hardware

#### OSC Testing with sendosc/oscdump

```bash
# Install oscdump to monitor OSC
pip install python-osc

# Send test OSC messages
python -c "
from pythonosc import udp_client
client = udp_client.SimpleUDPClient('127.0.0.1', 9000)
client.send_message('/live/tempo', 128.5)
"

# Monitor OSC messages
python -c "
from pythonosc import dispatcher, osc_server
def print_handler(addr, *args):
    print(f'{addr}: {args}')
d = dispatcher.Dispatcher()
d.set_default_handler(print_handler)
server = osc_server.ThreadingOSCUDPServer(('0.0.0.0', 9000), d)
server.serve_forever()
"
```

#### Simulation Mode

```python
# Run in simulation mode without display
class SimulatedDisplay:
    def draw(self, image):
        """Save to file instead of e-ink"""
        image.save(f'simulation_{time.time()}.png')
```

### Common Issues

1. **OSC Not Received**: Check firewall, verify port, ensure correct IP
2. **High Latency**: Use wired network if possible, reduce refresh rate
3. **Display Ghosting**: Perform full refresh every 10-20 updates
4. **Clock Drift**: Implement BPM smoothing/averaging
5. **Network Drops**: Buffer last known state, show "disconnected" indicator

### Performance Optimization

- **Update Rate**: Don't refresh display faster than 2-5 seconds
- **Partial Refresh**: Use partial refresh for small changes
- **Debouncing**: Debounce rapid parameter changes
- **Network**: Use local network, avoid WiFi congestion
- **Threading**: Handle OSC in separate thread from display

### Live Performance Best Practices

**Pre-Show Checklist**:
- [ ] Test OSC communication
- [ ] Load set list
- [ ] Verify display visibility from performance position
- [ ] Test all display modes
- [ ] Check network connection
- [ ] Test fallback if network fails
- [ ] Clear previous show data

**During Show**:
- Keep refresh rate reasonable (2-5 seconds)
- Don't stare at display - trust your setup
- Have backup method for critical info

**Post-Show**:
- Review logs for any errors
- Save performance metrics
- Note any issues for next show

### Future Enhancement Ideas

- **Recording indicator**: Show when recording/streaming
- **Audience audio**: Show audience mic levels
- **DMX integration**: Display light cue information
- **Video monitoring**: Camera input status
- **Social media**: Show live comment count
- **Set statistics**: Track average BPM, total bars played
- **Remote control**: Web interface to change modes
- **Multi-display**: Multiple Pi devices showing different info
- **Wireless footswitch**: Change modes with foot pedal

## Deployment

### Production Checklist

- [ ] Configure static IP or mDNS
- [ ] Set up systemd service for auto-start
- [ ] Configure OSC ports
- [ ] Load set list
- [ ] Test display in performance lighting
- [ ] Set up monitoring/logging
- [ ] Test network reconnection
- [ ] Configure firewall rules
- [ ] Test with actual Ableton/TD setup

### Network Configuration

**Recommended**: Dedicated performance network
- Router/switch dedicated to performance equipment
- Static IPs for all devices
- No internet access needed (reduces latency)
- Consider wired Ethernet via USB adapter for Pi

### Power Considerations

- Use quality power supply (2.5A minimum)
- Consider battery backup (UPS)
- Test power draw during performance
- Plan cable routing to avoid trip hazards

## Contributing

When contributing:
- Follow PEP 8 style guidelines
- Test with real performance software
- Consider latency impact of changes
- Update README.md for user-facing changes
- Document new OSC addresses
- Test in live performance scenario if possible

## Resources

- **OSC Specification**: http://opensoundcontrol.org/spec-1_0
- **python-osc**: https://github.com/attwad/python-osc
- **Ableton Connection Kit**: https://www.ableton.com/en/link/
- **TouchDesigner**: https://derivative.ca/
- **LiveOSC**: https://github.com/hanshuebner/LiveOSC

## License

MIT License - See README.md for details
