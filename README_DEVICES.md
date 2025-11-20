# Xin-Yi Hardware Devices

This directory contains firmware and configuration for ESP32-based IoT devices that integrate with the Xin-Yi logistics system.

## Quick Start

**For SenseCAP Watcher setup, run:**
```bash
./sensecap_quickstart.sh
```

This interactive script will guide you through:
1. Backing up factory data (required before first flash)
2. Building XiaoZhi firmware
3. Flashing to your SenseCAP Watcher
4. Monitoring serial output

## Directory Structure

```
Xin-Yi/
├── heysalad_xiao_og/          # XIAO ESP32S3 Sense camera firmware (Arduino/PlatformIO)
├── devices/
│   └── xiaozhi-esp32/         # XiaoZhi AI chatbot firmware (ESP-IDF)
│       └── main/boards/
│           ├── sensecap-watcher/    # SenseCAP Watcher configuration
│           ├── esp-box-3/           # ESP32-S3-BOX-3 configuration
│           ├── m5stack-core-s3/     # M5Stack CoreS3 configuration
│           └── ... (70+ board configs)
├── backend/                   # Flask API server
├── frontend-next/             # Next.js dashboard
└── docs/
    ├── SENSECAP_SETUP.md      # Detailed setup instructions
    ├── HARDWARE_ANALYSIS.md   # Hardware comparison & integration analysis
    └── README_DEVICES.md      # This file
```

## Available Devices

### 1. SenseCAP Watcher
- **MCU:** ESP32-S3 @ 240MHz, 32MB flash
- **Display:** 412x412 QSPI touchscreen
- **Audio:** Dual codec (I2S), built-in speaker & mic
- **AI:** Himax vision processor
- **Features:** Voice wake-up, camera, battery-powered
- **Use Case:** Warehouse voice terminal, delivery confirmations

### 2. XIAO ESP32S3 Sense (HeySalad)
- **MCU:** ESP32-S3, 8-16MB flash
- **Display:** 240x240 round GC9A01
- **Camera:** OV2640 (240x240 JPEG)
- **Audio:** PDM microphone only
- **Features:** Web dashboard, BLE, camera streaming
- **Use Case:** Mobile scanner, document capture, barcode reading

## Installation Prerequisites

### macOS Setup

