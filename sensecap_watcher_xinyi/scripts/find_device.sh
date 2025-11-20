#!/bin/bash
##############################################################################
# Find SenseCAP Watcher USB Port
# This script tests all available serial ports to find your ESP32-S3 device
##############################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Finding SenseCAP Watcher Device${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if esptool is available
if ! command -v esptool.py &> /dev/null; then
    echo -e "${RED}ERROR: esptool.py not found!${NC}"
    echo -e "${YELLOW}Install with: pip install esptool${NC}"
    exit 1
fi

# Find all potential serial devices
DEVICES=$(ls /dev/ttyACM* /dev/ttyUSB* /dev/cu.usbmodem* 2>/dev/null || true)

if [ -z "$DEVICES" ]; then
    echo -e "${RED}No USB serial devices found!${NC}"
    echo ""
    echo "Please check:"
    echo "  1. SenseCAP Watcher is plugged in via USB-C"
    echo "  2. USB cable supports data (not just charging)"
    echo "  3. USB port on Raspberry Pi is working"
    exit 1
fi

echo -e "${YELLOW}Found devices:${NC}"
for dev in $DEVICES; do
    echo "  - $dev"
done
echo ""

echo -e "${BLUE}Testing each device...${NC}"
echo ""

FOUND_DEVICE=""

for port in $DEVICES; do
    echo -e "${YELLOW}Testing $port...${NC}"

    # Try to read chip info with timeout
    OUTPUT=$(timeout 5 esptool.py --port "$port" --no-stub chip_id 2>&1 || true)

    if echo "$OUTPUT" | grep -qi "esp32-s3"; then
        echo -e "${GREEN}✅ Found ESP32-S3 on $port!${NC}"
        FOUND_DEVICE="$port"

        # Get more details
        MAC=$(echo "$OUTPUT" | grep "MAC:" | head -1)
        if [ -n "$MAC" ]; then
            echo -e "   $MAC"
        fi

        FLASH=$(echo "$OUTPUT" | grep -i "flash size" | head -1)
        if [ -n "$FLASH" ]; then
            echo -e "   $FLASH"
        fi

        break
    else
        echo -e "${RED}❌ Not an ESP32-S3${NC}"
    fi
    echo ""
done

echo ""
echo -e "${BLUE}========================================${NC}"

if [ -n "$FOUND_DEVICE" ]; then
    echo -e "${GREEN}SUCCESS! SenseCAP Watcher found on:${NC}"
    echo -e "${GREEN}$FOUND_DEVICE${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Backup factory data:"
    echo "     ./scripts/build_and_flash.sh backup $FOUND_DEVICE"
    echo ""
    echo "  2. Build and flash firmware:"
    echo "     ./scripts/build_and_flash.sh flash $FOUND_DEVICE"
    echo ""
    echo "  3. Monitor serial output:"
    echo "     ./scripts/build_and_flash.sh monitor $FOUND_DEVICE"
else
    echo -e "${RED}No ESP32-S3 device found!${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check USB cable (must support data, not just power)"
    echo "  2. Try different USB port on Raspberry Pi"
    echo "  3. Press BOOT + RESET buttons on SenseCAP:"
    echo "     - Hold BOOT button"
    echo "     - Press RESET button"
    echo "     - Release both"
    echo "     - Run this script again"
    echo "  4. Check USB connection: lsusb | grep -i espressif"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
