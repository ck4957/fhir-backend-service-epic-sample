# RevStream Integration Pipeline

## CAC/CDI Interface Developer MVP Project

A complete end-to-end **Revenue Cycle Integration Pipeline** demonstrating healthcare integration skills using InterSystems IRIS for Health. This project simulates a production "Ensemble Production" that takes clinical notes, extracts medical codes using a CAC (Computer-Assisted Coding) engine, and routes financial transactions to a billing system.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RevStream Integration Pipeline                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   EHR    │───►│  HL7 TCP    │───►│   Message   │───►│   CAC Pipeline  │  │
│  │ (MDM^T02)│    │  Service    │    │   Router    │    │   (Code Extr.)  │  │
│  └──────────┘    │  Port:2021  │    └─────────────┘    └────────┬────────┘  │
│                  └─────────────┘           │                    │           │
│                                            │                    ▼           │
│                                            │           ┌─────────────────┐  │
│                                            │           │   CAC Engine    │  │
│                                            │           │  (Python/NLP)   │  │
│                                            │           └────────┬────────┘  │
│                                            │                    │           │
│                                            │                    ▼           │
│  ┌──────────┐    ┌─────────────┐    ┌──────┴──────┐    ┌─────────────────┐  │
│  │ Billing  │◄───│  HL7 TCP    │◄───│   DTL       │◄───│   DFT^P03      │  │
│  │ System   │    │  Operation  │    │  Transform  │    │   Financial     │  │
│  └──────────┘    │  Port:2022  │    └─────────────┘    └─────────────────┘  │
│                  └─────────────┘                                            │
│                                                                              │
│                         ┌─────────────────┐                                  │
│                         │  Error Handler  │──► Error Files + Alerts         │
│                         └─────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Features

### Business Components

| Component | Type | Description |
|-----------|------|-------------|
| `HL7.Inbound.Service` | Business Service | Receives HL7 v2 messages via MLLP/TCP on port 2021 |
| `Message.Router` | Business Process | Routes messages based on MSH-9 message type |
| `CAC.Pipeline` | Business Process | Extracts clinical text, calls CAC engine, transforms messages |
| `CAC.Engine` | Business Operation | Interfaces with Python-based code extraction service |
| `Billing.Output` | Business Operation | Sends DFT^P03 messages to downstream billing system |
| `Error.Handler` | Business Process | Handles invalid messages, logging, and alerting |

### Custom HL7 Schema

- **ZCD Segment**: Custom Coding Data (ICD-10, CPT codes from CAC engine)
- **ZCN Segment**: Clinical Note Extended Data (processing status, priority)

### CAC Engine

A Python Flask service that simulates Computer-Assisted Coding:
- Keyword-based NLP for code extraction
- ICD-10-CM and CPT-4 code mappings
- Confidence scoring
- REST API for integration

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- (Optional) InterSystems IRIS Studio or VS Code with ObjectScript extension

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd RevStream
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Access the IRIS Management Portal:**
   - URL: http://localhost:52773/csp/sys/UtilHome.csp
   - Username: `SuperUser`
   - Password: `SYS` (change on first login)

4. **Import the Production classes:**
   - Navigate to **System Explorer > Classes**
   - Import all `.cls` files from the `src/` directory
   - Compile the classes

5. **Start the Production:**
   - Navigate to **Interoperability > Configure > Production**
   - Select `RevStream.Production.RevStreamProduction`
   - Click **Start**

### Testing

**Send test HL7 messages:**
```bash
chmod +x scripts/send-test-message.sh
./scripts/send-test-message.sh
```

**Test individual samples:**
```bash
./scripts/send-test-message.sh samples/01_appendectomy.hl7
```

**Test the CAC Engine directly:**
```bash
chmod +x scripts/test-cac-engine.sh
./scripts/test-cac-engine.sh
```

---

## 📁 Project Structure

```
RevStream/
├── docker-compose.yml          # Container orchestration
├── setup.sh                    # One-click setup script
├── PLAN.md                     # Original project plan
├── README.md                   # This file
│
├── src/                        # InterSystems ObjectScript source
│   └── RevStream/
│       ├── DTL/
│       │   └── MDMtoDFT.cls           # Data Transformation Language
│       ├── Message/
│       │   ├── AlertMessage.cls        # Alert message class
│       │   ├── CACRequest.cls          # CAC request message
│       │   ├── CACResponse.cls         # CAC response message
│       │   ├── CodeItem.cls            # Individual code item
│       │   └── ErrorRecord.cls         # Error record message
│       ├── Operation/
│       │   ├── AlertOperation.cls      # Alert sender
│       │   ├── BillingOutput.cls       # Billing system output
│       │   ├── CACEngine.cls           # CAC engine interface
│       │   └── ErrorFileOutput.cls     # Error file writer
│       ├── Process/
│       │   ├── CACPipeline.cls         # Main CAC processing
│       │   ├── ErrorHandler.cls        # Error handling logic
│       │   └── MessageRouter.cls       # Message routing
│       ├── Production/
│       │   └── RevStreamProduction.cls # Production definition
│       ├── Rules/
│       │   └── MainRoutingRule.cls     # Routing rules
│       ├── Schema/
│       │   ├── Custom25.cls            # Custom schema class
│       │   ├── RevStream25.hl7         # Schema definition file
│       │   ├── ZCD.cls                 # ZCD segment class
│       │   └── ZCN.cls                 # ZCN segment class
│       └── Service/
│           └── HL7InboundService.cls   # HL7 TCP listener
│
├── samples/                    # Sample HL7 messages for testing
│   ├── 01_appendectomy.hl7           # Appendectomy operative note
│   ├── 02_pneumonia_discharge.hl7    # Pneumonia discharge summary
│   ├── 03_hip_fracture.hl7           # Hip fracture operative note
│   ├── 04_heart_failure_progress.hl7 # CHF progress note
│   ├── 05_missing_patient_id.hl7     # Error test case
│   └── 06_ct_scan_abdomen.hl7        # Radiology report
│
├── cac-engine/                 # Python CAC service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── cac_engine.py          # Main CAC service
│
├── billing-simulator/          # Mock billing system
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py              # MLLP receiver
│
├── hl7-sender/                 # Test message sender
│   ├── Dockerfile
│   ├── requirements.txt
│   └── sender.py              # MLLP sender
│
└── scripts/                    # Utility scripts
    ├── send-test-message.sh
    ├── import-classes.sh
    └── test-cac-engine.sh
```

