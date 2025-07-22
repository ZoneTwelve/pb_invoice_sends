# invoice.py
import hashlib
import time
import json
from dotenv import load_dotenv
import os

load_dotenv()

APP_KEY = os.environ.get("APP_KEY") or "sHeq7t8G1wiQvhAuIM27"


def generate_signature(data_str, timestamp, app_key):
    """Generate MD5 signature."""
    hash_input = data_str + str(timestamp) + app_key
    return hashlib.md5(hash_input.encode("utf-8")).hexdigest()


def build_invoice_payload(
    price,
    buyer_identifier="0000000000",
    buyer_name="消費者",
    description="餐費",
    quantity="1",
    unit="份",
    remark="",
    tax_type="1",
    unit_price=None,
    amount=None,
    tax_amount="0",
    tax_rate="0.05",
):
    """
    Build invoice post_data dict and return (post_data, order_id)
    """
    timestamp = int(time.time())
    order_id = f"ORDER{timestamp}"
    unit_price = unit_price if unit_price is not None else price
    amount = amount if amount is not None else price

    invoice_data = {
        "OrderId": order_id,
        "BuyerIdentifier": buyer_identifier,
        "BuyerName": buyer_name,
        "NPOBAN": "",
        "ProductItem": [
            {
                "Description": description,
                "Quantity": quantity,
                "Unit": unit,
                "UnitPrice": str(unit_price),
                "Amount": str(amount),
                "Remark": remark,
                "TaxType": tax_type
            }
        ],
        "SalesAmount": str(price),
        "FreeTaxSalesAmount": "0",
        "ZeroTaxSalesAmount": "0",
        "TaxType": tax_type,
        "TaxRate": tax_rate,
        "TaxAmount": tax_amount,
        "TotalAmount": str(price)
    }

    data_str = json.dumps(invoice_data, indent=0)
    sign = generate_signature(data_str, timestamp, APP_KEY)

    post_data = {
        "invoice": "12345678",
        "data": data_str,
        "time": timestamp,
        "sign": sign
    }

    return post_data, order_id
