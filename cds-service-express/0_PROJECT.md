# Da Vinci Prior Authorization Project

## Project Overview
- Part of the HL7 Da Vinci project
- Aims to automate the prior authorization process using FHIR
- Involves multiple implementation guides: CRD, DTR, and PAS
- Focuses on reducing burden and improving efficiency in healthcare

## Key Components
1. Coverage Requirements Discovery (CRD)
2. Documentation Templates and Rules (DTR)
3. Prior Authorization Support (PAS)

## Technical Stack
- FHIR R4
- CDS Hooks
- SMART on FHIR
- OAuth 2.0
- Clinical Quality Language (CQL)

## GitHub Repository Contents
1. Reference Implementation
   - Demonstrates end-to-end prior authorization workflow
   - Includes sample applications for CRD, DTR, and PAS
2. Documentation
   - Setup instructions
   - User guides
   - API documentation
3. Docker Compose files
   - Facilitates easy deployment of the reference implementation
4. Test Data and Scripts
   - Sample FHIR resources
   - Test scenarios

## Implementation Resources
1. FHIR Servers
   - HAPI FHIR server for storing and retrieving FHIR resources
2. CDS Hooks Server
   - Implements CRD functionality
3. DTR SMART on FHIR App
   - Renders questionnaires and captures responses
4. PAS Server
   - Handles prior authorization requests and responses

## Integration Points
1. EHR Systems
   - Integration with CDS Hooks for CRD
   - SMART on FHIR launch for DTR
2. Payer Systems
   - Exposure of coverage requirements
   - Processing of prior authorization requests
3. Intermediaries
   - Conversion between FHIR and X12 formats

## Testing and Validation
1. Touchstone Testing Platform
   - Provides automated testing for implementation guide conformance
2. Connectathon Events
   - Allows for testing of implementations with multiple participants

## Current Status and Roadmap
- Continuous development and refinement of implementation guides
- Focus on real-world implementation and adoption
- Alignment with regulatory requirements (e.g., CMS Interoperability Rule)

## Get Involved
- Participation in HL7 Working Groups
- Contribution to GitHub repository
- Attendance at Connectathon events