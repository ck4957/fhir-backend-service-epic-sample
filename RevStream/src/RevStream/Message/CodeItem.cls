/// Code Item
/// Represents a single extracted code (ICD-10, CPT, etc.)
///
Class RevStream.Message.CodeItem Extends %SerialObject
{

/// The code value (e.g., K35.80, 44970)
Property Code As %String(MAXLEN = 20);

/// Code description
Property Description As %String(MAXLEN = 500);

/// Code type (ICD10, CPT, HCPCS, SNOMED)
Property CodeType As %String(MAXLEN = 20);

/// Code system (ICD-10-CM, CPT-4, etc.)
Property CodeSystem As %String(MAXLEN = 50);

/// Confidence score (0-100)
Property Confidence As %Integer;

/// Source of extraction (CAC, MANUAL, NLP)
Property Source As %String(MAXLEN = 20);

/// Is this a primary diagnosis/procedure
Property IsPrimary As %Boolean [ InitialExpression = 0 ];

Storage Default
{
<Data name="CodeItemState">
<Value name="1">
<Value>Code</Value>
</Value>
<Value name="2">
<Value>Description</Value>
</Value>
<Value name="3">
<Value>CodeType</Value>
</Value>
<Value name="4">
<Value>CodeSystem</Value>
</Value>
<Value name="5">
<Value>Confidence</Value>
</Value>
<Value name="6">
<Value>Source</Value>
</Value>
<Value name="7">
<Value>IsPrimary</Value>
</Value>
</Data>
<State>CodeItemState</State>
<Type>%Storage.Serial</Type>
}

}
