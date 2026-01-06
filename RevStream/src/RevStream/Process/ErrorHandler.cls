/// RevStream Error Handler
/// Business Process for handling invalid or problematic messages
/// 
/// Responsibilities:
///   - Log detailed error information
///   - Move bad messages to error folder
///   - Send alerts for critical errors
///   - Create audit trail
///
Class RevStream.Process.ErrorHandler Extends Ens.BusinessProcess
{

/// File operation for storing error messages
Property ErrorFileTarget As %String(MAXLEN = 128) [ InitialExpression = "RevStream.Operation.ErrorFileOutput" ];

/// Alert operation target
Property AlertTarget As %String(MAXLEN = 128) [ InitialExpression = "RevStream.Operation.AlertOperation" ];

/// Enable alerting
Property AlertingEnabled As %Boolean [ InitialExpression = 1 ];

/// Settings
Parameter SETTINGS = "ErrorFileTarget:Basic:selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId},AlertTarget:Basic:selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId},AlertingEnabled:Basic";

/// Handle error message
Method OnRequest(pRequest As EnsLib.HL7.Message, Output pResponse As EnsLib.HL7.Message) As %Status
{
    Set tStatus = $$$OK
    
    Try {
        // Extract error details
        Set tMsgType = pRequest.GetValueAt("MSH:9")
        Set tMsgID = pRequest.GetValueAt("MSH:10")
        Set tPatientID = pRequest.GetValueAt("PID:3.1")
        Set tSendingApp = pRequest.GetValueAt("MSH:3")
        Set tSendingFacility = pRequest.GetValueAt("MSH:4")
        
        // Determine error reason
        Set tErrorReason = ..DetermineErrorReason(pRequest)
        
        $$$LOGERROR("ERROR HANDLER: Processing error for message "_tMsgID)
        $$$LOGERROR("  Message Type: "_tMsgType)
        $$$LOGERROR("  Patient ID: "_tPatientID)
        $$$LOGERROR("  Source: "_tSendingApp_" @ "_tSendingFacility)
        $$$LOGERROR("  Error Reason: "_tErrorReason)
        
        // Create error record
        Set tErrorRecord = ##class(RevStream.Message.ErrorRecord).%New()
        Set tErrorRecord.OriginalMessageID = tMsgID
        Set tErrorRecord.MessageType = tMsgType
        Set tErrorRecord.PatientID = tPatientID
        Set tErrorRecord.ErrorReason = tErrorReason
        Set tErrorRecord.ErrorTimestamp = $ZDateTime($Horolog, 3)
        Set tErrorRecord.OriginalMessage = pRequest.OutputToString()
        
        // Save to error file
        Set tStatus = ..SendRequestAsync(..ErrorFileTarget, tErrorRecord)
        
        // Send alert if enabled and critical
        If ..AlertingEnabled && ..IsCriticalError(tErrorReason) {
            Set tAlert = ##class(RevStream.Message.AlertMessage).%New()
            Set tAlert.AlertType = "CRITICAL"
            Set tAlert.Subject = "RevStream Error: "_tErrorReason
            Set tAlert.Message = "Message ID: "_tMsgID_$Char(13,10)_"Patient: "_tPatientID_$Char(13,10)_"Error: "_tErrorReason
            
            Set tStatus = ..SendRequestAsync(..AlertTarget, tAlert)
            $$$LOGWARNING("Critical alert sent for message "_tMsgID)
        }
        
        // Generate NAK response
        Set pResponse = ..GenerateNAK(pRequest, tErrorReason)
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        $$$LOGERROR("Exception in error handler: "_ex.DisplayString())
    }
    
    Quit tStatus
}

/// Determine the reason for the error
Method DetermineErrorReason(pMessage As EnsLib.HL7.Message) As %String
{
    Set tReason = "Unknown Error"
    
    // Check for missing required fields
    If pMessage.GetValueAt("PID:3.1") = "" {
        Set tReason = "Missing Patient ID (PID-3)"
    }
    ElseIf pMessage.GetValueAt("MSH:9") = "" {
        Set tReason = "Missing Message Type (MSH-9)"
    }
    ElseIf pMessage.GetValueAt("MSH:10") = "" {
        Set tReason = "Missing Message Control ID (MSH-10)"
    }
    ElseIf '..IsValidMessageType(pMessage.GetValueAt("MSH:9.1")) {
        Set tReason = "Unsupported Message Type: "_pMessage.GetValueAt("MSH:9")
    }
    
    Quit tReason
}

/// Check if message type is valid
Method IsValidMessageType(pMsgType As %String) As %Boolean
{
    Set tValidTypes = ",ADT,MDM,DFT,ORM,ORU,"
    Quit tValidTypes [ (","_pMsgType_",")
}

/// Check if error is critical
Method IsCriticalError(pReason As %String) As %Boolean
{
    // Critical errors that require immediate attention
    If pReason [ "Missing Patient ID" Quit 1
    If pReason [ "Connection" Quit 1
    Quit 0
}

/// Generate NAK (Negative Acknowledgment)
Method GenerateNAK(pOriginal As EnsLib.HL7.Message, pErrorReason As %String) As EnsLib.HL7.Message
{
    Set tNAK = ##class(EnsLib.HL7.Message).%New()
    
    Set tTimestamp = $ZDateTime($Horolog, 3, 1)
    Set tTimestamp = $Translate(tTimestamp, "- :", "")
    
    // MSH
    Do tNAK.SetValueAt("|", "MSH:1")
    Do tNAK.SetValueAt("^~\&", "MSH:2")
    Do tNAK.SetValueAt("REVSTREAM", "MSH:3")
    Do tNAK.SetValueAt("ERROR", "MSH:4")
    Do tNAK.SetValueAt(pOriginal.GetValueAt("MSH:3"), "MSH:5")
    Do tNAK.SetValueAt(pOriginal.GetValueAt("MSH:4"), "MSH:6")
    Do tNAK.SetValueAt(tTimestamp, "MSH:7")
    Do tNAK.SetValueAt("ACK", "MSH:9")
    Do tNAK.SetValueAt(pOriginal.GetValueAt("MSH:10"), "MSH:10")
    Do tNAK.SetValueAt("P", "MSH:11")
    Do tNAK.SetValueAt("2.5", "MSH:12")
    
    // MSA - Application Reject
    Do tNAK.SetValueAt("AR", "MSA:1")
    Do tNAK.SetValueAt(pOriginal.GetValueAt("MSH:10"), "MSA:2")
    Do tNAK.SetValueAt(pErrorReason, "MSA:3")
    
    // ERR segment
    Do tNAK.SetValueAt("207^Application Internal Error^HL70357", "ERR:3")
    Do tNAK.SetValueAt("E", "ERR:4")
    Do tNAK.SetValueAt(pErrorReason, "ERR:7")
    
    Quit tNAK
}

}
