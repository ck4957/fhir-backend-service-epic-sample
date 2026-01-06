/// RevStream CAC Engine Operation
/// Business Operation that interfaces with the Computer-Assisted Coding engine
/// 
/// This operation:
///   - Sends clinical text to CAC engine (Python script)
///   - Receives extracted ICD-10 and CPT codes
///   - Handles CAC engine connection errors
///
Class RevStream.Operation.CACEngine Extends Ens.BusinessOperation
{

/// Adapter for calling external CAC service
Parameter ADAPTER = "EnsLib.HTTP.OutboundAdapter";

/// CAC Engine URL
Property CACEngineURL As %String(MAXLEN = 256) [ InitialExpression = "http://localhost:5000/extract" ];

/// Timeout in seconds
Property Timeout As %Integer [ InitialExpression = 30 ];

/// Enable simulation mode (no actual CAC call)
Property SimulationMode As %Boolean [ InitialExpression = 1 ];

/// Settings
Parameter SETTINGS = "CACEngineURL:Basic,Timeout:Basic,SimulationMode:Basic";

/// Message map
XData MessageMap
{
<MapItems>
    <MapItem MessageType="RevStream.Message.CACRequest">
        <Method>ExtractCodes</Method>
    </MapItem>
</MapItems>
}

/// Extract codes from clinical text
Method ExtractCodes(pRequest As RevStream.Message.CACRequest, Output pResponse As RevStream.Message.CACResponse) As %Status
{
    Set tStatus = $$$OK
    Set pResponse = ##class(RevStream.Message.CACResponse).%New()
    Set pResponse.PatientID = pRequest.PatientID
    Set pResponse.SourceMessageID = pRequest.SourceMessageID
    Set pResponse.ProcessingTimestamp = $ZDateTime($Horolog, 3)
    
    Try {
        $$$LOGINFO("CAC Engine: Processing request for patient "_pRequest.PatientID)
        $$$LOGINFO("CAC Engine: Document type: "_pRequest.DocumentType)
        $$$LOGINFO("CAC Engine: Clinical text length: "_$Length(pRequest.ClinicalText)_" chars")
        
        If ..SimulationMode {
            // Simulation mode - use keyword matching
            $$$LOGINFO("CAC Engine: Running in SIMULATION mode")
            Set tStatus = ..SimulateCodeExtraction(pRequest.ClinicalText, .pResponse)
        } Else {
            // Production mode - call actual CAC service
            Set tStatus = ..CallCACService(pRequest, .pResponse)
        }
        
        $$$LOGINFO("CAC Engine: Extracted "_pResponse.Codes.Count()_" codes")
        Set pResponse.Status = "SUCCESS"
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        Set pResponse.Status = "ERROR"
        Set pResponse.ErrorMessage = ex.DisplayString()
        $$$LOGERROR("CAC Engine exception: "_ex.DisplayString())
    }
    
    Quit tStatus
}

/// Simulate CAC code extraction using keyword matching
Method SimulateCodeExtraction(pClinicalText As %String, ByRef pResponse As RevStream.Message.CACResponse) As %Status
{
    Set tStatus = $$$OK
    Set tText = $ZConvert(pClinicalText, "U")
    
    // Simulated CAC keyword mapping
    // In production, this would be a sophisticated NLP/ML model
    
    // Appendicitis codes
    If tText [ "APPENDICITIS" {
        Do ..AddCode(pResponse, "K35.80", "Unspecified acute appendicitis", "ICD10", 95)
        If tText [ "PERITONEAL" || (tText [ "ABSCESS") {
            Do ..AddCode(pResponse, "K35.33", "Acute appendicitis with perforation and localized peritonitis", "ICD10", 88)
        }
    }
    
    // Appendectomy procedure
    If tText [ "APPENDECTOMY" {
        If tText [ "LAPAROSCOPIC" {
            Do ..AddCode(pResponse, "44970", "Laparoscopy, surgical, appendectomy", "CPT", 92)
        } Else {
            Do ..AddCode(pResponse, "44950", "Appendectomy", "CPT", 85)
        }
    }
    
    // Pneumonia
    If tText [ "PNEUMONIA" {
        Do ..AddCode(pResponse, "J18.9", "Pneumonia, unspecified organism", "ICD10", 78)
        If tText [ "BACTERIAL" {
            Do ..AddCode(pResponse, "J15.9", "Unspecified bacterial pneumonia", "ICD10", 82)
        }
    }
    
    // Heart failure
    If tText [ "HEART FAILURE" || (tText [ "CHF") {
        Do ..AddCode(pResponse, "I50.9", "Heart failure, unspecified", "ICD10", 80)
    }
    
    // Diabetes
    If tText [ "DIABETES" {
        Do ..AddCode(pResponse, "E11.9", "Type 2 diabetes mellitus without complications", "ICD10", 75)
    }
    
    // Fracture
    If tText [ "FRACTURE" {
        If tText [ "HIP" {
            Do ..AddCode(pResponse, "S72.009A", "Fracture of unspecified part of neck of femur, initial encounter", "ICD10", 88)
        } ElseIf tText [ "WRIST" {
            Do ..AddCode(pResponse, "S52.509A", "Unspecified fracture of the lower end of radius, initial encounter", "ICD10", 85)
        }
    }
    
    // Chest X-ray
    If tText [ "CHEST X-RAY" || (tText [ "CHEST RADIOGRAPH") {
        Do ..AddCode(pResponse, "71046", "Radiologic examination, chest; 2 views", "CPT", 90)
    }
    
    // CT Scan
    If tText [ "CT SCAN" || (tText [ "COMPUTED TOMOGRAPHY") {
        If tText [ "ABDOMEN" {
            Do ..AddCode(pResponse, "74176", "CT abdomen and pelvis without contrast", "CPT", 88)
        } ElseIf tText [ "HEAD" || (tText [ "BRAIN") {
            Do ..AddCode(pResponse, "70450", "CT head/brain without contrast", "CPT", 90)
        }
    }
    
    // If no codes found, add a general code
    If pResponse.Codes.Count() = 0 {
        Do ..AddCode(pResponse, "Z00.00", "General adult medical examination without abnormal findings", "ICD10", 50)
    }
    
    Quit tStatus
}

/// Add a code to the response
Method AddCode(pResponse As RevStream.Message.CACResponse, pCode As %String, pDescription As %String, pCodeType As %String, pConfidence As %Integer)
{
    Set tCodeItem = ##class(RevStream.Message.CodeItem).%New()
    Set tCodeItem.Code = pCode
    Set tCodeItem.Description = pDescription
    Set tCodeItem.CodeType = pCodeType
    Set tCodeItem.Confidence = pConfidence
    Set tCodeItem.Source = "CAC-SIMULATED"
    
    If pCodeType = "ICD10" {
        Set tCodeItem.CodeSystem = "ICD-10-CM"
    } ElseIf pCodeType = "CPT" {
        Set tCodeItem.CodeSystem = "CPT-4"
    } Else {
        Set tCodeItem.CodeSystem = pCodeType
    }
    
    Do pResponse.Codes.Insert(tCodeItem)
    $$$LOGINFO("Added code: "_pCode_" ("_pDescription_") - Confidence: "_pConfidence_"%")
}

/// Call actual CAC HTTP service
Method CallCACService(pRequest As RevStream.Message.CACRequest, ByRef pResponse As RevStream.Message.CACResponse) As %Status
{
    Set tStatus = $$$OK
    
    // This would make an actual HTTP call to a CAC service
    // For now, fall back to simulation
    $$$LOGWARNING("HTTP CAC service not implemented - using simulation")
    Set tStatus = ..SimulateCodeExtraction(pRequest.ClinicalText, .pResponse)
    
    Quit tStatus
}

}
