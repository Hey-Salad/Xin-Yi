# SenseCAP Watcher Xin-Yi Firmware

A custom firmware for the **SenseCAP Watcher** that integrates with the **Xin-Yi logistics system**. This firmware is inspired by the `heysalad_xiao_og` project but completely redesigned for the SenseCAP Watcher hardware and ESP-IDF framework.

## Features

### Core Capabilities
- **WiFi Connectivity** with AP fallback mode
- **HTTP/WebSocket Server** for camera streaming and control
- **412x412 Touchscreen UI** for warehouse operations
- **Camera Streaming** via Himax AI vision processor
- **Xin-Yi Backend Integration** via REST API and WebSocket
- **BLE UART** for mobile app control
- **SPIFFS Storage** for assets and configuration
- **OTA Updates** for remote firmware updates

### Xin-Yi System Integration
- Auto-registration with Xin-Yi Flask backend
- Real-time status updates and heartbeat
- Document capture and upload
- Barcode/QR code scanning for inventory
- Delivery confirmation workflow
- Voice commands (future integration with XiaoZhi)

## Hardware Requirements

- **SenseCAP Watcher** (W1-A or compatible)
  - ESP32-S3 @ 240MHz
  - 32MB flash
  - 412x412 QSPI touchscreen
  - Himax AI vision processor
  - Dual I2S audio codec
  - Battery powered

## Software Requirements

### Development Environment

**For Raspberry Pi (or Linux):**

```bash
# Install ESP-IDF 5.4
mkdir -p ~/esp
cd ~/esp
git clone -b v5.4 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32s3

# Set up environment
echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.bashrc
source ~/.bashrc
```

**For macOS:** See [SENSECAP_SETUP.md](../SENSECAP_SETUP.md)

## Quick Start

### 1. Backup Factory Data (CRITICAL!)

Before flashing custom firmware, **you MUST backup** the factory partition:

```bash
# Find your USB port
ls /dev/ttyUSB* # Linux
ls /dev/cu.usbmodem* # macOS

# Backup factory partition
esptool.py --port /dev/ttyUSB0 \
  --chip esp32s3 \
  --baud 2000000 \
  --before default_reset \
  --after hard_reset \
  --no-stub \
  read_flash 0x9000 204800 \
  ~/sensecap_factory_backup_$(date +%Y%m%d).bin

# Verify backup exists
ls -lh ~/sensecap_factory_backup_*.bin
```

**Store this file safely!** Without it, you cannot restore to factory firmware.

### 2. Configure for Your Network

Edit [main/include/config.h](main/include/config.h):

```c
// Change this to your Xin-Yi Flask backend IP address
#define XINYI_API_URL "http://192.168.1.100:5000"

// Optional: Set default WiFi credentials
#define WIFI_SSID_DEFAULT "YourWiFiSSID"
#define WIFI_PASSWORD_DEFAULT "YourWiFiPassword"

// Change default password!
#define DEFAULT_AUTH_PASSWORD "your-secure-password"
```

### 3. Build Firmware

```bash
# Navigate to project directory
cd /home/admin/Xin-Yi/sensecap_watcher_xinyi

# Activate ESP-IDF environment
get_idf

# Set target to ESP32-S3
idf.py set-target esp32s3

# Build firmware
idf.py build
```

### 4. Flash to Device

**First-time flash (erases everything):**

```bash
idf.py -p /dev/ttyUSB0 flash
```

**Subsequent flashes (keeps settings):**

```bash
idf.py -p /dev/ttyUSB0 app-flash
```

### 5. Monitor Serial Output

```bash
idf.py -p /dev/ttyUSB0 monitor

# Exit with Ctrl+]
```

**Or combine flash + monitor:**

```bash
idf.py -p /dev/ttyUSB0 flash monitor
```

## Initial Setup

After flashing, the device will:

1. **Generate unique Device ID** based on MAC address
2. **Start in AP mode** if no WiFi configured
   - SSID: `XinYi-Watcher`
   - Password: `xinyi2024` (change in config.h)
3. **Display setup screen** on 412x412 LCD
4. **Web interface** at `http://192.168.4.1`

### Configure via Web Interface

1. Connect to `XinYi-Watcher` WiFi network
2. Navigate to `http://192.168.4.1`
3. Enter your WiFi credentials
4. Configure Xin-Yi backend URL
5. Set device role:
   - **Warehouse Terminal** - Fixed terminal in warehouse
   - **Mobile Scanner** - Handheld scanner
   - **Delivery Confirm** - Delivery confirmation device
   - **Inventory Checker** - Inventory checking device

