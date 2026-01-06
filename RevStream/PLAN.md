To build an MVP for a **CAC/CDI Interface Developer** role, you need to simulate a production "InterSystems Ensemble Production." Since you likely don't have a $10k InterSystems license at home, you can use **InterSystems IRIS for Health (Community Edition)**, which is free for developers and includes the same Ensemble-style integration engine features.

This MVP will demonstrate an **End-to-End Revenue Cycle Pipeline**: taking a clinical note, "extracting" it for a coding engine, and "loading" the resulting codes into a billing system.

---

## MVP Project: "RevStream" Integration Pipeline

### 1. The Architecture (InterSystems "Production")

In InterSystems terminology, your pipeline is called a **Production**. It consists of three parts:

| Component              | Role in MVP    | Technical Implementation                                                                                                       |
| ---------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Business Service**   | The "Listener" | `EnsLib.HL7.Service.TCPService` — Listens for incoming HL7 v2 messages (ADT or MDM) from an EHR.                               |
| **Business Process**   | The "Brain"    | `EnsLib.HL7.MsgRouter.RoutingEngine` — Uses **Routing Rules** to decide: "Is this a clinical note? Send it to the CAC engine." |
| **Business Operation** | The "Sender"   | `EnsLib.HL7.Operation.TCPOperation` — Sends the transformed "Coded" message to the Billing/Financial system.                   |

---

### 2. The Data Flow (ETL Plan)

#### **Step A: Extraction (HL7 v2 Ingest)**

- **Source:** Simulate an EHR sending an **MDM^T02** (Medical Document Management) message.
- **Segment of Interest:** The `OBX` or `TXA` segment containing the physician's clinical text.

#### **Step B: Transformation (DTL - Data Transformation Language)**

This is where you show off your "Interface Developer" skills. You will create a **DTL map** to:

1. Strip out the raw text from the clinical note.
2. (Optional/Simulated) Call a "CAC Python Script" that scans for keywords (e.g., "Appendicitis") and returns an **ICD-10 code** (e.g., `K35.80`).
3. Map that code into a new HL7 **FT1^P03** (Financial Transaction) message.

#### **Step C: Loading (Downstream Delivery)**

- **Destination:** Send the new `FT1` message to a file directory or a local TCP port (simulating the Billing system).

---

### 3. Development Milestones (2-Week Sprint)

#### **Phase 1: Environment Setup (Days 1-3)**

- Download **InterSystems IRIS for Health Community Edition** (Docker container is easiest).
- Install **HL7 Spy** or **MLLP Sender** (free tools) to "blast" sample HL7 messages at your local engine.

#### **Phase 2: Building the Production (Days 4-7)**

- Define a **Custom HL7 Schema**. (Healthcare systems often have "Z-segments"—non-standard data. Creating a custom schema shows you can handle "messy" real-world data).
- Build the **Routing Rule**: If `MSH:9.1 = "MDM"`, route to your Transformation process.

#### **Phase 3: The ETL Logic (Days 8-10)**

- Write a **DTL** that maps:
- `Source.{PID:PatientName.familyname}` → `Target.{PID:PatientName.familyname}`
- `Source.{TXA:DocumentType}` → Logic to determine the correct Billing Category.

#### **Phase 4: Error Handling & Logging (Days 11-14)**

- Implement a **"Bad Message" Handler**. If a message is missing a Patient ID (PID), the pipeline should catch it and move it to an "Error" folder rather than crashing.

---

### 4. Demonstrating the MVP

Since this is an "Interface" project, you won't have a flashy UI. Instead, your "Demo" is the **InterSystems Management Portal**:

1. **Visual Trace:** Show the "Visual Trace" diagram in IRIS that shows a message entering as a Note and exiting as a Charge.
2. **Message Viewer:** Show how you can search for a message by "Patient ID"—this is a core "support" task mentioned in the job description.
3. **Logs:** Show your "Alerting" logic for when a connection to the billing system is "down."

---

### Pro-Tool Tip: "SMART on FHIR" Bridge

To bridge your original FHIR interest with this HL7 job, add a **FHIR Service** to this production.

- **Requirement:** "Desirable integrations include FHIR."
- **Action:** Add an InterSystems **FHIR Business Service** that takes the same MDM note and saves it as a `DocumentReference` FHIR resource. This proves you are "future-ready."

[HL7 V2 Message Routing in InterSystems IRIS](https://www.youtube.com/watch?v=kwWioDry9YQ)

This video provides a deep dive into how InterSystems handles the "Routing" and "Transformation" steps described in the MVP architecture above.
