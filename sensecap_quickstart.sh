#!/bin/bash

# SenseCAP Watcher Quick Start Script
# This script helps you build and flash XiaoZhi firmware to your SenseCAP Watcher

set -e  # Exit on error

echo "============================================"
echo "SenseCAP Watcher Quick Start"
echo "============================================"
echo ""

# Check if ESP-IDF is installed
if [ ! -d "$HOME/esp/esp-idf" ]; then
    echo "ERROR: ESP-IDF not found at ~/esp/esp-idf"
    echo "Please run the installation first:"
    echo "  cd ~/esp"
    echo "  git clone -b v5.4 --recursive https://github.com/espressif/esp-idf.git"
    echo "  cd esp-idf"
    echo "  ./install.sh esp32s3"
    exit 1
fi

# Activate ESP-IDF environment
echo "Step 1: Activating ESP-IDF environment..."
source $HOME/esp/esp-idf/export.sh

# Navigate to xiaozhi-esp32 directory
XIAOZHI_DIR="/Users/chilumbam/Xin-Yi/devices/xiaozhi-esp32"
if [ ! -d "$XIAOZHI_DIR" ]; then
    echo "ERROR: xiaozhi-esp32 not found at $XIAOZHI_DIR"
    exit 1
fi

cd "$XIAOZHI_DIR"
echo "Working directory: $(pwd)"
echo ""

# Menu
echo "What would you like to do?"
echo "1) Backup factory data (REQUIRED before first flash)"
echo "2) Build firmware only"
echo "3) Build and flash firmware"
echo "4) Flash pre-built firmware"
echo "5) Monitor serial output"
echo "6) Build, flash, and monitor"
echo "7) Exit"
echo ""
read -p "Enter choice [1-7]: " choice

case $choice in
    1)
        echo ""
        echo "Step 2: Backing up factory data..."
        echo "Please connect your SenseCAP Watcher via USB-C"
        echo ""
        echo "Available serial ports:"
        ls /dev/cu.usbmodem* 2>/dev/null || echo "No USB devices found!"
        echo ""
        read -p "Enter your serial port (e.g., /dev/cu.usbmodem14101): " PORT

        BACKUP_FILE="$HOME/sensecap_watcher_factory_backup_$(date +%Y%m%d_%H%M%S).bin"

        esptool.py --port "$PORT" \
            --chip esp32s3 \
            --baud 2000000 \
            --before default_reset \
            --after hard_reset \
            --no-stub \
            read_flash 0x9000 204800 \
            "$BACKUP_FILE"

        echo ""
        echo "Factory backup saved to: $BACKUP_FILE"
        echo "File size: $(ls -lh "$BACKUP_FILE" | awk '{print $5}')"
        echo "KEEP THIS FILE SAFE!"
        ;;

    2)
        echo ""
        echo "Step 2: Building firmware..."
        python scripts/release.py sensecap-watcher
        echo ""
        echo "Build complete! Binary location:"
        find build -name "*.bin" -type f | grep -v bootloader | grep -v partition
        ;;

    3)
        echo ""
        echo "Step 2: Building and flashing firmware..."
        echo ""
        echo "Available serial ports:"
        ls /dev/cu.usbmodem* 2>/dev/null || echo "No USB devices found!"
        echo ""
        read -p "Enter your serial port (e.g., /dev/cu.usbmodem14101): " PORT

        python scripts/release.py sensecap-watcher

        idf.py -p "$PORT" -DBOARD_NAME=sensecap-watcher flash

        echo ""
        echo "Flash complete!"
        echo "Run 'idf.py -p $PORT monitor' to see serial output"
        ;;

    4)
        echo ""
        echo "Step 2: Flashing pre-built firmware..."
        echo ""
        echo "Available serial ports:"
        ls /dev/cu.usbmodem* 2>/dev/null || echo "No USB devices found!"
        echo ""
        read -p "Enter your serial port (e.g., /dev/cu.usbmodem14101): " PORT

        idf.py -p "$PORT" -DBOARD_NAME=sensecap-watcher flash

        echo ""
        echo "Flash complete!"
        ;;

    5)
        echo ""
        echo "Step 2: Monitoring serial output..."
        echo ""
        echo "Available serial ports:"
        ls /dev/cu.usbmodem* 2>/dev/null || echo "No USB devices found!"
        echo ""
        read -p "Enter your serial port (e.g., /dev/cu.usbmodem14101): " PORT

        echo ""
        echo "Press Ctrl+] to exit monitor"
        sleep 2
        idf.py -p "$PORT" monitor
        ;;

    6)
        echo ""
        echo "Step 2: Building, flashing, and monitoring..."
        echo ""
        echo "Available serial ports:"
        ls /dev/cu.usbmodem* 2>/dev/null || echo "No USB devices found!"
        echo ""
        read -p "Enter your serial port (e.g., /dev/cu.usbmodem14101): " PORT

        python scripts/release.py sensecap-watcher

        echo ""
        echo "Press Ctrl+] to exit monitor"
        sleep 2
        idf.py -p "$PORT" -DBOARD_NAME=sensecap-watcher flash monitor
        ;;

    7)
        echo "Exiting..."
        exit 0
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Done!"
