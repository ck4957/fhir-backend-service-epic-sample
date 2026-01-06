/// Alert Message
/// Message for sending alerts about critical events
///
Class RevStream.Message.AlertMessage Extends Ens.Request
{

/// Alert type (CRITICAL, WARNING, INFO)
Property AlertType As %String(MAXLEN = 20);

/// Alert subject line
Property Subject As %String(MAXLEN = 200);

/// Alert message body
Property Message As %String(MAXLEN = 2000);

/// Timestamp
Property Timestamp As %String [ InitialExpression = {$ZDateTime($Horolog, 3)} ];

Storage Default
{
<Data name="AlertMessageDefaultData">
<Subscript>"AlertMessage"</Subscript>
<Value name="1">
<Value>AlertType</Value>
</Value>
<Value name="2">
<Value>Subject</Value>
</Value>
<Value name="3">
<Value>Message</Value>
</Value>
<Value name="4">
<Value>Timestamp</Value>
</Value>
</Data>
<DefaultData>AlertMessageDefaultData</DefaultData>
<Type>%Storage.Persistent</Type>
}

}
