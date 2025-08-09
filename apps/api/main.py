# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, condecimal, Field
from typing import Optional, List, Annotated
from fastapi import APIRouter, Body, Query, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler

from invoice.create import create_full_invoice
from invoice.search import get_invoice_status, get_invoice_status_by_period
from invoice.cancel import cancel_invoices
from invoice.constants import INVOICE_API_TEST_KEY, INVOICE_API_TAX_ID


from invoice.api_requests import (
    CreateInvoiceRequest,
    QueryInvoicesRequest,
    CancelInvoicesRequest,
    InvoiceByPeriodRequest,
)

app = FastAPI(title="發票開立 API")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

router = APIRouter(prefix="/api/v1")

@router.post("/create/invoice", summary="開立發票")
def create_invoice_request(
    authorization: Annotated[str, Header(alias="Authorization")],
    vatid: Annotated[str, Header(alias="VATID")],
    debug: Annotated[str, Header(alias='debug')] = 'false',
    req: CreateInvoiceRequest = Body(...),
):
    # convert req to JSON
    invoice_data = req.dict()
    response = create_full_invoice(invoice_data, authorization, vatid)
    if "invoice_number" not in response or "error" in response:
        return "1" if debug == 'false' else response
    return response["invoice_number"]



@router.post("/get/invoices", summary="Search invoices")
def get_inovices_request(
    req: QueryInvoicesRequest,
    authorization: Annotated[str, Header(alias="Authorization")],
    vatid: Annotated[str, Header(alias="VATID")],
    debug: Annotated[str, Header(alias='debug')] = 'false',
):
    # convert req to JSON
    invoice_numbers_json = [item.dict() for item in req]
    response = get_invoice_status(invoice_numbers_json, authorization, vatid)
    if "error" in response:
        # raise HTTPException(status_code=response.get("status_code", 500), detail=response["error"])
        # http status code 500 and return error data string "1"
        # set status code to 500
        return "1"
    # preprocess into a "$date,$time,$invoice_id,$vat_id,$amount,$state,$carrier_id。$date,$time,$invoice_id,$vat_id,$amount,$state,$carrier_id" format
    # csv headless foramt but replace \n with '。'
    return response

@router.post("/cancel/invoices", summary="Cancel multiple invoices")
def cancel_invoices_request(
    req: CancelInvoicesRequest,
    authorization: Annotated[str, Header(alias="Authorization")],
    vatid: Annotated[str, Header(alias="VATID")],
    debug: Annotated[str, Header(alias='debug')] = 'false',
):
    # convert req to JSON
    cancel_invoice_numbers_json = [item.dict() for item in req]
    response = cancel_invoices(cancel_invoice_numbers_json, authorization, vatid)
    if "error" in response:
        raise HTTPException(status_code=response.get("status_code", 500), detail=response["error"])
    return response

@router.post("/get/invoice/period", summary="發票列表/發票的主檔資料")
def get_invoice_by_period_request(
    authorization: Annotated[str, Header(alias="Authorization")],
    vatid: Annotated[str, Header(alias="VATID")],
    req: InvoiceByPeriodRequest = Body(...),
    debug: Annotated[str, Header(alias='debug')] = 'false',
):
    # convert req to JSON
    invoice_data = req.dict()
    response = get_invoice_status_by_period(invoice_data, authorization, vatid)
    if "error" in response:
        # raise HTTPException(status_code=response.get("status_code", 500), detail=response["error"])
        print(response)
        return "1"
    if "data" not in response:
        print(response)
        return "2"
    ret_data = []
    for item in response["data"]:
        ret_data.append(
            f"{item['invoice_date']},{item['invoice_time']},{item['invoice_number']},{item['buyer_identifier']},{item['total_amount']},{item['invoice_type']},{item['invoice_status']},{item['carrier_id1']}"
        )
    return "。".join(ret_data)
    # return response
    
app.include_router(router)