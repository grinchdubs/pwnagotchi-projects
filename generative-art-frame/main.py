#!/usr/bin/env python3
"""
Generative Art Frame - Main Application
Displays generative art from TouchDesigner/Hydra on e-ink display via MQTT
"""

import json
import base64
import time
import logging
from io import BytesIO
from pathlib import Path
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GenerativeArtFrame:
    def __init__(self, config_path='config.json'):
        """Initialize the art frame with configuration"""
        self.config = self.load_config(config_path)
        self.running = False
        self.last_image = None
        self.display = None
        
        # Initialize display based on config
        self.init_display()
        
        # Setup MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        
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
            "mqtt": {
                "broker": "localhost",
                "port": 1883,
                "topics": {
                    "image": "art/frame/image",
                    "command": "art/frame/command",
                    "status": "art/frame/status"
                }
            },
            "display": {
                "model": "epd2in13_V2",
                "rotation": 0,
                "width": 250,
                "height": 122
            },
            "processing": {
                "dither_method": "floyd-steinberg",
                "resize_mode": "contain",
                "refresh_interval": 30
            }
        }
    
    def init_display(self):
        """Initialize the e-ink display"""
        try:
            # Import display driver based on config
            display_model = self.config['display']['model']
            logger.info(f"Initializing display: {display_model}")
            
            # This is a placeholder - actual implementation depends on display model
            # Example for Waveshare:
            # from waveshare_epd import epd2in13_V2
            # self.display = epd2in13_V2.EPD()
            # self.display.init()
            # self.display.Clear()
            
            logger.warning("Display initialization placeholder - implement for your specific model")
            
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            self.display = None
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to topics
            topics = self.config['mqtt']['topics']
            client.subscribe(topics['image'])
            client.subscribe(topics['command'])
            logger.info(f"Subscribed to: {topics['image']}, {topics['command']}")
            
            # Publish online status
            self.publish_status("online")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        logger.warning(f"Disconnected from MQTT broker: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Callback for MQTT messages"""
        topic = msg.topic
        
        if topic == self.config['mqtt']['topics']['image']:
            self.handle_image_message(msg.payload)
        elif topic == self.config['mqtt']['topics']['command']:
            self.handle_command_message(msg.payload)
    
    def handle_image_message(self, payload):
        """Handle incoming image data"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(payload)
            image = Image.open(BytesIO(image_data))
            
            logger.info(f"Received image: {image.size}, {image.mode}")
            
            # Process and display
            processed_image = self.process_image(image)
            self.display_image(processed_image)
            self.last_image = processed_image
            
        except Exception as e:
            logger.error(f"Failed to handle image: {e}")
    
    def handle_command_message(self, payload):
        """Handle command messages"""
        try:
            command = payload.decode('utf-8')
            logger.info(f"Received command: {command}")
            
            if command == "clear":
                self.clear_display()
            elif command == "refresh":
                if self.last_image:
                    self.display_image(self.last_image)
            elif command == "status":
                self.publish_status("running")
                
        except Exception as e:
            logger.error(f"Failed to handle command: {e}")
    
    def process_image(self, image):
        """Process image for e-ink display"""
        width = self.config['display']['width']
        height = self.config['display']['height']
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize maintaining aspect ratio
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        
        # Create new image with exact display dimensions
        processed = Image.new('RGB', (width, height), 'white')
        
        # Center the image
        x = (width - image.width) // 2
        y = (height - image.height) // 2
        processed.paste(image, (x, y))
        
        # Convert to 1-bit with dithering
        processed = processed.convert('1')
        
        # Apply rotation if configured
        rotation = self.config['display'].get('rotation', 0)
        if rotation:
            processed = processed.rotate(rotation, expand=True)
        
        return processed
    
    def display_image(self, image):
        """Send image to e-ink display"""
        if not self.display:
            logger.warning("Display not initialized - saving to file instead")
            image.save('/tmp/art_frame_output.png')
            logger.info("Image saved to /tmp/art_frame_output.png")
            return
        
        try:
            # Display on e-ink
            # This is a placeholder - implement for your specific display
            # Example: self.display.display(self.display.getbuffer(image))
            logger.info("Image displayed on e-ink screen")
            
        except Exception as e:
            logger.error(f"Failed to display image: {e}")
    
    def clear_display(self):
        """Clear the e-ink display"""
        if self.display:
            try:
                # self.display.Clear()
                logger.info("Display cleared")
            except Exception as e:
                logger.error(f"Failed to clear display: {e}")
    
    def publish_status(self, status):
        """Publish status to MQTT"""
        topic = self.config['mqtt']['topics']['status']
        payload = json.dumps({
            "status": status,
            "timestamp": time.time()
        })
        self.mqtt_client.publish(topic, payload)
    
    def start(self):
        """Start the art frame application"""
        logger.info("Starting Generative Art Frame...")
        self.running = True
        
        # Connect to MQTT broker
        broker = self.config['mqtt']['broker']
        port = self.config['mqtt']['port']
        
        try:
            self.mqtt_client.connect(broker, port, 60)
            self.mqtt_client.loop_start()
            
            # Keep running
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the application"""
        self.running = False
        self.publish_status("offline")
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        
        if self.display:
            self.clear_display()
        
        logger.info("Generative Art Frame stopped")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    frame = GenerativeArtFrame()
    frame.start()
