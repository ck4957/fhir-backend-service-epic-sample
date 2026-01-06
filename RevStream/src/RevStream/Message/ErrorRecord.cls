/// Error Record Message
/// Contains details about a message processing error
///
Class RevStream.Message.ErrorRecord Extends Ens.Request
{

/// Original message control ID
Property OriginalMessageID As %String(MAXLEN = 100);

/// Message type (MSH-9)
Property MessageType As %String(MAXLEN = 50);

/// Patient ID (if available)
Property PatientID As %String(MAXLEN = 50);

/// Error reason
Property ErrorReason As %String(MAXLEN = 500);

/// Timestamp of error
Property ErrorTimestamp As %String;

/// Original message content
Property OriginalMessage As %String(MAXLEN = 32000);

Storage Default
{
<Data name="ErrorRecordDefaultData">
<Subscript>"ErrorRecord"</Subscript>
<Value name="1">
<Value>OriginalMessageID</Value>
</Value>
<Value name="2">
<Value>MessageType</Value>
</Value>
<Value name="3">
<Value>PatientID</Value>
</Value>
<Value name="4">
<Value>ErrorReason</Value>
</Value>
<Value name="5">
<Value>ErrorTimestamp</Value>
</Value>
<Value name="6">
<Value>OriginalMessage</Value>
</Value>
</Data>
<DefaultData>ErrorRecordDefaultData</DefaultData>
<Type>%Storage.Persistent</Type>
}

}
