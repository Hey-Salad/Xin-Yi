# ReCamera USB Gadget Configuration Guide

## Problem
The reCamera's USB gadget stack is not responding, causing the Pi to be unable to communicate with 192.168.42.1.

## Current Status on Pi
- reCamera detected: `Cvitek USB Com Port` (3346:1003)
- Serial device: `/dev/ttyACM2`
- USB network interface `usb0` is UP with IP 192.168.42.110/24
- ARP for 192.168.42.1 shows **FAILED** - camera not responding
- Kernel errors: continuous NETDEV WATCHDOG transmit queue timeouts

## Solution Steps

### Step 1: Connect to reCamera Serial Console

```bash
sudo screen /dev/ttyACM2 115200
```

**Note:** To exit screen: Press `Ctrl+A` then `K` then `Y`

### Step 2: Login to reCamera
- Default credentials (try these):
  - Username: `root` (no password) OR
  - Username: `root`, Password: `cvitek`

### Step 3: Check Current USB Gadget Status

Once logged in, run these commands on the reCamera:

```bash
# Check if USB gadget modules are loaded
lsmod | grep -E "usb|rndis|ncm|ether"

# Check USB OTG role
cat /proc/cviusb/otg_role

# Check network interfaces
ifconfig -a
```

### Step 4: Configure USB Gadget (RNDIS/NCM Mode)

#### Method A: Using run_usb.sh script (if available)
```bash
# Check if the script exists
ls -l /etc/run_usb.sh

# If it exists, run:
/etc/run_usb.sh stop
/etc/run_usb.sh probe rndis
/etc/run_usb.sh start
```

#### Method B: Manual Module Loading
```bash
# Set OTG to device mode
echo device > /proc/cviusb/otg_role

# Load required kernel modules
modprobe configfs
modprobe libcomposite
modprobe u_ether
modprobe usb_f_ecm
modprobe usb_f_eem
modprobe usb_f_rndis
modprobe usb_f_ncm

# Verify modules loaded
lsmod | grep -E "usb|rndis|ncm"
```

#### Method C: ConfigFS Manual Setup (if scripts fail)
```bash
#!/bin/sh
# USB Gadget ConfigFS setup for RNDIS

cd /sys/kernel/config/usb_gadget/
mkdir -p g1
cd g1

# Device descriptor
echo 0x3346 > idVendor
echo 0x1003 > idProduct
echo 0x0100 > bcdDevice
echo 0x0200 > bcdUSB

# String descriptors
mkdir -p strings/0x409
echo "0123456789" > strings/0x409/serialnumber
echo "CVITEK" > strings/0x409/manufacturer
echo "USB RNDIS Device" > strings/0x409/product

# Configuration
mkdir -p configs/c.1
mkdir -p configs/c.1/strings/0x409
echo "RNDIS" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

# RNDIS function
mkdir -p functions/rndis.usb0
echo "02:99:00:64:b3:d7" > functions/rndis.usb0/dev_addr
echo "02:99:00:64:b3:d6" > functions/rndis.usb0/host_addr

# Link function to configuration
ln -s functions/rndis.usb0 configs/c.1/

# Enable gadget (find your UDC device first with: ls /sys/class/udc/)
UDC_DEVICE=$(ls /sys/class/udc/ | head -n1)
echo $UDC_DEVICE > UDC
```

### Step 5: Configure Network on reCamera

```bash
# Configure the USB network interface (usually usb0 or rndis0)
ifconfig usb0 192.168.42.1 netmask 255.255.255.0 up

# Or if using rndis0:
ifconfig rndis0 192.168.42.1 netmask 255.255.255.0 up

# Verify
ifconfig
ping 192.168.42.110
```

### Step 6: Verify on Raspberry Pi

Back on the Pi (in a new terminal):

```bash
# Check if camera responds to ARP now
ip neigh show dev usb0

# Should show: 192.168.42.1 lladdr ... REACHABLE

# Test connectivity
ping -c 4 192.168.42.1

# Try accessing web interface
curl http://192.168.42.1/
```

## Troubleshooting

### If USB gadget still fails:

1. **Check kernel messages on reCamera:**
   ```bash
   dmesg | tail -50
   ```

2. **Restart USB subsystem:**
   ```bash
   # On reCamera
   /etc/init.d/usb-gadget restart
   # or
   reboot
   ```

3. **On Pi, reset the USB connection:**
   ```bash
   sudo nmcli connection down usb0
   sudo nmcli connection up usb0
   # or
   sudo ip link set usb0 down
   sudo ip link set usb0 up
   ```

4. **Check Pi's NetworkManager configuration:**
   ```bash
   sudo nmcli connection show usb0
   sudo nmcli connection modify usb0 connection.autoconnect yes
   sudo nmcli connection modify usb0 ipv4.method manual
   sudo nmcli connection modify usb0 ipv4.addresses 192.168.42.110/24
   sudo nmcli connection modify usb0 ipv4.never-default yes
   sudo nmcli connection up usb0
   ```

### If you need to rebuild firmware:

The reCamera firmware can be rebuilt from source:
```bash
git clone https://github.com/milkv-duo/duo-buildroot-sdk.git --depth=1
cd duo-buildroot-sdk
# Follow build instructions in the repository
```

## Quick Diagnostic Script

Save this as `check_recamera.sh` on the Pi:

```bash
#!/bin/bash
echo "=== ReCamera Connection Status ==="
echo
echo "USB Devices:"
lsusb | grep -i cvitek
echo
echo "Serial Device:"
ls -l /dev/ttyACM* 2>/dev/null
echo
echo "USB Network Interface:"
ip addr show usb0
echo
echo "ARP Status:"
ip neigh show dev usb0
echo
echo "Recent Errors:"
dmesg | grep -i "cdc_ncm\|usb0" | tail -10
echo
echo "Ping Test:"
ping -c 2 -W 1 192.168.42.1 2>&1
```

## Expected Working State

When properly configured, you should see:
- `lsmod | grep rndis` shows `usb_f_rndis` and related modules on reCamera
- `ifconfig` shows `usb0` or `rndis0` with IP 192.168.42.1 on reCamera
- `ip neigh show dev usb0` shows 192.168.42.1 as REACHABLE on Pi
- `ping 192.168.42.1` works from Pi
- Web interface accessible at `http://192.168.42.1/`
