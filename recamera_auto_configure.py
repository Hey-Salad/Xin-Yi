#!/usr/bin/env python3
"""
Auto-configure reCamera USB gadget over serial connection.
"""
import serial
import time
import sys
import re

SERIAL_PORT = '/dev/ttyACM2'
BAUD_RATE = 115200
TIMEOUT = 2

def send_command(ser, command, wait_time=1.0, read_output=True):
    """Send command to serial port and optionally read response."""
    print(f"  → {command}")
    ser.write(f"{command}\n".encode())
    ser.flush()
    time.sleep(wait_time)

    if read_output:
        output = ""
        while ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            output += chunk
            time.sleep(0.1)
        if output:
            print(f"  ← {output.strip()}")
        return output
    return ""

def main():
    print("=== ReCamera USB Gadget Auto-Configuration ===\n")

    try:
        print(f"Opening serial port {SERIAL_PORT} at {BAUD_RATE} baud...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        time.sleep(1)

        # Clear any existing data
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        print("Connected! Sending initial newlines to wake up console...\n")
        ser.write(b"\n\n")
        time.sleep(1)

        # Read any welcome/login prompt
        initial_output = ""
        while ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            initial_output += chunk
            time.sleep(0.1)

        if initial_output:
            print("Initial output:")
            print(initial_output)
            print()

        # Check if we need to login
        if "login:" in initial_output.lower():
            print("Login prompt detected. Attempting login as root...")
            send_command(ser, "root", wait_time=1)
            time.sleep(1)

            # Check if password is needed
            output = ""
            while ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                output += chunk
                time.sleep(0.1)

            if "password:" in output.lower():
                print("Password prompt detected. Trying default password 'cvitek'...")
                send_command(ser, "cvitek", wait_time=1)
        else:
            print("No login prompt - assuming already logged in or console is at shell\n")

        time.sleep(1)

        # Send a test command to verify we're at a shell
        print("\n[Step 1] Verifying shell access...")
        send_command(ser, "whoami", wait_time=0.5)

        print("\n[Step 2] Checking current USB gadget status...")
        send_command(ser, "lsmod | grep -E 'usb|rndis|ncm|ether'", wait_time=1)

        print("\n[Step 3] Checking USB OTG role...")
        send_command(ser, "cat /proc/cviusb/otg_role", wait_time=0.5)

        print("\n[Step 4] Checking network interfaces...")
        send_command(ser, "ifconfig -a | grep -E 'usb|rndis'", wait_time=1)

        print("\n[Step 5] Checking for USB configuration script...")
        script_output = send_command(ser, "ls -l /etc/run_usb.sh", wait_time=0.5)

        has_script = "run_usb.sh" in script_output and "No such file" not in script_output

        if has_script:
            print("\n[Step 6] Found /etc/run_usb.sh - using it to configure USB gadget...")
            send_command(ser, "/etc/run_usb.sh stop", wait_time=1)
            send_command(ser, "/etc/run_usb.sh probe rndis", wait_time=2)
            send_command(ser, "/etc/run_usb.sh start", wait_time=2)
        else:
            print("\n[Step 6] No run_usb.sh script - configuring manually...")

            # Set OTG to device mode
            send_command(ser, "echo device > /proc/cviusb/otg_role", wait_time=0.5)

            # Load modules
            modules = ["configfs", "libcomposite", "u_ether", "usb_f_ecm", "usb_f_rndis", "usb_f_ncm"]
            for module in modules:
                send_command(ser, f"modprobe {module}", wait_time=0.5)

        print("\n[Step 7] Configuring USB network interface...")
        send_command(ser, "ifconfig usb0 192.168.42.1 netmask 255.255.255.0 up", wait_time=1)

        # Also try rndis0 in case that's the interface name
        send_command(ser, "ifconfig rndis0 192.168.42.1 netmask 255.255.255.0 up 2>/dev/null", wait_time=1)

        print("\n[Step 8] Verifying network configuration...")
        send_command(ser, "ifconfig | grep -A 3 '192.168.42'", wait_time=1)

        print("\n[Step 9] Testing connectivity to Pi (192.168.42.110)...")
        send_command(ser, "ping -c 3 192.168.42.110", wait_time=4)

        print("\n✓ Configuration complete!")
        print("\nYou can now test connectivity from the Pi:")
        print("  ping 192.168.42.1")
        print("  curl http://192.168.42.1/")

        ser.close()
        print("\nSerial connection closed.")

    except serial.SerialException as e:
        print(f"✗ Serial port error: {e}")
        print(f"\nMake sure:")
        print(f"  1. reCamera is connected")
        print(f"  2. {SERIAL_PORT} exists")
        print(f"  3. You have permission to access it (are you in the dialout group?)")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
