import os
import sys
import socket
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.txt")

SERVER_ADDR = os.getenv("SERVER_ADDR")
VATID = os.getenv("VATID")
AUTHORIZATION = os.getenv("Authorization")
PRINTER_IP = os.getenv("PRINTER_IP", "192.168.1.147")
PRINTER_PORT = int(os.getenv("PRINTER_PORT", "9100"))

def print_to_printer(base64_data: str):
    """Decode base64 ESC/POS data and send to printer via TCP."""
    raw_bytes = base64.b64decode(base64_data)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((PRINTER_IP, PRINTER_PORT))
        s.sendall(raw_bytes)
    print("✅ Print command sent successfully.")

def get_invoice_data(invoice_number: str):
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
        "print_invoice_type": 1,
        "invoice_number": invoice_number
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    if "data" in data and "base64_data" in data["data"]:
        return data["data"]["base64_data"]
    else:
        raise ValueError("No base64_data found in API response")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Usage: invoice_print.exe <invoice_number>")
        sys.exit(1)

    invoice_number = sys.argv[1]

    try:
        base64_data = get_invoice_data(invoice_number)
        print(base64_data)
        #print_to_printer(base64_data)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

