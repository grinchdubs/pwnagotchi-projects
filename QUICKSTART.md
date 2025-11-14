# Quick Start Guide

Get one of your Pwnagotchi repurposing projects up and running in 15 minutes!

## Prerequisites Checklist

- [ ] Raspberry Pi Zero W with Raspberry Pi OS installed
- [ ] Waveshare e-ink display connected
- [ ] WiFi configured
- [ ] SSH access enabled
- [ ] Know which project you want to start with

## Step-by-Step Setup

### 1. Prepare Your Pi Zero W

```bash
# SSH into your Pi
ssh pi@raspberrypi.local

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install base dependencies
sudo apt-get install -y python3-pip python3-pil git
```

### 2. Enable SPI for E-ink Display

```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Yes
sudo reboot
```

### 3. Install Waveshare Library

```bash
# Clone Waveshare repository
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python/
sudo python3 setup.py install
cd ~
```

### 4. Clone This Repository

```bash
git clone <your-repo-url> pwnagotchi-projects
cd pwnagotchi-projects
```

### 5. Choose Your Project

#### Option A: Generative Art Frame

```bash
cd generative-art-frame
pip3 install -r requirements.txt
cp config.example.json config.json
nano config.json  # Edit MQTT broker address
```

**Test it:**
```bash
python3 main.py
# In another terminal, publish a test image:
# mosquitto_pub -h localhost -t art/frame/command -m "status"
```

#### Option B: APRS iGate Display

```bash
cd aprs-igate-display
pip3 install -r requirements.txt
cp config.example.json config.json
nano config.json  # Edit callsign, passcode, location
```

**Get your APRS passcode:**
Visit: https://apps.magicbug.co.uk/passcode/

**Test it:**
```bash
python3 main.py
# You should see APRS packets appearing on the display
```

#### Option C: Live Performance Companion

```bash
cd performance-companion
pip3 install -r requirements.txt
cp config.example.json config.json
nano config.example.json  # Verify OSC ports
```

**Test it:**
```bash
python3 main.py
# From your computer, send OSC message:
# /live/tempo 128.0
```

### 6. Verify Display Hardware

If the display doesn't work, test with Waveshare examples:

```bash
cd ~/e-Paper/RaspberryPi_JetsonNano/python/examples/
python3 epd_2in13_V2_test.py  # Adjust for your display model
```

### 7. Run as Service (Optional)

Create a systemd service to run on boot:

```bash
# For generative art frame example
sudo nano /etc/systemd/system/art-frame.service
```

Add this content:
```ini
[Unit]
Description=Generative Art Frame
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pwnagotchi-projects/generative-art-frame
ExecStart=/usr/bin/python3 /home/pi/pwnagotchi-projects/generative-art-frame/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable art-frame.service
sudo systemctl start art-frame.service
sudo systemctl status art-frame.service
```

## Troubleshooting

### Display shows nothing
1. Check SPI is enabled: `lsmod | grep spi`
2. Verify wiring connections
3. Test with Waveshare example code
4. Check display model in config matches your hardware

### Can't connect to MQTT/OSC
1. Verify broker/server is running
2. Check firewall settings
3. Test network connectivity: `ping <broker-ip>`
4. Verify ports in config.json

### Import errors
```bash
# Install missing dependencies
pip3 install -r requirements.txt

# If still errors, try:
sudo pip3 install -r requirements.txt
```

### APRS connection fails
1. Verify callsign and passcode are correct
2. Check APRS-IS server is reachable
3. Ensure you have internet connectivity
4. Check firewall isn't blocking port 14580

### Permission denied errors
```bash
# Add user to GPIO group
sudo usermod -a -G spi,gpio,i2c pi
# Reboot
sudo reboot
```

## Next Steps

### Customize Your Display
1. Edit `main.py` to modify display layouts
2. Adjust refresh rates in `config.json`
3. Add new display modes

### Integration Examples

**TouchDesigner → Art Frame:**
- Add MQTT Out CHOP
- Set broker and topic
- Send images as base64

**Ableton → Performance Companion:**
- Install LiveOSC or use Connection Kit
- Configure OSC output
- Map controls to companion

**APRS Radio → iGate:**
- Configure your station location
- Set appropriate filters
- Monitor local packet activity

## Getting Help

- Check individual project READMEs for detailed info
- Review example configurations
- Test components individually
- Check logs: `journalctl -u art-frame.service -f`

## What's Next?

- **Generative Art Frame**: Connect to your TouchDesigner projects
- **APRS iGate**: Add GPS for mobile operation
- **Performance Companion**: Create Max for Live devices

Happy making! 🎨📻🎵
