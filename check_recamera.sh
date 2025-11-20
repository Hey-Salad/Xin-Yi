#!/bin/bash
echo "=== ReCamera Connection Status ==="
echo
echo "USB Devices:"
lsusb | grep -i cvitek
echo
echo "Serial Device:"
ls -l /dev/ttyACM* 2>/dev/null || echo "No ACM devices found"
echo
echo "USB Network Interface (usb0):"
ip addr show usb0 2>/dev/null || echo "usb0 interface not found"
echo
echo "ARP Status for 192.168.42.1:"
ip neigh show dev usb0 2>/dev/null | grep "192.168.42.1" || echo "No ARP entry"
echo
echo "Recent USB/Network Errors (last 5):"
dmesg | grep -i "cdc_ncm\|usb0\|WATCHDOG" | tail -5
echo
echo "Connectivity Test:"
if ping -c 2 -W 1 192.168.42.1 &>/dev/null; then
    echo "✓ Camera is reachable at 192.168.42.1"
else
    echo "✗ Camera is NOT reachable at 192.168.42.1"
fi
