#!/usr/bin/env python3
"""
Web Interface for Performance Companion
Flask web server for configuring and controlling the performance display
"""

from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

CONFIG_FILE = 'config.json'
SETLIST_FILE = 'setlist.json'
DEFAULT_CONFIG = {
    'sources': {
        'ableton': {
            'enabled': True,
            'method': 'osc',
            'address': '0.0.0.0',
            'port': 9000
        },
        'touchdesigner': {
            'enabled': True,
            'method': 'osc',
            'address': '0.0.0.0',
            'port': 9001
        },
        'mqtt': {
            'enabled': False,
            'broker': 'localhost',
            'port': 1883,
            'topics': ['performance/#']
        }
    },
    'display': {
        'model': 'epd2in13_V2',
        'rotation': 0,
        'default_mode': 0,
        'auto_rotate': False,
        'refresh_rate': 2
    }
}

DEFAULT_SETLIST = {
    'show_name': 'My Performance',
    'set_list': []
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

def load_setlist():
    """Load set list from file"""
    if os.path.exists(SETLIST_FILE):
        with open(SETLIST_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_SETLIST.copy()

def save_setlist(setlist):
    """Save set list to file"""
    with open(SETLIST_FILE, 'w') as f:
        json.dump(setlist, f, indent=2)

@app.route('/')
def index():
    """Main dashboard page"""
    config = load_config()
    setlist = load_setlist()
    return render_template('index.html', config=config, setlist=setlist)

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration"""
    if request.method == 'POST':
        config = request.json
        save_config(config)
        return jsonify({'status': 'success', 'message': 'Configuration saved'})
    else:
        return jsonify(load_config())

@app.route('/api/setlist', methods=['GET', 'POST'])
def api_setlist():
    """Get or update set list"""
    if request.method == 'POST':
        setlist = request.json
        save_setlist(setlist)
        return jsonify({'status': 'success', 'message': 'Set list saved'})
    else:
        return jsonify(load_setlist())

@app.route('/api/change_mode', methods=['POST'])
def change_mode():
    """Change display mode"""
    mode = request.json.get('mode', 0)
    # TODO: Send OSC command to change mode
    return jsonify({'status': 'success', 'message': f'Display mode changed to {mode}'})

@app.route('/api/send_note', methods=['POST'])
def send_note():
    """Send a note to the display"""
    note = request.json.get('note', '')
    # TODO: Send OSC note to display
    return jsonify({'status': 'success', 'message': 'Note sent to display'})

@app.route('/api/clear_notes', methods=['POST'])
def clear_notes():
    """Clear all notes"""
    # TODO: Send OSC command to clear notes
    return jsonify({'status': 'success', 'message': 'Notes cleared'})

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
