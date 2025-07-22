from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import os
import posixpath
import logging
from colorlog import ColoredFormatter

# Configure logging with colored output
logger = logging.getLogger("invoice_utils")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)s: %(message)s%(reset)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "red",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    }
)
handler.setFormatter(formatter)
logger.addHandler(handler)

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

def check_environment():
    """
    Check if the required environment variables for the invoice API are set.
    Raises ValueError if any required variables are not set or use test values in non-debug mode.
    """
    from invoice.constants import (
        INVOICE_API_KEY, INVOICE_API_TEST_KEY,
        INVOICE_API_ACCOUNT, INVOICE_API_TEST_ACCOUNT,
        INVOICE_API_PASSWD, INVOICE_API_TEST_PASSWD,
        INVOICE_API_TAX_ID, INVOICE_API_TEST_TAX_ID,
        INVOICE_API_COMPANY_NAME, INVOICE_API_TEST_COMPANY_NAME
    )

    # Check if debug mode is enabled
    if os.getenv("DEBUG", "false").lower() == "true":
        # In debug mode, warn if test values are used
        if (INVOICE_API_KEY == INVOICE_API_TEST_KEY or
            INVOICE_API_ACCOUNT == INVOICE_API_TEST_ACCOUNT or
            INVOICE_API_PASSWD == INVOICE_API_TEST_PASSWD or
            INVOICE_API_TAX_ID == INVOICE_API_TEST_TAX_ID or
            INVOICE_API_COMPANY_NAME == INVOICE_API_TEST_COMPANY_NAME):
            logger.warning("Using test values for invoice API in debug mode.")
    else:
        # In non-debug mode, ensure no test values are used
        errors = []
        if not INVOICE_API_KEY or INVOICE_API_KEY == INVOICE_API_TEST_KEY:
            errors.append("INVOICE_API_KEY is not set or is using the test key")
        if not INVOICE_API_ACCOUNT or INVOICE_API_ACCOUNT == INVOICE_API_TEST_ACCOUNT:
            errors.append("INVOICE_API_ACCOUNT is not set or is using the test account")
        if not INVOICE_API_PASSWD or INVOICE_API_PASSWD == INVOICE_API_TEST_PASSWD:
            errors.append("INVOICE_API_PASSWD is not set or is using the test password")
        if not INVOICE_API_TAX_ID or INVOICE_API_TAX_ID == INVOICE_API_TEST_TAX_ID:
            errors.append("INVOICE_API_TAX_ID is not set or is using the test tax ID")
        if not INVOICE_API_COMPANY_NAME or INVOICE_API_COMPANY_NAME == INVOICE_API_TEST_COMPANY_NAME:
            errors.append("INVOICE_API_COMPANY_NAME is not set or is using the test company name")
        
        if errors:
            logger.warning("The application may not function correctly due to invalid environment variables: %s", "; ".join(errors))
            raise ValueError("Invalid environment variables: " + "; ".join(errors))
    
    logger.info("Environment variables for invoice API are set correctly.")
    return True