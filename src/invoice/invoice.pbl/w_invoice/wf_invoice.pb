OLEObject ole_http
Integer li_rc
String ls_url, ls_payload, ls_response
Integer li_status

// ls_url = "https://invoice-api.amego.tw/json/f0401"
ls_url = "http://192.168.1.75:8000/create-invoice"
ole_http = CREATE OLEObject
li_rc = ole_http.ConnectToNewObject("MSXML2.XMLHTTP")

IF li_rc <> 0 THEN
    MessageBox("Error", "Failed to create XMLHTTP object.")
    RETURN
END IF

TRY
    ole_http.Open("POST", ls_url, FALSE)
    ole_http.setRequestHeader("Content-Type", "application/json")
    
    ls_payload = this.wf_create_invoice_price("1230")
    
    ole_http.Send(ls_payload)

    li_status = ole_http.Status
    IF li_status = 200 THEN
        ls_response = ole_http.ResponseText
        IF Len(Trim(ls_response)) > 0 THEN
            MessageBox("Success", ls_response)
        ELSE
            MessageBox("No Response", "Server returned status 200 but no body.")
        END IF
    ELSE
        MessageBox("HTTP Error", "Status: " + String(li_status))
    END IF

CATCH (OLERuntimeError ole_err)
    MessageBox("OLE Error", ole_err.Description)

FINALLY
    DESTROY ole_http
END TRY