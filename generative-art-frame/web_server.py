#!/usr/bin/env python3
"""
Web Interface for Generative Art Frame
Simple Flask web server for configuring and controlling the e-ink display
"""

from flask import Flask, render_template, request, jsonify
import json
import os
import base64
from pathlib import Path

app = Flask(__name__)

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'mqtt': {
        'broker': 'mqtt.local',
        'port': 1883,
        'topics': {
            'image': 'art/frame/image',
            'command': 'art/frame/command',
            'status': 'art/frame/status'
        }
    },
    'display': {
        'model': 'epd2in13_V2',
        'rotation': 0,
        'refresh_interval': 5
    },
    'image_processing': {
        'dither_method': 'floyd-steinberg',
        'contrast': 1.2,
        'brightness': 1.0
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

@app.route('/')
def index():
    """Main dashboard page"""
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration"""
    if request.method == 'POST':
        config = request.json
        save_config(config)
        return jsonify({'status': 'success', 'message': 'Configuration saved'})
    else:
        return jsonify(load_config())

@app.route('/api/clear_display', methods=['POST'])
def clear_display():
    """Clear the display"""
    # TODO: Implement display clear via MQTT command
    return jsonify({'status': 'success', 'message': 'Display cleared'})

@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    """Upload and display an image"""
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    # Read and encode image
    img_data = file.read()
    img_base64 = base64.b64encode(img_data).decode('utf-8')

    # TODO: Send via MQTT
    # For now, save to temp file
    with open('temp_upload.txt', 'w') as f:
        f.write(img_base64)

    return jsonify({
        'status': 'success',
        'message': 'Image uploaded',
        'size': len(img_data)
    })

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
