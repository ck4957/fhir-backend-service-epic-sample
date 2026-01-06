/// RevStream HL7 Inbound Service
/// Business Service that listens for incoming HL7 v2 messages from EHR systems
/// 
/// This service accepts MDM^T02 (Medical Document Management) and ADT messages
/// on a TCP port using MLLP (Minimal Lower Layer Protocol)
///
Class RevStream.Service.HL7InboundService Extends Ens.BusinessService
{

/// Adapter class for TCP/MLLP communication
Parameter ADAPTER = "EnsLib.HL7.Adapter.TCPInboundAdapter";

/// Target configuration item for routing
Property TargetConfigName As %String(MAXLEN = 128) [ InitialExpression = "RevStream.Process.MessageRouter" ];

/// Settings for this service
Parameter SETTINGS = "TargetConfigName:Basic:selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId}";

/// Process incoming HL7 message
Method OnProcessInput(pInput As EnsLib.HL7.Message, Output pOutput As EnsLib.HL7.Message) As %Status
{
    Set tStatus = $$$OK
    
    Try {
        // Log receipt of message
        $$$LOGINFO("Received HL7 message: "_pInput.Name)
        
        // Validate message has required segments
        Set tMSH = pInput.GetSegmentAt(1)
        If '$IsObject(tMSH) {
            $$$LOGERROR("Message missing MSH segment")
            Set tStatus = $$$ERROR($$$GeneralError, "Message missing MSH segment")
            Quit
        }
        
        // Get message type for logging
        Set tMsgType = pInput.GetValueAt("MSH:9.1")_"^"_pInput.GetValueAt("MSH:9.2")
        $$$LOGINFO("Message Type: "_tMsgType)
        
        // Send to router for processing
        Set tStatus = ..SendRequestSync(..TargetConfigName, pInput, .pOutput)
        
        If $$$ISERR(tStatus) {
            $$$LOGERROR("Error sending to router: "_$System.Status.GetErrorText(tStatus))
        }
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        $$$LOGERROR("Exception processing message: "_ex.DisplayString())
    }
    
    Quit tStatus
}

/// Generate acknowledgment for incoming message
Method OnGenerateAck(pOriginal As EnsLib.HL7.Message, pReplyCode As %String, pErrorStatus As %Status, Output pAck As EnsLib.HL7.Message) As %Status
{
    Set tStatus = $$$OK
    
    Try {
        // Generate standard HL7 ACK
        Set pAck = ##class(EnsLib.HL7.Message).%New()
        
        // Build ACK message
        Set tTimestamp = $ZDateTime($Horolog, 3, 1)
        Set tTimestamp = $Translate(tTimestamp, "- :", "")
        
        // Create MSH segment
        Do pAck.SetValueAt("^~\&", "MSH:2")
        Do pAck.SetValueAt("REVSTREAM", "MSH:3")
        Do pAck.SetValueAt("INTEGRATION", "MSH:4")
        Do pAck.SetValueAt(pOriginal.GetValueAt("MSH:3"), "MSH:5")
        Do pAck.SetValueAt(pOriginal.GetValueAt("MSH:4"), "MSH:6")
        Do pAck.SetValueAt(tTimestamp, "MSH:7")
        Do pAck.SetValueAt("ACK", "MSH:9.1")
        Do pAck.SetValueAt(pOriginal.GetValueAt("MSH:10"), "MSH:10")
        Do pAck.SetValueAt("P", "MSH:11")
        Do pAck.SetValueAt("2.5", "MSH:12")
        
        // Create MSA segment
        If $$$ISOK(pErrorStatus) {
            Do pAck.SetValueAt("AA", "MSA:1")
        } Else {
            Do pAck.SetValueAt("AE", "MSA:1")
        }
        Do pAck.SetValueAt(pOriginal.GetValueAt("MSH:10"), "MSA:2")
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
    }
    
    Quit tStatus
}

}
