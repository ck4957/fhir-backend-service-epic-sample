"""Streamlit demo application for HL7/FHIR Transformation Agent."""

import json
import streamlit as st
import httpx

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="HL7/FHIR Transformation Agent",
    page_icon="🏥",
    layout="wide",
)

# Custom CSS for better layout
st.markdown("""
<style>
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 12px;
    }
    .agent-message {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .error-message {
        color: #ff4b4b;
    }
    .success-message {
        color: #00c853;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🏥 HL7/FHIR Transformation Agent")
st.markdown("Transform HL7v2 messages and C-CDA documents to FHIR R4")

# Sample messages
SAMPLE_HL7_ADT = """MSH|^~\\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20240115120000||ADT^A01|MSG00001|P|2.5.1
PID|1||123456789^^^HOSP^MR||DOE^JOHN^ADAM||19800515|M|||123 MAIN STREET^^ANYTOWN^CA^12345^USA||555-123-4567
NK1|1|DOE^JANE^M|SPO^Spouse|123 MAIN STREET^^ANYTOWN^CA^12345|555-123-4567
PV1|1|I|4EAST^401^A|E|||1234567^SMITH^ROBERT^MD||||MED|||||||I||||||||||||||||||||20240115100000
DG1|1|ICD10|R07.9^Chest pain, unspecified||20240115|A
AL1|1|DA|70618^Penicillin|SV|Anaphylaxis"""

SAMPLE_HL7_ORU = """MSH|^~\\&|LAB|FAC|EMR|FAC|20240115140000||ORU^R01|LAB001|P|2.5.1
PID|1||123456789^^^HOSP^MR||DOE^JOHN||19800515|M
OBR|1|ORD123|LAB123|24323-8^Comprehensive metabolic panel^LN|||20240115100000
OBX|1|NM|2345-7^Glucose^LN||95|mg/dL|70-100|N|||F
OBX|2|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.7-1.3|N|||F"""

SAMPLE_HL7_ZSEG = """MSH|^~\\&|BILLING|HOSPITAL|CLAIMS|PAYER|20240115160000||ADT^A01|BILL001|P|2.5.1
PID|1||123456789^^^HOSP^MR||DOE^JOHN^A||19800515|M|||123 MAIN ST^^ANYTOWN^CA^12345||555-123-4567
PV1|1|I|4EAST^401^A|E|||1234567^SMITH^ROBERT^MD||||MED|||||||I||||||||||||||||||||20240115100000
ZIN|1|PREMIUM|250.00|MONTHLY|20240101|ACH|****1234|CHECKING|ANYTOWN BANK|ACTIVE"""


def check_api_health():
    """Check if the API is running."""
    try:
        response = httpx.get(f"{API_BASE_URL}/", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def transform_message(content: str, input_type: str):
    """Call the transform API endpoint."""
    try:
        response = httpx.post(
            f"{API_BASE_URL}/transform",
            json={"content": content, "input_type": input_type, "validate": True},
            timeout=120.0,
        )
        return response.json()
    except httpx.ConnectError:
        return {"success": False, "error": "Cannot connect to API. Is it running?"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_message(content: str, input_type: str):
    """Call the parse API endpoint."""
    try:
        response = httpx.post(
            f"{API_BASE_URL}/parse",
            json={"content": content, "input_type": input_type},
            timeout=30.0,
        )
        return response.json()
    except httpx.ConnectError:
        return {"success": False, "error": "Cannot connect to API. Is it running?"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_fhir(bundle: dict):
    """Call the validate API endpoint."""
    try:
        response = httpx.post(
            f"{API_BASE_URL}/validate",
            json={"bundle": bundle},
            timeout=30.0,
        )
        return response.json()
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}


# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Status
    api_healthy = check_api_health()
    if api_healthy:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Not Running")
        st.info("Start the API with:\n```\nuvicorn src.api.app:app --reload\n```")
    
    st.divider()
    
    # Input type selection
    input_type = st.radio(
        "Input Format",
        ["hl7v2", "ccda"],
        format_func=lambda x: "HL7v2" if x == "hl7v2" else "C-CDA",
    )
    
    st.divider()
    
    # Sample messages
    st.header("📝 Sample Messages")
    
    if st.button("Load ADT^A01 (Admission)", use_container_width=True):
        st.session_state.input_message = SAMPLE_HL7_ADT
        st.session_state.input_type = "hl7v2"
    
    if st.button("Load ORU^R01 (Lab Results)", use_container_width=True):
        st.session_state.input_message = SAMPLE_HL7_ORU
        st.session_state.input_type = "hl7v2"
    
    if st.button("Load ADT with Z-Segment", use_container_width=True):
        st.session_state.input_message = SAMPLE_HL7_ZSEG
        st.session_state.input_type = "hl7v2"

# Initialize session state
if "input_message" not in st.session_state:
    st.session_state.input_message = SAMPLE_HL7_ADT
if "input_type" not in st.session_state:
    st.session_state.input_type = "hl7v2"
if "result" not in st.session_state:
    st.session_state.result = None
if "parsed" not in st.session_state:
    st.session_state.parsed = None

# Main content - Three column layout
col1, col2, col3 = st.columns([1, 1, 1])

# Column 1: Input
with col1:
    st.header("📥 Input")
    
    input_message = st.text_area(
        "HL7v2 Message or C-CDA Document",
        value=st.session_state.input_message,
        height=400,
        key="input_area",
    )
    
    col_parse, col_transform = st.columns(2)
    
    with col_parse:
        if st.button("🔍 Parse Only", use_container_width=True, disabled=not api_healthy):
            with st.spinner("Parsing..."):
                st.session_state.parsed = parse_message(input_message, input_type)
                st.session_state.result = None
    
    with col_transform:
        if st.button("🔄 Transform to FHIR", type="primary", use_container_width=True, disabled=not api_healthy):
            with st.spinner("Transforming... (this may take a minute)"):
                st.session_state.result = transform_message(input_message, input_type)
                st.session_state.parsed = None

# Column 2: Agent Reasoning
with col2:
    st.header("🤖 Agent Reasoning")
    
    if st.session_state.parsed:
        parsed = st.session_state.parsed
        if parsed.get("success"):
            st.success(f"✅ Parsed successfully")
            st.write(f"**Message Type:** {parsed.get('message_type', 'Unknown')}")
            st.write(f"**Segments Found:** {', '.join(parsed.get('segments', []))}")
            
            with st.expander("View Parsed Structure", expanded=True):
                st.json(parsed.get("parsed", {}))
        else:
            st.error(f"❌ Parse Error: {parsed.get('error')}")
    
    elif st.session_state.result:
        result = st.session_state.result
        
        # Show segments identified
        if result.get("segments_identified"):
            st.write("**Segments Identified:**")
            st.write(", ".join(result["segments_identified"]))
        
        # Show target resources
        if result.get("target_resources"):
            st.write("**Target FHIR Resources:**")
            st.write(", ".join(result["target_resources"]))
        
        st.divider()
        
        # Show agent messages (thought process)
        if result.get("agent_messages"):
            st.write("**Agent Thought Process:**")
            for msg in result["agent_messages"]:
                with st.container():
                    st.markdown(f'<div class="agent-message">{msg.get("content", "")}</div>', 
                               unsafe_allow_html=True)
        
        # Show validation results
        if result.get("validation_results"):
            st.divider()
            st.write("**Validation Results:**")
            val = result["validation_results"]
            
            if val.get("valid"):
                st.success("✅ FHIR validation passed")
            else:
                st.error("❌ FHIR validation failed")
            
            if val.get("errors"):
                with st.expander(f"Errors ({len(val['errors'])})", expanded=True):
                    for err in val["errors"]:
                        st.markdown(f'<span class="error-message">• {err}</span>', 
                                   unsafe_allow_html=True)
            
            if val.get("warnings"):
                with st.expander(f"Warnings ({len(val['warnings'])})"):
                    for warn in val["warnings"]:
                        st.warning(warn)
    else:
        st.info("Parse or transform a message to see the agent's reasoning here.")

# Column 3: FHIR Output
with col3:
    st.header("📤 FHIR Output")
    
    if st.session_state.result:
        result = st.session_state.result
        
        if result.get("success") and result.get("fhir_bundle"):
            # Validation status badge
            if result.get("is_valid"):
                st.success("✅ Valid FHIR R4 Bundle")
            else:
                st.warning("⚠️ Bundle has validation issues")
            
            # FHIR Bundle
            fhir_json = json.dumps(result["fhir_bundle"], indent=2)
            
            st.text_area(
                "FHIR Bundle JSON",
                value=fhir_json,
                height=400,
                key="fhir_output",
            )
            
            # Download button
            st.download_button(
                label="⬇️ Download FHIR Bundle",
                data=fhir_json,
                file_name="fhir_bundle.json",
                mime="application/json",
                use_container_width=True,
            )
            
            # Resource summary
            entries = result["fhir_bundle"].get("entry", [])
            if entries:
                st.divider()
                st.write("**Resources in Bundle:**")
                resource_counts = {}
                for entry in entries:
                    res_type = entry.get("resource", {}).get("resourceType", "Unknown")
                    resource_counts[res_type] = resource_counts.get(res_type, 0) + 1
                
                for res_type, count in sorted(resource_counts.items()):
                    st.write(f"• {res_type}: {count}")
        
        elif result.get("error"):
            st.error(f"❌ Transformation Error")
            st.write(result["error"])
        else:
            st.warning("No FHIR output generated")
    else:
        st.info("Transform a message to see the FHIR output here.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>HL7/FHIR Transformation Agent | Powered by LangGraph + GPT-4</small>
</div>
""", unsafe_allow_html=True)
