#!/bin/bash
################################################################################
# Build and Flash Script for SenseCAP Watcher Xin-Yi Firmware
#
# Usage:
#   ./scripts/build_and_flash.sh [command] [port]
#
# Commands:
#   build       - Build firmware only
#   flash       - Build and flash firmware
#   monitor     - Open serial monitor
#   clean       - Clean build files
#   menuconfig  - Open configuration menu
#   backup      - Backup factory data from device
#
# Examples:
#   ./scripts/build_and_flash.sh build
#   ./scripts/build_and_flash.sh flash /dev/ttyUSB0
#   ./scripts/build_and_flash.sh backup /dev/ttyUSB0
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$HOME/sensecap_backups"
DEFAULT_PORT="/dev/ttyUSB0"

# Detect port
detect_port() {
    # Raspberry Pi often uses ttyACM for ESP32
    if [ -e "/dev/ttyACM0" ]; then
        echo "/dev/ttyACM0"
    elif [ -e "/dev/ttyUSB0" ]; then
        echo "/dev/ttyUSB0"
    elif [ -e "/dev/cu.usbmodem14101" ]; then
        echo "/dev/cu.usbmodem14101"
    elif ls /dev/ttyACM* 1> /dev/null 2>&1; then
        ls /dev/ttyACM* | head -n 1
    elif ls /dev/cu.usbmodem* 1> /dev/null 2>&1; then
        ls /dev/cu.usbmodem* | head -n 1
    elif ls /dev/ttyUSB* 1> /dev/null 2>&1; then
        ls /dev/ttyUSB* | head -n 1
    else
        echo ""
    fi
}

# Print colored message
print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

# Print header
print_header() {
    echo ""
    print_msg "$BLUE" "=========================================="
    print_msg "$BLUE" "  $1"
    print_msg "$BLUE" "=========================================="
    echo ""
}

# Check if ESP-IDF is activated
check_idf() {
    if [ -z "$IDF_PATH" ]; then
        print_msg "$RED" "ERROR: ESP-IDF environment not activated!"
        print_msg "$YELLOW" "Please run: get_idf"
        print_msg "$YELLOW" "Or: source ~/esp/esp-idf/export.sh"
        exit 1
    fi
    print_msg "$GREEN" "ESP-IDF path: $IDF_PATH"
}

# Build firmware
cmd_build() {
    print_header "Building Firmware"
    check_idf
    cd "$PROJECT_DIR"

    print_msg "$BLUE" "Setting target to ESP32-S3..."
    idf.py set-target esp32s3

    print_msg "$BLUE" "Building..."
    idf.py build

    print_msg "$GREEN" "Build successful!"
    print_msg "$YELLOW" "Binary location: $PROJECT_DIR/build/sensecap_watcher_xinyi.bin"
}

# Flash firmware
cmd_flash() {
    local port=${1:-$(detect_port)}

    if [ -z "$port" ]; then
        print_msg "$RED" "ERROR: No device found!"
        print_msg "$YELLOW" "Please specify port: $0 flash /dev/ttyUSB0"
        exit 1
    fi

    print_header "Flashing Firmware"
    print_msg "$BLUE" "Port: $port"

    check_idf
    cd "$PROJECT_DIR"

    # Build if not already built
    if [ ! -f "build/sensecap_watcher_xinyi.bin" ]; then
        print_msg "$YELLOW" "Firmware not built yet, building..."
        cmd_build
    fi

    print_msg "$BLUE" "Flashing to $port..."
    idf.py -p "$port" flash

    print_msg "$GREEN" "Flash successful!"
    print_msg "$YELLOW" "To monitor serial output, run:"
    print_msg "$YELLOW" "  idf.py -p $port monitor"
}

# App flash only (faster, keeps nvs/spiffs)
cmd_app_flash() {
    local port=${1:-$(detect_port)}

    if [ -z "$port" ]; then
        print_msg "$RED" "ERROR: No device found!"
        exit 1
    fi

    print_header "Flashing App Only"
    print_msg "$BLUE" "Port: $port"

    check_idf
    cd "$PROJECT_DIR"

    print_msg "$BLUE" "Building and flashing app..."
    idf.py -p "$port" app-flash

    print_msg "$GREEN" "App flash successful!"
}

