/// MDM to DFT Data Transformation
/// Transforms Medical Document Management (MDM^T02) messages
/// to Financial Transaction (DFT^P03) messages
///
/// This DTL demonstrates the core ETL logic:
///   1. Copy patient demographics from source
///   2. Transform document metadata to financial context
///   3. Map clinical codes to procedure codes
///
Class RevStream.DTL.MDMtoDFT Extends Ens.DataTransformDTL
{

Parameter IGNOREMISSINGSOURCE = 1;
Parameter REPORTERRORS = 1;
Parameter TREATEMPTYREPEATINGFIELDASNULL = 0;

/// Transform MDM^T02 to DFT^P03
XData DTL [ XMLNamespace = "http://www.intersystems.com/dtl" ]
{
<transform sourceClass='EnsLib.HL7.Message' targetClass='EnsLib.HL7.Message' 
           sourceDocType='2.5:MDM_T02' targetDocType='2.5:DFT_P03' create='new'>

<!-- MSH Segment: Message Header -->
<assign value='"^~\&amp;"' property='target.{MSH:2}' action='set' />
<assign value='"REVSTREAM"' property='target.{MSH:3}' action='set' />
<assign value='"CAC-ENGINE"' property='target.{MSH:4}' action='set' />
<assign value='"BILLING"' property='target.{MSH:5}' action='set' />
<assign value='"FINANCIAL"' property='target.{MSH:6}' action='set' />
<assign value='##class(Ens.Util.FunctionSet).CurrentDateTime("yyyyMMddHHmmss")' property='target.{MSH:7}' action='set' />
<assign value='"DFT^P03"' property='target.{MSH:9}' action='set' />
<assign value='"MSG"_$Random(999999)' property='target.{MSH:10}' action='set' />
<assign value='"P"' property='target.{MSH:11}' action='set' />
<assign value='"2.5"' property='target.{MSH:12}' action='set' />

<!-- EVN Segment: Event Type -->
<assign value='"P03"' property='target.{EVN:1}' action='set' />
<assign value='##class(Ens.Util.FunctionSet).CurrentDateTime("yyyyMMddHHmmss")' property='target.{EVN:2}' action='set' />

<!-- PID Segment: Patient Identification (Copy from source) -->
<assign value='source.{PID:1}' property='target.{PID:1}' action='set' />
<assign value='source.{PID:3}' property='target.{PID:3}' action='set' />
<assign value='source.{PID:5}' property='target.{PID:5}' action='set' />
<assign value='source.{PID:7}' property='target.{PID:7}' action='set' />
<assign value='source.{PID:8}' property='target.{PID:8}' action='set' />
<assign value='source.{PID:11}' property='target.{PID:11}' action='set' />
<assign value='source.{PID:13}' property='target.{PID:13}' action='set' />
<assign value='source.{PID:18}' property='target.{PID:18}' action='set' />

<!-- PV1 Segment: Patient Visit (Copy from source) -->
<assign value='source.{PV1:1}' property='target.{PV1:1}' action='set' />
<assign value='source.{PV1:2}' property='target.{PV1:2}' action='set' />
<assign value='source.{PV1:3}' property='target.{PV1:3}' action='set' />
<assign value='source.{PV1:4}' property='target.{PV1:4}' action='set' />
<assign value='source.{PV1:7}' property='target.{PV1:7}' action='set' />
<assign value='source.{PV1:10}' property='target.{PV1:10}' action='set' />
<assign value='source.{PV1:17}' property='target.{PV1:17}' action='set' />

<!-- FT1 Segment: Financial Transaction -->
<!-- Note: In production, codes would come from CAC engine response -->
<!-- This template creates a placeholder FT1 -->
<assign value='"1"' property='target.{FT1(1):1}' action='set' />
<assign value='##class(Ens.Util.FunctionSet).CurrentDateTime("yyyyMMddHHmmss")' property='target.{FT1(1):4}' action='set' />
<assign value='##class(Ens.Util.FunctionSet).CurrentDateTime("yyyyMMddHHmmss")' property='target.{FT1(1):5}' action='set' />
<assign value='"CG"' property='target.{FT1(1):6}' action='set' />
<assign value='"DOCUMENT REVIEW"' property='target.{FT1(1):7}' action='set' />
<assign value='source.{TXA:2}' property='target.{FT1(1):10}' action='set' />
<assign value='"1"' property='target.{FT1(1):13}' action='set' />

<!-- Map document type to billing category -->
<if condition='source.{TXA:2}="OP"'>
    <true>
        <assign value='"SURGICAL"' property='target.{FT1(1):20}' action='set' />
    </true>
    <false>
        <if condition='source.{TXA:2}="DS"'>
            <true>
                <assign value='"INPATIENT"' property='target.{FT1(1):20}' action='set' />
            </true>
            <false>
                <assign value='"GENERAL"' property='target.{FT1(1):20}' action='set' />
            </false>
        </if>
    </false>
</if>

</transform>
}

}
