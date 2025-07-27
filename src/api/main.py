# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, condecimal, Field
from typing import Optional, List, Annotated
from fastapi import APIRouter, Body, Query, Header

from invoice.create import create_invoice_online, create_full_invoice
from invoice.search import get_invoice_status
from invoice.cancel import cancel_invoices

app = FastAPI(title="發票開立 API")

from invoice.api_requests import (
    CreateInvoiceRequest,
    QueryInvoicesRequest,
    CancelInvoicesRequest,
)

router = APIRouter(prefix="/api/v1")
    
@router.post("/get/invoices", summary="Search invoices")
def get_inovices_request(
    req: QueryInvoicesRequest,
    authorization: Annotated[str, Header(alias="Authorization")] = None,
    vatid: Annotated[str, Header(alias="VATID")] = None,
):
    # convert req to JSON
    invoice_numbers_json = [item.dict() for item in req]
    response = get_invoice_status(invoice_numbers_json)
    if "error" in response:
        raise HTTPException(status_code=response.get("status_code", 500), detail=response["error"])
    return response

@router.post("/cancel/invoices", summary="Cancel multiple invoices")
def cancel_invoices_request(
    req: CancelInvoicesRequest,
    authorization: Annotated[str, Header(alias="Authorization")] = None,
    vatid: Annotated[str, Header(alias="VATID")] = None,
):
    # convert req to JSON
    cancel_invoice_numbers_json = [item.dict() for item in req]
    response = cancel_invoices(cancel_invoice_numbers_json)
    if "error" in response:
        raise HTTPException(status_code=response.get("status_code", 500), detail=response["error"])
    return response
    

@router.post("/create/invoice", summary="開立發票")
def create_invoice_request(
    req: CreateInvoiceRequest = Body(...),
    authorization: Annotated[str, Header(alias="Authorization")] = None,
    vatid: Annotated[str, Header(alias="VATID")] = None,
):
    # convert req to JSON
    invoice_data = req.dict()
    response = create_full_invoice(invoice_data, authorization, vatid)
    if "error" in response:
        raise HTTPException(status_code=response.get("status_code", 500), detail=response["error"])
    return response

app.include_router(router)