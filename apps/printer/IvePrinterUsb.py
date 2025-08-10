import os
import base64
import requests
import usb.core
import usb.util
from dotenv import load_dotenv
from pathlib import Path

# -------------------------
# Configuration
# -------------------------
VENDOR_ID = 0x1FC9   # From your USB device
PRODUCT_ID = 0x2016  # From your USB device
INTERFACE = 0        # Usually 0
PRINT_TIMEOUT = 5000  # in milliseconds

# Load environment variables
load_dotenv("IveConfig.txt")

SERVER_ADDR = os.getenv("SERVER_ADDR")
VATID = os.getenv("VATID")
AUTHORIZATION = os.getenv("Authorization")
PRINT_FOLDER = os.getenv("PRINT_FOLDER", r"C:\BDPOS7\Invoice")


# -------------------------
# USB Printing Function
# -------------------------
def print_to_usb_printer(base64_data: str):
    raw_data = base64.b64decode(base64_data)

    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise ValueError("USB printer not found.")

    # Safely try to detach kernel driver if supported
    try:
        if dev.is_kernel_driver_active(INTERFACE):
            dev.detach_kernel_driver(INTERFACE)
    except NotImplementedError:
        pass  # Windows does not support this, ignore safely

    usb.util.claim_interface(dev, INTERFACE)

    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]
    ep_out = usb.util.find_descriptor(
        intf,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
    )
    if ep_out is None:
        raise ValueError("No OUT endpoint found on USB device.")

    ep_out.write(raw_data, timeout=PRINT_TIMEOUT)
    print("✅ Data sent to USB printer.")

    usb.util.release_interface(dev, INTERFACE)
    usb.util.dispose_resources(dev)

# -------------------------
# API Data Fetch Function
# -------------------------
def get_invoice_data(invoice_number: str, print_invoice_type: int):
    """Fetch invoice ESC/POS data from the API."""
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


# -------------------------
# Main Processing Function
# -------------------------
def process_latest_invoice():
    """Find the newest invoice file, print it via USB, then delete it."""
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

        invoice_number, print_invoice_type = parts[0], int(parts[1])
        print(f"🖨 Printing {invoice_number} (type {print_invoice_type}) to USB printer...")

        base64_data = get_invoice_data(invoice_number, print_invoice_type)
        print_to_usb_printer(base64_data)

    except Exception as e:
        print(f"❌ Error processing {latest_file.name}: {e}")

    finally:
        try:
            latest_file.unlink()
            print(f"🗑 Deleted {latest_file.name}")
        except Exception as del_err:
            print(f"⚠ Failed to delete file: {del_err}")


# -------------------------
# Run the script
# -------------------------
if __name__ == "__main__":
    process_latest_invoice()