## Project Structure

```
sensecap_watcher_xinyi/
├── CMakeLists.txt                 # Main CMake project file
├── sdkconfig.defaults             # ESP-IDF configuration defaults
├── partitions.csv                 # Partition table (32MB flash)
├── README.md                      # This file
├── main/
│   ├── CMakeLists.txt
│   ├── main.c                     # Main application entry point
│   ├── config.c                   # Configuration management
│   ├── wifi_manager.c             # WiFi connection handler
│   ├── http_server.c              # HTTP/WebSocket server
│   ├── websocket_handler.c        # WebSocket frame streaming
│   ├── xinyi_client.c             # Xin-Yi backend client
│   └── include/
│       └── config.h               # Main configuration header
├── components/
│   ├── camera/                    # Himax camera abstraction
│   ├── display/                   # 412x412 LCD + touch driver
│   ├── network/                   # Networking utilities
│   └── xinyi_client/              # Xin-Yi API client library
├── scripts/
│   └── build_and_flash.sh         # Build automation script
├── data/
│   └── assets/                    # UI assets (logos, icons)
└── docs/
    ├── API.md                     # REST API documentation
    ├── INTEGRATION.md             # Xin-Yi integration guide
    └── HARDWARE.md                # Hardware pin mappings
```

## Architecture

### Similar to heysalad_xiao_og:
- HTTP server with WebSocket streaming
- BLE UART service for mobile control
- SPIFFS asset management
- JSON-based REST API
- Authentication system
- Status broadcasting

### Improvements for SenseCAP:
- **Native ESP-IDF** (no Arduino) for better performance
- **Larger display** (412x412 vs 240x240)
- **Touchscreen support** for interactive UI
- **Xin-Yi backend integration** instead of Laura cloud
- **Modular component architecture**
- **Device role system** for different use cases

## REST API Endpoints

### Device Management
- `GET /` - Web dashboard
- `GET /api/status` - Get device status (JSON)
- `POST /api/settings` - Update configuration
- `POST /api/restart` - Restart device

### Camera Operations
- `WS /ws` - WebSocket camera stream (JPEG frames)
- `POST /api/stream/start` - Start streaming
- `POST /api/stream/stop` - Stop streaming
- `POST /api/photo` - Capture high-quality photo

### Xin-Yi Integration
- `POST /api/register` - Register with Xin-Yi backend
- `POST /api/scan/barcode` - Process barcode scan
- `POST /api/document/capture` - Capture and upload document
- `GET /api/deliveries/today` - Get today's deliveries from backend

## Xin-Yi Backend Integration

### Backend Requirements

Your Flask backend needs the following routes (add to `backend/routes/device_routes.py`):

```python
from flask import Blueprint, request, jsonify

device_bp = Blueprint('devices', __name__, url_prefix='/api/devices')

@device_bp.route('/register', methods=['POST'])
def register_device():
    """Register SenseCAP Watcher"""
    data = request.json
    device_id = data.get('device_id')
    device_type = data.get('type')  # 'sensecap-watcher'
    firmware_version = data.get('firmware_version')

    # Store in database...
    return jsonify({"status": "registered", "device_id": device_id})

@device_bp.route('/<device_id>/status', methods=['POST'])
def update_status(device_id):
    """Receive status updates from device"""
    data = request.json
    # Update last_seen, battery level, etc.
    return jsonify({"status": "ok"})

@device_bp.route('/<device_id>/command', methods=['GET'])
def get_commands(device_id):
    """Device polls for pending commands"""
    # Return queued commands for this device
    return jsonify({"commands": []})
```

### WebSocket for Real-time Updates

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('device_connect')
def handle_device_connect(data):
    device_id = data.get('device_id')
    # Track connected devices
    emit('welcome', {'message': 'Connected to Xin-Yi backend'})

@socketio.on('camera_frame')
def handle_camera_frame(data):
    device_id = data.get('device_id')
    frame_data = data.get('frame')  # Base64 JPEG
    # Process or forward frame
