# invoice/search.py

import time
from typing import List
from urllib.parse import urljoin
from invoice.utils import create_package, send_request
from invoice.utils import InvoiceNumberItem
from invoice.constants import INVOICE_API_BASE_URL, STATUS_INVOICE_URI, SEARCH_INVOICE_LIST_URI

from invoice.utils import InvoiceNumberByPeriod

def get_invoice_status(
    invoice_numbers: List[InvoiceNumberItem] = []
):
    timestamp = int(time.time())
    # check invoice_numberse at least one item
    if not invoice_numbers:
        raise ValueError("At least one invoice number is required for search.")
    if len(invoice_numbers) == 0:
        raise ValueError("invoice_numbers cannot be empty.")
    url = urljoin(INVOICE_API_BASE_URL, STATUS_INVOICE_URI)
    package = create_package(timestamp, invoice_numbers)

    return send_request(url, package)

def get_invoice_status_by_period(
        data: InvoiceNumberByPeriod
):
    timestamp = int(time.time())
    url = urljoin(INVOICE_API_BASE_URL, SEARCH_INVOICE_LIST_URI)
    package = create_package(timestamp, data)

    return send_request(url, package)