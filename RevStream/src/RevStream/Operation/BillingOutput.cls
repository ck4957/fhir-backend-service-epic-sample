/// RevStream Billing Output Operation
/// Business Operation that sends DFT^P03 messages to downstream billing system
///
Class RevStream.Operation.BillingOutput Extends Ens.BusinessOperation
{

/// TCP Adapter for HL7 output
Parameter ADAPTER = "EnsLib.HL7.Adapter.TCPOutboundAdapter";

/// Settings
Parameter SETTINGS = "IPAddress:Basic,Port:Basic";

/// Billing system IP address
Property IPAddress As %String [ InitialExpression = "billing-simulator" ];

/// Billing system port
Property Port As %Integer [ InitialExpression = 2022 ];

/// Message map
XData MessageMap
{
<MapItems>
    <MapItem MessageType="EnsLib.HL7.Message">
        <Method>SendToBilling</Method>
    </MapItem>
</MapItems>
}

/// Send HL7 message to billing system
Method SendToBilling(pRequest As EnsLib.HL7.Message, Output pResponse As EnsLib.HL7.Message) As %Status
{
    Set tStatus = $$$OK
    
    Try {
        Set tMsgID = pRequest.GetValueAt("MSH:10")
        Set tPatientID = pRequest.GetValueAt("PID:3.1")
        
        $$$LOGINFO("Sending DFT to Billing System - Message: "_tMsgID_", Patient: "_tPatientID)
        
        // Send via adapter
        Set tStatus = ..Adapter.SendMessageSync(pRequest, .pResponse, ..Timeout)
        
        If $$$ISERR(tStatus) {
            $$$LOGERROR("Failed to send to billing: "_$System.Status.GetErrorText(tStatus))
        } Else {
            $$$LOGINFO("Successfully sent to billing system")
            
            // Log acknowledgment
            If $IsObject(pResponse) {
                Set tAckCode = pResponse.GetValueAt("MSA:1")
                $$$LOGINFO("Billing ACK: "_tAckCode)
            }
        }
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        $$$LOGERROR("Billing operation exception: "_ex.DisplayString())
    }
    
    Quit tStatus
}

/// Timeout for billing system connection
Property Timeout As %Integer [ InitialExpression = 30 ];

}
