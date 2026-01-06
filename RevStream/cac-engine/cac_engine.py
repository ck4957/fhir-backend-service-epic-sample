#!/usr/bin/env python3
"""
CAC Engine - Computer-Assisted Coding Engine
A simulated NLP-based code extraction service that analyzes clinical text
and returns ICD-10 and CPT codes.

This is a standalone Flask service that can be called by the IRIS integration engine.
In production, this would be replaced by a proper CAC/NLP solution like:
- 3M CodeFinder
- Optum EncoderPro
- Nuance CDI
- Custom ML models
"""

from flask import Flask, request, jsonify
import re
from datetime import datetime
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CAC-Engine')

app = Flask(__name__)

# ICD-10-CM Code Mappings
ICD10_MAPPINGS = {
    # Appendicitis
    'appendicitis': [
        {'code': 'K35.80', 'description': 'Unspecified acute appendicitis', 'confidence': 95},
    ],
    'appendicitis peritoneal': [
        {'code': 'K35.33', 'description': 'Acute appendicitis with perforation and localized peritonitis', 'confidence': 92},
    ],
    'appendicitis abscess': [
        {'code': 'K35.33', 'description': 'Acute appendicitis with perforation and localized peritonitis', 'confidence': 90},
    ],
    
    # Pneumonia
    'pneumonia': [
        {'code': 'J18.9', 'description': 'Pneumonia, unspecified organism', 'confidence': 78},
    ],
    'bacterial pneumonia': [
        {'code': 'J15.9', 'description': 'Unspecified bacterial pneumonia', 'confidence': 85},
    ],
    'community-acquired pneumonia': [
        {'code': 'J18.9', 'description': 'Pneumonia, unspecified organism', 'confidence': 82},
    ],
    
    # Heart conditions
    'heart failure': [
        {'code': 'I50.9', 'description': 'Heart failure, unspecified', 'confidence': 80},
    ],
    'chf': [
        {'code': 'I50.9', 'description': 'Heart failure, unspecified', 'confidence': 82},
    ],
    'systolic heart failure': [
        {'code': 'I50.20', 'description': 'Unspecified systolic (congestive) heart failure', 'confidence': 88},
    ],
    'coronary artery disease': [
        {'code': 'I25.10', 'description': 'Atherosclerotic heart disease of native coronary artery', 'confidence': 85},
    ],
    
    # Diabetes
    'diabetes': [
        {'code': 'E11.9', 'description': 'Type 2 diabetes mellitus without complications', 'confidence': 75},
    ],
    'type 2 diabetes': [
        {'code': 'E11.9', 'description': 'Type 2 diabetes mellitus without complications', 'confidence': 90},
    ],
    
    # Hypertension
    'hypertension': [
        {'code': 'I10', 'description': 'Essential (primary) hypertension', 'confidence': 88},
    ],
    
    # Fractures
    'hip fracture': [
        {'code': 'S72.009A', 'description': 'Fracture of unspecified part of neck of femur, initial encounter', 'confidence': 85},
    ],
    'intertrochanteric fracture': [
        {'code': 'S72.141A', 'description': 'Displaced intertrochanteric fracture of right femur, initial encounter', 'confidence': 92},
    ],
    'wrist fracture': [
        {'code': 'S52.509A', 'description': 'Unspecified fracture of the lower end of radius, initial encounter', 'confidence': 85},
    ],
    
    # Other conditions
    'sepsis': [
        {'code': 'A41.9', 'description': 'Sepsis, unspecified organism', 'confidence': 80},
    ],
    'acute kidney injury': [
        {'code': 'N17.9', 'description': 'Acute kidney failure, unspecified', 'confidence': 82},
    ],
    'copd': [
        {'code': 'J44.9', 'description': 'Chronic obstructive pulmonary disease, unspecified', 'confidence': 85},
    ],
}

# CPT Code Mappings
CPT_MAPPINGS = {
    # Surgical procedures
    'laparoscopic appendectomy': [
        {'code': '44970', 'description': 'Laparoscopy, surgical, appendectomy', 'confidence': 95},
    ],
    'appendectomy': [
        {'code': '44950', 'description': 'Appendectomy', 'confidence': 88},
    ],
    'intramedullary nail': [
        {'code': '27245', 'description': 'Treatment of intertrochanteric, peritrochanteric, or subtrochanteric femoral fracture; with intramedullary implant', 'confidence': 92},
    ],
    'orif hip': [
        {'code': '27236', 'description': 'Open treatment of femoral fracture, proximal end, neck', 'confidence': 88},
    ],
    
    # Radiology
    'ct abdomen': [
        {'code': '74176', 'description': 'CT abdomen and pelvis without contrast', 'confidence': 85},
    ],
    'ct abdomen pelvis contrast': [
        {'code': '74177', 'description': 'CT abdomen and pelvis with contrast', 'confidence': 90},
    ],
    'chest x-ray': [
        {'code': '71046', 'description': 'Radiologic examination, chest; 2 views', 'confidence': 92},
    ],
    'ct head': [
        {'code': '70450', 'description': 'CT head/brain without contrast', 'confidence': 90},
    ],
    
    # E/M codes (would need more context in production)
    'hospital admission': [
        {'code': '99223', 'description': 'Initial hospital care, high complexity', 'confidence': 70},
    ],
    'discharge': [
        {'code': '99238', 'description': 'Hospital discharge day management; 30 minutes or less', 'confidence': 75},
    ],
}


