#!/usr/bin/env python3
"""
APRS iGate Display - Main Application
Display APRS packets and statistics on e-ink display
"""

import json
import time
import logging
from datetime import datetime
from collections import deque
import aprslib
from PIL import Image, ImageDraw, ImageFont
import signal
import sys
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APRSiGateDisplay:
    def __init__(self, config_path='config.json'):
        """Initialize APRS iGate with display"""
        self.config = self.load_config(config_path)
        self.running = False
        self.display = None
        
        # Packet storage
        self.recent_packets = deque(maxlen=100)
        self.stats = {
            'total_packets': 0,
            'unique_stations': set(),
            'start_time': time.time(),
            'packets_by_type': {}
        }
        
        # Display mode
        self.display_mode = 0  # 0: packets, 1: stats, 2: weather
        self.mode_names = ['Packets', 'Statistics', 'Weather']
        
        # Initialize display
        self.init_display()
        
        # Setup APRS connection
        self.aprs_client = None
        self.setup_aprs()
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            logger.info("Creating default config...")
            default_config = self.create_default_config()
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def create_default_config(self):
        """Create default configuration"""
        return {
            "station": {
                "callsign": "N0CALL",
                "ssid": "10",
                "passcode": "-1",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "comment": "Pwnagotchi APRS iGate"
            },
            "aprs_is": {
                "servers": ["rotate.aprs2.net:14580"],
                "filter": "r/40.7128/-74.0060/50"
            },
            "display": {
                "model": "epd2in13_V2",
                "rotation": 0,
                "width": 250,
                "height": 122,
                "refresh_interval": 30,
                "auto_rotate_modes": True,
                "mode_duration": 60
            }
        }
    
    def init_display(self):
        """Initialize the e-ink display"""
        try:
            display_model = self.config['display']['model']
            logger.info(f"Initializing display: {display_model}")
            
            # Placeholder for actual display initialization
            logger.warning("Display initialization placeholder - implement for your specific model")
            
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            self.display = None
    
    def setup_aprs(self):
        """Setup APRS-IS connection"""
        callsign = f"{self.config['station']['callsign']}-{self.config['station']['ssid']}"
        passcode = self.config['station']['passcode']
        
        if passcode == "-1":
            logger.warning("Using read-only APRS-IS connection (passcode: -1)")
        
        try:
            self.aprs_client = aprslib.IS(
                callsign,
                passwd=passcode,
                host=self.config['aprs_is']['servers'][0].split(':')[0],
                port=int(self.config['aprs_is']['servers'][0].split(':')[1])
            )
            
            # Set callback for received packets
            self.aprs_client.set_filter(self.config['aprs_is']['filter'])
            
        except Exception as e:
            logger.error(f"Failed to setup APRS connection: {e}")
    
    def packet_callback(self, packet):
        """Handle received APRS packet"""
        try:
            # Parse packet
            parsed = aprslib.parse(packet)
            
            # Store packet
            self.recent_packets.append({
                'time': datetime.now(),
                'raw': packet,
                'parsed': parsed
            })
            
            # Update statistics
            self.stats['total_packets'] += 1
            if 'from' in parsed:
                self.stats['unique_stations'].add(parsed['from'])
            
            packet_type = parsed.get('format', 'unknown')
            self.stats['packets_by_type'][packet_type] = \
                self.stats['packets_by_type'].get(packet_type, 0) + 1
            
            logger.info(f"Packet from {parsed.get('from', 'unknown')}: {packet_type}")
            
            # Trigger display update
            self.update_display()
            
        except Exception as e:
            logger.error(f"Failed to process packet: {e}")
    
    def create_display_image(self):
        """Create image for current display mode"""
        width = self.config['display']['width']
        height = self.config['display']['height']
        
        # Create blank image
        image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(image)
        
        try:
            # Use default font
            font = ImageFont.load_default()
        except:
            font = None
        
        if self.display_mode == 0:
            # Recent packets mode
            self.draw_packets_mode(draw, font, width, height)
        elif self.display_mode == 1:
            # Statistics mode
            self.draw_stats_mode(draw, font, width, height)
        elif self.display_mode == 2:
            # Weather mode
            self.draw_weather_mode(draw, font, width, height)
        
        return image
    
    def draw_packets_mode(self, draw, font, width, height):
        """Draw recent packets on display"""
        y = 0
        line_height = 12
        
        # Title
        draw.text((0, y), f"APRS Packets ({len(self.recent_packets)})", font=font, fill=0)
        y += line_height + 2
        
        # Draw line
        draw.line([(0, y), (width, y)], fill=0)
        y += 2
        
        # Recent packets
        for packet in list(self.recent_packets)[-5:]:
            parsed = packet['parsed']
            callsign = parsed.get('from', 'N0CALL')
            time_str = packet['time'].strftime('%H:%M')
            
            # Format line based on packet type
            if 'latitude' in parsed and 'longitude' in parsed:
                lat = parsed['latitude']
                lon = parsed['longitude']
                text = f"{time_str} {callsign} {lat:.2f},{lon:.2f}"
            elif 'message_text' in parsed:
                msg = parsed['message_text'][:20]
                text = f"{time_str} {callsign}: {msg}"
            else:
                text = f"{time_str} {callsign}"
            
            if y + line_height < height:
                draw.text((0, y), text, font=font, fill=0)
                y += line_height
    
    def draw_stats_mode(self, draw, font, width, height):
        """Draw statistics on display"""
        y = 0
        line_height = 12
        
        # Title
        draw.text((0, y), "APRS Statistics", font=font, fill=0)
        y += line_height + 2
        draw.line([(0, y), (width, y)], fill=0)
        y += 4
        
        # Calculate uptime
        uptime = int(time.time() - self.stats['start_time'])
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        
        # Statistics
        stats_lines = [
            f"Uptime: {hours}h {minutes}m",
            f"Packets: {self.stats['total_packets']}",
            f"Stations: {len(self.stats['unique_stations'])}",
            f"Rate: {self.stats['total_packets'] / max(uptime/3600, 0.1):.1f}/hr"
        ]
        
        for line in stats_lines:
            if y + line_height < height:
                draw.text((0, y), line, font=font, fill=0)
                y += line_height
        
        # Packet types
        y += 4
        if y + line_height < height:
            draw.text((0, y), "By Type:", font=font, fill=0)
            y += line_height
            
            for ptype, count in list(self.stats['packets_by_type'].items())[:3]:
                if y + line_height < height:
                    draw.text((0, y), f"  {ptype}: {count}", font=font, fill=0)
                    y += line_height
    
    def draw_weather_mode(self, draw, font, width, height):
        """Draw weather information on display"""
        y = 0
        line_height = 12
        
        # Title
        draw.text((0, y), "APRS Weather", font=font, fill=0)
        y += line_height + 2
        draw.line([(0, y), (width, y)], fill=0)
        y += 4
        
        # Find weather packets
        weather_packets = [p for p in self.recent_packets 
                          if p['parsed'].get('format') == 'wx']
        
        if weather_packets:
            latest = weather_packets[-1]['parsed']
            
            weather_lines = []
            if 'temperature' in latest:
                weather_lines.append(f"Temp: {latest['temperature']}°F")
            if 'pressure' in latest:
                weather_lines.append(f"Press: {latest['pressure']} mb")
            if 'wind_speed' in latest:
                weather_lines.append(f"Wind: {latest['wind_speed']} mph")
            if 'humidity' in latest:
                weather_lines.append(f"Humid: {latest['humidity']}%")
            
            station = latest.get('from', 'Unknown')
            draw.text((0, y), f"Station: {station}", font=font, fill=0)
            y += line_height
            
            for line in weather_lines:
                if y + line_height < height:
                    draw.text((0, y), line, font=font, fill=0)
                    y += line_height
        else:
            draw.text((0, y), "No weather data", font=font, fill=0)
    
    def update_display(self):
        """Update the e-ink display"""
        image = self.create_display_image()
        
        if not self.display:
            # Save to file for testing
            image.save('/tmp/aprs_display.png')
            logger.debug("Display image saved to /tmp/aprs_display.png")
            return
        
        try:
            # Update e-ink display
            # self.display.display(self.display.getbuffer(image))
            logger.debug("Display updated")
        except Exception as e:
            logger.error(f"Failed to update display: {e}")
    
    def display_rotation_thread(self):
        """Thread to automatically rotate display modes"""
        if not self.config['display'].get('auto_rotate_modes', False):
            return
        
        mode_duration = self.config['display'].get('mode_duration', 60)
        
        while self.running:
            time.sleep(mode_duration)
            self.display_mode = (self.display_mode + 1) % len(self.mode_names)
            logger.info(f"Switching to display mode: {self.mode_names[self.display_mode]}")
            self.update_display()
    
    def start(self):
        """Start the APRS iGate application"""
        logger.info("Starting APRS iGate Display...")
        self.running = True
        
        # Start display rotation thread
        rotation_thread = threading.Thread(target=self.display_rotation_thread, daemon=True)
        rotation_thread.start()
        
        try:
            # Connect to APRS-IS
            self.aprs_client.connect()
            logger.info("Connected to APRS-IS")
            
            # Start receiving packets
            self.aprs_client.consumer(
                self.packet_callback,
                raw=True,
                blocking=True
            )
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the application"""
        self.running = False
        
        if self.aprs_client:
            self.aprs_client.close()
        
        logger.info("APRS iGate Display stopped")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    igate = APRSiGateDisplay()
    igate.start()
