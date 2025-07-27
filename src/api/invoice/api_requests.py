from pydantic import BaseModel, condecimal, Field
from typing import Optional, List


from invoice.utils import (
    InvoiceNumberItem,
    CancelInvoiceNumber,
    TheProductItem,
    InvoiceNumberByPeriod,
)

class CreateInvoiceRequestLegacy(BaseModel):
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

class CreateInvoiceRequest(BaseModel):
    OrderId: str = Field(..., description="訂單編號")
    BuyerIdentifier: Optional[str] = Field(default="0000000000", description="買方統一編號")
    BuyerName: Optional[str] = Field(default="客人", description="買方名稱")
    BuyerAddress: Optional[str] = Field(default="", description="買方地址")
    BuyerTelephoneNumber: Optional[str] = Field(default="", description="買方電話")
    BuyerEmailAddress: Optional[str] = Field(default="", description="買方電子信箱")
    MainRemark: Optional[str] = Field(default="", description="主要備註")
    CarrierType: Optional[str] = Field(default="", description="載具類別")
    CarrierId1: Optional[str] = Field(default="", description="載具編號1")
    CarrierId2: Optional[str] = Field(default="", description="載具編號2")
    NPOBAN: Optional[str] = Field(default="", description="捐贈碼")
    ProductItem: List[TheProductItem] = Field(..., description="商品明細列表")
    SalesAmount: str = Field(..., description="應稅銷售額")
    FreeTaxSalesAmount: str = Field(..., description="免稅銷售額")
    ZeroTaxSalesAmount: str = Field(..., description="零稅率銷售額")
    TaxType: str = Field(..., description="課稅別")
    TaxRate: str = Field(..., description="稅率")
    TaxAmount: str = Field(..., description="稅額")
    TotalAmount: str = Field(..., description="總計金額")

class InvoiceByPeriodRequest(BaseModel):
    date_select: int = Field(default=1, description="日期條件 1:發票日期 2:建立日期")
    date_start: int = Field(default=20230101, description="開始日期，格式：YYYYMMDD，例如：20240901")
    date_end: int = Field(default=20230228, description="結束日期，格式：YYYYMMDD，例如：20241031")
    limit: int = Field(default=20, ge=1, le=500, description="每頁顯示資料筆數 20~500，預設 20 筆")
    page: int = Field(default=1, ge=1, description="目前頁數，預設第1頁")


QueryInvoicesRequest = List[InvoiceNumberItem]
CancelInvoicesRequest = List[CancelInvoiceNumber]
# InvoiceByPeriodRequest = InvoiceNumberByPeriod