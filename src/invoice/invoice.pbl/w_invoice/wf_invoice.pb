OLEObject ole_http
Integer li_rc
String ls_url, ls_payload, ls_response, ls_auth_token, ls_hash
Integer li_status

ls_url = "http://127.0.0.1:8001/v1/invoice"
ls_auth_token = "Bearer YOUR_ACCESS_TOKEN"

ole_http = CREATE OLEObject
li_rc = ole_http.ConnectToNewObject("MSXML2.XMLHTTP")

IF li_rc <> 0 THEN
    MessageBox("Error", "Failed to create XMLHTTP object.")
    RETURN
END IF

TRY
    ole_http.Open("POST", ls_url, FALSE)

    ole_http.setRequestHeader("Content-Type", "application/json")
    ole_http.setRequestHeader("Authorization", ls_auth_token)
    
    ls_payload = this.wf_create_invoice_data( "123" )
	
    ole_http.Send(ls_payload)

    // Check HTTP status
    li_status = ole_http.Status

    IF ole_http.Status = 200 THEN
        ls_response = ole_http.ResponseText
        IF Len(Trim(ls_response)) > 0 THEN
            MessageBox("Success", ls_response)
        ELSE
            MessageBox("No Response", "Server returned status 200 but no body.")
        END IF
    ELSE
        MessageBox("HTTP Error", "Status: " + String(ole_http.Status))
    END IF


CATCH (OLERuntimeError ole_err)
    MessageBox("OLE Error", ole_err.Description)

FINALLY
    DESTROY ole_http
END TRY