def extract_codes(clinical_text: str) -> Dict[str, Any]:
    """
    Extract ICD-10 and CPT codes from clinical text using keyword matching.
    
    In production, this would use:
    - Named Entity Recognition (NER)
    - Medical concept extraction (UMLS, SNOMED)
    - Deep learning models trained on clinical data
    - Rule-based expert systems
    """
    text_lower = clinical_text.lower()
    extracted_codes = []
    seen_codes = set()
    
    # Extract ICD-10 codes
    for keyword, codes in ICD10_MAPPINGS.items():
        if keyword in text_lower:
            for code_info in codes:
                if code_info['code'] not in seen_codes:
                    extracted_codes.append({
                        'code': code_info['code'],
                        'description': code_info['description'],
                        'codeType': 'ICD10',
                        'codeSystem': 'ICD-10-CM',
                        'confidence': code_info['confidence'],
                        'source': 'CAC-NLP',
                        'matchedKeyword': keyword
                    })
                    seen_codes.add(code_info['code'])
    
    # Extract CPT codes
    for keyword, codes in CPT_MAPPINGS.items():
        if keyword in text_lower:
            for code_info in codes:
                if code_info['code'] not in seen_codes:
                    extracted_codes.append({
                        'code': code_info['code'],
                        'description': code_info['description'],
                        'codeType': 'CPT',
                        'codeSystem': 'CPT-4',
                        'confidence': code_info['confidence'],
                        'source': 'CAC-NLP',
                        'matchedKeyword': keyword
                    })
                    seen_codes.add(code_info['code'])
    
    # Sort by confidence (highest first)
    extracted_codes.sort(key=lambda x: x['confidence'], reverse=True)
    
    return extracted_codes


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'CAC-Engine',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/extract', methods=['POST'])
def extract_endpoint():
    """
    Main code extraction endpoint.
    
    Request body:
    {
        "patientId": "PAT001",
        "clinicalText": "Patient has acute appendicitis...",
        "documentType": "OPNOTE"
    }
    
    Response:
    {
        "status": "success",
        "patientId": "PAT001",
        "processingTime": 0.123,
        "codes": [
            {
                "code": "K35.80",
                "description": "Unspecified acute appendicitis",
                "codeType": "ICD10",
                "confidence": 95
            }
        ]
    }
    """
    try:
        start_time = datetime.now()
        
        # Parse request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        patient_id = data.get('patientId', 'UNKNOWN')
        clinical_text = data.get('clinicalText', '')
        document_type = data.get('documentType', 'UNKNOWN')
        
        if not clinical_text:
            return jsonify({
                'status': 'error',
                'message': 'No clinical text provided'
            }), 400
        
        logger.info(f"Processing request for patient: {patient_id}")
        logger.info(f"Document type: {document_type}")
        logger.info(f"Clinical text length: {len(clinical_text)} characters")
        
        # Extract codes
        codes = extract_codes(clinical_text)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Extracted {len(codes)} codes in {processing_time:.3f}s")
        for code in codes:
            logger.info(f"  - {code['code']}: {code['description']} ({code['confidence']}%)")
        
        return jsonify({
            'status': 'success',
            'patientId': patient_id,
            'documentType': document_type,
            'processingTime': processing_time,
            'timestamp': datetime.now().isoformat(),
            'codeCount': len(codes),
            'codes': codes
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/codes/icd10', methods=['GET'])
def list_icd10_codes():
    """List all supported ICD-10 codes."""
    codes = []
    for keyword, code_list in ICD10_MAPPINGS.items():
        for code_info in code_list:
            codes.append({
                'keyword': keyword,
                'code': code_info['code'],
                'description': code_info['description']
            })
    return jsonify({'codes': codes})


@app.route('/codes/cpt', methods=['GET'])
def list_cpt_codes():
    """List all supported CPT codes."""
    codes = []
    for keyword, code_list in CPT_MAPPINGS.items():
        for code_info in code_list:
            codes.append({
                'keyword': keyword,
                'code': code_info['code'],
                'description': code_info['description']
            })
    return jsonify({'codes': codes})


if __name__ == '__main__':
    logger.info("Starting CAC Engine...")
    logger.info("Supported ICD-10 keywords: " + ", ".join(ICD10_MAPPINGS.keys()))
    logger.info("Supported CPT keywords: " + ", ".join(CPT_MAPPINGS.keys()))
    app.run(host='0.0.0.0', port=5000, debug=True)
