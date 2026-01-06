/// RevStream Message Router
/// Business Process that routes HL7 messages based on message type
/// 
/// Routing Logic:
///   - MDM^T02 (Medical Documents) -> CAC Processing Pipeline
///   - ADT^A01 (Admissions) -> Patient Registration
///   - DFT^P03 (Financial) -> Billing System
///   - All others -> Error Handler
///
Class RevStream.Process.MessageRouter Extends Ens.BusinessProcess
{

/// CAC Pipeline target
Property CACPipelineTarget As %String(MAXLEN = 128) [ InitialExpression = "RevStream.Process.CACPipeline" ];

/// Billing Operation target
Property BillingTarget As %String(MAXLEN = 128) [ InitialExpression = "RevStream.Operation.BillingOutput" ];

/// Error Handler target  
Property ErrorHandlerTarget As %String(MAXLEN = 128) [ InitialExpression = "RevStream.Process.ErrorHandler" ];

/// Settings exposed in Management Portal
Parameter SETTINGS = "CACPipelineTarget:Basic:selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId},BillingTarget:Basic:selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId},ErrorHandlerTarget:Basic:selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId}";

/// Main request handler
Method OnRequest(pRequest As EnsLib.HL7.Message, Output pResponse As EnsLib.HL7.Message) As %Status
{
    Set tStatus = $$$OK
    
    Try {
        // Extract message type from MSH-9
        Set tMsgType = pRequest.GetValueAt("MSH:9.1")
        Set tMsgEvent = pRequest.GetValueAt("MSH:9.2")
        Set tFullType = tMsgType_"^"_tMsgEvent
        
        $$$LOGINFO("Routing message type: "_tFullType)
        
        // Validate required PID segment
        Set tPatientID = pRequest.GetValueAt("PID:3.1")
        If tPatientID = "" {
            $$$LOGWARNING("Message missing Patient ID - routing to error handler")
            Set tStatus = ..SendRequestSync(..ErrorHandlerTarget, pRequest, .pResponse)
            Quit
        }
        
        // Route based on message type
        If tMsgType = "MDM" {
            // Medical Document Management - send to CAC Pipeline
            $$$LOGINFO("Routing MDM message to CAC Pipeline for patient: "_tPatientID)
            Set tStatus = ..SendRequestSync(..CACPipelineTarget, pRequest, .pResponse)
            
        } ElseIf tMsgType = "ADT" {
            // Admission/Discharge/Transfer - log and acknowledge
            $$$LOGINFO("Received ADT message for patient: "_tPatientID_" - Acknowledged")
            Set pResponse = pRequest
            
        } ElseIf tMsgType = "DFT" {
            // Financial Transaction - send directly to billing
            $$$LOGINFO("Routing DFT message to Billing for patient: "_tPatientID)
            Set tStatus = ..SendRequestSync(..BillingTarget, pRequest, .pResponse)
            
        } Else {
            // Unknown message type - send to error handler
            $$$LOGWARNING("Unknown message type: "_tFullType_" - routing to error handler")
            Set tStatus = ..SendRequestSync(..ErrorHandlerTarget, pRequest, .pResponse)
        }
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        $$$LOGERROR("Exception in router: "_ex.DisplayString())
    }
    
    Quit tStatus
}

}
