# Prior Authorization Support (PAS) Implementation Guide

## Overview
- Part of the Da Vinci project
- Focuses on automating the prior authorization process
- Defines FHIR-based interactions for submitting, updating, and querying prior authorization requests
- Aims to reduce administrative burden and improve care delivery efficiency

## Key Features
1. FHIR-based prior authorization request and response
2. Support for attachments and additional documentation
3. Real-time status checks and updates
4. Integration with X12 278 transactions (through intermediaries)

## FHIR Resources
- Uses FHIR R4
- Key resources: Claim, ClaimResponse, Bundle, Task

## Operations
1. $submit: Submit a prior authorization request
2. $inquire: Check the status of a prior authorization
3. $poll: Retrieve updated prior authorization information

## Workflow
1. Initial submission of prior authorization request
2. Handling of pended requests and additional information
3. Updating and cancelling existing requests
4. Checking status and final determination

## Integration with X12
- Defines mapping between FHIR resources and X12 278 transactions
- Supports use of intermediaries for FHIR-to-X12 conversion

## Security and Privacy
- Recommends SMART on FHIR authorization
- Supports OAuth 2.0 for authorization

## Error Handling
- Defines error codes and handling procedures
- Supports partial acceptance/rejection of requests

## Use Cases
1. Medication prior authorization
2. Durable Medical Equipment (DME) authorization
3. Home health services authorization
4. Referral to specialists

## Implementation Considerations
- Integration with provider and payer systems
- Handling of attachments and supporting documentation
- Performance and scalability for high-volume transactions
- Compliance with regulatory requirements (e.g., CMS rules)