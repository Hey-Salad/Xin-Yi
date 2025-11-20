#!/bin/bash
################################################################################
# Create SPIFFS partition image from data/ directory
################################################################################

set -e

# Activate ESP-IDF
if [ -z "$IDF_PATH" ]; then
    source ~/esp/esp-idf/export.sh > /dev/null 2>&1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Creating SPIFFS image from data/ directory..."
cd "$PROJECT_DIR"

# SPIFFS parameters from partitions.csv
# spiffs starts at 0xc10000 and is 0x13F0000 bytes (20,381,696 bytes ~19.4MB)
SPIFFS_OFFSET=0xc10000
SPIFFS_SIZE=0x13F0000

# Create SPIFFS image using ESP-IDF tool
python "$IDF_PATH/components/spiffs/spiffsgen.py" \
    "$SPIFFS_SIZE" \
    data \
    build/spiffs.bin \
    --page-size 256 \
    --block-size 4096

echo "✅ SPIFFS image created: build/spiffs.bin"
echo "   Size: $(du -h build/spiffs.bin | cut -f1)"
echo ""
echo "To flash SPIFFS:"
echo "  idf.py -p /dev/ttyACM1 write_flash $SPIFFS_OFFSET build/spiffs.bin"
echo ""
echo "Or flash everything (firmware + SPIFFS):"
echo "  idf.py -p /dev/ttyACM1 flash"
echo "  esptool.py -p /dev/ttyACM1 write_flash $SPIFFS_OFFSET build/spiffs.bin"
