# SenseCAP Watcher Development Setup

## Current System Analysis

**Backend:** Flask (Python) + SQLite
**Frontend:** Next.js (TypeScript)
**Hardware Target:** SenseCAP Watcher (ESP32-S3)

## Step 1: Install ESP-IDF 5.4

The SenseCAP Watcher requires ESP-IDF 5.4 or newer. Here's how to install it on macOS:

### Option A: Quick Install (Recommended)

```bash
# Create esp directory in your home folder
mkdir -p ~/esp
cd ~/esp

# Clone ESP-IDF v5.4
git clone -b v5.4 --recursive https://github.com/espressif/esp-idf.git

# Run the installer
cd esp-idf
./install.sh esp32s3

# Add to your shell profile (choose one based on your shell)
# For zsh (default on macOS):
echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.zshrc

# For bash:
echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.bashrc
```

After installation, **restart your terminal** or run:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Option B: Using Espressif IDE (VSCode Extension)

1. Install VSCode extension: "ESP-IDF"
2. Follow the extension's setup wizard
3. Select ESP-IDF v5.4 or newer

## Step 2: Activate ESP-IDF Environment

Every time you want to build firmware, activate the environment:

```bash
get_idf
```

You should see output like:
```
Done! You can now compile ESP-IDF projects.
Go to the project directory and run:
  idf.py build
```

## Step 3: Backup SenseCAP Watcher Factory Data (CRITICAL!)

Before flashing any custom firmware, **you MUST backup** the factory partition. This contains credentials needed to restore the device to SenseCraft firmware.

```bash
# Connect your SenseCAP Watcher via USB-C
# Find the serial port (usually /dev/cu.usbmodem* on macOS)
ls /dev/cu.*

# Backup factory partition (replace PORT with your actual port)
esptool.py --port /dev/cu.usbmodem14101 \
  --chip esp32s3 \
  --baud 2000000 \
  --before default_reset \
  --after hard_reset \
  --no-stub \
  read_flash 0x9000 204800 \
  ~/sensecap_watcher_factory_backup_$(date +%Y%m%d).bin

# Verify the backup was created
ls -lh ~/sensecap_watcher_factory_backup_*.bin
```

Save this file somewhere safe! If you lose it, you cannot restore the device to factory SenseCraft firmware.

## Step 4: Build XiaoZhi Firmware for SenseCAP Watcher

```bash
cd /Users/chilumbam/Xin-Yi/devices/xiaozhi-esp32

# Activate ESP-IDF if not already active
get_idf

# Use the automated build script
python scripts/release.py sensecap-watcher
```

This will:
- Configure the build for ESP32-S3
- Set the board type to SenseCAP Watcher
- Apply the custom 32MB partition table
- Compile the firmware
- Generate a flashable binary

Expected output location:
```
build/xiaozhi-sensecap-watcher.bin
```

### Manual Build (Alternative)

If the automated script fails:

```bash
cd /Users/chilumbam/Xin-Yi/devices/xiaozhi-esp32

# Set target
idf.py set-target esp32s3

# Configure
idf.py menuconfig
# Navigate to: Xiaozhi Assistant -> Board Type -> SenseCAP Watcher
# Press 'S' to save, then 'Q' to quit

# Build
idf.py -DBOARD_NAME=sensecap-watcher build
```

## Step 5: Flash Firmware to SenseCAP Watcher

### First-Time Flash (Erase Everything)

```bash
# Find your port
ls /dev/cu.usbmodem*

# Flash with erase
idf.py -p /dev/cu.usbmodem14101 -DBOARD_NAME=sensecap-watcher flash
```

### Subsequent Flashes (Keep Settings)

```bash
idf.py -p /dev/cu.usbmodem14101 -DBOARD_NAME=sensecap-watcher app-flash
```

## Step 6: Monitor Serial Output

```bash
idf.py -p /dev/cu.usbmodem14101 monitor
```

Press `Ctrl+]` to exit the monitor.

Or combine flash + monitor:
```bash
idf.py -p /dev/cu.usbmodem14101 -DBOARD_NAME=sensecap-watcher flash monitor
```

## Step 7: Initial Configuration

After flashing, the device will:

1. **Start in AP mode** (if no WiFi configured)
   - SSID: Will be displayed on the 412x412 screen
   - Connect from your phone/computer
   - Navigate to captive portal

2. **Configure WiFi**
   - Select your network
   - Enter password

