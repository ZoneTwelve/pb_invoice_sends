# invoice/utils.py

import hashlib
import json
import logging
import urllib.parse
import time
import requests
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import List
from pydantic import BaseModel, Field
import posixpath

from invoice.constants import (
    INVOICE_API_BASE_URL,
    INVOICE_API_KEY,
    INVOICE_API_TAX_ID,
)

class InvoiceNumberItem(BaseModel):
    InvoiceNumber: str = Field(..., description="發票號碼")

class CancelInvoiceNumber(BaseModel):
    CancelInvoiceNumber: str = Field(..., description="要作廢的發票號碼")

def normalize_url(url):
    parsed = urlparse(url)
    
    # Lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.hostname.lower()
    if parsed.port:
        if (scheme == 'http' and parsed.port != 80) or (scheme == 'https' and parsed.port != 443):
            netloc += f":{parsed.port}"
    
    # Normalize path
    path = parsed.path or '/'
    path = posixpath.normpath(path)
    if not path.startswith('/'):
        path = '/' + path
    
    # Sort query parameters
    query = urlencode(sorted(parse_qsl(parsed.query)))
    
    return urlunparse((scheme, netloc, path, '', query, ''))

def create_package(timestamp: int, data: dict) -> str:
    # Match reference: serialize JSON with no spaces
    encoded_data = json.dumps(data, separators=(',', ':'))

    # Signature: data + timestamp + key
    raw_string = f"{encoded_data}{timestamp}{INVOICE_API_KEY}"
    sign = hashlib.md5(raw_string.encode("utf-8")).hexdigest()

    payload = {
        "invoice": INVOICE_API_TAX_ID,
        "data": encoded_data,
        "time": timestamp,
        "sign": sign,
    }

    return urllib.parse.urlencode(payload, doseq=True)

def send_request(url: str, data: str) -> dict:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "invoice-app/1.0"
    }

    try:
        proxies = {
            "http": "http://localhost:8080",
            "https": "http://localhost:8080"
        }
        response = requests.post(url, headers=headers, data=data, verify=False)
        response.raise_for_status()

        return response.json()
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {"error": "Request failed", "details": e, "status_code": response.status_code if response else 500}
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return {"error": "Invalid JSON response", "status_code": 500, "details": e}