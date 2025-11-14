# Generative Art Frame - Development Guide

## Project Overview

A Raspberry Pi Zero W + e-ink display system that subscribes to generative art outputs from TouchDesigner or Hydra via MQTT and displays them with e-ink optimized dithering.

## Technical Stack

- **Hardware**: Raspberry Pi Zero W, Waveshare e-ink display (2.13", 2.7", or 4.2")
- **Language**: Python 3
- **Key Libraries**:
  - `paho-mqtt` - MQTT client for receiving art frames
  - `Pillow` (PIL) - Image processing and dithering
  - `numpy` - Numerical operations for image manipulation
  - Waveshare e-Paper library - Display driver

## Architecture

```
TouchDesigner/Hydra → MQTT Broker → Pi Zero W → Image Processing → e-ink Display
                                        ↓
                                   Queue Storage
```

### Data Flow
1. Art generation software (TouchDesigner/Hydra) sends base64 encoded images via MQTT
2. Pi Zero W receives images on topic `art/frame/image`
3. Image is decoded and processed (resize, dither)
4. Dithered image is rendered to e-ink display
5. Optionally queued for pen plotter output on topic `plotter/queue`

## File Structure

```
generative-art-frame/
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
  "mqtt": {
    "broker": "mqtt.example.com",
    "port": 1883,
    "topics": {
      "image": "art/frame/image",
      "command": "art/frame/command",
      "status": "art/frame/status",
      "plotter_queue": "plotter/queue"
    }
  },
  "display": {
    "model": "epd2in13_V2",
    "rotation": 0,
    "refresh_interval": 5
  },
  "image_processing": {
    "dither_method": "floyd-steinberg",
    "contrast": 1.2,
    "brightness": 1.0
  }
}
```

## Development Guidelines

### Setting Up Development Environment

1. **Test without hardware**: Use PIL to save dithered images to files for testing without physical e-ink display
2. **MQTT testing**: Use `mosquitto_pub` to send test images
3. **Virtual environment**: Always use a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Key Components to Implement

#### MQTT Client
- Subscribe to image topic
- Handle reconnection on network failures
- Publish status updates

#### Image Processing Pipeline
- Base64 decode incoming images
- Resize to display dimensions
- Apply dithering algorithms:
  - Floyd-Steinberg (default) - Good for photographs and complex art
  - Bayer ordered dithering - Good for geometric patterns
- Optional contrast/brightness adjustment

#### Display Driver Integration
- Initialize Waveshare display based on config
- Handle partial vs full refresh
- Error recovery if display fails

#### Queue Management
- Store received images for pen plotter
- FIFO queue with configurable size
- Publish queue status to MQTT

### Code Organization Best Practices

```python
# Suggested module structure
class MQTTArtClient:
    """Handles MQTT connection and message handling"""

class ImageProcessor:
    """Processes and dithers images for e-ink display"""

class DisplayController:
    """Controls the e-ink display hardware"""

class PlotterQueue:
    """Manages queue for pen plotter integration"""
```

### Dithering Algorithms

**Floyd-Steinberg Dithering**:
- Error diffusion algorithm
- Produces organic, natural looking results
- Best for photographs and complex gradients

**Bayer Ordered Dithering**:
- Pattern-based dithering
- Produces consistent, predictable patterns
- Best for geometric art and typography

### E-ink Display Considerations

1. **Refresh Rate**: E-ink displays are slow (1-3 seconds). Don't refresh too frequently.
2. **Ghosting**: Periodic full refresh needed to prevent ghosting
3. **Partial Refresh**: Faster but can cause artifacts over time
4. **1-bit Display**: Most e-ink displays are 1-bit (black/white only), requiring dithering

### Testing

**MQTT Testing**:
```bash
# Send test image
base64 test.png | mosquitto_pub -h localhost -t art/frame/image -s

# Monitor status
mosquitto_sub -h localhost -t art/frame/status
```

**Image Processing Testing**:
```python
# Test dithering without display
from PIL import Image
img = Image.open('test.png')
# Apply dithering
dithered = apply_floyd_steinberg(img)
dithered.save('test_dithered.png')
```

### Common Issues

1. **SPI Not Enabled**: Run `sudo raspi-config` and enable SPI under Interface Options
2. **Display Not Found**: Check physical connections and verify correct display model in config
3. **MQTT Connection Failed**: Verify broker address, check firewall, ensure network connectivity
4. **Image Too Large**: Images should be resized to display dimensions before dithering

### Performance Optimization

- Use numpy for fast array operations during dithering
- Avoid unnecessary image copies
- Cache dithering matrices
- Consider PIL's native dithering methods for speed

### TouchDesigner Integration Notes

TouchDesigner can send images via MQTT using:
1. Export frame to file
2. Convert to base64
3. Publish via MQTT Out TOP or Python script

Example TouchDesigner Python:
```python
import base64
import paho.mqtt.client as mqtt

# Convert TOP to bytes, base64 encode, publish
# (Implementation details depend on TD version)
```

### Future Enhancement Ideas

- Web interface for configuration
- Multiple frame buffers for animation
- Support for multi-color e-ink displays (red/black/white)
- Image history/gallery mode
- Integration with Stable Diffusion
- Battery monitoring and low-power mode
- WiFi AP mode for standalone operation

## Deployment

### Production Checklist

- [ ] Configure static IP or mDNS
- [ ] Set up systemd service for auto-start
- [ ] Configure MQTT credentials
- [ ] Test display refresh cycles
- [ ] Set up monitoring/logging
- [ ] Configure firewall rules
- [ ] Test network reconnection handling

### Systemd Service

See README.md for systemd service configuration.

## Contributing

When contributing:
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Test on actual hardware before committing
- Update README.md if adding user-facing features
- Consider power consumption impact

## Hardware Notes

### Waveshare Display Models

- **2.13" V2** (250x122): Compact, low power, perfect for desk display
- **2.7"** (264x176): Good middle ground
- **4.2"** (400x300): Large, more visible, higher power consumption

### Power Consumption

- Pi Zero W idle: ~100mA
- Pi Zero W active: ~150-200mA
- Display refresh: +50-100mA peak
- Total: Budget for 300-400mA peak

## License

MIT License - See README.md for details
