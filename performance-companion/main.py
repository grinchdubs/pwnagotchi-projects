#!/usr/bin/env python3
"""
Live Performance Companion - Main Application
Display real-time Ableton/TouchDesigner data on e-ink display
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pythonosc import dispatcher, osc_server
from pythonosc import udp_client
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont
import signal
import sys
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceCompanion:
    def __init__(self, config_path='config.json'):
        """Initialize the performance companion"""
        self.config = self.load_config(config_path)
        self.running = False
        self.display = None
        
        # Performance data
        self.performance_data = {
            'ableton': {
                'bpm': 120.0,
                'scene': 'No Scene',
                'playing': False,
                'time': 0,
                'track_volumes': {}
            },
            'touchdesigner': {
                'fps': 0.0,
                'composition': 'No Composition',
                'parameters': {}
            },
            'notes': [],
            'set_list': [],
            'current_song': 0
        }
        
        # Display state
        self.display_mode = self.config['display'].get('default_mode', 0)
        self.mode_names = ['Ableton', 'Levels', 'TouchDesigner', 'Notes', 'MIDI']
        self.last_update = time.time()
        
        # Initialize display
        self.init_display()
        
        # Setup OSC
        self.setup_osc()
        
        # Setup MQTT if enabled
        if self.config['sources']['mqtt']['enabled']:
            self.setup_mqtt()
        
        # Load set list if available
        self.load_set_list()
        
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
            "sources": {
                "ableton": {
                    "enabled": True,
                    "method": "osc",
                    "address": "0.0.0.0",
                    "port": 9000
                },
                "touchdesigner": {
                    "enabled": True,
                    "method": "osc",
                    "address": "0.0.0.0",
                    "port": 9001
                },
                "mqtt": {
                    "enabled": False,
                    "broker": "localhost",
                    "port": 1883,
                    "topics": ["performance/#"]
                }
            },
            "display": {
                "model": "epd2in13_V2",
                "rotation": 0,
                "width": 250,
                "height": 122,
                "default_mode": 0,
                "auto_rotate": False,
                "refresh_rate": 2
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
    
    def setup_osc(self):
        """Setup OSC servers for receiving data"""
        self.osc_dispatcher = dispatcher.Dispatcher()
        
        # Map OSC addresses to handlers
        self.osc_dispatcher.map("/live/tempo", self.handle_tempo)
        self.osc_dispatcher.map("/live/scene", self.handle_scene)
        self.osc_dispatcher.map("/live/playing", self.handle_playing)
        self.osc_dispatcher.map("/live/time", self.handle_time)
        self.osc_dispatcher.map("/live/track/*/volume", self.handle_track_volume)
        
        self.osc_dispatcher.map("/td/fps", self.handle_td_fps)
        self.osc_dispatcher.map("/td/composition", self.handle_td_composition)
        self.osc_dispatcher.map("/td/param/*", self.handle_td_param)
        
        self.osc_dispatcher.map("/companion/mode", self.handle_mode_change)
        self.osc_dispatcher.map("/companion/note", self.handle_note)
        
        # Catch-all for unhandled messages
        self.osc_dispatcher.set_default_handler(self.handle_default)
        
        # Create OSC servers (Ableton and TouchDesigner use different ports)
        self.osc_servers = []
        
        if self.config['sources']['ableton']['enabled']:
            port = self.config['sources']['ableton']['port']
            server = osc_server.ThreadingOSCUDPServer(
                ("0.0.0.0", port),
                self.osc_dispatcher
            )
            self.osc_servers.append(('Ableton', port, server))
        
        if self.config['sources']['touchdesigner']['enabled']:
            port = self.config['sources']['touchdesigner']['port']
            if port != self.config['sources']['ableton']['port']:
                server = osc_server.ThreadingOSCUDPServer(
                    ("0.0.0.0", port),
                    self.osc_dispatcher
                )
                self.osc_servers.append(('TouchDesigner', port, server))
    
    def setup_mqtt(self):
        """Setup MQTT client for receiving data"""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        broker = self.config['sources']['mqtt']['broker']
        port = self.config['sources']['mqtt']['port']
        
        try:
            self.mqtt_client.connect(broker, port, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            for topic in self.config['sources']['mqtt']['topics']:
                client.subscribe(topic)
                logger.info(f"Subscribed to: {topic}")
    
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = json.loads(msg.payload.decode())
            # Handle MQTT messages similar to OSC
            logger.debug(f"MQTT: {msg.topic} = {payload}")
        except Exception as e:
            logger.error(f"Failed to handle MQTT message: {e}")
    
    # OSC Handlers
    def handle_tempo(self, address, *args):
        """Handle tempo/BPM updates"""
        self.performance_data['ableton']['bpm'] = float(args[0])
        logger.debug(f"BPM: {args[0]}")
        self.trigger_display_update()
    
    def handle_scene(self, address, *args):
        """Handle scene name updates"""
        self.performance_data['ableton']['scene'] = str(args[0])
        logger.info(f"Scene: {args[0]}")
        self.trigger_display_update()
    
    def handle_playing(self, address, *args):
        """Handle play/stop status"""
        self.performance_data['ableton']['playing'] = bool(args[0])
        logger.info(f"Playing: {args[0]}")
        self.trigger_display_update()
    
    def handle_time(self, address, *args):
        """Handle playback time"""
        self.performance_data['ableton']['time'] = float(args[0])
        self.trigger_display_update()
    
    def handle_track_volume(self, address, *args):
        """Handle track volume updates"""
        # Extract track number from address
        parts = address.split('/')
        track_num = parts[3] if len(parts) > 3 else '0'
        self.performance_data['ableton']['track_volumes'][track_num] = float(args[0])
        self.trigger_display_update()
    
    def handle_td_fps(self, address, *args):
        """Handle TouchDesigner FPS"""
        self.performance_data['touchdesigner']['fps'] = float(args[0])
        self.trigger_display_update()
    
    def handle_td_composition(self, address, *args):
        """Handle TouchDesigner composition name"""
        self.performance_data['touchdesigner']['composition'] = str(args[0])
        logger.info(f"TD Composition: {args[0]}")
        self.trigger_display_update()
    
    def handle_td_param(self, address, *args):
        """Handle TouchDesigner parameters"""
        param_name = address.split('/')[-1]
        self.performance_data['touchdesigner']['parameters'][param_name] = args[0]
        self.trigger_display_update()
    
    def handle_mode_change(self, address, *args):
        """Handle display mode change"""
        mode = int(args[0])
        if 0 <= mode < len(self.mode_names):
            self.display_mode = mode
            logger.info(f"Display mode changed to: {self.mode_names[mode]}")
            self.trigger_display_update()
    
    def handle_note(self, address, *args):
        """Handle custom note display"""
        note = str(args[0])
        self.performance_data['notes'].append({
            'time': datetime.now(),
            'text': note
        })
        # Keep only last 10 notes
        self.performance_data['notes'] = self.performance_data['notes'][-10:]
        logger.info(f"Note: {note}")
        self.trigger_display_update()
    
    def handle_default(self, address, *args):
        """Handle unregistered OSC messages"""
        logger.debug(f"Unhandled OSC: {address} {args}")
    
    def load_set_list(self, path='setlist.json'):
        """Load set list from JSON file"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                self.performance_data['set_list'] = data.get('set_list', [])
                logger.info(f"Loaded set list with {len(self.performance_data['set_list'])} songs")
        except FileNotFoundError:
            logger.debug("No set list file found")
        except Exception as e:
            logger.error(f"Failed to load set list: {e}")
    
    def trigger_display_update(self):
        """Trigger a display update (rate-limited)"""
        refresh_rate = self.config['display']['refresh_rate']
        now = time.time()
        
        if now - self.last_update >= refresh_rate:
            self.update_display()
            self.last_update = now
    
    def create_display_image(self):
        """Create image for current display mode"""
        width = self.config['display']['width']
        height = self.config['display']['height']
        
        # Create blank image
        image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Render based on mode
        if self.display_mode == 0:
            self.draw_ableton_mode(draw, font, width, height)
        elif self.display_mode == 1:
            self.draw_levels_mode(draw, font, width, height)
        elif self.display_mode == 2:
            self.draw_touchdesigner_mode(draw, font, width, height)
        elif self.display_mode == 3:
            self.draw_notes_mode(draw, font, width, height)
        elif self.display_mode == 4:
            self.draw_midi_mode(draw, font, width, height)
        
        return image
    
    def draw_ableton_mode(self, draw, font, width, height):
        """Draw Ableton overview"""
        y = 0
        line_height = 12
        
        # Title
        mode_title = f"{self.mode_names[self.display_mode]} Mode"
        draw.text((0, y), mode_title, font=font, fill=0)
        y += line_height + 2
        draw.line([(0, y), (width, y)], fill=0)
        y += 4
        
        # BPM - Large
        bpm = self.performance_data['ableton']['bpm']
        draw.text((0, y), f"BPM: {bpm:.1f}", font=font, fill=0)
        y += line_height
        
        # Scene
        scene = self.performance_data['ableton']['scene']
        if len(scene) > 25:
            scene = scene[:22] + "..."
        draw.text((0, y), f"Scene: {scene}", font=font, fill=0)
        y += line_height
        
        # Status
        status = "PLAYING" if self.performance_data['ableton']['playing'] else "STOPPED"
        draw.text((0, y), f"Status: {status}", font=font, fill=0)
        y += line_height
        
        # Time
        time_sec = self.performance_data['ableton']['time']
        minutes = int(time_sec // 60)
        seconds = int(time_sec % 60)
        draw.text((0, y), f"Time: {minutes}:{seconds:02d}", font=font, fill=0)
    
    def draw_levels_mode(self, draw, font, width, height):
        """Draw audio levels"""
        y = 0
        line_height = 12
        
        draw.text((0, y), "Audio Levels", font=font, fill=0)
        y += line_height + 2
        draw.line([(0, y), (width, y)], fill=0)
        y += 4
        
        # Draw level bars for each track
        track_volumes = self.performance_data['ableton']['track_volumes']
        bar_height = 8
        bar_width = width - 60
        
        for track_num, volume in list(track_volumes.items())[:6]:
            if y + bar_height + 2 < height:
                # Track label
                draw.text((0, y), f"T{track_num}:", font=font, fill=0)
                
                # Volume bar
                bar_x = 30
                draw.rectangle([(bar_x, y), (bar_x + bar_width, y + bar_height)], outline=0)
                filled_width = int(bar_width * volume)
                if filled_width > 0:
                    draw.rectangle([(bar_x, y), (bar_x + filled_width, y + bar_height)], fill=0)
                
                y += bar_height + 3
    
    def draw_touchdesigner_mode(self, draw, font, width, height):
        """Draw TouchDesigner info"""
        y = 0
        line_height = 12
        
        draw.text((0, y), "TouchDesigner", font=font, fill=0)
        y += line_height + 2
        draw.line([(0, y), (width, y)], fill=0)
        y += 4
        
        # FPS
        fps = self.performance_data['touchdesigner']['fps']
        draw.text((0, y), f"FPS: {fps:.1f}", font=font, fill=0)
        y += line_height
        
        # Composition
        comp = self.performance_data['touchdesigner']['composition']
        if len(comp) > 25:
            comp = comp[:22] + "..."
        draw.text((0, y), f"Comp: {comp}", font=font, fill=0)
        y += line_height + 4
        
        # Parameters
        params = self.performance_data['touchdesigner']['parameters']
        for param_name, value in list(params.items())[:4]:
            if y + line_height < height:
                display_name = param_name[:15]
                if isinstance(value, float):
                    value_str = f"{value:.2f}"
                else:
                    value_str = str(value)[:10]
                draw.text((0, y), f"{display_name}: {value_str}", font=font, fill=0)
                y += line_height
    
    def draw_notes_mode(self, draw, font, width, height):
        """Draw performance notes"""
        y = 0
        line_height = 12
        
        draw.text((0, y), "Performance Notes", font=font, fill=0)
        y += line_height + 2
        draw.line([(0, y), (width, y)], fill=0)
        y += 4
        
        # Recent notes
        notes = self.performance_data['notes'][-5:]
        for note in notes:
            if y + line_height < height:
                time_str = note['time'].strftime('%H:%M')
                text = note['text'][:25]
                draw.text((0, y), f"{time_str}: {text}", font=font, fill=0)
                y += line_height
        
        if not notes:
            draw.text((0, y), "No notes", font=font, fill=0)
    
    def draw_midi_mode(self, draw, font, width, height):
        """Draw MIDI monitor"""
        y = 0
        line_height = 12
        
        draw.text((0, y), "MIDI Monitor", font=font, fill=0)
        y += line_height + 2
        draw.line([(0, y), (width, y)], fill=0)
        y += 4
        
        draw.text((0, y), "MIDI monitoring", font=font, fill=0)
        y += line_height
        draw.text((0, y), "not yet implemented", font=font, fill=0)
    
    def update_display(self):
        """Update the e-ink display"""
        image = self.create_display_image()
        
        if not self.display:
            # Save to file for testing
            image.save('/tmp/performance_display.png')
            logger.debug("Display image saved to /tmp/performance_display.png")
            return
        
        try:
            # Update e-ink display
            # self.display.display(self.display.getbuffer(image))
            logger.debug("Display updated")
        except Exception as e:
            logger.error(f"Failed to update display: {e}")
    
    def start(self):
        """Start the performance companion"""
        logger.info("Starting Live Performance Companion...")
        self.running = True
        
        # Start OSC servers in threads
        for name, port, server in self.osc_servers:
            thread = threading.Thread(
                target=server.serve_forever,
                daemon=True,
                name=f"OSC-{name}"
            )
            thread.start()
            logger.info(f"OSC server started for {name} on port {port}")
        
        try:
            # Main loop
            while self.running:
                time.sleep(1)
                # Periodic display refresh
                if self.config['display'].get('auto_rotate', False):
                    # Implement mode rotation if desired
                    pass
                    
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the application"""
        self.running = False
        
        # Shutdown OSC servers
        for name, port, server in self.osc_servers:
            server.shutdown()
            logger.info(f"Stopped OSC server for {name}")
        
        # Disconnect MQTT
        if hasattr(self, 'mqtt_client'):
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        logger.info("Live Performance Companion stopped")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    companion = PerformanceCompanion()
    companion.start()
