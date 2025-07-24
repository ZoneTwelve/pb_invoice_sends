# invoice/constants.py

import os

# Define constants
INVOICE_WEBSITE_BASE_URL = "https://invoice.amego.tw"
INVOICE_API_BASE_URL = "https://invoice-api.amego.tw"
INVOICE_API_TEST_ACCOUNT = "test@amego.tw"
INVOICE_API_TEST_PASSWD = "12345678"
INVOICE_API_TEST_TAX_ID = "12345678"
INVOICE_API_TEST_COMPANY_NAME = "測試環境有限公司"
INVOICE_API_TEST_KEY = "sHeq7t8G1wiQvhAuIM27"

# API endpoints
CREATE_INVOICE_URI = "/json/f0401"
DELETE_INVOICE_URI = "/json/f0501"
STATUS_INVOICE_URI = "/json/invoice_status"
SEARCH_INVOICE_URI = "/json/invoice_query"
SEARCH_INVOICE_LIST_URI = "/json/invoice_list"
GET_INVOICE_FILE_URI = "/json/invoice_file"
GET_INVOICE_PRINT_URI = "/json/invoice_print"

# Flattened environment variable declarations
INVOICE_API_ACCOUNT = os.getenv("INVOICE_API_ACCOUNT", INVOICE_API_TEST_ACCOUNT)
INVOICE_API_PASSWD = os.getenv("INVOICE_API_PASSWD", INVOICE_API_TEST_PASSWD)
INVOICE_API_TAX_ID = os.getenv("INVOICE_API_TAX_ID", INVOICE_API_TEST_TAX_ID)
INVOICE_API_COMPANY_NAME = os.getenv("INVOICE_API_COMPANY_NAME", INVOICE_API_TEST_COMPANY_NAME)
INVOICE_API_KEY = os.getenv("INVOICE_API_KEY", INVOICE_API_TEST_KEY)

# Define __all__ for module exports
__all__ = [
    "INVOICE_API_BASE_URL",
    "CREATE_INVOICE_URI",
    "DELETE_INVOICE_URI",
    "STATUS_INVOICE_URI",
    "SEARCH_INVOICE_URI",
    "SEARCH_INVOICE_LIST_URI",
    "GET_INVOICE_FILE_URI",
    "GET_INVOICE_PRINT_URI",
    "INVOICE_API_ACCOUNT",
    "INVOICE_API_PASSWD",
    "INVOICE_API_TAX_ID",
    "INVOICE_API_COMPANY_NAME",
]

# Conditionally add test constants to __all__ if DEBUG is True
if os.getenv("DEBUG", "false").lower() == "true":
    __all__.extend([
        "INVOICE_API_TEST_ACCOUNT",
        "INVOICE_API_TEST_PASSWD",
        "INVOICE_API_TEST_TAX_ID",
        "INVOICE_API_TEST_COMPANY_NAME",
        "INVOICE_API_TEST_KEY",
    ])
