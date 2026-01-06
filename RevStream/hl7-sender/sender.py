#!/usr/bin/env python3
"""
HL7 Message Sender
Sends sample HL7 MDM^T02 messages to the InterSystems IRIS integration engine
"""

import socket
import os
import sys
import time
import logging
from pathlib import Path

# MLLP Frame characters
MLLP_START = b'\x0b'  # Vertical Tab
MLLP_END = b'\x1c\x0d'  # File Separator + Carriage Return

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SAMPLES_DIR = Path('/app/samples')


def send_hl7_message(host: str, port: int, message: str) -> str:
    """Send HL7 message via MLLP and return the response."""
    
    # Wrap message in MLLP frame
    mllp_message = MLLP_START + message.encode() + MLLP_END
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    
    try:
        logger.info(f"Connecting to {host}:{port}...")
        sock.connect((host, port))
        
        logger.info("Sending message...")
        sock.send(mllp_message)
        
        # Receive response
        response = b''
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data
            if MLLP_END in response:
                break
        
        # Strip MLLP framing from response
        if response:
            response = response.replace(MLLP_START, b'').replace(MLLP_END, b'')
            return response.decode('utf-8', errors='replace')
        
        return "No response received"
        
    except socket.timeout:
        return "Connection timed out"
    except ConnectionRefusedError:
        return "Connection refused - is the server running?"
    except Exception as e:
        return f"Error: {e}"
    finally:
        sock.close()


def load_sample_messages():
    """Load all sample HL7 messages from the samples directory."""
    messages = []
    
    if not SAMPLES_DIR.exists():
        logger.warning(f"Samples directory not found: {SAMPLES_DIR}")
        return messages
    
    for hl7_file in sorted(SAMPLES_DIR.glob('*.hl7')):
        with open(hl7_file, 'r') as f:
            content = f.read().strip()
            messages.append({
                'filename': hl7_file.name,
                'content': content
            })
    
    return messages


def main():
    """Main function to send sample messages."""
    # Default to IRIS container
    host = os.getenv('HL7_HOST', 'iris')
    port = int(os.getenv('HL7_PORT', '2021'))
    
    # Wait for IRIS to be ready
    logger.info("Waiting for IRIS to be ready...")
    time.sleep(10)
    
    # Load sample messages
    messages = load_sample_messages()
    
    if not messages:
        logger.info("No sample messages found. Creating default test message...")
        messages = [{
            'filename': 'default.hl7',
            'content': create_default_mdm_message()
        }]
    
    logger.info(f"Found {len(messages)} sample message(s)")
    
    for msg in messages:
        logger.info("=" * 60)
        logger.info(f"Sending: {msg['filename']}")
        logger.info("=" * 60)
        
        response = send_hl7_message(host, port, msg['content'])
        
        logger.info("Response:")
        logger.info(response)
        logger.info("")
        
        time.sleep(2)  # Wait between messages
    
    logger.info("All messages sent!")


def create_default_mdm_message() -> str:
    """Create a default MDM^T02 message for testing."""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    message = (
        f"MSH|^~\\&|EHR|HOSPITAL|REVSTREAM|INTEGRATION|{timestamp}||MDM^T02|MSG001|P|2.5\r"
        f"EVN|T02|{timestamp}\r"
        f"PID|1||PAT001^^^HOSPITAL^MR||DOE^JOHN^A||19800115|M|||123 MAIN ST^^ANYTOWN^ST^12345\r"
        f"PV1|1|I|MED^101^A|E|||DOC001^SMITH^JANE|||MED||||ADM\r"
        f"TXA|1|OP|TX|{timestamp}|DOC001^SMITH^JANE|{timestamp}||||DOC123||||||AU\r"
        f"OBX|1|TX|PROCEDURE^Operative Note||Patient presents with acute appendicitis. "
        f"Laparoscopic appendectomy performed successfully. "
        f"No complications observed. "
        f"Diagnosis: Acute appendicitis with peritoneal abscess.||\r"
    )
    
    return message


if __name__ == '__main__':
    main()
