# invoice/search.py

import time
from typing import List
from urllib.parse import urljoin
from invoice.utils import create_package, send_request
from invoice.utils import InvoiceNumberItem
from invoice.constants import INVOICE_API_BASE_URL, CANCEL_INVOICE_URI

def cancel_invoices(
    invoice_numbers: List[InvoiceNumberItem] = [],
    api_key: str = None,
    vatid: str = None
):
    timestamp = int(time.time())
    # check invoice_numberse at least one item
    if not invoice_numbers:
        raise ValueError("At least one invoice number is required for search.")
    if len(invoice_numbers) == 0:
        raise ValueError("invoice_numbers cannot be empty.")
    url = urljoin(INVOICE_API_BASE_URL, CANCEL_INVOICE_URI)
    package = create_package(timestamp, invoice_numbers, api_key, vatid)

    return send_request(url, package)
