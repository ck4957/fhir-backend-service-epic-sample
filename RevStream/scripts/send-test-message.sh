#!/bin/bash
#
# Send Test HL7 Message Script
# Sends sample HL7 messages to the RevStream integration engine
#

set -e

HOST=${HL7_HOST:-localhost}
PORT=${HL7_PORT:-2021}
SAMPLE_DIR="./samples"

# MLLP frame characters
START_BLOCK=$(printf '\x0b')
END_BLOCK=$(printf '\x1c\x0d')

send_hl7_message() {
    local file=$1
    local content=$(cat "$file")
    
    echo "Sending: $(basename $file)"
    echo "----------------------------------------"
    
    # Send via netcat with MLLP framing
    response=$(echo -e "${START_BLOCK}${content}${END_BLOCK}" | nc -w 10 $HOST $PORT 2>/dev/null || echo "Connection failed")
    
    if [[ "$response" == *"MSA|AA"* ]]; then
        echo "✓ Message accepted (ACK received)"
    elif [[ "$response" == *"MSA|AE"* ]] || [[ "$response" == *"MSA|AR"* ]]; then
        echo "✗ Message rejected (NAK received)"
    elif [[ "$response" == "Connection failed" ]]; then
        echo "✗ Connection failed - is IRIS running?"
    else
        echo "? Unknown response"
    fi
    
    echo ""
}

echo "=============================================="
echo "  RevStream HL7 Message Sender"
echo "=============================================="
echo "Target: $HOST:$PORT"
echo ""

# Check if we have a specific file argument
if [ -n "$1" ]; then
    if [ -f "$1" ]; then
        send_hl7_message "$1"
    elif [ -f "$SAMPLE_DIR/$1" ]; then
        send_hl7_message "$SAMPLE_DIR/$1"
    else
        echo "ERROR: File not found: $1"
        exit 1
    fi
else
    # Send all sample messages
    echo "Sending all sample messages..."
    echo ""
    
    for file in $SAMPLE_DIR/*.hl7; do
        if [ -f "$file" ]; then
            send_hl7_message "$file"
            sleep 1
        fi
    done
fi

echo "=============================================="
echo "  Done!"
echo "=============================================="
