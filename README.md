# Pwnagotchi Repurposing Projects

Three creative projects that repurpose Pwnagotchi hardware (Raspberry Pi Zero W + e-ink display) for artistic, amateur radio, and performance applications.

## Projects

### 1. [Generative Art Frame](./generative-art-frame/)
Display generative art from TouchDesigner/Hydra on an e-ink screen via MQTT.

**Key Features:**
- MQTT subscription for real-time art updates
- Dithering optimized for e-ink displays
- TouchDesigner/Hydra integration
- Pen plotter preview queue management

**Use Cases:**
- Studio art display
- Pen plotting previews
- Interactive installations
- Gallery exhibitions

### 2. [APRS iGate Display](./aprs-igate-display/)
Amateur radio APRS iGate with local packet display and statistics.

**Key Features:**
- APRS-IS gateway functionality
- Real-time packet display
- Weather data visualization
- Station statistics and tracking

**Use Cases:**
- APRS monitoring station
- Portable iGate for events
- Weather station display
- Ham radio shack companion

**Requirements:** Valid amateur radio license for APRS operation

### 3. [Live Performance Companion](./performance-companion/)
Real-time performance data display for Ableton Live and TouchDesigner performances.

**Key Features:**
- Ableton Live integration (BPM, scenes, tracks)
- TouchDesigner parameter monitoring
- OSC and MQTT support
- Performance notes and set list management

**Use Cases:**
- Live A/V performances
- DJ sets
- Interactive installations
- Live coding sessions

## Hardware

All projects use the same base hardware:
- **Raspberry Pi Zero W** - WiFi-enabled single-board computer
- **Waveshare e-ink display** - Low power, always-readable display
- **Power supply** - USB power or battery pack
- **Case** - Original Pwnagotchi case or custom 3D printed enclosure

### Recommended Display Models
- Waveshare 2.13" (250x122) - Compact, perfect for portable use
- Waveshare 2.7" (264x176) - Larger display area, more information
- Waveshare 4.2" (400x300) - Maximum visibility

## Getting Started

### Prerequisites

1. **Raspberry Pi Zero W Setup**
   ```bash
   # Flash Raspberry Pi OS Lite to SD card
   # Enable WiFi and SSH
   # Update system
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Install Common Dependencies**
   ```bash
   sudo apt-get install -y python3-pip python3-pil git
   ```

3. **Clone Repository**
   ```bash
   git clone <your-repo-url>
   cd pwnagotchi-projects
   ```

### Choose Your Project

Navigate to the project directory and follow its specific README:

```bash
# For Generative Art Frame
cd generative-art-frame
pip3 install -r requirements.txt
cp config.example.json config.json
# Edit config.json with your settings
python3 main.py

# For APRS iGate Display
cd aprs-igate-display
pip3 install -r requirements.txt
cp config.example.json config.json
# Edit config.json with your callsign and location
python3 main.py

# For Live Performance Companion
cd performance-companion
pip3 install -r requirements.txt
cp config.example.json config.json
# Edit config.json with your OSC settings
python3 main.py
```

## Display Driver Installation

Each project requires the appropriate Waveshare e-ink library. Install based on your display model:

```bash
# Clone Waveshare e-Paper library
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python/
sudo python3 setup.py install
```

## Running as System Services

To run any project automatically on boot:

```bash
# Create systemd service file
sudo nano /etc/systemd/system/art-frame.service

# Add service configuration (see project README)
sudo systemctl enable art-frame.service
sudo systemctl start art-frame.service
```

## Network Configuration

### WiFi Setup
Edit `/etc/wpa_supplicant/wpa_supplicant.conf`:
```
network={
    ssid="YourNetworkName"
    psk="YourPassword"
}
```

### Static IP (Optional)
For reliable MQTT/OSC connections, configure static IP in `/etc/dhcpcd.conf`:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

## Power Optimization

E-ink displays are naturally low-power. Additional optimizations:

```bash
# Disable HDMI (saves ~20mA)
sudo /opt/vc/bin/tvservice -o

# Disable LEDs
echo 0 | sudo tee /sys/class/leds/led0/brightness

# Disable WiFi power management
sudo iwconfig wlan0 power off
```

## Troubleshooting

### Display Not Updating
- Check SPI is enabled: `sudo raspi-config` → Interface Options → SPI
- Verify display connections
- Test with Waveshare example code

### MQTT Connection Issues
- Verify broker address and port
- Check firewall settings
- Test connection: `mosquitto_sub -h broker -t test`

### OSC Not Receiving
- Verify correct port configuration
- Check firewall: `sudo ufw allow 9000/udp`
- Test with OSC debugging tools

### Performance Issues
- Reduce display refresh rate
- Optimize Python code
- Consider overclocking (carefully)

## Development

### Project Structure
```
pwnagotchi-projects/
├── generative-art-frame/
│   ├── main.py
│   ├── config.example.json
│   ├── requirements.txt
│   └── README.md
├── aprs-igate-display/
│   ├── main.py
│   ├── config.example.json
│   ├── requirements.txt
│   └── README.md
├── performance-companion/
│   ├── main.py
│   ├── config.example.json
│   ├── setlist.example.json
│   ├── requirements.txt
│   └── README.md
└── README.md (this file)
```

### Contributing
Contributions welcome! Areas for improvement:
- Additional display modes
- Web configuration interfaces
- More integration examples
- Power optimization
- Alternative display support

## Credits

**Hardware:** Original Pwnagotchi project by [@evilsocket](https://github.com/evilsocket)

**Projects:** Built by Grnch for creative and technical applications

**Libraries:**
- [aprslib](https://github.com/rossengeorgiev/aprs-python) for APRS functionality
- [python-osc](https://github.com/attwad/python-osc) for OSC communication
- [paho-mqtt](https://github.com/eclipse/paho.mqtt.python) for MQTT
- [Pillow](https://python-pillow.org/) for image processing
- [Waveshare e-Paper](https://github.com/waveshare/e-Paper) for display drivers

## License

MIT License - Feel free to modify and distribute these projects.

## Resources

- [Pwnagotchi Project](https://pwnagotchi.ai/)
- [Raspberry Pi Zero W Documentation](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
- [Waveshare e-Paper Displays](https://www.waveshare.com/product/displays/e-paper.htm)
- [APRS.fi](https://aprs.fi/) - APRS tracking and information
- [TouchDesigner](https://derivative.ca/) - Visual development platform
- [Ableton Live](https://www.ableton.com/) - Music production software

## Contact

Questions or ideas? Open an issue or reach out!

---

**Note:** These projects are intended for educational and creative purposes. Always respect applicable laws and regulations, especially for amateur radio operations.
