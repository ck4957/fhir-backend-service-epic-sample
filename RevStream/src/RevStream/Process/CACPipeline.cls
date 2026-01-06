/// RevStream CAC Pipeline
/// Business Process for Computer-Assisted Coding pipeline
/// 
/// This process:
///   1. Extracts clinical text from MDM/TXA/OBX segments
///   2. Calls the CAC Engine to extract ICD-10/CPT codes
///   3. Transforms MDM message to DFT^P03 Financial Transaction
///   4. Routes to Billing System
///
Class RevStream.Process.CACPipeline Extends Ens.BusinessProcess
{

/// CAC Engine Operation target
Property CACEngineTarget As %String(MAXLEN = 128) [ InitialExpression = "RevStream.Operation.CACEngine" ];

/// Billing Output target
Property BillingTarget As %String(MAXLEN = 128) [ InitialExpression = "RevStream.Operation.BillingOutput" ];

/// DTL Transformation class
Property TransformClass As %String(MAXLEN = 256) [ InitialExpression = "RevStream.DTL.MDMtoDFT" ];

/// Settings
Parameter SETTINGS = "CACEngineTarget:Basic:selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId},BillingTarget:Basic:selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId},TransformClass:Basic";

/// Process MDM message through CAC pipeline
Method OnRequest(pRequest As EnsLib.HL7.Message, Output pResponse As EnsLib.HL7.Message) As %Status
{
    Set tStatus = $$$OK
    
    Try {
        Set tPatientID = pRequest.GetValueAt("PID:3.1")
        Set tDocType = pRequest.GetValueAt("TXA:2")
        
        $$$LOGINFO("CAC Pipeline: Processing document type '"_tDocType_"' for patient: "_tPatientID)
        
        // Step 1: Extract clinical text from OBX segments
        Set tClinicalText = ..ExtractClinicalText(pRequest)
        
        If tClinicalText = "" {
            $$$LOGWARNING("No clinical text found in message")
        } Else {
            $$$LOGINFO("Extracted "_$Length(tClinicalText)_" characters of clinical text")
        }
        
        // Step 2: Create CAC request with clinical text
        Set tCACRequest = ##class(RevStream.Message.CACRequest).%New()
        Set tCACRequest.PatientID = tPatientID
        Set tCACRequest.ClinicalText = tClinicalText
        Set tCACRequest.DocumentType = tDocType
        Set tCACRequest.SourceMessageID = pRequest.GetValueAt("MSH:10")
        
        // Step 3: Call CAC Engine to extract codes
        $$$LOGINFO("Sending to CAC Engine for code extraction...")
        Set tStatus = ..SendRequestSync(..CACEngineTarget, tCACRequest, .tCACResponse)
        
        If $$$ISERR(tStatus) {
            $$$LOGERROR("CAC Engine error: "_$System.Status.GetErrorText(tStatus))
            Quit
        }
        
        // Step 4: Transform MDM to DFT with extracted codes
        $$$LOGINFO("Transforming MDM to DFT with "_tCACResponse.Codes.Count()_" extracted codes")
        
        Set tStatus = ..TransformMessage(pRequest, tCACResponse, .tDFTMessage)
        
        If $$$ISERR(tStatus) {
            $$$LOGERROR("Transformation error: "_$System.Status.GetErrorText(tStatus))
            Quit
        }
        
        // Step 5: Send DFT to Billing System
        $$$LOGINFO("Sending DFT to Billing System...")
        Set tStatus = ..SendRequestSync(..BillingTarget, tDFTMessage, .pResponse)
        
        If $$$ISERR(tStatus) {
            $$$LOGERROR("Billing send error: "_$System.Status.GetErrorText(tStatus))
        } Else {
            $$$LOGINFO("Successfully processed and sent to billing")
        }
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        $$$LOGERROR("CAC Pipeline exception: "_ex.DisplayString())
    }
    
    Quit tStatus
}

/// Extract clinical text from OBX segments
Method ExtractClinicalText(pMessage As EnsLib.HL7.Message) As %String
{
    Set tText = ""
    
    Try {
        // Get count of OBX segments
        Set tSegmentCount = pMessage.SegCount
        
        For i = 1:1:tSegmentCount {
            Set tSegment = pMessage.GetSegmentAt(i)
            If $IsObject(tSegment) {
                Set tSegName = tSegment.Name
                
                If tSegName = "OBX" {
                    // OBX-5 contains the observation value (clinical text)
                    Set tValue = pMessage.GetValueAt("OBX("_i_"):5")
                    If tValue '= "" {
                        Set tText = tText_" "_tValue
                    }
                }
            }
        }
        
    } Catch ex {
        $$$LOGERROR("Error extracting clinical text: "_ex.DisplayString())
    }
    
    Quit $ZStrip(tText, "<>W")
}

