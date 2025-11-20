# Quick Start Guide - SenseCAP Watcher Xin-Yi Firmware

## 🚀 Get Running in 5 Minutes

### Step 1: Backup Factory Data (CRITICAL - 2 minutes)

```bash
# Make script executable
chmod +x /home/admin/Xin-Yi/sensecap_watcher_xinyi/scripts/build_and_flash.sh

# Backup factory partition
cd /home/admin/Xin-Yi/sensecap_watcher_xinyi
./scripts/build_and_flash.sh backup
```

**Save this backup file!** You'll need it to restore factory firmware.

### Step 2: Configure WiFi & Backend (1 minute)

Edit the config file:
```bash
nano main/include/config.h
```

Change these lines:
```c
// Line 26: Your Xin-Yi Flask backend IP
#define XINYI_API_URL "http://192.168.1.100:5000"  // ← Change this!

// Optional: Set WiFi (or configure via web UI later)
#define WIFI_SSID_DEFAULT "YourWiFiName"
#define WIFI_PASSWORD_DEFAULT "YourWiFiPassword"
```

Save with `Ctrl+X`, `Y`, `Enter`

### Step 3: Build & Flash (2 minutes)

```bash
# Activate ESP-IDF environment
get_idf

# Build and flash
./scripts/build_and_flash.sh flash

# This will:
# - Set target to ESP32-S3
# - Build firmware
# - Flash to device
# - Show you the serial output
```

### Step 4: Connect & Test

1. **Device boots up**
   - Generates unique device ID from MAC address
   - Shows "XinYi Watcher" on screen

2. **Connect to WiFi**
   - If no WiFi configured, creates AP: `XinYi-Watcher` / `xinyi2024`
   - Connect from phone/laptop
   - Go to `http://192.168.4.1`
   - Enter your WiFi credentials

3. **Access web interface**
   - Device gets IP from your router
   - IP shown on screen
   - Navigate to `http://[device-ip]`
   - Camera stream + controls

4. **Device registers with Xin-Yi backend**
   - Auto-registers on first connection
   - Sends heartbeat every 30 seconds
   - Ready for commands!

## 🎯 Quick Commands

```bash
cd /home/admin/Xin-Yi/sensecap_watcher_xinyi

# Build only (no flash)
./scripts/build_and_flash.sh build

# Flash app only (faster, keeps settings)
./scripts/build_and_flash.sh app

# Monitor serial output
./scripts/build_and_flash.sh monitor

# Open config menu
./scripts/build_and_flash.sh menuconfig

# Clean build
./scripts/build_and_flash.sh clean

# Full erase (warning: destructive!)
./scripts/build_and_flash.sh erase
```

## 🔧 Troubleshooting

**"ESP-IDF not found"**
```bash
get_idf
# Or: source ~/esp/esp-idf/export.sh
```

**"Permission denied on /dev/ttyUSB0"**
```bash
sudo usermod -a -G dialout $USER
# Then logout and login
```

**"No device found"**
```bash
# Specify port manually
./scripts/build_and_flash.sh flash /dev/ttyUSB0
# Or on Mac:
./scripts/build_and_flash.sh flash /dev/cu.usbmodem14101
```

**Build fails**
```bash
# Full clean and rebuild
./scripts/build_and_flash.sh clean
get_idf
./scripts/build_and_flash.sh build
```

## 📱 Testing with Xin-Yi Backend

### 1. Start your Flask backend
```bash
cd /home/admin/Xin-Yi/backend
python3 app.py
```

### 2. Device should auto-register
Check backend logs for:
```
POST /api/devices/register - Device: xinyi-watcher-xxxxxxxxxxxx
```

### 3. Check device status
```bash
curl http://localhost:5000/api/devices/xinyi-watcher-xxxxxxxxxxxx/status
```

### 4. Send command to device
```bash
curl -X POST http://localhost:5000/api/devices/xinyi-watcher-xxxxxxxxxxxx/command \
  -H "Content-Type: application/json" \
  -d '{"command": "start_stream"}'
```

## 🎨 What's Different from heysalad_xiao_og?

| Feature | heysalad_xiao_og | This Firmware |
|---------|------------------|---------------|
| Framework | Arduino/PlatformIO | ESP-IDF (native) |
| Display | 240x240 round | 412x412 square touchscreen |
| Backend | Laura cloud | Xin-Yi Flask API |
| Camera | Direct OV2640 | Via Himax AI chip |
| Audio | PDM mic only | Dual codec (speaker+mic) |
| Use case | Mobile camera | Warehouse terminal |

## 📝 Next Steps

1. **Implement camera module** - See `components/camera/`
2. **Build display UI** - See `components/display/`
3. **Complete HTTP server** - See `main/http_server.c`
4. **Add Xin-Yi API calls** - See `components/xinyi_client/`
5. **Create web dashboard** - See `data/web/`

Full details in [README.md](README.md)

## 🆘 Need Help?

1. Check serial output: `./scripts/build_and_flash.sh monitor`
2. Read full docs: [README.md](README.md)
3. Hardware setup: [../SENSECAP_SETUP.md](../SENSECAP_SETUP.md)
4. Integration guide: [../HARDWARE_ANALYSIS.md](../HARDWARE_ANALYSIS.md)

---

**You're ready to go! Flash the firmware and start building.**
