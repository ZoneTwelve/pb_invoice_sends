# invoice/create.py

import time
import uuid

from invoice.utils import create_package, send_request
from invoice.constants import INVOICE_API_BASE_URL, CREATE_INVOICE_URI
from urllib.parse import urljoin

# https://www.einvoice.nat.gov.tw/static/ptl/ein_upload/attachments/1693297176294_0.pdf
def create_full_invoice(data: dict, api_key: str = None, vatid: str = None):
    if api_key is None or vatid is None:
        msg = {
            "error": "缺少必要的標頭：請在請求標頭中包含 'Authorization' 和 'VATID'。",
            "status_code": 400,
        }
        print(msg)
        # return msg
    timestamp = int(time.time())
    order_id = f"ORDER{timestamp}{uuid.uuid4().hex[:4]}"
    # Overwrite the order id in the data
    data['OrderId'] = order_id
    
    url = urljoin(INVOICE_API_BASE_URL, CREATE_INVOICE_URI)
    package = create_package(timestamp, data)

    return send_request(url, package)

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
