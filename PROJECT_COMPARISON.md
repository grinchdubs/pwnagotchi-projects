# Project Comparison

Quick comparison to help you decide which project to build first based on your needs and existing setup.

## At a Glance

| Feature | Generative Art Frame | APRS iGate Display | Performance Companion |
|---------|---------------------|-------------------|----------------------|
| **Difficulty** | ⭐⭐ Intermediate | ⭐⭐⭐ Advanced | ⭐⭐ Intermediate |
| **Setup Time** | 30 mins | 45 mins | 30 mins |
| **Dependencies** | MQTT Broker | Internet, Ham License | Ableton/TouchDesigner |
| **Best For** | Artists, Makers | Ham Radio Operators | Musicians, VJs |
| **Power Usage** | Very Low | Low | Low |
| **Portability** | High | High | Medium |

## Detailed Comparison

### Generative Art Frame

**Pros:**
- Simple MQTT-based architecture
- Works with TouchDesigner and Hydra (your existing tools!)
- Great for studio display
- Battery-powered operation
- Integrates with your pen plotter workflow
- Unique e-ink aesthetic

**Cons:**
- Requires MQTT broker setup
- Image conversion needed
- E-ink refresh rate limits animation

**Best If:**
- You're actively using TouchDesigner/Hydra
- You want a display for your studio at NYC Resistor
- You're working on pen plotter projects
- You appreciate the e-ink aesthetic

**Integration Effort:**
- TouchDesigner: Add MQTT Out CHOP (5 mins)
- Hydra: Write small Node.js bridge (15 mins)
- Python scripts: Direct integration (easy)

---

### APRS iGate Display

**Pros:**
- Contributes to APRS network infrastructure
- Real-time packet monitoring
- Weather data integration
- Station statistics
- Portable for field operations
- Multiple display modes

**Cons:**
- Requires amateur radio license
- Needs APRS-IS passcode
- More complex configuration
- Must be connected to internet

**Best If:**
- You have an amateur radio license
- You're active in APRS
- You want to contribute to ham radio infrastructure
- You attend field day events
- You like monitoring local RF activity

**License Requirement:**
⚠️ **Important**: You MUST have a valid amateur radio license to operate this as an iGate. It's required by law.

---

### Live Performance Companion

**Pros:**
- Direct integration with Ableton and TouchDesigner
- Real-time performance monitoring
- OSC-based (flexible)
- Multiple display modes
- Set list management
- Great for live shows

**Cons:**
- Requires Ableton or TouchDesigner
- OSC configuration needed
- Most useful during active performances

**Best If:**
- You perform live A/V sets
- You use Ableton Live regularly
- You do live coding performances
- You want at-a-glance performance data
- You're tired of checking screens during shows

**Integration Effort:**
- Ableton: Install OSC tools or use Connection Kit
- TouchDesigner: Native OSC support (very easy)
- Max for Live: Create monitoring device

---

## Decision Matrix

### Choose Generative Art Frame if:
- [x] You use TouchDesigner/Hydra regularly
- [x] You want a studio/workshop display
- [x] You have an MQTT broker (or willing to set one up)
- [x] You like the e-ink aesthetic
- [x] You work with generative art

### Choose APRS iGate Display if:
- [x] You have an amateur radio license
- [x] You're interested in APRS
- [x] You want to contribute to ham infrastructure
- [x] You attend ham radio events
- [x] You like monitoring radio activity

### Choose Performance Companion if:
- [x] You perform live A/V sets
- [x] You use Ableton Live or TouchDesigner for performances
- [x] You want glanceable performance data
- [x] You're comfortable with OSC
- [x] You want to reduce screen-checking during shows

## Recommended Build Order

### If you're primarily a creative technologist:
1. **Generative Art Frame** - Integrates with your existing TD workflow
2. **Performance Companion** - Enhances your live performances
3. **APRS iGate** - If you get into amateur radio

### If you're primarily a ham radio operator:
1. **APRS iGate Display** - Core use case
2. **Performance Companion** - If you do radio presentations
3. **Generative Art Frame** - Fun side project

### If you're primarily a performer:
1. **Performance Companion** - Immediate utility
2. **Generative Art Frame** - Studio monitoring
3. **APRS iGate** - If you pursue ham radio license

## Multi-Unit Setup

Got multiple Pwnagotchis? Here's how to use them together:

**Studio Setup:**
- Unit 1: Generative Art Frame (always on, art display)
- Unit 2: Performance Companion (near performance area)

**Performance Setup:**
- Unit 1: Performance Companion (Ableton monitoring)
- Unit 2: Performance Companion (TouchDesigner monitoring)

**Ham Shack Setup:**
- Unit 1: APRS iGate (main station)
- Unit 2: APRS iGate (field operations)

## Resource Requirements

### Generative Art Frame
- **Software**: MQTT broker (Mosquitto)
- **Network**: WiFi to MQTT broker
- **External Tools**: TouchDesigner/Hydra
- **Ongoing**: Update art via MQTT

### APRS iGate Display
- **Software**: None extra (uses aprslib)
- **Network**: Internet connection required
- **External Tools**: None
- **Ongoing**: Receives packets automatically

### Performance Companion
- **Software**: None extra (OSC is built-in)
- **Network**: WiFi to performance computer
- **External Tools**: Ableton Live or TouchDesigner
- **Ongoing**: Active during performances only

## First Project Recommendation

**For you specifically (based on your profile):**

Start with **Generative Art Frame** because:
1. You're already deep into TouchDesigner
2. You have MQTT experience from ESP32 projects
3. You work on generative art and pen plotting
4. It integrates with your existing Hydra work
5. Perfect display for NYC Resistor workspace

Then build **Performance Companion** for your live A/V shows with Ableton.

Consider **APRS iGate Display** if you decide to pursue your amateur radio license!

## Next Steps

1. Read the project README you've chosen
2. Follow the QUICKSTART.md guide
3. Join the community (if available)
4. Share your builds!

Happy building! 🛠️
