# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, condecimal, Field
from typing import Optional, List
from fastapi import APIRouter, Body, Query

from invoice.create import create_invoice_online
from invoice.search import get_invoice_status
from invoice.cancel import cancel_invoices

from invoice.utils import (
    InvoiceNumberItem,
    CancelInvoiceNumber
)

app = FastAPI(title="發票開立 API")

class CreateInvoiceRequest(BaseModel):
    price: condecimal(ge=0) = Field(..., description="商品價格（含稅）")

    buyer_identifier: Optional[str] = Field(default="0000000000", description="統一編號（預設為無統編）")
    buyer_name: Optional[str] = Field(default="消費者", description="買方名稱（預設為消費者）")
    description: Optional[str] = Field(default="餐費", description="商品描述")
    quantity: Optional[str] = Field(default="1", description="商品數量")
    unit: Optional[str] = Field(default="份", description="商品單位")
    remark: Optional[str] = Field(default="", description="商品備註")
    tax_type: Optional[str] = Field(default="1", description="課稅別（1:應稅）")
    number_only: Optional[bool] = Field(default=False, description="是否只回傳發票號碼")

class SearchInvoiceRequest(BaseModel):
    date_select: int = Field(default=1, description="日期選擇方式")
    date_start: int = Field(default=20230101, description="開始日期")
    date_end: int = Field(default=20230228, description="結束日期")
    limit: int = Field(default=20, ge=1, le=100, description="每頁顯示數量（預設20，最大100）")
    page: int = Field(default=1, ge=1, description="頁碼（預設1）")

class SearchInvoiceListResponse(BaseModel):
    invoices: List[dict] = Field(..., description="發票列表")
    total: int = Field(..., description="總發票數量")

class QueryInvoiceRequest(BaseModel):
    type: str = Field(..., description="查詢類型 ('order' 或 'invoice')")
    order_id: Optional[str] = Field(default=None, max_length=40, description="訂單編號 (type='order' 時必填，最大40字)")
    invoice_number: Optional[str] = Field(default=None, max_length=10, description="發票號碼 (type='invoice' 時必填，最大10字)" )

class CancelInvoiceRequest(BaseModel):
    cancel_invoice_number: str = Field(..., max_length=10, description="要作廢的發票號碼")

class CancelMultipleInvoicesRequest(BaseModel):
    cancel_invoice_numbers: List[str] = Field(..., min_items=1, description="要作廢的發票號碼列表")

QueryInvoicesRequest = List[InvoiceNumberItem]
CancelInvoicesRequest = List[CancelInvoiceNumber]


router = APIRouter(prefix="/api/v1")

@router.get("/invoices", summary="Get invoice(s) by query")
def get_invoices():
    pass
    
@router.post("/get/invoices", summary="Search invoices")
def get_invoices_details(req: QueryInvoicesRequest):
    # convert req to JSON
    invoice_numbers_json = [item.dict() for item in req]
    response = get_invoice_status(invoice_numbers_json)
    if "error" in response:
        raise HTTPException(status_code=response.get("status_code", 500), detail=response["error"])
    return response

@router.post("/cancel/invoices", summary="Cancel multiple invoices")
def cancel_invoices_data(req: CancelInvoicesRequest):
    # convert req to JSON
    cancel_invoice_numbers_json = [item.dict() for item in req]
    response = cancel_invoices(cancel_invoice_numbers_json)
    if "error" in response:
        raise HTTPException(status_code=response.get("status_code", 500), detail=response["error"])
    return response
    

@router.post("/invoice", summary="Create an invoice")
def create_invoice(req: CreateInvoiceRequest = Body(...)):
    response = create_invoice_online(
        price=req.price,
        buyer_identifier=req.buyer_identifier,
        buyer_name=req.buyer_name,
        description=req.description,
        quantity=req.quantity,
        unit=req.unit,
        remark=req.remark,
        tax_type=req.tax_type
    )

    if "error" in response:
        raise HTTPException(
            status_code=response.get("status_code", 500),
            detail=response.get("error", "Unknown error")
        )
    # if number_only is True, return only the invoice number
    if req.number_only:
        return response['invoice_number']
    else:
        return response

@router.delete("/invoice")
def cancel_invoice(req: CancelInvoiceRequest):
    pass

app.include_router(router)