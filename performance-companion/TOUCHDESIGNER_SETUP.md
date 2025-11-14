# TouchDesigner Setup for Performance Companion

This guide helps you set up TouchDesigner to send performance data to your e-ink display via OSC.

## Quick Start

### 1. Run the Network Builder Script

In TouchDesigner textport:
```python
exec(open(r'build_osc_network.py').read())
```

This creates:
- Timer CHOP for periodic updates
- Constant CHOPs for FPS and custom parameters
- Merge CHOP combining all data
- OSC Out CHOP for sending data
- Execute DAT for Python OSC (alternative method)
- Info DAT with setup instructions

### 2. Customize Configuration

Edit the script before running:

```python
result = build_osc_output_network(
    parent_comp=op('/project1'),
    pi_ip='192.168.1.100',  # Your Pi Zero W IP
    pi_port=9001,  # OSC port
    update_rate=2.0  # Seconds between updates
)
```

### 3. Start Sending Data

Method 1 (OSC Out CHOP - Automatic):
- Network starts automatically when created
- Data is sent continuously

Method 2 (Python OSC - Manual):
```python
# Start the timer
op('osc_update_timer').par.start.pulse()
```

## How It Works

### Data Collection Process

1. **FPS Tracking**: Constant CHOP reads `me.time.rate`
2. **Custom Parameters**: Constant CHOP holds user parameters
3. **Merge**: All CHOPs combined into single stream
4. **OSC Out CHOP**: Automatically sends all channels as OSC messages
5. **Timer**: Triggers Python alternative at regular intervals

### Network Structure

```
[FPS Constant] ─┐
                ├→ [Merge CHOP] → [OSC Out CHOP] → Pi Zero W
[Params Const] ─┘
                         ↓
                  [Timer] → [Execute DAT] (Alternative Python method)
```

### OSC Address Mapping

Channels are automatically mapped to OSC addresses:

| Channel | OSC Address | Value Type |
|---------|-------------|------------|
| `fps` | `/td/fps` | float (current FPS) |
| `blur` | `/td/param/blur` | float (0.0-1.0) |
| `feedback` | `/td/param/feedback` | float (0.0-1.0) |
| Scene name | `/td/scene` | string (composition name) |

## Adding Custom Parameters

### Method 1: Edit Constant CHOP

```python
params = op('td_params')
params.par.name2 = 'brightness'
params.par.value2 = 1.0
params.par.name3 = 'speed'
params.par.value3 = 0.5
```

### Method 2: Link to UI Controls

```python
# Link to slider
params.par.value0.expr = "op('slider1')['chan1']"

# Link to noise TOP parameter
params.par.value1.expr = "op('noise1').par.amp"

# Link to audio analysis
params.par.value2.expr = "op('audioanalysis1')['bass']"
```

### Method 3: Add More Constant CHOPs

```python
# Create new constant for more parameters
extra_params = parent().create(constantCHOP, 'extra_params')
extra_params.par.name0 = 'rotation'
extra_params.par.value0 = 0

# Add to merge
merge = op('osc_data_merge')
merge.par.chop2 = extra_params.path
```

## Two Methods for Sending OSC

### Method 1: OSC Out CHOP (Recommended)

**Pros**:
- No code required
- Automatic and continuous
- Built-in to TouchDesigner
- Low overhead

**Cons**:
- Less flexible for complex logic
- Harder to debug

**Usage**:
Already configured and running when network is created. Monitor with:
```python
op('osc_out').par.messages
```

### Method 2: Python OSC

**Pros**:
- Full control over message formatting
- Easy to add conditional logic
- Better debugging (print statements)
- Can send to multiple destinations

**Cons**:
- Requires python-osc installation
- More code to maintain

**Setup**:
1. Install python-osc via tdPyEnvManager
2. Edit `osc_send_execute` DAT
3. Uncomment the OSC client code
4. Start timer

## Configuration Options

### Update Rate

Balance between:
- **Fast (1-2 sec)**: Responsive, but e-ink can't keep up
- **Medium (2-5 sec)**: Good balance (recommended)
- **Slow (5-10 sec)**: Minimal network traffic

E-ink displays refresh slowly, so 2-3 seconds is optimal.

### Network Performance

For low latency:
1. Use wired Ethernet (USB adapter for Pi Zero W)
2. Dedicated network for performance gear
3. Static IPs (avoid DNS lookups)
4. Reduce update rate during critical moments

## Monitoring OSC Output

### In TouchDesigner

Check OSC Out CHOP info:
```python
osc = op('osc_out')
print(osc.par.messages)  # Recent messages sent
```

### On Pi Zero W