3. **Register device** (optional)
   - By default, connects to xiaozhi.me server
   - You can configure custom server later

4. **Test voice wake-up**
   - Say "Ni Hao Xiao Zhi" (你好小智) in Chinese
   - Or configure custom wake word

## Step 8: Connect to Xin-Yi Flask Backend

To integrate with your Flask backend instead of the default xiaozhi.me server:

### Option A: Modify Firmware Configuration

Edit `devices/xiaozhi-esp32/main/Kconfig.projbuild`:

```kconfig
config XIAOZHI_SERVER_URL
    string "XiaoZhi Server URL"
    default "https://your-xin-yi-server.com"
    help
        The URL of your custom XiaoZhi server
```

Then rebuild firmware.

### Option B: Runtime Configuration via Web UI

1. Connect to device's web interface (IP shown on screen)
2. Navigate to Settings
3. Change server URL to your Flask backend
4. Restart device

### Backend Integration Required

Your Flask backend will need new routes to handle XiaoZhi protocol:

```python
# backend/routes/xiaozhi_routes.py

from flask import Blueprint, request, jsonify
import json

xiaozhi_bp = Blueprint('xiaozhi', __name__, url_prefix='/api/xiaozhi')

@xiaozhi_bp.route('/register', methods=['POST'])
def register_device():
    """Register a new XiaoZhi device"""
    data = request.json
    device_id = data.get('device_id')
    # Store device info in database
    return jsonify({"status": "ok", "device_id": device_id})

@xiaozhi_bp.route('/ws', methods=['GET'])
def websocket_handler():
    """WebSocket endpoint for real-time communication"""
    # Implement WebSocket handling
    pass

@xiaozhi_bp.route('/command', methods=['POST'])
def handle_command():
    """Handle voice commands from device"""
    data = request.json
    command = data.get('command')
    # Process command and return response
    return jsonify({"response": "Command processed"})
```

Register in `backend/app.py`:
```python
from routes.xiaozhi_routes import xiaozhi_bp
app.register_blueprint(xiaozhi_bp)
```

## Troubleshooting

### Issue: "Permission denied" on /dev/cu.usbmodem*

```bash
# Add your user to dialout group (may need to log out/in)
sudo dseditgroup -o edit -a $USER -t user dialout
```

### Issue: "Flash size mismatch"

The SenseCAP Watcher has 32MB flash. Ensure `sdkconfig` has:
```
CONFIG_ESPTOOLPY_FLASHSIZE_32MB=y
```

### Issue: Device stuck in boot loop

1. Hold BOOT button while connecting USB
2. Flash bootloader separately:
```bash
idf.py -p PORT bootloader-flash
```

### Issue: No voice wake-up

1. Check microphone in `idf.py menuconfig`:
   - Xiaozhi Assistant -> Audio Config
2. Volume may be too low - adjust in settings
3. Try Chinese pronunciation: "nee how shao jer"

### Issue: Display not working

1. Verify QSPI configuration in menuconfig
2. Check power rail settings (IO expander)
3. Test with simple display example first

## Next Steps

After successful flash:

1. **Test basic functionality:**
   - Voice wake-up
   - Display rendering
   - Touch input
   - Audio playback

2. **Configure custom features:**
   - Custom wake words
   - Custom fonts/emojis
   - Adjust audio levels

3. **Integrate with Xin-Yi:**
   - Add Flask routes for device communication
   - Implement voice commands for inventory/deliveries
   - Add camera integration for document scanning

4. **Develop custom applications:**
   - Warehouse terminal UI
   - Delivery confirmation workflow
   - Inventory voice queries

## Resources

- **XiaoZhi Documentation:** devices/xiaozhi-esp32/docs/
- **ESP-IDF Programming Guide:** https://docs.espressif.com/projects/esp-idf/en/v5.4/
- **SenseCAP Watcher Specs:** https://www.seeedstudio.com/SenseCAP-Watcher-W1-A-p-5979.html
- **XiaoZhi Tutorial Videos:** https://www.bilibili.com/video/BV1bpjgzKEhd/

## Important Notes

- Always activate ESP-IDF environment with `get_idf` before building
- Keep your factory backup safe - store multiple copies
- The 412x412 touchscreen uses QSPI, not standard SPI
- Audio codec requires proper I2S initialization sequence
- Power management via IO expander is critical for battery life
- Default language is Chinese - change in menuconfig for English/Japanese
