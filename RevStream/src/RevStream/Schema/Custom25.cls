/// RevStream Custom HL7 2.5 Schema
/// Extends standard HL7 2.5 with custom Z-segments for CAC/CDI processing
/// 
/// Z-Segments defined:
///   ZCD - Custom Coding Data (carries ICD-10/CPT codes from CAC engine)
///   ZCN - Clinical Note Extended Data
///
Class RevStream.Schema.Custom25 Extends EnsLib.HL7.Schema
{

/// Schema category name
Parameter Category = "RevStream.2.5";

/// Base schema this extends
Parameter Base = "2.5";

}
