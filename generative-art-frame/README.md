# Generative Art Frame

A repurposed Pwnagotchi (Raspberry Pi Zero W + e-ink display) that subscribes to TouchDesigner/Hydra generative art outputs and displays them with distinctive e-ink dithering.

## Hardware
- Raspberry Pi Zero W
- Waveshare e-ink display (typically 2.13" or 2.7")
- Original Pwnagotchi case/hardware

## Features
- MQTT subscription to art generation topics
- Real-time dithering for e-ink display optimization
- Queue management for pen plotter previews
- TouchDesigner/Hydra integration
- Battery status display
- Auto-refresh with configurable intervals

## Architecture

```
TouchDesigner/Hydra → MQTT Broker → Pi Zero W → Image Processing → e-ink Display
                                        ↓
                                   Queue Storage
```

## MQTT Topics
- `art/frame/image` - Receive base64 encoded images
- `art/frame/command` - Control commands (clear, refresh, queue)
- `art/frame/status` - Publish device status
- `plotter/queue` - Pen plotter preview queue

## Installation

### Prerequisites
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy
sudo pip3 install paho-mqtt Pillow numpy
```

### E-ink Display Setup
Install the appropriate Waveshare library for your display model.

### Configuration
Copy `config.example.json` to `config.json` and update:
- MQTT broker address
- Display model
- Refresh intervals
- Image processing settings

## Usage

```bash
python3 main.py
```

## TouchDesigner Integration

Send images to the frame using the MQTT Out TOP:
1. Configure MQTT Out with broker address
2. Set topic to `art/frame/image`
3. Convert image to base64
4. Send at desired intervals

## Configuration Options

- `display_model`: Waveshare display model (e.g., "epd2in13_V2")
- `mqtt_broker`: MQTT broker address
- `mqtt_port`: MQTT broker port (default: 1883)
- `refresh_interval`: Seconds between display updates
- `dither_method`: "floyd-steinberg" or "bayer"
- `rotation`: Display rotation (0, 90, 180, 270)

## Development Roadmap

- [ ] Core MQTT subscription
- [ ] Image processing pipeline
- [ ] E-ink display driver integration
- [ ] Dithering algorithms
- [ ] Queue management
- [ ] TouchDesigner example patches
- [ ] Battery monitoring
- [ ] Web configuration interface

## Credits

Built by Grnch for creative display applications.
Hardware originally from Pwnagotchi project.
