/// ZCD Segment - Custom Coding Data
/// Carries diagnostic and procedure codes extracted by the CAC engine
/// 
/// Fields:
///   ZCD-1: Set ID
///   ZCD-2: Code Type (ICD10, CPT, HCPCS)
///   ZCD-3: Code Value
///   ZCD-4: Code Description
///   ZCD-5: Confidence Score (0-100)
///   ZCD-6: Extraction Source (CAC, Manual, NLP)
///   ZCD-7: Timestamp
///   ZCD-8: Coding Professional ID
///
Class RevStream.Schema.ZCD Extends EnsLib.HL7.Segment
{

/// Segment code
Parameter Code = "ZCD";

/// Field definitions
XData MessageStructure
{
<Segment code="ZCD">
  <Field name="SetID" required="true" dataType="SI" length="4"/>
  <Field name="CodeType" required="true" dataType="ID" table="RevStream.ZCDCodeType" length="10"/>
  <Field name="CodeValue" required="true" dataType="ST" length="20"/>
  <Field name="CodeDescription" required="false" dataType="ST" length="200"/>
  <Field name="ConfidenceScore" required="false" dataType="NM" length="5"/>
  <Field name="ExtractionSource" required="false" dataType="ID" table="RevStream.ZCDSource" length="10"/>
  <Field name="Timestamp" required="false" dataType="TS" length="26"/>
  <Field name="CodingProfessionalID" required="false" dataType="XCN" length="250"/>
</Segment>
}

}
