# Test SenseCAP Watcher Connection

Your Raspberry Pi detected these USB serial devices:
- `/dev/ttyACM0` ✅
- `/dev/ttyACM1`
- `/dev/ttyACM2`

The SenseCAP Watcher is likely on **ttyACM0** (most recent).

## Quick Connection Test

### 1. Check if device responds:

```bash
# Try to read device info
esptool.py --port /dev/ttyACM0 chip_id
```

If this works, you'll see ESP32-S3 chip information!

### 2. If permission denied, add yourself to dialout group:

```bash
sudo usermod -a -G dialout $USER
# Then logout and login (or reboot)
```

### 3. Or run with sudo temporarily:

```bash
sudo ./scripts/build_and_flash.sh backup /dev/ttyACM0
```

## Manual Commands (if script doesn't work)

### Backup factory data:
```bash
esptool.py --port /dev/ttyACM0 \
  --chip esp32s3 \
  --baud 2000000 \
  --before default_reset \
  --after hard_reset \
  --no-stub \
  read_flash 0x9000 204800 \
  ~/sensecap_factory_backup_$(date +%Y%m%d).bin
```

### Build firmware:
```bash
cd /home/admin/Xin-Yi/sensecap_watcher_xinyi
get_idf
idf.py set-target esp32s3
idf.py build
```

### Flash firmware:
```bash
idf.py -p /dev/ttyACM0 flash
```

### Monitor output:
```bash
idf.py -p /dev/ttyACM0 monitor
# Press Ctrl+] to exit
```

### Flash + Monitor (combined):
```bash
idf.py -p /dev/ttyACM0 flash monitor
```

## Using the Build Script (Recommended)

Now that the script is updated for Raspberry Pi, try:

```bash
cd /home/admin/Xin-Yi/sensecap_watcher_xinyi

# Should auto-detect /dev/ttyACM0 now
./scripts/build_and_flash.sh backup

# Or specify port explicitly
./scripts/build_and_flash.sh backup /dev/ttyACM0

# Build and flash
./scripts/build_and_flash.sh flash /dev/ttyACM0

# Monitor serial output
./scripts/build_and_flash.sh monitor /dev/ttyACM0
```

## Troubleshooting

### Wrong device?
If `/dev/ttyACM0` isn't your SenseCAP Watcher, try the others:

```bash
./scripts/build_and_flash.sh backup /dev/ttyACM1
# or
./scripts/build_and_flash.sh backup /dev/ttyACM2
```

### Check which device is ESP32-S3:
```bash
for port in /dev/ttyACM*; do
  echo "Testing $port..."
  esptool.py --port $port chip_id 2>&1 | grep -i "esp32" && echo "✅ Found ESP32 on $port"
done
```

### Device not responding:
1. Unplug and replug USB cable
2. Press and hold BOOT button on SenseCAP
3. Press RESET button while holding BOOT
4. Release both buttons
5. Try flashing again

---

**Next:** Once you confirm connection works, proceed with [QUICKSTART.md](QUICKSTART.md)
