# Complete Setup Guide for Raspberry Pi

Your firmware is ready, but we need to install ESP-IDF first!

## 📋 What You Need

- ✅ Raspberry Pi (you have this!)
- ✅ SenseCAP Watcher connected via USB-C
- ⚠️ ESP-IDF 5.4+ (need to install)
- ⚠️ esptool (comes with ESP-IDF)

## 🚀 One-Time Setup (15 minutes)

### Step 1: Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y git wget flex bison gperf python3 python3-pip \
  python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util \
  libusb-1.0-0 python3-setuptools
```

### Step 2: Install ESP-IDF 5.4

```bash
# Create esp directory
mkdir -p ~/esp
cd ~/esp

# Clone ESP-IDF v5.4
git clone -b v5.4 --recursive https://github.com/espressif/esp-idf.git

# This takes ~5 minutes
cd esp-idf

# Install ESP32-S3 toolchain
./install.sh esp32s3

# This takes ~10 minutes on Raspberry Pi
```

### Step 3: Set Up Environment

```bash
# Add to your .bashrc for permanent access
echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.bashrc

# Reload bash configuration
source ~/.bashrc
```

### Step 4: Test Installation

```bash
# Activate ESP-IDF
get_idf

# You should see:
# "Done! You can now compile ESP-IDF projects."

# Verify esptool is available
esptool.py version
```

## ✅ Quick Install (Copy-Paste All)

If you want to run everything at once:

```bash
# Install dependencies
sudo apt-get update && sudo apt-get install -y git wget flex bison gperf \
  python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev \
  libssl-dev dfu-util libusb-1.0-0 python3-setuptools

# Clone and install ESP-IDF
mkdir -p ~/esp && cd ~/esp && \
git clone -b v5.4 --recursive https://github.com/espressif/esp-idf.git && \
cd esp-idf && ./install.sh esp32s3

# Set up environment
echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.bashrc && source ~/.bashrc

# Activate ESP-IDF
. ~/esp/esp-idf/export.sh

# Test
esptool.py version && echo "✅ Setup complete!"
```

## 🔌 After Setup - Find Your Device

```bash
# Go to firmware directory
cd /home/admin/Xin-Yi/sensecap_watcher_xinyi

# Activate ESP-IDF (do this every time you open a new terminal)
get_idf

# Find your SenseCAP Watcher
./scripts/find_device.sh
```

This will tell you which port your device is on (likely `/dev/ttyACM0`).

## 📝 Build & Flash

Once ESP-IDF is installed and device is found:

```bash
cd /home/admin/Xin-Yi/sensecap_watcher_xinyi

# 1. Activate ESP-IDF (required in every new terminal session)
get_idf

# 2. Backup factory data (IMPORTANT - do this first!)
./scripts/build_and_flash.sh backup /dev/ttyACM0

# 3. Configure your backend (edit config.h)
nano main/include/config.h
# Change XINYI_API_URL to your Flask server IP

# 4. Build and flash
./scripts/build_and_flash.sh flash /dev/ttyACM0

# 5. Monitor output
./scripts/build_and_flash.sh monitor /dev/ttyACM0
```

## 🔧 Troubleshooting

### "Permission denied" on /dev/ttyACM0

```bash
# Add yourself to dialout group
sudo usermod -a -G dialout $USER

# Then logout and login (or reboot)
sudo reboot
```

### "command not found: get_idf"

```bash
# Manually activate ESP-IDF
source ~/esp/esp-idf/export.sh

# Or add to .bashrc
echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.bashrc
source ~/.bashrc
```

### ESP-IDF install fails

```bash
# Make sure you have enough disk space
df -h

# You need at least 2GB free for ESP-IDF
```

### Device not found

```bash
# Check if SenseCAP is connected
lsusb | grep -i espressif

# Check available ports
ls -l /dev/ttyACM* /dev/ttyUSB*

# Try putting device in download mode:
# 1. Hold BOOT button on SenseCAP
# 2. Press RESET button while holding BOOT
# 3. Release both buttons
# 4. Try flashing again
```

## ⏱️ How Long Does This Take?

- **Dependencies install:** 2-5 minutes
- **ESP-IDF download:** 3-5 minutes
- **ESP-IDF install:** 5-10 minutes
- **First firmware build:** 3-5 minutes
- **Flash to device:** 1-2 minutes

**Total first-time setup:** ~15-25 minutes on Raspberry Pi

After setup, rebuilding and flashing takes only 1-2 minutes!

## 🎯 Alternative: Use Pre-compiled ESP-IDF

If you want faster setup, you can use the system Python packages:

```bash
# Install with --break-system-packages (not recommended but faster)
pip3 install --break-system-packages esptool

# Then you can at least backup factory data and flash
esptool.py --port /dev/ttyACM0 chip_id
```

But for full development, you really need ESP-IDF.

## ✅ Verification Checklist

After setup, verify:

- [ ] `get_idf` command works
- [ ] `esptool.py version` shows output
- [ ] `idf.py --version` shows ESP-IDF v5.4.x
- [ ] `/dev/ttyACM0` (or similar) exists
- [ ] You're in `dialout` group: `groups | grep dialout`

## 📚 Next Steps

Once ESP-IDF is installed:

1. **[TEST_CONNECTION.md](TEST_CONNECTION.md)** - Test device connection
2. **[QUICKSTART.md](QUICKSTART.md)** - Build and flash firmware
3. **[README.md](README.md)** - Full documentation

---

**Questions?** Check the [ESP-IDF Getting Started Guide](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/get-started/)
