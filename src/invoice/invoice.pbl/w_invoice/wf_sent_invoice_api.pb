// as_url
// as_payload
// as_api_key
// as_vatid

OLEObject ole_http
Integer li_rc
String ls_url, ls_payload, ls_response, ls_error_message
Integer li_status

// Basic variables
String ls_base_url, ls_create_uri, ls_search_uri, ls_cancel_uri, ls_search_by_period_uri
String ls_payload_create_general, ls_payload_create_carrier, ls_payload_create_vat
String ls_payload_search_general, ls_payload_search_period, ls_payload_cancel_general
String ls_api_key, ls_vat_id

// Default values
ls_error_message = ""

// Base URI
ls_base_url = "http://34.80.35.26:35206"
ls_create_uri = "/api/v1/create/invoice" // 創建發票
ls_search_uri = "/api/v1/get/invoices" // 查詢發票
ls_cancel_uri = "/api/v1/create/invoice" // 作廢發票
ls_search_by_period_uri = "/api/v1/get/invoice/period" // 查詢發票列表/發票的主檔資料

// Example payload
// - Create Invoice
ls_payload_create_general = '{"BuyerIdentifier":"28080623","BuyerName":"光貿科技有限公司","BuyerAddress":"","BuyerTelephoneNumber":"","BuyerEmailAddress":"","MainRemark":"","CarrierType":"","CarrierId1":"","CarrierId2":"","NPOBAN":"","ProductItem":[{"Description":"測試商品1","Quantity":"1","UnitPrice":"170","Amount":"170","Remark":"","TaxType":"1"}],"SalesAmount":"162","FreeTaxSalesAmount":"0","ZeroTaxSalesAmount":"0","TaxType":"1","TaxRate":"0.05","TaxAmount":"8","TotalAmount":"170"}'
ls_payload_create_carrier = '{"BuyerIdentifier":"0000000000","BuyerName":"客人","BuyerAddress":"","BuyerTelephoneNumber":"","BuyerEmailAddress":"","MainRemark":"","CarrierType":"3J0002","CarrierId1":"/TRM+O+P","CarrierId2":"/TRM+O+P","NPOBAN":"","ProductItem":[{"Description":"測試商品1","Quantity":"1","UnitPrice":"170","Amount":"170","Remark":"","TaxType":"1"}],"SalesAmount":"170","FreeTaxSalesAmount":"0","ZeroTaxSalesAmount":"0","TaxType":"1","TaxRate":"0.05","TaxAmount":"0","TotalAmount":"170"}'
ls_payload_create_vat     = '{"BuyerIdentifier":"28080623","BuyerName":"光貿科技有限公司","BuyerAddress":"","BuyerTelephoneNumber":"","BuyerEmailAddress":"","MainRemark":"","CarrierType":"","CarrierId1":"","CarrierId2":"","NPOBAN":"","ProductItem":[{"Description":"測試商品1","Quantity":"1","UnitPrice":"170","Amount":"170","Remark":"","TaxType":"1"}],"SalesAmount":"162","FreeTaxSalesAmount":"0","ZeroTaxSalesAmount":"0","TaxType":"1","TaxRate":"0.05","TaxAmount":"8","TotalAmount":"170"}'
// - Search Invoice
ls_payload_search_general = '[{"InvoiceNumber": "ABC12345"}]'
ls_payload_search_period  = '{"date_select": 1,"date_start": 20230101,"date_end": 20230228,"limit": 20,"page": 1}'
// cancel invoice
ls_payload_cancel_general = '[{"InvoiceNumber": "ABC12345"}]'

// System variables
ls_api_key = "sHeq7t8G1wiQvhAuIM27"
ls_vat_id = "12345678"

// Program start
ls_url = ls_base_url + ls_create_uri
ls_payload = ls_payload_create_general

ole_http = CREATE OLEObject
li_rc = ole_http.ConnectToNewObject("MSXML2.XMLHTTP")

IF li_rc <> 0 THEN
    MessageBox("Error", "Failed to create XMLHTTP object.")
    RETURN
END IF

TRY
    ole_http.Open("POST", as_url, FALSE)
    ole_http.setRequestHeader("Content-Type", "application/json")
    ole_http.setRequestHeader("Authorization", as_api_key)
    ole_http.setRequestHeader("VATID", as_vatid)
    
    ole_http.Send(as_payload)

    li_status = ole_http.Status
    IF li_status = 200 THEN
        ls_response = ole_http.ResponseText
        IF Len(Trim(ls_response)) > 0 THEN
            // MessageBox("Success", ls_response)
        ELSE
            // MessageBox("No Response", "Server returned status 200 but no body.")
            ls_error_message = "Server returned status 200 but no body."
        END IF
    ELSE
        // MessageBox("HTTP Error", "Status: " + String(li_status))
        ls_error_message = "HTTP Error: Status " + String(li_status) + " - " + ole_http.statusText
    END IF

CATCH (OLERuntimeError ole_err)
    // MessageBox("OLE Error", ole_err.Description)
    ls_error_message = "OLE Error: " + ole_err.Description

FINALLY
    DESTROY ole_http
END TRY

// If there no error message, return response
IF ls_error_message <> "" THEN
    return ls_error_message
ELSE
    return ls_response
END IF