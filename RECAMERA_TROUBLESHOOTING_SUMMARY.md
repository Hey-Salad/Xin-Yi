# ReCamera USB Connection Troubleshooting Summary

## Problem Diagnosis

Your reCamera is connected to the Raspberry Pi but cannot be accessed at 192.168.42.1.

### What I Found

✓ **Hardware Connection**: Camera is detected on USB Bus 001 Device 004
✓ **USB Device ID**: 3346:1003 (Cvitek USB Com Port)
✓ **USB Interfaces**: Device properly exposes CDC NCM/Ethernet interfaces
✓ **Pi Drivers**: cdc_ncm driver is loaded and working
✓ **Serial Port**: /dev/ttyACM2 exists but camera is not responding on serial console

✗ **Camera's USB Gadget Stack**: NOT RESPONDING to USB configuration requests
✗ **Network Interface**: usb0 interface cannot be created due to camera timeout (error -110)
✗ **Serial Console**: No output from /dev/ttyACM2 (camera may not have console enabled by default)

### Root Cause

**The reCamera's USB gadget software stack is not running or not properly configured.**

The camera hardware and USB descriptors are correct, but the camera's Linux system is not:
1. Running the USB gadget network service
2. Configuring its network interface with IP 192.168.42.1
3. Responding to USB configuration requests from the host

## Solutions (in order of preference)

### Option 1: Manual Serial Console Access (RECOMMENDED)

You need to manually connect to the camera's serial console to configure it:

1. **Connect to serial console:**
   ```bash
   sudo screen /dev/ttyACM2 115200
   ```

   (To exit screen: Press Ctrl+A, then K, then Y)

2. **If you see a login prompt:**
   - Try username: `root` (no password)
   - Or username: `root`, password: `cvitek`

3. **If you don't see anything:**
   - Try pressing Enter several times
   - Try unplugging and replugging the camera USB cable
   - The camera may need to be powered on differently or may not have serial console enabled

4. **Once logged in, configure USB gadget:**
   ```bash
   # Check if run_usb.sh exists
   ls -l /etc/run_usb.sh

   # If it exists:
   /etc/run_usb.sh stop
   /etc/run_usb.sh probe rndis
   /etc/run_usb.sh start

   # Configure network
   ifconfig usb0 192.168.42.1 netmask 255.255.255.0 up

   # Test from camera to Pi
   ping 192.168.42.110
   ```

5. **On the Pi (in another terminal):**
   ```bash
   # Recreate the network connection
   sudo nmcli connection add type ethernet ifname usb0 con-name usb0 \
     ipv4.method manual ipv4.addresses 192.168.42.110/24 \
     ipv4.never-default yes connection.autoconnect yes

   sudo nmcli connection up usb0

   # Test
   ping 192.168.42.1
   curl http://192.168.42.1/
   ```

### Option 2: Physical Power Cycle

Sometimes the camera just needs a complete restart:

1. **Unplug the camera's USB cable** from the Pi
2. **Wait 10 seconds**
3. **Plug it back in**
4. **Wait 30 seconds** for it to boot
5. **Run the diagnostic script:**
   ```bash
   ./check_recamera.sh
   ```
6. If usb0 interface appears, configure it:
   ```bash
   sudo nmcli connection add type ethernet ifname usb0 con-name usb0 \
     ipv4.method manual ipv4.addresses 192.168.42.110/24 \
     ipv4.never-default yes connection.autoconnect yes
   sudo nmcli connection up usb0
   ping 192.168.42.1
   ```

### Option 3: SSH Access (if available)

If the camera is accessible via SSH on a different network interface:

1. Check camera documentation for default network configuration
2. Camera might be on WiFi or might have DHCP enabled on USB
3. Try scanning your network: `nmap -sn 192.168.1.0/24` or your LAN subnet
4. Look for Cvitek devices with open port 22

### Option 4: Firmware Reflash

If the camera's firmware is corrupted or misconfigured:

1. **Download fresh firmware** from Seeed Studio or Milk-V:
   - Check: https://wiki.seeedstudio.com/recamera/
   - Or: https://github.com/milkv-duo/

2. **Flash using official tools** (usually requires SD card or special flashing cable)

3. **Build from source** (if you need custom configuration):
   ```bash
   git clone https://github.com/milkv-duo/duo-buildroot-sdk.git --depth=1
   cd duo-buildroot-sdk
   # Follow SDK build instructions
   ```

## Files Created for You

I've created these helper files:

1. **recamera_usb_gadget_fix.md** - Complete step-by-step manual configuration guide
2. **check_recamera.sh** - Quick diagnostic script
3. **recamera_auto_configure.py** - Automated serial configuration (didn't work due to no serial response)
4. **RECAMERA_TROUBLESHOOTING_SUMMARY.md** - This file

## Quick Diagnostic Commands

Run these to check status:

```bash
# Check if camera is detected
lsusb | grep -i cvitek

# Check serial port
ls -l /dev/ttyACM*

# Check network interfaces
ip link show

# Run full diagnostic
./check_recamera.sh

# Check recent errors
dmesg | grep -i "cdc_ncm\|usb0" | tail -20
```

## Expected Working State

When properly configured:

```bash
$ lsusb | grep Cvitek
Bus 001 Device 004: ID 3346:1003 Cvitek USB Com Port

$ ip addr show usb0
3: usb0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP
    inet 192.168.42.110/24 scope global usb0

$ ip neigh show dev usb0
192.168.42.1 lladdr 02:99:00:64:b3:d7 REACHABLE

$ ping -c 2 192.168.42.1
64 bytes from 192.168.42.1: icmp_seq=1 ttl=64 time=0.5 ms

$ curl http://192.168.42.1/
<html>... (camera web interface)
```

## Additional Notes

- The camera's USB CDC NCM interface is correctly configured at the hardware level
- The Pi has all necessary drivers (cdc_ncm, cdc_ether, etc.)
- The issue is purely on the camera's software side
- You may need to check the camera's documentation for the correct boot mode or initialization sequence

## Next Steps

1. **Try Option 1** (manual serial console) - this is most likely to work
2. **If serial doesn't respond**, try Option 2 (power cycle)
3. **Check camera documentation** for any special initialization steps
4. **As a last resort**, reflash the firmware (Option 4)

Good luck! Once you get the camera responding on serial or if the power cycle creates the usb0 interface, the network configuration from the Pi side is straightforward.
