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

### TouchDesigner Integration

## TouchDesigner Documentation Requirements

**CRITICAL: When answering TouchDesigner questions, you MUST:**

1. **Reference the TouchDesigner documentation** for accurate parameter names and API usage:
   - Main UserGuide: https://derivative.ca/UserGuide
   - Python API Documentation: https://derivative.ca/UserGuide/Category%3APython

2. **Always Verify Parameter Names**
   - **DO NOT guess** TouchDesigner parameter names or methods
   - **ALWAYS check** the official documentation for exact parameter syntax
   - **Common TouchDesigner objects** to reference:
     - `op()` - Operator references
     - `me` - Current operator context
     - `parent()` - Parent component access
     - Parameter syntax: `op.par.parametername`

3. **Key TouchDesigner Python Classes to Reference:**
   - `OP` class - Base operator class
   - `COMP` class - Component operators
   - `TOP` class - Texture operators
   - `CHOP` class - Channel operators
   - `DAT` class - Data operators

4. **Parameter Access Patterns:**
   ```python
   # Correct parameter access patterns to verify in docs:
   op.par.parameter_name.val          # Get parameter value
   op.par.parameter_name = value       # Set parameter value
   op.par.parameter_name.expr = "expr" # Set expression
   ```

### TouchDesigner Modern Python Features

**IMPORTANT: TouchDesigner has introduced new Python libraries:**

#### TDI Library (TouchDesigner Interface Library)
- **Documentation:** https://docs.derivative.ca/TDI_Library
- **Purpose:** Modern Python interface with improved type hints and IDE support
- **When to use:** For new Python scripts that benefit from better autocomplete

#### Thread Manager
- **Documentation:** https://docs.derivative.ca/Thread_Manager
- **Community Post:** https://derivative.ca/community-post/enhancing-your-python-toolbox-touchdesigner%E2%80%99s-thread-manager/72022
- **Purpose:** Simplified multi-threading in TouchDesigner
- **When to use:** For background tasks, parallel processing, non-blocking operations

#### Python Environment Manager (tdPyEnvManager)
- **Documentation:** https://docs.derivative.ca/Palette:tdPyEnvManager
- **Community Post:** https://derivative.ca/community-post/introducing-touchdesigner-python-environment-manager-tdpyenvmanager/72024
- **Purpose:** Manage Python packages and virtual environments
- **When to use:** For installing external Python dependencies (like `paho-mqtt`)

### Common TouchDesigner Pitfalls to Avoid

- Guessing parameter names instead of looking them up
- Using incorrect callback signatures
- Mixing up operator reference syntax
- Not handling TouchDesigner's frame-based execution model
- **Pulse button callbacks**: Pulse parameters trigger `onPulse(par)`, NOT `onValueChange(par, prev)`
- **Falsy parameter values**: Use `if par is not None:` instead of `if par:` because values like `0`, `""`, `False` are falsy
- **Node sizing**: Use `op.nodeWidth` and `op.nodeHeight`, NOT `op.par.w` or `op.par.h`

### Sending Images from TouchDesigner via MQTT

TouchDesigner can send images to this e-ink display using MQTT:

**Method 1: Using MQTT DAT (Recommended)**
```python
# In a Timer CHOP callback or Execute DAT
import base64

# Get the render TOP
render_top = op('render1')

# Export as bytes (PNG or JPEG)
img_bytes = render_top.save('temp.png')  # or use .save() to memory

# Convert to base64
img_base64 = base64.b64encode(img_bytes).decode('utf-8')

# Publish via MQTT DAT
mqtt_dat = op('mqtt1')
mqtt_dat.sendBytes('art/frame/image', img_base64.encode('utf-8'))
```

**Method 2: Using Python paho-mqtt**
```python
# Install paho-mqtt via tdPyEnvManager first
import base64
import paho.mqtt.client as mqtt

# Get TOP pixel data
render_top = op('render1')
img_bytes = render_top.save('memory.png')  # Save to memory buffer

# Convert to base64
img_base64 = base64.b64encode(img_bytes).decode('utf-8')

# Publish
client = mqtt.Client()
client.connect('mqtt.broker.address', 1883)
client.publish('art/frame/image', img_base64)
client.disconnect()
```

**Method 3: Using numpyArray for custom encoding**
```python
import numpy as np
from PIL import Image
import base64
import io

# Get pixel data as numpy array
render_top = op('render1')
img_array = render_top.numpyArray(delayed=False)
# Returns shape (height, width, channels) as float32 (0.0-1.0)

# Convert to uint8 and flip (TD is bottom-left origin)
img_array = np.flipud(img_array)
img_array = (img_array * 255).astype(np.uint8)

# Convert to PIL Image
img = Image.fromarray(img_array)

# Encode to JPEG/PNG
buffer = io.BytesIO()
img.save(buffer, format='JPEG', quality=85)
img_bytes = buffer.getvalue()

# Base64 encode and publish
img_base64 = base64.b64encode(img_bytes).decode('utf-8')
# ... publish via MQTT
```

**Performance Considerations:**
- Use JPEG for faster encoding and smaller payload (better for MQTT)
- Adjust quality parameter to balance size vs quality
- Consider resizing image to e-ink display dimensions before encoding
- Use Timer CHOP to control update rate (don't send faster than display can refresh)

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
