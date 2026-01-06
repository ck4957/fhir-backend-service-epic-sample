/// RevStream Alert Operation
/// Sends alerts for critical errors via email/SMS/webhook
///
Class RevStream.Operation.AlertOperation Extends Ens.BusinessOperation
{

/// Email adapter (can be swapped for SMS or webhook)
Parameter ADAPTER = "EnsLib.EMail.OutboundAdapter";

/// Alert email recipient
Property AlertRecipient As %String(MAXLEN = 256) [ InitialExpression = "oncall@hospital.org" ];

/// Enable console logging (for demo purposes)
Property ConsoleAlertEnabled As %Boolean [ InitialExpression = 1 ];

/// Settings
Parameter SETTINGS = "AlertRecipient:Basic,ConsoleAlertEnabled:Basic";

/// Message map
XData MessageMap
{
<MapItems>
    <MapItem MessageType="RevStream.Message.AlertMessage">
        <Method>SendAlert</Method>
    </MapItem>
</MapItems>
}

/// Send alert message
Method SendAlert(pRequest As RevStream.Message.AlertMessage, Output pResponse As Ens.Response) As %Status
{
    Set tStatus = $$$OK
    
    Try {
        // Log to console (always)
        If ..ConsoleAlertEnabled {
            $$$LOGALERT("==========================================")
            $$$LOGALERT("ALERT: "_pRequest.AlertType)
            $$$LOGALERT("Subject: "_pRequest.Subject)
            $$$LOGALERT("Message: "_pRequest.Message)
            $$$LOGALERT("==========================================")
        }
        
        // In production, send via email/SMS
        // Set tEmail = ##class(%Net.MailMessage).%New()
        // Set tEmail.To = ..AlertRecipient
        // Set tEmail.Subject = "[REVSTREAM ALERT] "_pRequest.Subject
        // Do tEmail.TextData.Write(pRequest.Message)
        // Set tStatus = ..Adapter.SendMail(tEmail)
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        $$$LOGERROR("Alert operation exception: "_ex.DisplayString())
    }
    
    Quit tStatus
}

}
