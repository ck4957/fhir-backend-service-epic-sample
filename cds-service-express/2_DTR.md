# Documentation Templates and Rules (DTR) Implementation Guide

## Overview
- Part of the Da Vinci project
- Focuses on capturing structured documentation to support ordering and prior authorization processes
- Uses FHIR Questionnaires and CQL (Clinical Quality Language) to define documentation requirements
- Aims to reduce burden on providers and improve efficiency in healthcare delivery

## Key Features
1. Dynamic form generation based on payer requirements
2. Integration with EHR systems through SMART on FHIR
3. Use of CQL to pre-populate forms with existing EHR data
4. Support for various documentation scenarios (orders, prior authorizations, etc.)

## FHIR Resources
- Uses FHIR R4
- Key resources: Questionnaire, QuestionnaireResponse, Library (for CQL), Task

## SMART on FHIR App
- Defines a SMART on FHIR app for rendering questionnaires and capturing responses
- Supports EHR Launch and Standalone Launch

## CQL Integration
- Uses CQL to define rules for extracting data from EHR
- Allows for dynamic pre-population of questionnaires

## Security and Privacy
- Leverages SMART on FHIR security model
- Supports OAuth 2.0 for authorization

## Questionnaire Design
- Provides guidelines for creating effective questionnaires
- Supports adaptive questionnaires based on user responses

## Data Persistence
- Defines methods for persisting captured data back to the EHR
- Supports creation of various FHIR resources based on questionnaire responses

## Use Cases
1. Documenting home oxygen therapy orders
2. Capturing information for medication prior authorization
3. Documenting durable medical equipment (DME) orders

## Implementation Considerations
- Integration with existing EHR workflows
- Handling of partially completed questionnaires
- Performance optimization for questionnaire rendering and submission