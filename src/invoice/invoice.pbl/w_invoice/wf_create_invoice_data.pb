string ls_invoice_data, ls_invoice_payload
string PBLR, SYSLR

SYSLR = "\n"
PBLR = '~n'

ls_invoice_data = '{' + SYSLR + &
'"OrderId": "A20200817105934",' + SYSLR + &
'"BuyerIdentifier": "28080623",' + SYSLR + &
'"BuyerName": "\u5149\u8cbf\u79d1\u6280\u6709\u9650\u516c\u53f8",' + SYSLR + &
'"NPOBAN": "",' + SYSLR + &
'"ProductItem": [' + SYSLR + &
'{' + SYSLR + &
'"Description": "\u6e2c\u8a66\u5546\u54c11",' + SYSLR + &
'"Quantity": "1",' + SYSLR + &
'"UnitPrice": "170",' + SYSLR + &
'"Amount": "170",' + SYSLR + &
'"Remark": "",' + SYSLR + &
'"TaxType": "1"' + SYSLR + &
'},' + SYSLR + &
'{' + SYSLR + &
'"Description": "\u6703\u54e1\u6298\u62b5",' + SYSLR + &
'"Quantity": "1",' + SYSLR + &
'"UnitPrice": "-2",' + SYSLR + &
'"Amount": "-2",' + SYSLR + &
'"Remark": "",' + SYSLR + &
'"TaxType": "1"' + SYSLR + &
'}' + SYSLR + &
'],' + SYSLR + &
'"SalesAmount": "160",' + SYSLR + &
'"FreeTaxSalesAmount": "0",' + SYSLR + &
'"ZeroTaxSalesAmount": "0",' + SYSLR + &
'"TaxType": "1",' + SYSLR + &
'"TaxRate": "0.05",' + SYSLR + &
'"TaxAmount": "8",' + SYSLR + &
'"TotalAmount": "168"' + SYSLR + &
'}'

ls_invoice_payload = '{' + PBLR + &
  '"invoice": "12345678",' + PBLR + &
  '"data": "' + ls_invoice_data + '",' + PBLR + &
  '"time": 1752991187,' + PBLR + &
  '"sign": "' + this.wf_md5(ls_invoice_data) + '"' + PBLR + &
'}'

return ls_invoice_payload
