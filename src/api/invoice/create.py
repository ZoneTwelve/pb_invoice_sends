# invoice/create.py

import time
import uuid

from invoice.utils import create_package, send_request
from invoice.constants import INVOICE_API_BASE_URL, CREATE_INVOICE_URI
from urllib.parse import urljoin

def create_invoice_online(
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
    timestamp = int(time.time())
    order_id = f"ORDER{timestamp}{uuid.uuid4().hex[:4]}"
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
                "Quantity": str(quantity),
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

    url = urljoin(INVOICE_API_BASE_URL, CREATE_INVOICE_URI)
    package = create_package(timestamp, invoice_data)

    return send_request(url, package)
