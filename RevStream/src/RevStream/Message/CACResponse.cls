/// CAC Response Message
/// Response from CAC Engine containing extracted codes
///
Class RevStream.Message.CACResponse Extends Ens.Response
{

/// Patient identifier
Property PatientID As %String(MAXLEN = 50);

/// Source message control ID
Property SourceMessageID As %String(MAXLEN = 100);

/// Processing status (SUCCESS, ERROR, PARTIAL)
Property Status As %String(MAXLEN = 20);

/// Error message if status is ERROR
Property ErrorMessage As %String(MAXLEN = 500);

/// Timestamp of processing
Property ProcessingTimestamp As %String;

/// List of extracted codes
Property Codes As list Of RevStream.Message.CodeItem;

Storage Default
{
<Data name="CACResponseDefaultData">
<Subscript>"CACResponse"</Subscript>
<Value name="1">
<Value>PatientID</Value>
</Value>
<Value name="2">
<Value>SourceMessageID</Value>
</Value>
<Value name="3">
<Value>Status</Value>
</Value>
<Value name="4">
<Value>ErrorMessage</Value>
</Value>
<Value name="5">
<Value>ProcessingTimestamp</Value>
</Value>
<Value name="6">
<Value>Codes</Value>
</Value>
</Data>
<DefaultData>CACResponseDefaultData</DefaultData>
<Type>%Storage.Persistent</Type>
}

}
