# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, condecimal, Field
from typing import Optional
import requests
import urllib.parse
import json

from invoice import build_invoice_payload

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