# Monitor serial output
cmd_monitor() {
    local port=${1:-$(detect_port)}

    if [ -z "$port" ]; then
        print_msg "$RED" "ERROR: No device found!"
        exit 1
    fi

    print_header "Serial Monitor"
    print_msg "$BLUE" "Port: $port"
    print_msg "$YELLOW" "Press Ctrl+] to exit"
    echo ""

    check_idf
    cd "$PROJECT_DIR"

    idf.py -p "$port" monitor
}

# Backup factory data
cmd_backup() {
    local port=${1:-$(detect_port)}

    if [ -z "$port" ]; then
        print_msg "$RED" "ERROR: No device found!"
        exit 1
    fi

    print_header "Backing Up Factory Data"
    print_msg "$RED" "⚠️  IMPORTANT: This backup is required to restore factory firmware!"

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/sensecap_factory_${timestamp}.bin"

    print_msg "$BLUE" "Port: $port"
    print_msg "$BLUE" "Backup file: $backup_file"
    print_msg "$BLUE" "Reading flash..."

    esptool.py --port "$port" \
        --chip esp32s3 \
        --baud 2000000 \
        --before default_reset \
        --after hard_reset \
        --no-stub \
        read_flash 0x9000 204800 \
        "$backup_file"

    if [ -f "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        print_msg "$GREEN" "Backup successful! ($size)"
        print_msg "$YELLOW" "Backup saved to: $backup_file"
        print_msg "$YELLOW" "KEEP THIS FILE SAFE!"
    else
        print_msg "$RED" "ERROR: Backup failed!"
        exit 1
    fi
}

# Clean build files
cmd_clean() {
    print_header "Cleaning Build Files"
    check_idf
    cd "$PROJECT_DIR"

    idf.py fullclean
    print_msg "$GREEN" "Clean complete!"
}

# Open menuconfig
cmd_menuconfig() {
    print_header "ESP-IDF Configuration Menu"
    check_idf
    cd "$PROJECT_DIR"

    idf.py menuconfig
}

# Erase flash
cmd_erase() {
    local port=${1:-$(detect_port)}

    if [ -z "$port" ]; then
        print_msg "$RED" "ERROR: No device found!"
        exit 1
    fi

    print_header "Erasing Flash"
    print_msg "$RED" "⚠️  WARNING: This will erase ALL data on the device!"
    print_msg "$YELLOW" "Press Ctrl+C to cancel, or Enter to continue..."
    read

    check_idf
    cd "$PROJECT_DIR"

    print_msg "$BLUE" "Erasing flash on $port..."
    idf.py -p "$port" erase-flash

    print_msg "$GREEN" "Flash erased!"
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [command] [port]

Commands:
  build          Build firmware only
  flash [port]   Build and flash firmware
  app [port]     Flash app only (faster, keeps settings)
  monitor [port] Open serial monitor
  backup [port]  Backup factory data (IMPORTANT before first flash!)
  clean          Clean build files
  menuconfig     Open configuration menu
  erase [port]   Erase entire flash (WARNING: destructive!)

Examples:
  $0 build
  $0 flash
  $0 flash /dev/ttyUSB0
  $0 backup
  $0 app /dev/cu.usbmodem14101
  $0 monitor

Port is auto-detected if not specified.

EOF
}

# Main script
main() {
    local command=${1:-help}
    local port=$2

    case "$command" in
        build)
            cmd_build
            ;;
        flash)
            cmd_flash "$port"
            ;;
        app)
            cmd_app_flash "$port"
            ;;
        monitor)
            cmd_monitor "$port"
            ;;
        backup)
            cmd_backup "$port"
            ;;
        clean)
            cmd_clean
            ;;
        menuconfig)
            cmd_menuconfig
            ;;
        erase)
            cmd_erase "$port"
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_msg "$RED" "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main
main "$@"
