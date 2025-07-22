# main.py
from invoice.utils import check_environment
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, condecimal, Field
from typing import Optional, List
import requests
import urllib.parse
import json

from invoice.create import build_invoice_payload
from invoice.search import get_invoice_list, query_invoice
from invoice.cancel import cancel_invoice, cancel_multiple_invoices

check_environment() # Ensure environment variables are set before starting the app
app = FastAPI(title="發票開立 API")

API_URL = "https://invoice-api.amego.tw/json/f0401"


class InvoiceRequest(BaseModel):
    price: condecimal(gt=0) = Field(..., description="商品價格（含稅）")

    # Optional fields
    buyer_identifier: Optional[str] = Field(default="0000000000", description="統一編號（預設為無統編）")
    buyer_name: Optional[str] = Field(default="消費者", description="買方名稱（預設為消費者）")
    description: Optional[str] = Field(default="餐費", description="商品描述")
    quantity: Optional[str] = Field(default="1", description="商品數量")
    unit: Optional[str] = Field(default="份", description="商品單位")
    remark: Optional[str] = Field(default="", description="商品備註")
    tax_type: Optional[str] = Field(default="1", description="課稅別（1:應稅）")

class SearchInvoiceListRequest(BaseModel):
    date_select: int = Field(default=1, description="日期選擇方式")
    date_start: int = Field(default=20230101, description="開始日期")
    date_end: int = Field(default=20230228, description="結束日期")
    limit: int = Field(default=20, ge=1, le=100, description="每頁顯示數量（預設20，最大100）")
    page: int = Field(default=1, ge=1, description="頁碼（預設1）")


class QueryInvoiceRequest(BaseModel):
    type: str = Field(..., description="查詢類型 ('order' 或 'invoice')")
    order_id: Optional[str] = Field(default=None, max_length=40, description="訂單編號 (type='order' 時必填，最大40字)")
    invoice_number: Optional[str] = Field(default=None, max_length=10, description="發票號碼 (type='invoice' 時必填，最大10字)")

class CancelInvoiceRequest(BaseModel):
    cancel_invoice_number: str = Field(..., max_length=10, description="要作廢的發票號碼")

class CancelMultipleInvoicesRequest(BaseModel):
    cancel_invoice_numbers: List[str] = Field(..., min_items=1, description="要作廢的發票號碼列表")

@app.post("/create-invoice", summary="開立發票（自動配號）")
def create_invoice(req: InvoiceRequest):
    try:
        post_data, order_id = build_invoice_payload(
            price=str(req.price),
            buyer_identifier=req.buyer_identifier,
            buyer_name=req.buyer_name,
            description=req.description,
            quantity=req.quantity,
            unit=req.unit,
            remark=req.remark,
            tax_type=req.tax_type,
        )

        encoded_payload = urllib.parse.urlencode(post_data, doseq=True)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(API_URL, headers=headers, data=encoded_payload)
        response.raise_for_status()

        try:
            result = response.json()
        except json.JSONDecodeError:
            raise HTTPException(status_code=502, detail="Invalid JSON from invoice API")

        if 'invoice_number' in result:
            return result['invoice_number']
        else:
            return {
                "order_id": order_id,
                "invoice_result": result
            }

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Invoice API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-invoice", summary="查詢發票")
def search_invoice(req: SearchInvoiceListRequest):
    try:
        result = get_invoice_list(
            date_select=req.date_select,
            date_start=req.date_start,
            date_end=req.date_end,
            limit=req.limit,
            page=req.page
        )
        return result
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Invoice API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query-invoice", summary="查詢發票內容")
def query_invoice_endpoint(req: QueryInvoiceRequest):
    try:
        result = query_invoice(
            type=req.type,
            order_id=req.order_id,
            invoice_number=req.invoice_number
        )
        return result
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Invoice API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel-single-invoice", summary="作廢單張發票")
def cancel_single_invoice(req: CancelInvoiceRequest):
    try:
        result = cancel_invoice(cancel_invoice_number=req.cancel_invoice_number)
        return result
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Invoice API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel-multiple-invoices", summary="作廢多張發票")
def cancel_multiple_invoices_endpoint(req: CancelMultipleInvoicesRequest):
    try:
        result = cancel_multiple_invoices(cancel_invoice_numbers=req.cancel_invoice_numbers)
        return result
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Invoice API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))