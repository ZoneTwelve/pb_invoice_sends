from invoice.utils import normalize_url
from invoice.constants import (
    INVOICE_API_BASE_URL,
    INVOICE_API_KEY,
    INVOICE_API_TAX_ID,
)
from urllib.parse import urlencode
import urllib.parse
import json
import requests
import time
import hashlib

def cancel_invoice(cancel_invoice_number, app_key=INVOICE_API_KEY, invoice=INVOICE_API_TAX_ID):
    """
    Cancel a single invoice using the API.
    
    Parameters:
    - cancel_invoice_number (str): Invoice number to cancel (e.g., 'AB00001111')
    - app_key (str, optional): API key (default from INVOICE_API_KEY)
    - invoice (str, optional): Tax ID (default from INVOICE_API_TAX_ID)
    
    Returns:
    - dict: JSON response from the API
    """
    # Validate input parameter
    if not cancel_invoice_number:
        return {"error": "cancel_invoice_number is required"}
    if len(cancel_invoice_number) > 10:
        return {"error": "cancel_invoice_number must not exceed 10 characters"}
    
    # API endpoint
    sUrl = normalize_url(INVOICE_API_BASE_URL, "/json/f0501")
    
    # Create invoice data array with single object
    invoice_data = [
        {
            "CancelInvoiceNumber": cancel_invoice_number
        }
    ]
    
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

def cancel_multiple_invoices(cancel_invoice_numbers, app_key=INVOICE_API_KEY, invoice=INVOICE_API_TAX_ID):
    """
    Cancel multiple invoices using the API.
    
    Parameters:
    - cancel_invoice_numbers (list): List of invoice numbers to cancel (e.g., ['AB00001111', 'AB00001112'])
    - app_key (str, optional): API key (default from INVOICE_API_KEY)
    - invoice (str, optional): Tax ID (default from INVOICE_API_TAX_ID)
    
    Returns:
    - dict: JSON response from the API
    """
    # Validate input parameter
    if not cancel_invoice_numbers or not isinstance(cancel_invoice_numbers, list):
        return {"error": "cancel_invoice_numbers must be a non-empty list"}
    for number in cancel_invoice_numbers:
        if len(number) > 10:
            return {"error": f"Invoice number {number} exceeds 10 characters"}
    
    # API endpoint
    sUrl = normalize_url(INVOICE_API_BASE_URL, "/json/f0501")
    
    # Create invoice data array with multiple objects
    invoice_data = [{"CancelInvoiceNumber": number} for number in cancel_invoice_numbers]
    
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