# TouchDesigner Setup for Generative Art Frame

This guide helps you set up TouchDesigner to send rendered images to your e-ink display via MQTT.

## Quick Start

### 1. Run the Network Builder Script

In TouchDesigner textport:
```python
exec(open(r'build_mqtt_network.py').read())
```

This creates:
- Timer CHOP for triggering uploads
- Execute DAT with image capture and encoding code
- Info DAT with detailed setup instructions

### 2. Customize Configuration

Edit the script before running to match your setup:

```python
result = build_mqtt_upload_network(
    parent_comp=op('/project1'),
    source_top_name='render1',  # Your render TOP name
    mqtt_broker='raspberrypi.local',  # Your Pi's hostname or IP
    mqtt_port=1883,
    mqtt_topic='art/frame/image',
    upload_interval=5.0,  # Seconds between uploads
    image_format='JPEG',  # or 'PNG'
    image_quality=85  # JPEG quality 1-100
)
```

### 3. Install MQTT Library

You need `paho-mqtt` Python library:

1. Open Palette in TouchDesigner (Alt+L)
2. Search for "tdPyEnvManager"
3. Drag it into your network
4. Use it to install "paho-mqtt" package

### 4. Enable MQTT Publishing

Edit the Execute DAT created by the script:

1. Find the `# TODO: Publish to MQTT` section
2. Uncomment the paho-mqtt code:

```python
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect('raspberrypi.local', 1883)
client.publish('art/frame/image', img_base64)
client.disconnect()
```

### 5. Start Uploading

In textport:
```python
op('mqtt_upload_timer').par.start.pulse()
```

## How It Works

### Image Capture Process

1. **Timer triggers** every `upload_interval` seconds
2. **Execute DAT callback** captures the frame:
   - Gets pixel data from source TOP using `numpyArray()`
   - Converts float32 (0-1) to uint8 (0-255)
   - Flips vertically (TD uses bottom-left origin)
   - Converts RGBA to RGB if needed
3. **Encodes image** to JPEG or PNG using PIL
4. **Base64 encodes** for MQTT transmission
5. **Publishes** to MQTT broker

### Network Structure

```
[Source TOP (render1)]
         ↓
[Timer CHOP] → [Execute DAT] → MQTT Publish
         ↓
  Triggers every N seconds
```

## Configuration Options

### Image Format

**JPEG (Recommended)**:
- Smaller file size (better for MQTT/network)
- Faster encoding
- Adjust quality 70-95 for size/quality balance
- Best for: photographs, complex art

**PNG**:
- Lossless compression
- Larger file size
- Slower encoding
- Best for: graphics, text, solid colors

### Upload Interval

Balance between:
- **Faster (1-2 sec)**: More responsive, higher network load
- **Slower (5-10 sec)**: Less network traffic, e-ink refresh rate limited anyway

E-ink displays refresh slowly (1-3 seconds), so uploading faster than 2-3 seconds provides diminishing returns.

### Image Quality

For JPEG, quality parameter affects:
- **85-95**: High quality, larger files
- **70-85**: Good balance (recommended)
- **50-70**: Lower quality, smaller files

## Troubleshooting

### "Source TOP not found"

Error: `ERROR: Source TOP 'render1' not found`

Solution: Change `source_top_name` to your actual render TOP:
```python
build_mqtt_upload_network(source_top_name='my_render_top')
```

### MQTT Connection Failed

Error: `Connection refused` or `Timeout`

Check:
1. Pi Zero W is powered on and connected to network
2. MQTT broker is running on Pi: `systemctl status mosquitto`
3. Network is reachable: `ping raspberrypi.local`
4. Firewall allows port 1883: `sudo ufw allow 1883`

### No Images on Display

Check:
1. MQTT messages are being sent (check textport for "Frame ready for upload")
2. Pi is receiving messages: `mosquitto_sub -h localhost -t art/frame/image`
3. Pi display script is running: `systemctl status art-frame`
4. Check Pi logs: `journalctl -u art-frame -f`

### Performance Issues

If TouchDesigner is slowing down:
1. Increase `upload_interval` to reduce frequency
2. Use JPEG instead of PNG
3. Lower JPEG quality
4. Reduce source TOP resolution before capture

## Advanced: Multiple Sources

To send from multiple TOPs:

```python
# Build network for first source
build_mqtt_upload_network(
    source_top_name='render1',
    mqtt_topic='art/frame/image/render1'
)

# Build network for second source
build_mqtt_upload_network(
    source_top_name='noise1',
    mqtt_topic='art/frame/image/noise1'
)
```

Configure Pi to subscribe to multiple topics or use wildcard: `art/frame/image/#`

## Advanced: Custom Image Processing

Edit the Execute DAT to add custom processing:

```python
# After getting img as PIL Image:
img = Image.fromarray(img_array, mode='RGB')

# Resize to match e-ink display
img = img.resize((250, 122), Image.LANCZOS)  # For 2.13" display

# Apply filters
from PIL import ImageFilter
img = img.filter(ImageFilter.SHARPEN)

# Adjust contrast/brightness
from PIL import ImageEnhance
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(1.2)  # Increase contrast 20%

# Then encode and send
buffer = io.BytesIO()
img.save(buffer, format='JPEG', quality=85)
```

## References

- [TouchDesigner Python API](https://derivative.ca/UserGuide/Category%3APython)
- [Paho MQTT Python Client](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
- [Pillow (PIL) Documentation](https://pillow.readthedocs.io/)
