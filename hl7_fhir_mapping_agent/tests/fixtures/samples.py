"""Test fixtures for HL7 and FHIR samples."""

# Sample HL7v2 ADT^A01 message
SAMPLE_ADT_A01 = """MSH|^~\\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20240115120000||ADT^A01|MSG00001|P|2.5.1
PID|1||123456789^^^HOSP^MR||DOE^JOHN^ADAM||19800515|M|||123 MAIN STREET^^ANYTOWN^CA^12345^USA||555-123-4567
NK1|1|DOE^JANE^M|SPO^Spouse|123 MAIN STREET^^ANYTOWN^CA^12345|555-123-4567
PV1|1|I|4EAST^401^A|E|||1234567^SMITH^ROBERT^MD||||MED|||||||I||||||||||||||||||||20240115100000
DG1|1|ICD10|R07.9^Chest pain, unspecified||20240115|A
AL1|1|DA|70618^Penicillin|SV|Anaphylaxis"""

# Sample HL7v2 ORU^R01 message
SAMPLE_ORU_R01 = """MSH|^~\\&|LAB|FAC|EMR|FAC|20240115140000||ORU^R01|LAB001|P|2.5.1
PID|1||123456789^^^HOSP^MR||DOE^JOHN||19800515|M
OBR|1|ORD123|LAB123|24323-8^Comprehensive metabolic panel^LN|||20240115100000
OBX|1|NM|2345-7^Glucose^LN||95|mg/dL|70-100|N|||F
OBX|2|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.7-1.3|N|||F"""

# Sample FHIR Patient resource
SAMPLE_FHIR_PATIENT = {
    "resourceType": "Patient",
    "id": "example-patient",
    "identifier": [
        {
            "system": "http://hospital.example.org/mrn",
            "value": "123456789"
        }
    ],
    "name": [
        {
            "use": "official",
            "family": "Doe",
            "given": ["John", "Adam"]
        }
    ],
    "gender": "male",
    "birthDate": "1980-05-15",
    "address": [
        {
            "use": "home",
            "line": ["123 Main Street"],
            "city": "Anytown",
            "state": "CA",
            "postalCode": "12345",
            "country": "USA"
        }
    ],
    "telecom": [
        {
            "system": "phone",
            "value": "555-123-4567",
            "use": "home"
        }
    ]
}

# Sample FHIR Bundle
SAMPLE_FHIR_BUNDLE = {
    "resourceType": "Bundle",
    "type": "batch",
    "entry": [
        {
            "fullUrl": "urn:uuid:patient-1",
            "resource": SAMPLE_FHIR_PATIENT,
            "request": {
                "method": "POST",
                "url": "Patient"
            }
        }
    ]
}

# Sample FHIR Observation
SAMPLE_FHIR_OBSERVATION = {
    "resourceType": "Observation",
    "id": "example-glucose",
    "status": "final",
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "2345-7",
                "display": "Glucose [Mass/volume] in Serum or Plasma"
            }
        ]
    },
    "subject": {
        "reference": "Patient/example-patient"
    },
    "effectiveDateTime": "2024-01-15T14:00:00Z",
    "valueQuantity": {
        "value": 95,
        "unit": "mg/dL",
        "system": "http://unitsofmeasure.org",
        "code": "mg/dL"
    },
    "interpretation": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": "N",
                    "display": "Normal"
                }
            ]
        }
    ],
    "referenceRange": [
        {
            "low": {
                "value": 70,
                "unit": "mg/dL"
            },
            "high": {
                "value": 100,
                "unit": "mg/dL"
            }
        }
    ]
}
