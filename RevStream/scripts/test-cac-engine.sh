#!/bin/bash
#
# Test CAC Engine Script
# Tests the CAC Engine HTTP service with sample clinical text
#

set -e

CAC_HOST=${CAC_HOST:-localhost}
CAC_PORT=${CAC_PORT:-5000}

echo "=============================================="
echo "  CAC Engine Test"
echo "=============================================="
echo "Target: $CAC_HOST:$CAC_PORT"
echo ""

# Health check
echo "1. Health Check..."
curl -s "http://$CAC_HOST:$CAC_PORT/health" | python3 -m json.tool
echo ""

# Test appendicitis note
echo "2. Testing Appendicitis Operative Note..."
curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "patientId": "PAT001",
        "documentType": "OPNOTE",
        "clinicalText": "PREOPERATIVE DIAGNOSIS: Acute appendicitis with peritoneal abscess. POSTOPERATIVE DIAGNOSIS: Acute appendicitis with peritoneal abscess. PROCEDURE PERFORMED: Laparoscopic appendectomy."
    }' \
    "http://$CAC_HOST:$CAC_PORT/extract" | python3 -m json.tool
echo ""

# Test pneumonia discharge
echo "3. Testing Pneumonia Discharge Summary..."
curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "patientId": "PAT002",
        "documentType": "DCSUMMARY",
        "clinicalText": "DISCHARGE DIAGNOSIS: 1. Community-acquired bacterial pneumonia, resolved. 2. Type 2 diabetes mellitus, controlled. 3. Hypertension, controlled. Patient presented with community-acquired pneumonia and was treated with IV antibiotics."
    }' \
    "http://$CAC_HOST:$CAC_PORT/extract" | python3 -m json.tool
echo ""

# Test heart failure progress note
echo "4. Testing Heart Failure Progress Note..."
curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "patientId": "PAT003",
        "documentType": "PROGRESS",
        "clinicalText": "ASSESSMENT: 1. Acute on chronic systolic heart failure (CHF), decompensated. 2. Coronary artery disease. 3. Type 2 diabetes. Continue IV diuresis."
    }' \
    "http://$CAC_HOST:$CAC_PORT/extract" | python3 -m json.tool
echo ""

echo "=============================================="
echo "  Tests Complete"
echo "=============================================="