Monitor incoming OSC:
```python
from pythonosc import dispatcher, osc_server

def print_handler(addr, *args):
    print(f'{addr}: {args}')

d = dispatcher.Dispatcher()
d.set_default_handler(print_handler)
server = osc_server.ThreadingOSCUDPServer(('0.0.0.0', 9001), d)
print("Listening for OSC on port 9001...")
server.serve_forever()
```

## Live Performance Setup

### Pre-Show Checklist

1. **Test Network Connection**:
   ```bash
   ping 192.168.1.100  # Ping Pi Zero W
   ```

2. **Verify OSC is sending**:
   ```python
   op('osc_out').par.messages  # Check in TD
   ```

3. **Start Display Script on Pi**:
   ```bash
   systemctl start performance-companion
   ```

4. **Test Display Modes**:
   Send mode change: `/companion/mode 0` (via OSC)

5. **Load Set List** (if using):
   Edit `setlist.json` on Pi

### During Performance

**Display Controls**:
- Change mode: Send OSC `/companion/mode [0-4]`
- Add note: Send OSC `/companion/note "Check cables"`
- Clear notes: Send OSC `/companion/clear_notes`

**Monitor Performance**:
```python
# Check current FPS
fps = op('td_fps')['fps'].eval()
print(f"Current FPS: {fps}")

# Check OSC send rate
timer = op('osc_update_timer')
print(f"Update every {timer.par.length} seconds")
```

## Advanced: Ableton Live Integration

If you also have Ableton Live sending OSC, you can forward it to the Pi:

### Option 1: Merge in TouchDesigner

Create OSC In CHOP for Ableton data, merge with TD data:

```python
# Create OSC In CHOP for Ableton
ableton_in = parent().create(oscinCHOP, 'ableton_osc_in')
ableton_in.par.port = 9000  # Ableton sends here

# Add to merge
merge = op('osc_data_merge')
merge.par.chop3 = ableton_in.path
```

### Option 2: Python Bridge

Use Execute DAT to receive Ableton OSC and forward to Pi with TD data:

```python
# In Execute DAT
def onReceiveOSC(dat, address, *args):
    """Receive from Ableton, forward to Pi"""
    # Forward directly
    osc_client.send_message(address, args)
```

## Troubleshooting

### No Data on Pi Display

1. Check Pi is receiving OSC:
   - Run monitor script on Pi (see "Monitoring OSC Output")
   - Should see messages every 2 seconds

2. Check network:
   - `ping 192.168.1.100` from TD computer
   - Verify port 9001 is open: `sudo ufw allow 9001/udp`

3. Check OSC Out CHOP:
   - `op('osc_out').par.messages` should show recent sends
   - Verify IP and port are correct

### Display Shows Old Data

Display script might be stuck or crashed:
```bash
# On Pi
journalctl -u performance-companion -f  # Check logs
systemctl restart performance-companion  # Restart
```

### OSC Out CHOP Not Sending

Check:
1. Merge CHOP has data: `op('osc_data_merge').numChans > 0`
2. OSC Out CHOP is cooking: `op('osc_out').par.active == True`
3. Network address is valid: `op('osc_out').par.networkaddress`

### Performance Issues

If TouchDesigner is slowing down:
1. Increase update rate (less frequent sends)
2. Reduce number of OSC messages
3. Use OSC Out CHOP instead of Python method
4. Check for network congestion

## Example: Linking to Noise Parameters

```python
# Get the params constant
params = op('td_params')

# Link blur to noise amplitude
params.par.value0.expr = "op('noise1').par.amp"

# Link feedback to noise exponent
params.par.value1.expr = "op('noise1').par.exponent"

# Link to audio reactivity
audio = op('audioanalysis1')
params.par.value0.expr = "op('audioanalysis1')['bass'] * 0.5"
```

Now when you adjust noise or audio parameters, they automatically send to the display!

## Example: Beat-Synced Updates

Instead of timer-based updates, sync to beats:

```python
# Create Beat CHOP
beat = parent().create(beatCHOP, 'beat')
beat.par.bpm = 120

# Change execute DAT trigger
execute = op('osc_send_execute')
execute.par.chopexec0 = beat.path

# Now sends on every beat!
```

## References

- [TouchDesigner OSC Out CHOP](https://derivative.ca/UserGuide/OSC_Out_CHOP)
- [TouchDesigner OSC In CHOP](https://derivative.ca/UserGuide/OSC_In_CHOP)
- [python-osc Documentation](https://python-osc.readthedocs.io/)
- [Open Sound Control Specification](http://opensoundcontrol.org/spec-1_0)
