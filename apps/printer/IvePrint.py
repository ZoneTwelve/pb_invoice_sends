import os
import socket
import base64
import requests
import usb.core
import usb.util
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv("IveConfig.txt")

SERVER_ADDR = os.getenv("SERVER_ADDR")
VATID = os.getenv("VATID")
AUTHORIZATION = os.getenv("Authorization")

PRINTER_IP = os.getenv("PRINTER_IP", "192.168.1.147")
PRINTER_PORT = int(os.getenv("PRINTER_PORT", "9100"))
PRINT_FOLDER = os.getenv("PRINT_FOLDER", r"C:\BDPOS7\Invoice")
PRINT_TIMEOUT = 10  # seconds

# USB printer info from env (strings, convert to int if present)
USB_VENDOR_ID = os.getenv("PRINTER_VENDOR_ID")
USB_PRODUCT_ID = os.getenv("PRINTER_PRODUCT_ID")
INTERFACE = 0  # usually 0


def print_to_printer(base64_data: str):
    """Send print data over TCP to network printer."""
    raw_bytes = base64.b64decode(base64_data)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(PRINT_TIMEOUT)
            s.connect((PRINTER_IP, PRINTER_PORT))
            s.sendall(raw_bytes)
        print("✅ Print command sent successfully (IP printer).")
        return True
    except (socket.timeout, socket.error) as e:
        print(f"❌ Cannot print via IP printer: {e}")
        return False


def print_to_usb_printer(base64_data: str):
    """Send raw ESC/POS data to USB printer via pyusb."""
    if USB_VENDOR_ID is None or USB_PRODUCT_ID is None:
        raise ValueError("USB Vendor ID and Product ID must be set for USB printing.")

    raw_data = base64.b64decode(base64_data)

    vendor_id = int(USB_VENDOR_ID, 16) if USB_VENDOR_ID.startswith("0x") else int(USB_VENDOR_ID)
    product_id = int(USB_PRODUCT_ID, 16) if USB_PRODUCT_ID.startswith("0x") else int(USB_PRODUCT_ID)

    dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    if dev is None:
        raise ValueError(f"USB printer not found (VID={vendor_id}, PID={product_id}).")

    # Detach kernel driver if possible, ignore on Windows if not implemented
    try:
        if dev.is_kernel_driver_active(INTERFACE):
            dev.detach_kernel_driver(INTERFACE)
    except NotImplementedError:
        pass

    usb.util.claim_interface(dev, INTERFACE)

    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]
    ep_out = usb.util.find_descriptoOBOBr(
        intf,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
    )
    if ep_out is None:
        raise ValueError("No OUT endpoint found on USB device.")

    ep_out.write(raw_data, timeout=PRINT_TIMEOUT * 1000)  # pyusb timeout in ms
    print("✅ Data sent to USB printer.")

    usb.util.release_interface(dev, INTERFACE)
    usb.util.dispose_resources(dev)


def get_invoice_data(invoice_number: str, print_invoice_type: int):
    """Request invoice ESC/POS data from API."""
    url = f"{SERVER_ADDR}/api/v1/print/invoice"
    headers = {
        "accept": "application/json",
        "VATID": VATID,
        "Authorization": AUTHORIZATION,
        "debug": "false",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "invoice",
        "printer_type": 2,
        "print_invoice_type": print_invoice_type,
        "invoice_number": invoice_number
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "data" in data and "base64_data" in data["data"]:
        return data["data"]["base64_data"]
    else:
        raise ValueError("No base64_data found in API response")


def process_latest_invoice():
    """Find the newest invoice file, print it, then delete it (even if print fails)."""
    folder_path = Path(PRINT_FOLDER)
    if not folder_path.exists():
        print(f"❌ Print folder not found: {PRINT_FOLDER}")
        return

    files = sorted(folder_path.glob("*.xml"), key=lambda f: f.stat().st_ctime, reverse=True)

    if not files:
        print("ℹ No invoice files found.")
        return

    latest_file = files[0]
    try:
        parts = latest_file.stem.split("-")
        if len(parts) != 2:
            print(f"⚠ Skipping invalid file format: {latest_file.name}")
            return

        invoice_number = parts[0]
        print_invoice_type = int(parts[1])

        print(f"🖨 Printing {invoice_number} (type {print_invoice_type})...")

        base64_data = get_invoice_data(invoice_number, print_invoice_type)

        # Choose printing mode
        if USB_VENDOR_ID and USB_PRODUCT_ID:
            try:
                print_to_usb_printer(base64_data)
            except Exception as e_usb:
                print(f"❌ USB printing failed: {e_usb}")
                print("🔄 Falling back to IP printer...")
                print_to_printer(base64_data)
        else:
            print_to_printer(base64_data)

    except Exception as e:
        print(f"❌ Error processing {latest_file.name}: {e}")

    finally:
        try:
            latest_file.unlink()
            print(f"🗑 Deleted {latest_file.name}")
        except Exception as del_err:
            print(f"⚠ Failed to delete file: {del_err}")


if __name__ == "__main__":
    process_latest_invoice()

