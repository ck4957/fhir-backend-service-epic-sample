/// CAC Request Message
/// Request sent to CAC Engine for code extraction
///
Class RevStream.Message.CACRequest Extends Ens.Request
{

/// Patient identifier
Property PatientID As %String(MAXLEN = 50);

/// Clinical text to analyze
Property ClinicalText As %String(MAXLEN = 32000);

/// Type of clinical document (OPNOTE, DCSUMMARY, etc.)
Property DocumentType As %String(MAXLEN = 50);

/// Source HL7 message control ID
Property SourceMessageID As %String(MAXLEN = 100);

/// Encounter/Visit ID
Property EncounterID As %String(MAXLEN = 50);

/// Attending physician
Property AttendingPhysician As %String(MAXLEN = 200);

Storage Default
{
<Data name="CACRequestDefaultData">
<Subscript>"CACRequest"</Subscript>
<Value name="1">
<Value>PatientID</Value>
</Value>
<Value name="2">
<Value>ClinicalText</Value>
</Value>
<Value name="3">
<Value>DocumentType</Value>
</Value>
<Value name="4">
<Value>SourceMessageID</Value>
</Value>
<Value name="5">
<Value>EncounterID</Value>
</Value>
<Value name="6">
<Value>AttendingPhysician</Value>
</Value>
</Data>
<DefaultData>CACRequestDefaultData</DefaultData>
<Type>%Storage.Persistent</Type>
}

}
