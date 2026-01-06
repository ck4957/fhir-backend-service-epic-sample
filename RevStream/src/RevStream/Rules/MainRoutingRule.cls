/// RevStream Routing Rules
/// Defines message routing logic based on HL7 message content
///
Class RevStream.Rules.MainRoutingRule Extends Ens.Rule.Definition
{

/// Routing rule definition
XData RuleDefinition [ XMLNamespace = "http://www.intersystems.com/rule" ]
{
<ruleDefinition alias="RevStream Main Routing">
<ruleSet name="Main Routing Rules" effectiveBegin="" effectiveEnd="">

    <!-- Rule 1: Route MDM messages to CAC Pipeline -->
    <rule name="Route MDM to CAC" disabled="false">
        <constraint name="msgClass" value="EnsLib.HL7.Message"/>
        <when condition="HL7.{MSH:9.1}=&quot;MDM&quot;">
            <send transform="" target="CAC.Pipeline"/>
            <return/>
        </when>
    </rule>
    
    <!-- Rule 2: Route DFT messages directly to Billing -->
    <rule name="Route DFT to Billing" disabled="false">
        <constraint name="msgClass" value="EnsLib.HL7.Message"/>
        <when condition="HL7.{MSH:9.1}=&quot;DFT&quot;">
            <send transform="" target="Billing.Output"/>
            <return/>
        </when>
    </rule>
    
    <!-- Rule 3: ADT messages - log and acknowledge -->
    <rule name="Handle ADT Messages" disabled="false">
        <constraint name="msgClass" value="EnsLib.HL7.Message"/>
        <when condition="HL7.{MSH:9.1}=&quot;ADT&quot;">
            <trace value="ADT message received and acknowledged"/>
            <return/>
        </when>
    </rule>
    
    <!-- Rule 4: Reject messages without Patient ID -->
    <rule name="Reject Missing PID" disabled="false">
        <constraint name="msgClass" value="EnsLib.HL7.Message"/>
        <when condition="HL7.{PID:3.1}=&quot;&quot;">
            <send transform="" target="Error.Handler"/>
            <return/>
        </when>
    </rule>
    
    <!-- Rule 5: Default - Unknown message types to Error Handler -->
    <rule name="Default Route" disabled="false">
        <constraint name="msgClass" value="EnsLib.HL7.Message"/>
        <otherwise>
            <trace value="Unknown message type - routing to error handler"/>
            <send transform="" target="Error.Handler"/>
        </otherwise>
    </rule>
    
</ruleSet>
</ruleDefinition>
}

}
