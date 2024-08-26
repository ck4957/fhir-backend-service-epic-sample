# Coverage Requirements Discovery (CRD) Implementation Guide

## Overview
- The Coverage Requirements Discovery (CRD) IG is part of the Da Vinci project
- It provides a way for payers to communicate coverage requirements to healthcare providers in real-time
- Uses CDS Hooks specification to query payers for coverage requirements
- Supports value-based care by ensuring that prior authorization requirements are met

## Key Features
1. Real-time query of payer systems for coverage requirements
2. Integration with clinical workflows in EHR and other clinical systems
3. Support for various types of requirements (documentation, rules, prior authorization)
4. Use of FHIR resources to represent clinical data

## Supported Hooks
1. appointment-book
2. encounter-start
3. encounter-discharge
4. order-select
5. order-sign
6. medication-prescribe

## FHIR Resources
- Uses FHIR R4
- Key resources: Patient, Coverage, ServiceRequest, DeviceRequest, MedicationRequest, Appointment, Encounter

## CDS Hooks Integration
- Uses CDS Hooks specification for real-time queries
- Extends CDS Hooks with additional prefetch templates and context requirements

## Security and Privacy
- Recommends SMART on FHIR authorization
- Supports OAuth 2.0 for authorization

## Testing and Certification
- Provides testing scripts and tools
- Defines conformance requirements for implementers

## Use Cases
1. Prior Authorization Requirements
2. Documentation Requirements
3. Coverage Requirements
4. Alternative Therapy Requirements

## Implementation Considerations
- Integration with EHR systems
- Payer system requirements
- handling of sensitive information
- performance and scalability considerations


# Coverage Requirements Discovery (CRD) Implementation Insights

## Key Points

1. CRD Response Mechanism:
   - Debate between using CDS Hooks cards vs. system actions
   - Preference for system actions to allow EHRs to automatically process responses without user intervention
   - Need for codifiable, discrete information in responses

2. CRD Request Content:
   - Should include: what's being ordered, ordering provider, rendering provider, and when
   - Service Request profile in FHIR is key for order details
   - Need for clear examples of real-world use cases using these resources

3. Denial Reasons:
   - Importance of codifiable, discrete reason codes for denials
   - Existing X12 external reason codes may be a starting point
   - Need for standardization and categorization of denial reasons

4. Provider Information:
   - Both ordering and rendering provider information is crucial
   - Supports scenarios like gold card programs for expedited approvals

5. Location Information:
   - Requested location is mandatory in the Service Request profile, which may be problematic in some scenarios

6. Coordination of Benefits:
   - Generally not needed for CRD, but may require further investigation

7. Delegated Services:
   - Need to consider scenarios where utilization management is delegated to third parties
   - Challenges in surfacing this information to providers when issues arise

8. Pharmacy Prior Authorizations:
   - Currently use different underlying specs (NCPDP)
   - Potential future integration into CRD workflow, but not currently in scope

9. Write-back Functionality:
   - Focus on defining what information the EHR needs to learn and track about prior authorization requests
   - Avoid generic "write-back" discussions; instead, focus on specific use cases and workflows

## Next Steps

1. Create end-to-end examples for major CRD workflows:
   - Getting to "yes" (approval)
   - Getting to "no" (denial)
   - Show all inputs and outputs
   - Identify assumptions made and potential gaps in the current spec

2. Review examples against the current CRD specification:
   - Identify areas where the spec may need clarification or expansion
   - Prepare feedback for the Da Vinci project based on findings

3. Consider follow-up discussions to review findings and propose improvements to the CRD specification

## Action Items

- Volunteers to collaborate on creating end-to-end CRD examples
- Schedule follow-up call to review examples and discuss findings (if there's interest)
- Prepare feedback for Da Vinci project based on example creation exercise