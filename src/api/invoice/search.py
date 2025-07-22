from invoice.utils import normalize_url
from invoice.constants import (
    INVOICE_API_BASE_URL,
    SEARCH_INVOICE_URI,
    SEARCH_INVOICE_LIST_URI,
    INVOICE_API_TAX_ID,
    INVOICE_API_KEY
)
from urllib.parse import urlencode
import urllib.parse
import json
import requests
import time
import hashlib

def get_invoice_list(date_select, date_start, date_end, limit=20, page=1, app_key=INVOICE_API_KEY, invoice=INVOICE_API_TAX_ID):
    """
    Fetch invoice list from the API with specified parameters.
    
    Parameters:
    - date_select (int): Date condition (1: Invoice Date, 2: Creation Date)
    - date_start (str): Start date in YYYYMMDD format (e.g., '20230101')
    - date_end (str): End date in YYYYMMDD format (e.g., '20230228')
    - limit (int, optional): Number of records per page (20-500, default 20)
    - page (int, optional): Current page number (default 1)
    - app_key (str, optional): API key (default from INVOICE_API_KEY)
    - invoice (str, optional): Tax ID (default from INVOICE_API_TAX_ID)
    
    Returns:
    - dict: JSON response from the API
    """
    # API endpoint
    sUrl = normalize_url(f"{INVOICE_API_BASE_URL}/{SEARCH_INVOICE_LIST_URI}")
    
    # Create invoice data dictionary
    invoice_data = {
        "date_select": date_select,
        "date_start": date_start,
        "date_end": date_end,
        "limit": limit,
        "page": page
    }
    
    # Convert data to JSON string
    sApi_Data = json.dumps(invoice_data, separators=(',', ':'))
    
    # Get current Unix timestamp (10 digits, no milliseconds)
    nCurrent_Now_Time = int(time.time())
    
    # Create MD5 hash for sign
    sHash_Text = sApi_Data + str(nCurrent_Now_Time) + app_key
    m = hashlib.md5()
    m.update(sHash_Text.encode("utf-8"))
    sSign = m.hexdigest()
    
    # Prepare POST data
    aPost_Data = {
        "invoice": invoice,
        "data": sApi_Data,
        "time": nCurrent_Now_Time,
        "sign": sSign,
    }
    
    # URL encode the POST data
    payload = urllib.parse.urlencode(aPost_Data, doseq=True)
    
    # Set headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Make the POST request
    try:
        response = requests.post(sUrl, headers=headers, data=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        return json.loads(response.text)
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {str(e)}"}

def query_invoice(type, order_id=None, invoice_number=None, app_key=INVOICE_API_KEY, invoice=INVOICE_API_TAX_ID):
    """
    Query invoice details from the API using order ID or invoice number.
    
    Parameters:
    - type (str): Query type ('order' for order ID, 'invoice' for invoice number)
    - order_id (str, optional): Order ID (max 40 characters, within 180 days)
    - invoice_number (str, optional): Invoice number (max 10 characters, within 180 days)
    - app_key (str, optional): API key (default from INVOICE_API_KEY)
    - invoice (str, optional): Tax ID (default from INVOICE_API_TAX_ID)
    
    Returns:
    - dict: JSON response from the API
    """
    # Validate input parameters
    if type not in ["order", "invoice"]:
        return {"error": "Invalid type. Must be 'order' or 'invoice'"}
    if type == "order" and (not order_id or len(order_id) > 40):
        return {"error": "order_id is required for type 'order' and must not exceed 40 characters"}
    if type == "invoice" and (not invoice_number or len(invoice_number) > 10):
        return {"error": "invoice_number is required for type 'invoice' and must not exceed 10 characters"}
    
    # API endpoint
    sUrl = normalize_url(f"{INVOICE_API_BASE_URL}/{SEARCH_INVOICE_LIST_URI}")
    
    # Create invoice data dictionary
    invoice_data = {"type": type}
    if type == "order":
        invoice_data["order_id"] = order_id
    else:
        invoice_data["invoice_number"] = invoice_number
    
    # Convert data to JSON string
    sApi_Data = json.dumps(invoice_data, separators=(',', ':'))
    
    # Get current Unix timestamp (10 digits, no milliseconds)
    nCurrent_Now_Time = int(time.time())
    
    # Create MD5 hash for sign
    sHash_Text = sApi_Data + str(nCurrent_Now_Time) + app_key
    m = hashlib.md5()
    m.update(sHash_Text.encode("utf-8"))
    sSign = m.hexdigest()
    
    # Prepare POST data
    aPost_Data = {
        "invoice": invoice,
        "data": sApi_Data,
        "time": nCurrent_Now_Time,
        "sign": sSign,
    }
    
    # URL encode the POST data
    payload = urllib.parse.urlencode(aPost_Data, doseq=True)
    
    # Set headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Make the POST request
    try:
        response = requests.post(sUrl, headers=headers, data=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        return json.loads(response.text)
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {str(e)}"}