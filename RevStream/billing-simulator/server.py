#!/usr/bin/env python3
"""
Billing System Simulator
Receives HL7 FT1 (Financial Transaction) messages via MLLP protocol
Simulates a downstream billing/financial system
"""

import socket
import os
import datetime
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

RECEIVED_DIR = Path('/app/received')
RECEIVED_DIR.mkdir(exist_ok=True)


def create_ack(message: str) -> bytes:
    """Create an HL7 ACK message for the received message."""
    lines = message.split('\r')
    msh = lines[0] if lines else ''
    
    # Parse MSH segment
    fields = msh.split('|')
    if len(fields) >= 10:
        sending_app = fields[2]
        sending_facility = fields[3]
        receiving_app = fields[4]
        receiving_facility = fields[5]
        msg_control_id = fields[9]
    else:
        sending_app = "UNKNOWN"
        sending_facility = "UNKNOWN"
        receiving_app = "BILLING"
        receiving_facility = "HOSPITAL"
        msg_control_id = "0"
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    ack = (
        f"MSH|^~\\&|{receiving_app}|{receiving_facility}|{sending_app}|{sending_facility}|"
        f"{timestamp}||ACK^P03|{msg_control_id}|P|2.5\r"
        f"MSA|AA|{msg_control_id}|Message received successfully\r"
    )
    
    return MLLP_START + ack.encode() + MLLP_END


def save_message(message: str):
    """Save received message to file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = RECEIVED_DIR / f"FT1_{timestamp}.hl7"
    
    with open(filename, 'w') as f:
        f.write(message)
    
    logger.info(f"Message saved to {filename}")
    return filename


def extract_message_info(message: str) -> dict:
    """Extract key information from HL7 message."""
    info = {
        'message_type': 'Unknown',
        'patient_id': 'Unknown',
        'codes': []
    }
    
    lines = message.split('\r')
    for line in lines:
        if line.startswith('MSH|'):
            fields = line.split('|')
            if len(fields) > 8:
                info['message_type'] = fields[8]
        elif line.startswith('PID|'):
            fields = line.split('|')
            if len(fields) > 3:
                info['patient_id'] = fields[3]
        elif line.startswith('FT1|'):
            fields = line.split('|')
            if len(fields) > 25:
                # FT1-25 is Procedure Code
                info['codes'].append(fields[24] if len(fields) > 24 else 'N/A')
    
    return info


def handle_client(conn, addr):
    """Handle incoming client connection."""
    logger.info(f"Connection from {addr}")
    
    buffer = b''
    
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            
            buffer += data
            
            # Check for complete MLLP message
            while MLLP_START in buffer and MLLP_END in buffer:
                start_idx = buffer.index(MLLP_START)
                end_idx = buffer.index(MLLP_END) + len(MLLP_END)
                
                # Extract message
                mllp_message = buffer[start_idx:end_idx]
                buffer = buffer[end_idx:]
                
                # Strip MLLP framing
                hl7_message = mllp_message[1:-2].decode('utf-8', errors='replace')
                
                logger.info("=" * 60)
                logger.info("RECEIVED HL7 MESSAGE:")
                logger.info("=" * 60)
                
                # Extract and log message info
                info = extract_message_info(hl7_message)
                logger.info(f"Message Type: {info['message_type']}")
                logger.info(f"Patient ID: {info['patient_id']}")
                logger.info(f"Procedure Codes: {info['codes']}")
                
                # Save message
                save_message(hl7_message)
                
                # Send ACK
                ack = create_ack(hl7_message)
                conn.send(ack)
                logger.info("ACK sent")
                logger.info("=" * 60)
                
    except Exception as e:
        logger.error(f"Error handling client: {e}")
    finally:
        conn.close()
        logger.info(f"Connection closed from {addr}")


def main():
    """Main server loop."""
    host = '0.0.0.0'
    port = 2022
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        logger.info(f"Billing System Simulator listening on {host}:{port}")
        logger.info("Waiting for FT1 (Financial Transaction) messages...")
        
        while True:
            conn, addr = server.accept()
            handle_client(conn, addr)
            
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        server.close()


if __name__ == '__main__':
    main()