/// Transform MDM message to DFT with CAC codes
Method TransformMessage(pMDM As EnsLib.HL7.Message, pCACResponse As RevStream.Message.CACResponse, Output pDFT As EnsLib.HL7.Message) As %Status
{
    Set tStatus = $$$OK
    
    Try {
        // Create new DFT^P03 message
        Set pDFT = ##class(EnsLib.HL7.Message).%New()
        
        // Build timestamp
        Set tTimestamp = $ZDateTime($Horolog, 3, 1)
        Set tTimestamp = $Translate(tTimestamp, "- :", "")
        
        // MSH Segment
        Do pDFT.SetValueAt("|", "MSH:1")
        Do pDFT.SetValueAt("^~\&", "MSH:2")
        Do pDFT.SetValueAt("REVSTREAM", "MSH:3")
        Do pDFT.SetValueAt("CAC", "MSH:4")
        Do pDFT.SetValueAt("BILLING", "MSH:5")
        Do pDFT.SetValueAt("FINANCIAL", "MSH:6")
        Do pDFT.SetValueAt(tTimestamp, "MSH:7")
        Do pDFT.SetValueAt("DFT^P03", "MSH:9")
        Do pDFT.SetValueAt("MSG"_$Random(999999), "MSH:10")
        Do pDFT.SetValueAt("P", "MSH:11")
        Do pDFT.SetValueAt("2.5", "MSH:12")
        
        // EVN Segment
        Do pDFT.SetValueAt("P03", "EVN:1")
        Do pDFT.SetValueAt(tTimestamp, "EVN:2")
        
        // Copy PID from source
        Do pDFT.SetValueAt(pMDM.GetValueAt("PID:1"), "PID:1")
        Do pDFT.SetValueAt(pMDM.GetValueAt("PID:3"), "PID:3")
        Do pDFT.SetValueAt(pMDM.GetValueAt("PID:5"), "PID:5")
        Do pDFT.SetValueAt(pMDM.GetValueAt("PID:7"), "PID:7")
        Do pDFT.SetValueAt(pMDM.GetValueAt("PID:8"), "PID:8")
        
        // Copy PV1 from source
        Do pDFT.SetValueAt(pMDM.GetValueAt("PV1:1"), "PV1:1")
        Do pDFT.SetValueAt(pMDM.GetValueAt("PV1:2"), "PV1:2")
        Do pDFT.SetValueAt(pMDM.GetValueAt("PV1:3"), "PV1:3")
        
        // FT1 Segment(s) - one per code
        Set tCodeCount = pCACResponse.Codes.Count()
        
        For i = 1:1:tCodeCount {
            Set tCode = pCACResponse.Codes.GetAt(i)
            
            // FT1 fields
            Do pDFT.SetValueAt(i, "FT1("_i_"):1")  // Set ID
            Do pDFT.SetValueAt(tTimestamp, "FT1("_i_"):4")  // Transaction Date
            Do pDFT.SetValueAt(tTimestamp, "FT1("_i_"):5")  // Transaction Posting Date
            Do pDFT.SetValueAt("CG", "FT1("_i_"):6")  // Transaction Type (Charge)
            Do pDFT.SetValueAt(tCode.Code_"^"_tCode.Description_"^"_tCode.CodeSystem, "FT1("_i_"):25")  // Procedure Code
            
            // Add diagnosis codes to DG1
            If tCode.CodeType = "ICD10" {
                Do pDFT.SetValueAt(i, "DG1("_i_"):1")
                Do pDFT.SetValueAt(tCode.Code_"^"_tCode.Description_"^ICD10", "DG1("_i_"):3")
                Do pDFT.SetValueAt(tCode.Description, "DG1("_i_"):4")
                Do pDFT.SetValueAt(tTimestamp, "DG1("_i_"):5")
            }
        }
        
        $$$LOGINFO("Created DFT message with "_tCodeCount_" FT1 segments")
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        $$$LOGERROR("Transform error: "_ex.DisplayString())
    }
    
    Quit tStatus
}

}
