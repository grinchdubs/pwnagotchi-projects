"""
TouchDesigner Network Builder for Generative Art Frame MQTT Upload
Creates all necessary operators and wires them together for sending images to e-ink display

Usage in TouchDesigner textport:
exec(open(r'build_mqtt_network.py').read())
"""

def build_mqtt_upload_network(
    parent_comp=None,
    source_top_name='render1',
    mqtt_broker='mqtt.local',
    mqtt_port=1883,
    mqtt_topic='art/frame/image',
    upload_interval=5.0,
    image_format='JPEG',
    image_quality=85
):
    """
    Build a complete network for uploading rendered images to MQTT broker

    Args:
        parent_comp: Parent component (default: /project1)
        source_top_name: Name of TOP to capture (must exist)
        mqtt_broker: MQTT broker address
        mqtt_port: MQTT broker port
        mqtt_topic: MQTT topic to publish to
        upload_interval: Seconds between uploads
        image_format: 'JPEG' or 'PNG'
        image_quality: JPEG quality (1-100, ignored for PNG)

    Returns:
        dict with created operators
    """
    if parent_comp is None:
        parent_comp = op('/project1')

    print(f"Building MQTT upload network in {parent_comp.path}")

    # Verify source TOP exists
    source_top = parent_comp.op(source_top_name)
    if source_top is None:
        print(f"ERROR: Source TOP '{source_top_name}' not found in {parent_comp.path}")
        print(f"Available TOPs: {[o.name for o in parent_comp.ops('*') if o.isTOP]}")
        return None

    # Create Timer CHOP for triggering uploads
    timer_chop = parent_comp.create(timerCHOP, 'mqtt_upload_timer')
    timer_chop.par.initialize = 1
    timer_chop.par.start.pulse()
    timer_chop.par.length = upload_interval
    timer_chop.par.cyclelimit = 0  # Infinite cycles

    # Position
    timer_chop.nodeX = 0
    timer_chop.nodeY = 0

    print(f"Created Timer CHOP: {timer_chop.path}")

    # Create Execute DAT for the upload logic
    execute_dat = parent_comp.create(executeDAT, 'mqtt_upload_execute')
    execute_dat.par.chopexec0 = timer_chop.path
    execute_dat.par.chopexeccook0 = True  # Execute on cook

    # Position
    execute_dat.nodeX = 0
    execute_dat.nodeY = -150

    # IMPORTANT: The upload code will be added to this Execute DAT
    # You'll need to customize the MQTT publishing method based on your setup
    upload_code = f'''"""
Execute DAT for MQTT Image Upload
Triggered by {timer_chop.name}
"""

import base64
import io

def onValueChange(channel, sampleIndex, val, prev):
    """Called when timer completes a cycle"""
    if channel.name == 'done' and val == 1:
        upload_frame()

def upload_frame():
    """Capture frame and upload to MQTT"""
    try:
        # Get the source TOP
        source = op('{source_top_name}')
        if source is None:
            print(f"ERROR: Source TOP '{source_top_name}' not found")
            return

        # METHOD 1: Using numpyArray (most reliable)
        # This method works without external dependencies
        import numpy as np
        from PIL import Image

        # Get pixel data as numpy array
        img_array = source.numpyArray(delayed=False)
        # Returns shape (height, width, channels) as float32 (0.0-1.0)

        # Convert to uint8 and flip (TD is bottom-left origin)
        img_array = np.flipud(img_array)

        # Handle different channel counts
        if img_array.shape[2] == 4:
            # RGBA - convert to RGB
            img_array = img_array[:, :, :3]

        img_array = (img_array * 255).astype(np.uint8)

        # Convert to PIL Image
        img = Image.fromarray(img_array, mode='RGB')

        # Encode to JPEG/PNG
        buffer = io.BytesIO()
        img.save(buffer, format='{image_format}', quality={image_quality})
        img_bytes = buffer.getvalue()

        # Base64 encode
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        print(f"Captured frame: {{len(img_bytes)}} bytes, base64: {{len(img_base64)}} chars")

        # TODO: Publish to MQTT
        # You need to implement MQTT publishing here
        # Option A: Use MQTT DAT operator (create and reference it)
        # Option B: Use paho-mqtt library (install via tdPyEnvManager)

        # Example with paho-mqtt (requires installation):
        # import paho.mqtt.client as mqtt
        # client = mqtt.Client()
        # client.connect('{mqtt_broker}', {mqtt_port})
        # client.publish('{mqtt_topic}', img_base64)
        # client.disconnect()

        print(f"Frame ready for upload to {mqtt_topic}")

    except Exception as e:
        print(f"ERROR in upload_frame: {{e}}")
        import traceback
        traceback.print_exc()

def onCook(scriptOp):
    """Called every frame - not used for timer-based upload"""
    pass
'''

    execute_dat.text = upload_code
    print(f"Created Execute DAT: {execute_dat.path}")

    # Create info text DAT with setup instructions
    info_dat = parent_comp.create(textDAT, 'mqtt_setup_info')
    info_dat.nodeX = 300
    info_dat.nodeY = 0

    info_text = f'''MQTT Upload Network Setup Instructions

Created operators:
- {timer_chop.name}: Timer triggering uploads every {upload_interval} seconds
- {execute_dat.name}: Python code for capturing and encoding frames

Configuration:
- Source TOP: {source_top_name}
- MQTT Broker: {mqtt_broker}:{mqtt_port}
- MQTT Topic: {mqtt_topic}
- Image Format: {image_format} (Quality: {image_quality})

NEXT STEPS:

1. Install paho-mqtt library:
   - Open Palette (Alt+L)
   - Search for "tdPyEnvManager"
   - Drag to network
   - Use it to install "paho-mqtt"

2. Edit {execute_dat.name} to uncomment MQTT publishing code
   - Find the "TODO: Publish to MQTT" section
   - Uncomment the paho-mqtt code
   - Or implement using MQTT DAT operator

3. Start the upload timer:
   {timer_chop.name}.par.start.pulse()

4. Monitor textport for upload status

Troubleshooting:
- Check that '{source_top_name}' exists and is rendering
- Verify MQTT broker is accessible at {mqtt_broker}
- Check textport for error messages
- Test with mosquitto_sub: mosquitto_sub -h {mqtt_broker} -t {mqtt_topic}
'''

    info_dat.text = info_text
    print(f"Created Info DAT: {info_dat.path}")

    # Return created operators
    result = {{
        'timer': timer_chop,
        'execute': execute_dat,
        'info': info_dat,
        'source': source_top
    }}

    print("\\n" + "="*60)
    print("MQTT Upload Network Created Successfully!")
    print("="*60)
    print(f"Read {info_dat.name} for setup instructions")
    print(f"Start uploads with: op('{timer_chop.name}').par.start.pulse()")
    print("="*60 + "\\n")

    return result


# Execute if run directly
if __name__ == '__main__':
    # Default configuration - customize as needed
    result = build_mqtt_upload_network(
        parent_comp=op('/project1'),
        source_top_name='render1',  # CHANGE THIS to your render TOP name
        mqtt_broker='raspberrypi.local',  # CHANGE THIS to your Pi's address
        mqtt_port=1883,
        mqtt_topic='art/frame/image',
        upload_interval=5.0,  # Upload every 5 seconds
        image_format='JPEG',
        image_quality=85
    )

    if result:
        print("Network built successfully!")
        print(f"Available operators: {list(result.keys())}")
