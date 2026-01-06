/// RevStream Error File Output Operation
/// Writes error messages to a file for review
///
Class RevStream.Operation.ErrorFileOutput Extends Ens.BusinessOperation
{

/// File adapter
Parameter ADAPTER = "EnsLib.File.OutboundAdapter";

/// Output directory
Property FilePath As %String(MAXLEN = 256) [ InitialExpression = "/home/irisowner/errors/" ];

/// Settings
Parameter SETTINGS = "FilePath:Basic";

/// Message map
XData MessageMap
{
<MapItems>
    <MapItem MessageType="RevStream.Message.ErrorRecord">
        <Method>WriteErrorFile</Method>
    </MapItem>
</MapItems>
}

/// Write error record to file
Method WriteErrorFile(pRequest As RevStream.Message.ErrorRecord, Output pResponse As Ens.Response) As %Status
{
    Set tStatus = $$$OK
    
    Try {
        Set tTimestamp = $ZDateTime($Horolog, 3, 1)
        Set tTimestamp = $Translate(tTimestamp, "- :", "_")
        
        Set tFilename = "ERROR_"_tTimestamp_"_"_pRequest.OriginalMessageID_".txt"
        
        // Build error report
        Set tContent = "========================================="_$Char(13,10)
        Set tContent = tContent_"REVSTREAM ERROR REPORT"_$Char(13,10)
        Set tContent = tContent_"========================================="_$Char(13,10)
        Set tContent = tContent_"Timestamp: "_pRequest.ErrorTimestamp_$Char(13,10)
        Set tContent = tContent_"Message ID: "_pRequest.OriginalMessageID_$Char(13,10)
        Set tContent = tContent_"Message Type: "_pRequest.MessageType_$Char(13,10)
        Set tContent = tContent_"Patient ID: "_pRequest.PatientID_$Char(13,10)
        Set tContent = tContent_"Error Reason: "_pRequest.ErrorReason_$Char(13,10)
        Set tContent = tContent_"========================================="_$Char(13,10)
        Set tContent = tContent_"ORIGINAL MESSAGE:"_$Char(13,10)
        Set tContent = tContent_"========================================="_$Char(13,10)
        Set tContent = tContent_pRequest.OriginalMessage_$Char(13,10)
        
        // Write to file
        Set tStatus = ..Adapter.PutString(tFilename, tContent)
        
        $$$LOGINFO("Error record written to: "_..FilePath_tFilename)
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        $$$LOGERROR("Failed to write error file: "_ex.DisplayString())
    }
    
    Quit tStatus
}

}
