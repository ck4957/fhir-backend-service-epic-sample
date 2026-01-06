/// ZCN Segment - Clinical Note Extended Data  
/// Extended clinical note metadata for CAC processing
///
/// Fields:
///   ZCN-1: Set ID
///   ZCN-2: Note Type (OPNOTE, DCSUMMARY, PROGRESS, HPI)
///   ZCN-3: Clinical Specialty
///   ZCN-4: DRG Category
///   ZCN-5: CAC Processing Status (PENDING, PROCESSED, REVIEW, COMPLETE)
///   ZCN-6: Priority (STAT, ROUTINE, LOW)
///   ZCN-7: Reviewer ID
///   ZCN-8: Review Timestamp
///
Class RevStream.Schema.ZCN Extends EnsLib.HL7.Segment
{

/// Segment code
Parameter Code = "ZCN";

/// Field definitions
XData MessageStructure
{
<Segment code="ZCN">
  <Field name="SetID" required="true" dataType="SI" length="4"/>
  <Field name="NoteType" required="true" dataType="ID" table="RevStream.ZCNNoteType" length="20"/>
  <Field name="ClinicalSpecialty" required="false" dataType="ST" length="50"/>
  <Field name="DRGCategory" required="false" dataType="ST" length="20"/>
  <Field name="CACProcessingStatus" required="false" dataType="ID" table="RevStream.ZCNStatus" length="15"/>
  <Field name="Priority" required="false" dataType="ID" table="RevStream.ZCNPriority" length="10"/>
  <Field name="ReviewerID" required="false" dataType="XCN" length="250"/>
  <Field name="ReviewTimestamp" required="false" dataType="TS" length="26"/>
</Segment>
}

}
