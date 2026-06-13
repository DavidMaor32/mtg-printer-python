import usb.core

print("Scanning all connected USB devices...")
devices = usb.core.find(find_all=True)

found_any = False
for dev in devices:
    # Convert decimal IDs to standard Hex format for easy reading
    vid_hex = f"0x{dev.idVendor:04x}"
    pid_hex = f"0x{dev.idProduct:04x}"
    
    # Try to read the manufacturer string if accessible
    try:
        manufacturer = usb.util.get_string(dev, dev.iManufacturer)
        product = usb.util.get_string(dev, dev.iProduct)
        name_str = f"({manufacturer} - {product})"
    except Exception:
        name_str = ""

    # Look for anything matching SNBC or common printer IDs
    if "154f" in vid_hex or "snbc" in name_str.lower():
        print(f"⭐ FOUND MATCH: Vendor ID: {vid_hex} | Product ID: {pid_hex} {name_str}")
        found_any = True
    else:
        print(f"Device: Vendor ID: {vid_hex} | Product ID: {pid_hex} {name_str}")

if not found_any:
    print("\n⚠️ No SNBC vendor ID (0x154f) was detected on the USB bus.")