```

## Customization

### Change UI Colors

Edit `main/include/config.h`:

```c
#define COLOR_PRIMARY 0xED4C     // Cherry Red (Laura style)
#define COLOR_SUCCESS 0x07E0     // Green
#define COLOR_ERROR 0xF800       // Red
```

### Add Custom Device Role

```c
typedef enum {
    ROLE_WAREHOUSE_TERMINAL,
    ROLE_MOBILE_SCANNER,
    ROLE_DELIVERY_CONFIRM,
    ROLE_INVENTORY_CHECKER,
    ROLE_YOUR_CUSTOM_ROLE   // Add your role
} device_role_t;
```

### Adjust Camera Settings

```c
#define CAMERA_FRAME_SIZE FRAMESIZE_VGA  // Or FRAMESIZE_HD, FRAMESIZE_FHD
#define CAMERA_JPEG_QUALITY 12            // 0-63, lower = better quality
#define STREAM_FRAME_INTERVAL_MS 100      // 10 FPS
```

## Troubleshooting

### Build Errors

**Error: "ESP-IDF not found"**
```bash
get_idf  # Activate environment
which idf.py  # Should show path
```

**Error: "Target mismatch"**
```bash
idf.py fullclean
idf.py set-target esp32s3
idf.py build
```

### Flash Errors

**Error: "Permission denied"**
```bash
# Linux
sudo usermod -a -G dialout $USER
# Then logout and login

# Or use sudo
sudo idf.py -p /dev/ttyUSB0 flash
```

**Error: "Flash size mismatch"**
- Ensure `sdkconfig` has: `CONFIG_ESPTOOLPY_FLASHSIZE_32MB=y`
- Run: `idf.py fullclean` then rebuild

### Runtime Issues

**Device stuck in boot loop**
1. Check serial output for crash logs
2. Reflash bootloader: `idf.py bootloader-flash`
3. Full erase and reflash: `idf.py erase-flash && idf.py flash`

**Display not working**
- Check pin definitions in `config.h`
- Verify QSPI initialization in `components/display/`
- Test with simple fill-screen example

**Camera not streaming**
- Check Himax processor initialization
- Verify SPI communication
- Test frame capture separately from streaming

**Cannot connect to WiFi**
- Verify 2.4GHz network (ESP32 doesn't support 5GHz)
- Check credentials in NVS or config
- Monitor serial for WiFi connection logs

**Backend not responding**
- Verify Flask backend is running
- Check IP address in `config.h`
- Test with `curl http://YOUR_IP:5000/api/status`
- Check firewall settings

## Next Steps

1. **Implement Camera Module** (`components/camera/`)
   - Initialize Himax SPI communication
   - Configure camera settings
   - Implement frame capture and JPEG encoding

2. **Implement Display Module** (`components/display/`)
   - Initialize 412x412 QSPI LCD
   - Create UI framework (buttons, labels, etc.)
   - Implement touchscreen handler

3. **Complete HTTP Server** (`main/http_server.c`)
   - Serve web dashboard from SPIFFS
   - Implement REST API endpoints
   - Add WebSocket binary streaming

4. **Build Xin-Yi Client** (`components/xinyi_client/`)
   - HTTP client for REST API calls
   - WebSocket client for real-time updates
   - Auto-registration logic

5. **Create Web Dashboard** (`data/web/`)
   - HTML/CSS/JS interface
   - Live camera view
   - Device configuration page
   - Status monitoring

6. **Add Barcode Scanner** (optional)
   - Integrate ZBar or similar library
   - Process camera frames for QR/barcode detection
   - Send results to Xin-Yi backend

## Comparison with heysalad_xiao_og

| Feature | heysalad_xiao_og | sensecap_watcher_xinyi |
|---------|------------------|------------------------|
| **Framework** | Arduino/PlatformIO | ESP-IDF |
| **Display** | 240x240 round GC9A01 | 412x412 QSPI LCD |
| **Touch** | None | Capacitive touchscreen |
| **Camera** | Direct OV2640 | Via Himax AI processor |
| **Audio** | PDM mic only | Dual codec (speaker + mic) |
| **Backend** | Laura cloud | Xin-Yi Flask API |
| **Use Case** | Mobile camera | Warehouse terminal |

## Resources

- **ESP-IDF Documentation**: https://docs.espressif.com/projects/esp-idf/en/v5.4/
- **SenseCAP Watcher**: https://www.seeedstudio.com/SenseCAP-Watcher-W1-A-p-5979.html
- **Xin-Yi Project**: ../README.md
- **heysalad_xiao_og Reference**: ../heysalad_xiao_og/

## License

This firmware is part of the Xin-Yi logistics system project.

## Support

For issues or questions:
1. Check serial monitor output for error messages
2. Review ESP-IDF documentation for API reference
3. Consult `SENSECAP_SETUP.md` for hardware setup
4. Check `HARDWARE_ANALYSIS.md` for integration strategies

---

**Built for the Xin-Yi logistics system** | **Powered by ESP-IDF** | **Optimized for SenseCAP Watcher**
