import usb.core
import usb.util

# Vulnerable VID:PID pairs
VULN_IDS = {
    ("04f2", "0976"): "AmazonBasics Wireless Mouse MG-0975 (USB dongle RG-0976)",
    ("046d", "c52b"): "Dell KM714 Wireless Keyboard and Mouse Combo",
    ("413c", "2501"): "Dell KM632 Wireless Mouse",
    ("04b4", "0060"): "Gigabyte K7600 Wireless Keyboard",
    ("03f0", "d407"): "HP Wireless Elite v2 Keyboard",
    ("17ef", "6071"): "Lenovo 500 Wireless Mouse (MS-436)",
    ("046d", "c539"): "Logitech G900 Wireless Gaming Mouse",
    ("045e", "0745"): "Microsoft Wireless Mouse 4000/5000",
    ("045e", "07b2"): "Microsoft USB Transceiver model 1496",
    ("045e", "07a5"): "Microsoft USB Transceiver model 1461",
    ("17ef", "6060"): "Lenovo N700 Wireless Mouse",
    ("17ef", "6032"): "Lenovo ThinkPad Ultraslim Keyboard & Mouse",
    ("17ef", "6022"): "Lenovo ThinkPad Ultraslim Plus Keyboard & Mouse",
    ("04F3", "06FA"): "Logitech mk 235 mouse and keyboard doungle",
}

def check_vulnerable_devices():
    devices = usb.core.find(find_all=True)
    found_any = False
    for dev in devices:
        vid = format(dev.idVendor, '04x')
        pid = format(dev.idProduct, '04x')
        print(dev)
        if (vid, pid) in VULN_IDS:
            print(f"[!!] Vulnerable device detected: {VULN_IDS[(vid, pid)]} (VID: {vid}, PID: {pid})")
            found_any = True
    if not found_any:
        print("No known vulnerable devices connected.")

# Run the check
from pywinusb import hid

# List of known vulnerable MouseJack devices (VID, PID): Expand as needed
vulnerable_devices = {
    (0x046D, 0xC52B): "Logitech Unifying Receiver",
    (0x046D, 0xC539): "Logitech Nano Receiver",
    (0x045E, 0x0745): "Microsoft Wireless Receiver 700 v2.0",
    (0x045E, 0x07A5): "Microsoft 2.4GHz Transceiver v9.0",
    (0x045E, 0x07B2): "Microsoft USB Dongle Model 1496",
    (0x1038, 0x1720): "SteelSeries Wireless Dongle",
    (0x25AE, 0x2042): "RAPOO Wireless Device",
    (0x25AE, 0x0625): "RAPOO Wireless Device",
    (0x1D57, 0xAD03): "Delux Wireless Dongle",
    (0x1D57, 0xFA60): "Delux 2.4GHz Mouse",
    (0x046D, 0XC534): "logitech M170"
    # Add more based on Bastille’s list
}

def detect_mousejack_devices():
    print("Scanning HID devices for MouseJack vulnerabilities...\n")
    found = False
    all_devices = hid.HidDeviceFilter().get_devices()

    for device in all_devices:
        vid = device.vendor_id
        pid = device.product_id
        name = device.product_name or "Unknown Product"

        if (vid, pid) in vulnerable_devices:
            print(f"[!] Vulnerable Device Found:")
            print(f"    Name: {name}")
            print(f"    VID: {hex(vid)}, PID: {hex(pid)}")
            print(f"    Known As: {vulnerable_devices[(vid, pid)]}\n")
            found = True

    if not found:
        print("✅ No known MouseJack-vulnerable HID devices detected.")

if __name__ == "__main__":
    detect_mousejack_devices()