1. **Install Homebrew** (if not already installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Python 3.9+**:
```bash
brew install python@3.11
```

3. **Install ESP-IDF dependencies**:
```bash
brew install cmake ninja dfu-util
```

4. **Install ESP-IDF v5.4** (for SenseCAP Watcher):
```bash
mkdir -p ~/esp
cd ~/esp
git clone -b v5.4 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32s3
```

5. **Set up environment**:
```bash
echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.zshrc
source ~/.zshrc
```

### PlatformIO Setup (for XIAO ESP32S3)

1. **Install PlatformIO Core**:
```bash
brew install platformio
```

Or install the VSCode/Cursor extension: "PlatformIO IDE"

2. **Test installation**:
```bash
cd heysalad_xiao_og
pio run
```

## Building Firmware

### SenseCAP Watcher (XiaoZhi Firmware)

**Quick method:**
```bash
./sensecap_quickstart.sh
```

**Manual method:**
```bash
# Activate ESP-IDF
get_idf

# Navigate to firmware directory
cd devices/xiaozhi-esp32

# Build for SenseCAP Watcher
python scripts/release.py sensecap-watcher

# Flash (replace PORT with your device)
idf.py -p /dev/cu.usbmodem14101 -DBOARD_NAME=sensecap-watcher flash

# Monitor output
idf.py -p /dev/cu.usbmodem14101 monitor
```

### XIAO ESP32S3 (HeySalad Firmware)

```bash
cd heysalad_xiao_og

# Build
pio run

# Upload
pio run -t upload

# Monitor serial
pio device monitor -b 115200
```

## Flashing Instructions

### First-Time Flash (SenseCAP Watcher)

**IMPORTANT:** Backup factory data first!

```bash
# Find your USB port
ls /dev/cu.usbmodem*

# Backup factory partition (REQUIRED!)
esptool.py --port /dev/cu.usbmodem14101 \
  --chip esp32s3 --baud 2000000 \
  --before default_reset --after hard_reset --no-stub \
  read_flash 0x9000 204800 \
  ~/sensecap_factory_backup_$(date +%Y%m%d).bin

# Then flash firmware
./sensecap_quickstart.sh
```

### Subsequent Flashes

```bash
# App flash only (keeps settings)
get_idf
cd devices/xiaozhi-esp32
idf.py -p /dev/cu.usbmodem14101 -DBOARD_NAME=sensecap-watcher app-flash
```

## Device Configuration

### SenseCAP Watcher Initial Setup

After flashing, the device will:

1. **Display setup screen** on 412x412 LCD
2. **Create WiFi AP** if no network configured
   - SSID shown on screen
   - Default password: (check display)
3. **Web portal** at http://192.168.4.1
4. **Configure:**
   - WiFi credentials
   - Server URL (default: xiaozhi.me)
   - Language (Chinese/English/Japanese)
   - Wake word settings

### XIAO ESP32S3 Setup

1. **Connect to WiFi AP:**
   - SSID: `HeySalad-Camera`
   - Password: (set in Config.h)
2. **Access web UI:** http://192.168.4.1
3. **Configure WiFi** and backend URL
4. **View camera stream** at http://[device-ip]/

## Integration with Xin-Yi Backend

The Flask backend needs additional routes to communicate with devices.

### Adding Device Routes

Create `backend/routes/device_routes.py`:

```python
from flask import Blueprint, request, jsonify, Response
import json

device_bp = Blueprint('devices', __name__, url_prefix='/api/devices')

@device_bp.route('/register', methods=['POST'])
def register_device():
    """Register new IoT device"""
    data = request.json
    device_id = data.get('device_id')
    device_type = data.get('type')  # 'watcher' or 'xiao'

    # Store in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO devices (device_id, type, registered_at)
        VALUES (?, ?, datetime('now'))
    ''', (device_id, device_type))
    conn.commit()

    return jsonify({"status": "registered", "device_id": device_id})

@device_bp.route('/<device_id>/command', methods=['POST'])
def send_command(device_id):
    """Send command to device"""
    data = request.json
    command = data.get('command')

    # Queue command for device
    # (implement using MQTT or WebSocket)

    return jsonify({"status": "queued", "command": command})

@device_bp.route('/<device_id>/status', methods=['GET'])
def get_status(device_id):
    """Get device status"""
    # Query device status from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,))
    device = cursor.fetchone()

    if not device:
        return jsonify({"error": "Device not found"}), 404

    return jsonify(dict(device))

@device_bp.route('/<device_id>/camera', methods=['GET'])
def camera_stream(device_id):
    """Proxy camera stream from XIAO device"""
    # Forward stream from device
    # (implement WebSocket or MJPEG proxy)
    pass
```

Register in `backend/app.py`:
```python
from routes.device_routes import device_bp
app.register_blueprint(device_bp)
```

### Database Schema

Add devices table to `backend/database.py`:

```python
def init_database():
    # ... existing code ...

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,  -- 'watcher' or 'xiao'
            name TEXT,
            location TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP,
            status TEXT DEFAULT 'offline',
            firmware_version TEXT,
            ip_address TEXT,
            metadata TEXT  -- JSON for device-specific data
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            command TEXT NOT NULL,
            payload TEXT,  -- JSON
            status TEXT DEFAULT 'pending',  -- pending/sent/completed/failed
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices(device_id)
        )
    ''')

    conn.commit()
```

## Use Cases

### Warehouse Voice Terminal (SenseCAP Watcher)

**Features:**
- Voice commands: "Show today's deliveries"
- Touchscreen interface for inventory
- Camera for barcode scanning
- Speaker for confirmation alerts

**Integration:**
```
User says: "Check stock for item A123"
  ↓
SenseCAP Watcher (voice to text)
  ↓
POST /api/devices/{id}/voice-command
  ↓
Flask backend queries inventory
  ↓
Response via WebSocket
  ↓
SenseCAP displays result + speaks answer
```

### Mobile Scanner (XIAO ESP32S3)

**Features:**
- Capture delivery receipts
- Scan barcodes/QR codes
- Take photos of damaged goods
- GPS location tagging

**Integration:**
```
Worker scans barcode
  ↓
XIAO camera captures image
  ↓
POST /api/documents/scan
  ↓
Flask backend processes OCR
  ↓
Update inventory/delivery status
  ↓
Confirmation on XIAO display
```

## Troubleshooting

### ESP-IDF Issues

**Error: "idf.py not found"**
```bash
get_idf  # Activate environment
```

**Error: "Permission denied on /dev/cu.usbmodem*"**
```bash
sudo dseditgroup -o edit -a $USER -t user dialout
# Then log out and log back in
```

**Error: "Flash size mismatch"**
- Ensure sdkconfig has: `CONFIG_ESPTOOLPY_FLASHSIZE_32MB=y`
- Run: `idf.py fullclean` then rebuild

### PlatformIO Issues

**Error: "Library not found"**
```bash
pio pkg install
pio lib install
```

**Error: "Upload failed"**
- Check USB cable (must be data cable, not charge-only)
- Try different USB port
- Reset device while uploading

### Device Issues

**SenseCAP Watcher not booting:**
1. Check battery charge
2. Hold BOOT button + press RESET
3. Reflash bootloader: `idf.py bootloader-flash`

**XIAO camera not streaming:**
1. Check camera ribbon cable connection
2. Verify PSRAM enabled in platformio.ini
3. Monitor serial for error messages

**No WiFi connection:**
1. Check credentials in Config.h or via web portal
2. Verify 2.4GHz WiFi (ESP32 doesn't support 5GHz)
3. Check router MAC filtering

## Next Steps

1. **Flash your SenseCAP Watcher:**
   ```bash
   ./sensecap_quickstart.sh
   ```

2. **Test voice wake-up:**
   - Say "Ni Hao Xiao Zhi"
   - Check display for response

3. **Configure for Xin-Yi backend:**
   - Update server URL in device settings
   - Add device routes to Flask backend
   - Test basic communication

4. **Develop custom features:**
   - Voice commands for inventory queries
   - Camera integration for scanning
   - Real-time delivery updates

## Resources

- **XiaoZhi Docs:** devices/xiaozhi-esp32/docs/
- **ESP-IDF Guide:** https://docs.espressif.com/projects/esp-idf/en/v5.4/
- **PlatformIO Docs:** https://docs.platformio.org/
- **SenseCAP Hardware:** https://www.seeedstudio.com/SenseCAP-Watcher-W1-A-p-5979.html

## Support

For issues or questions:
1. Check SENSECAP_SETUP.md for detailed instructions
2. Review HARDWARE_ANALYSIS.md for integration strategies
3. Monitor serial output for error messages
4. Check XiaoZhi community: QQ group 1011329060
