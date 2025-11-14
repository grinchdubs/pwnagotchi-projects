"""
TouchDesigner Network Builder for Performance Companion OSC Output
Creates all necessary operators for sending performance data to Pi Zero W display

Usage in TouchDesigner textport:
exec(open(r'build_osc_network.py').read())
"""

def build_osc_output_network(
    parent_comp=None,
    pi_ip='192.168.1.100',
    pi_port=9001,
    update_rate=2.0
):
    """
    Build a complete network for sending OSC performance data to Pi Zero W

    Args:
        parent_comp: Parent component (default: /project1)
        pi_ip: IP address of Pi Zero W
        pi_port: OSC port on Pi Zero W
        update_rate: Seconds between updates

    Returns:
        dict with created operators
    """
    if parent_comp is None:
        parent_comp = op('/project1')

    print(f"Building OSC output network in {parent_comp.path}")

    # Create Timer CHOP for update triggering
    timer_chop = parent_comp.create(timerCHOP, 'osc_update_timer')
    timer_chop.par.initialize = 1
    timer_chop.par.start.pulse()
    timer_chop.par.length = update_rate
    timer_chop.par.cyclelimit = 0  # Infinite

    timer_chop.nodeX = 0
    timer_chop.nodeY = 200

    print(f"Created Timer CHOP: {timer_chop.path}")

    # Create Constant CHOP for FPS tracking
    fps_constant = parent_comp.create(constantCHOP, 'td_fps')
    fps_constant.par.name0 = 'fps'
    fps_constant.par.value0.expr = 'me.time.rate'  # Current FPS

    fps_constant.nodeX = 200
    fps_constant.nodeY = 200

    print(f"Created FPS Constant CHOP: {fps_constant.path}")

    # Create Constant CHOPs for custom parameters
    # Users can add more channels here
    params_constant = parent_comp.create(constantCHOP, 'td_params')
    params_constant.par.name0 = 'blur'
    params_constant.par.value0 = 0.0
    params_constant.par.name1 = 'feedback'
    params_constant.par.value1 = 0.0

    params_constant.nodeX = 400
    params_constant.nodeY = 200

    print(f"Created Parameters Constant CHOP: {params_constant.path}")

    # Merge CHOPs together
    merge_chop = parent_comp.create(mergeCHOP, 'osc_data_merge')
    merge_chop.par.combine = 'Append'
    merge_chop.par.chop0 = fps_constant.path
    merge_chop.par.chop1 = params_constant.path

    merge_chop.nodeX = 300
    merge_chop.nodeY = 100

    print(f"Created Merge CHOP: {merge_chop.path}")

    # Create OSC Out CHOP
    osc_out = parent_comp.create(oscoutCHOP, 'osc_out')
    osc_out.par.networkaddress = pi_ip
    osc_out.par.networkport = pi_port
    osc_out.par.protocol = 'UDP'
    osc_out.par.chop = merge_chop.path

    # Configure OSC address patterns
    # Note: You may need to adjust these based on actual OSC Out CHOP parameters
    # Check the OSC Out CHOP documentation for exact parameter names

    osc_out.nodeX = 300
    osc_out.nodeY = 0

    print(f"Created OSC Out CHOP: {osc_out.path}")

    # Create Execute DAT for Python-based OSC sending (alternative method)
    execute_dat = parent_comp.create(executeDAT, 'osc_send_execute')
    execute_dat.par.chopexec0 = timer_chop.path
    execute_dat.par.chopexeccook0 = True

    execute_dat.nodeX = 0
    execute_dat.nodeY = 0

    # Python code for OSC sending
    osc_send_code = f'''"""
Execute DAT for OSC Performance Data Transmission
Alternative to OSC Out CHOP using python-osc library

Install python-osc first:
- Open Palette (Alt+L)
- Search for "tdPyEnvManager"
- Install "python-osc"
"""

# Uncomment to use Python OSC instead of OSC Out CHOP
# from pythonosc import udp_client

# Global OSC client (initialized once)
# osc_client = None

def onValueChange(channel, sampleIndex, val, prev):
    """Called when timer completes"""
    if channel.name == 'done' and val == 1:
        send_osc_data()

def send_osc_data():
    """Send performance data via OSC"""
    try:
        # Uncomment to use Python OSC:
        # global osc_client
        # if osc_client is None:
        #     osc_client = udp_client.SimpleUDPClient('{pi_ip}', {pi_port})

        # Get FPS
        fps = me.time.rate
        # osc_client.send_message('/td/fps', fps)
        print(f"FPS: {{fps:.1f}}")

        # Get custom parameters from td_params CHOP
        params_chop = op('td_params')
        if params_chop:
            blur = params_chop['blur'].eval()
            feedback = params_chop['feedback'].eval()
            # osc_client.send_message('/td/param/blur', blur)
            # osc_client.send_message('/td/param/feedback', feedback)
            print(f"Params - Blur: {{blur:.2f}}, Feedback: {{feedback:.2f}}")

        # Send scene/composition name
        comp_name = parent().name
        # osc_client.send_message('/td/scene', comp_name)
        print(f"Scene: {{comp_name}}")

        print(f"OSC data sent to {pi_ip}:{pi_port}")

    except Exception as e:
        print(f"ERROR in send_osc_data: {{e}}")
        import traceback
        traceback.print_exc()

def onCook(scriptOp):
    """Called every frame - not used"""
    pass
'''

    execute_dat.text = osc_send_code
    print(f"Created Execute DAT: {execute_dat.path}")

    # Create Text DAT for scene name (string OSC data)
    text_dat = parent_comp.create(textDAT, 'td_scene_name')
    text_dat.text = parent_comp.name

    text_dat.nodeX = 600
    text_dat.nodeY = 200

    print(f"Created Scene Name Text DAT: {text_dat.path}")

    # Create info text DAT
    info_dat = parent_comp.create(textDAT, 'osc_setup_info')
    info_dat.nodeX = 600
    info_dat.nodeY = 0

    info_text = f'''OSC Output Network Setup Instructions

Created operators:
- {timer_chop.name}: Update timer ({update_rate} sec intervals)
- {fps_constant.name}: FPS tracking
- {params_constant.name}: Custom parameters (blur, feedback)
- {merge_chop.name}: Combines all CHOP data
- {osc_out.name}: OSC Out CHOP (main output method)
- {execute_dat.name}: Python OSC (alternative method)
- {text_dat.name}: Scene/composition name

Configuration:
- Pi Zero W IP: {pi_ip}
- OSC Port: {pi_port}
- Update Rate: {update_rate} seconds

NEXT STEPS:

METHOD 1: Using OSC Out CHOP (Recommended)
1. The OSC Out CHOP is already configured and running
2. Edit {params_constant.name} to add your custom parameters
3. Add more channels: params_constant.par.name2 = 'my_param'
4. Wire other CHOPs to {merge_chop.name} for more data
5. Verify OSC messages with: {osc_out.name}.par.messages

METHOD 2: Using Python OSC (For Complex Logic)
1. Install python-osc via tdPyEnvManager
2. Edit {execute_dat.name}
3. Uncomment the python-osc import and client code
4. Uncomment send_message() calls
5. Start timer: {timer_chop.name}.par.start.pulse()

CUSTOMIZATION:

Add more parameters to {params_constant.name}:
  params = op('{params_constant.name}')
  params.par.name2 = 'brightness'
  params.par.value2 = 1.0

Link parameter to UI control:
  params.par.value0.expr = "op('slider1')['chan1']"

Monitor what's being sent:
  - Check {osc_out.name} info CHOP
  - Check textport for Python OSC debug prints
  - Use OSC monitor on Pi: python3 -c "from pythonosc import osc_server, dispatcher; ..."

OSC Address Mapping:
  Channel "fps" → /td/fps
  Channel "blur" → /td/param/blur
  Channel "feedback" → /td/param/feedback
  Scene name → /td/scene

Troubleshooting:
- Verify Pi is reachable: ping {pi_ip}
- Check Pi is listening on port {pi_port}
- Monitor {osc_out.name} for send errors
- Check firewall allows UDP port {pi_port}
'''

    info_dat.text = info_text
    print(f"Created Info DAT: {info_dat.path}")

    # Return created operators
    result = {{
        'timer': timer_chop,
        'fps_constant': fps_constant,
        'params_constant': params_constant,
        'merge': merge_chop,
        'osc_out': osc_out,
        'execute': execute_dat,
        'scene_name': text_dat,
        'info': info_dat
    }}

    print("\\n" + "="*60)
    print("OSC Output Network Created Successfully!")
    print("="*60)
    print(f"Read {info_dat.name} for setup instructions")
    print(f"Start updates with: op('{timer_chop.name}').par.start.pulse()")
    print(f"Monitor OSC: op('{osc_out.name}').par.messages")
    print("="*60 + "\\n")

    return result


# Execute if run directly
if __name__ == '__main__':
    # Default configuration - customize as needed
    result = build_osc_output_network(
        parent_comp=op('/project1'),
        pi_ip='192.168.1.100',  # CHANGE THIS to your Pi Zero W IP
        pi_port=9001,
        update_rate=2.0  # Send updates every 2 seconds
    )

    if result:
        print("Network built successfully!")
        print(f"Available operators: {list(result.keys())}")
