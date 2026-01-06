/// RevStream Production Definition
/// Main Integration Production for the Revenue Cycle Pipeline
///
/// Components:
///   - HL7 Inbound Service: Receives MDM/ADT messages from EHR
///   - Message Router: Routes based on message type
///   - CAC Pipeline: Extracts codes from clinical notes
///   - Billing Output: Sends DFT messages to billing system
///   - Error Handler: Manages invalid messages
///
Class RevStream.Production.RevStreamProduction Extends Ens.Production
{

/// Production settings
XData ProductionDefinition
{
<Production Name="RevStream.Production.RevStreamProduction" 
            LogGeneralTraceEvents="true"
            TestingEnabled="true">
    
    <!-- ===================== -->
    <!-- BUSINESS SERVICES     -->
    <!-- ===================== -->
    
    <!-- HL7 Inbound Service - Receives HL7 messages from EHR -->
    <Item Name="HL7.Inbound.Service" 
          Category="Inbound" 
          ClassName="RevStream.Service.HL7InboundService" 
          PoolSize="1" 
          Enabled="true" 
          Foreground="false" 
          InactivityTimeout="0">
        <Setting Target="Adapter" Name="Port">2021</Setting>
        <Setting Target="Adapter" Name="StayConnected">-1</Setting>
        <Setting Target="Adapter" Name="JobPerConnection">1</Setting>
        <Setting Target="Host" Name="TargetConfigName">Message.Router</Setting>
        <Setting Target="Host" Name="MessageSchemaCategory">2.5</Setting>
    </Item>
    
    <!-- ===================== -->
    <!-- BUSINESS PROCESSES    -->
    <!-- ===================== -->
    
    <!-- Message Router - Routes messages based on type -->
    <Item Name="Message.Router" 
          Category="Routing" 
          ClassName="RevStream.Process.MessageRouter" 
          PoolSize="1" 
          Enabled="true" 
          Foreground="false" 
          InactivityTimeout="0">
        <Setting Target="Host" Name="CACPipelineTarget">CAC.Pipeline</Setting>
        <Setting Target="Host" Name="BillingTarget">Billing.Output</Setting>
        <Setting Target="Host" Name="ErrorHandlerTarget">Error.Handler</Setting>
    </Item>
    
    <!-- CAC Pipeline - Code extraction process -->
    <Item Name="CAC.Pipeline" 
          Category="Processing" 
          ClassName="RevStream.Process.CACPipeline" 
          PoolSize="1" 
          Enabled="true" 
          Foreground="false" 
          InactivityTimeout="0">
        <Setting Target="Host" Name="CACEngineTarget">CAC.Engine</Setting>
        <Setting Target="Host" Name="BillingTarget">Billing.Output</Setting>
    </Item>
    
    <!-- Error Handler - Handles invalid messages -->
    <Item Name="Error.Handler" 
          Category="Error" 
          ClassName="RevStream.Process.ErrorHandler" 
          PoolSize="1" 
          Enabled="true" 
          Foreground="false" 
          InactivityTimeout="0">
        <Setting Target="Host" Name="ErrorFileTarget">Error.FileOutput</Setting>
        <Setting Target="Host" Name="AlertTarget">Alert.Operation</Setting>
        <Setting Target="Host" Name="AlertingEnabled">1</Setting>
    </Item>
    
    <!-- ===================== -->
    <!-- BUSINESS OPERATIONS   -->
    <!-- ===================== -->
    
    <!-- CAC Engine - Code extraction operation -->
    <Item Name="CAC.Engine" 
          Category="Processing" 
          ClassName="RevStream.Operation.CACEngine" 
          PoolSize="1" 
          Enabled="true" 
          Foreground="false" 
          InactivityTimeout="0">
        <Setting Target="Host" Name="SimulationMode">1</Setting>
        <Setting Target="Host" Name="Timeout">30</Setting>
    </Item>
    
    <!-- Billing Output - Sends DFT to billing system -->
    <Item Name="Billing.Output" 
          Category="Outbound" 
          ClassName="RevStream.Operation.BillingOutput" 
          PoolSize="1" 
          Enabled="true" 
          Foreground="false" 
          InactivityTimeout="0">
        <Setting Target="Adapter" Name="IPAddress">billing-simulator</Setting>
        <Setting Target="Adapter" Name="Port">2022</Setting>
        <Setting Target="Adapter" Name="StayConnected">-1</Setting>
        <Setting Target="Host" Name="Timeout">30</Setting>
    </Item>
    
    <!-- Error File Output - Writes errors to file -->
    <Item Name="Error.FileOutput" 
          Category="Error" 
          ClassName="RevStream.Operation.ErrorFileOutput" 
          PoolSize="1" 
          Enabled="true" 
          Foreground="false" 
          InactivityTimeout="0">
        <Setting Target="Adapter" Name="FilePath">/home/irisowner/errors/</Setting>
    </Item>
    
    <!-- Alert Operation - Sends critical alerts -->
    <Item Name="Alert.Operation" 
          Category="Alert" 
          ClassName="RevStream.Operation.AlertOperation" 
          PoolSize="1" 
          Enabled="true" 
          Foreground="false" 
          InactivityTimeout="0">
        <Setting Target="Host" Name="ConsoleAlertEnabled">1</Setting>
    </Item>
    
</Production>
}

}
