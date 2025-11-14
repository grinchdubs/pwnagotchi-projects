#!/usr/bin/env python3
"""
Web Interface for APRS iGate Display
Flask web server for configuring and monitoring the APRS iGate
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

CONFIG_FILE = 'config.json'
PACKETS_FILE = 'recent_packets.json'
DEFAULT_CONFIG = {
    'station': {
        'callsign': 'N0CALL',
        'ssid': 10,
        'passcode': 0,
        'latitude': 40.7128,
        'longitude': -74.0060,
        'comment': 'Pwnagotchi iGate'
    },
    'aprs_is': {
        'server': 'rotate.aprs2.net',
        'port': 14580,
        'filter': 'r/40.7128/-74.0060/50'
    },
    'display': {
        'model': 'epd2in13_V2',
        'rotation': 0,
        'refresh_interval': 30,
        'default_mode': 0
    }
}

def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_recent_packets():
    """Get recent APRS packets"""
    if os.path.exists(PACKETS_FILE):
        with open(PACKETS_FILE, 'r') as f:
            return json.load(f)
    return []

def get_statistics():
    """Get APRS statistics"""
    # TODO: Implement actual statistics tracking
    return {
        'total_packets': 0,
        'unique_stations': 0,
        'packets_per_hour': 0,
        'uptime_hours': 0
    }

@app.route('/')
def index():
    """Main dashboard page"""
    config = load_config()
    packets = get_recent_packets()
    stats = get_statistics()
    return render_template('index.html', config=config, packets=packets, stats=stats)

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration"""
    if request.method == 'POST':
        config = request.json
        save_config(config)
        return jsonify({'status': 'success', 'message': 'Configuration saved. Restart service to apply changes.'})
    else:
        return jsonify(load_config())

@app.route('/api/packets', methods=['GET'])
def api_packets():
    """Get recent packets"""
    return jsonify(get_recent_packets())

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get statistics"""
    return jsonify(get_statistics())

@app.route('/api/change_mode', methods=['POST'])
def change_mode():
    """Change display mode"""
    mode = request.json.get('mode', 0)
    # TODO: Send mode change command to display
    return jsonify({'status': 'success', 'message': f'Display mode changed to {mode}'})

@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
    import psutil

    return jsonify({
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'temperature': get_cpu_temperature()
    })

def get_cpu_temperature():
    """Get CPU temperature"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read()) / 1000.0
            return round(temp, 1)
    except:
        return None

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    # Run server
    app.run(host='0.0.0.0', port=5000, debug=False)