---

## 🔧 Configuration

### Port Mapping

| Port | Service | Description |
|------|---------|-------------|
| 52773 | IRIS Management Portal | Web-based administration |
| 51773 | IRIS SuperServer | Studio/VS Code connections |
| 2021 | HL7 Inbound | Receives HL7 messages from EHR |
| 2022 | HL7 Outbound | Sends to billing system |
| 5000 | CAC Engine | REST API for code extraction |

### Environment Variables

```bash
# HL7 Sender
HL7_HOST=iris          # Target host for HL7 messages
HL7_PORT=2021          # Target port

# IRIS Connection
IRIS_HOST=localhost
IRIS_PORT=52773
NAMESPACE=USER
USERNAME=SuperUser
PASSWORD=SYS

# CAC Engine
CAC_HOST=localhost
CAC_PORT=5000
```

---

## 📊 Demonstrating the MVP

### 1. Visual Trace

In the IRIS Management Portal:
1. Navigate to **Interoperability > View > Message Viewer**
2. Search by Session ID or Patient ID
3. Click on a message to see the **Visual Trace**
4. Observe the message flow from inbound to outbound

### 2. Message Viewer

1. Navigate to **Interoperability > View > Messages**
2. Search for messages by:
   - Patient ID (PID-3)
   - Message Control ID (MSH-10)
   - Time range
   - Source/Target

### 3. Production Monitor

1. Navigate to **Interoperability > Monitor > Production Monitor**
2. View real-time status of all components
3. Check queue depths and throughput
4. Monitor for errors and alerts

### 4. Error Handling

Send the error test message:
```bash
./scripts/send-test-message.sh samples/05_missing_patient_id.hl7
```

Then check:
- Error logs in IRIS Event Log
- Error files in `./errors/` directory
- Alert messages in production logs

---

## 📝 Sample Data Flow

### Input: MDM^T02 (Operative Note)

```
MSH|^~\&|EHR|HOSPITAL|REVSTREAM|INTEGRATION|20240115120000||MDM^T02|MSG001|P|2.5
PID|1||PAT001^^^HOSPITAL^MR||DOE^JOHN^A||19800115|M
TXA|1|OP|TX|20240115120000|DOC001^SMITH^JANE
OBX|1|TX|PROCEDURE^Operative Note||Patient presents with acute appendicitis. 
    Laparoscopic appendectomy performed successfully.
```

### Processing

1. **Inbound Service** receives message on port 2021
2. **Message Router** identifies MDM message, routes to CAC Pipeline
3. **CAC Pipeline** extracts clinical text from OBX segments
4. **CAC Engine** analyzes text, extracts codes:
   - K35.80 (Acute appendicitis)
   - 44970 (Laparoscopic appendectomy)
5. **DTL Transform** creates DFT^P03 with extracted codes
6. **Billing Output** sends to billing system on port 2022

### Output: DFT^P03 (Financial Transaction)

```
MSH|^~\&|REVSTREAM|CAC|BILLING|FINANCIAL|20240115120100||DFT^P03|MSG002|P|2.5
PID|1||PAT001^^^HOSPITAL^MR||DOE^JOHN^A||19800115|M
FT1|1|||20240115120100|20240115120100|CG||||||K35.80^Acute appendicitis^ICD10
FT1|2|||20240115120100|20240115120100|CG||||||44970^Laparoscopic appendectomy^CPT
DG1|1||K35.80^Acute appendicitis^ICD10
```

---

## 🧪 Extending the Project

### Add FHIR Support

To add FHIR capabilities (as mentioned in the job description):

1. Add a FHIR Business Service
2. Transform MDM documents to `DocumentReference` FHIR resources
3. Use IRIS FHIR Server capabilities

### Add Real CAC Integration

Replace the simulated CAC engine with a production service:

1. Update `CACEngine.cls` to use HTTP adapter
2. Configure endpoint URL and authentication
3. Map vendor-specific response format

### Add Database Persistence

Store processed transactions in an SQL table:

1. Create persistent classes for transactions
2. Add database operations to the pipeline
3. Create reporting views

---

## 📚 Resources

- [InterSystems IRIS for Health Documentation](https://docs.intersystems.com/irisforhealthlatest/)
- [HL7 Version 2 Message Routing (Video)](https://www.youtube.com/watch?v=kwWioDry9YQ)
- [InterSystems Learning Portal](https://learning.intersystems.com/)
- [HL7 v2 Standard](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=185)

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 👤 Author

CAC/CDI Interface Developer MVP Project
