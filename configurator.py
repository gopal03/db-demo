import streamlit as st
import json
import os
import sys
import copy
import subprocess

# --- Page Config & Theme ---
st.set_page_config(
    layout="wide",
    page_title="Database Demo Configurator",
    page_icon="⚙️",
    initial_sidebar_state="collapsed"
)

# --- Premium Dark Glassmorphism CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #0A0B10;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
        --text-color: #F8FAFC !important;
        --primary-color: #6366F1 !important;
    }
    
    /* Remove unnecessary space at the top */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Input field containers */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
        border-color: #6366F1 !important;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Force white background and dark text on the actual input elements */
    input, textarea, select {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    /* Prevent browser autofill from turning inputs dark or breaking text color */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus,
    textarea:-webkit-autofill,
    textarea:-webkit-autofill:hover,
    textarea:-webkit-autofill:focus {
        -webkit-box-shadow: 0 0 0px 1000px #FFFFFF inset !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    /* Input Field Labels visibility (sitting outside on dark background) */
    label, p[data-testid="stWidgetLabel"] {
        color: #E2E8F0 !important;
        font-weight: 500 !important;
        font-size: 0.95em !important;
    }

    /* Help Tooltip Icon color and visibility */
    button[data-testid="stTooltipIconButton"] svg,
    div[data-testid="stTooltipIcon"] svg,
    .stTooltipIcon svg {
        color: #6366F1 !important;
        fill: #6366F1 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    button[data-testid="stTooltipIconButton"] svg path,
    div[data-testid="stTooltipIcon"] svg path {
        fill: #6366F1 !important;
        stroke: #6366F1 !important;
    }
    div[data-testid="stTooltipIcon"] button, [data-testid="stTooltipIconButton"] button {
        opacity: 1 !important;
        visibility: visible !important;
        background: transparent !important;
    }
    
    /* Tooltip popup bubble styling */
    div[role="tooltip"], div[data-baseweb="tooltip"] {
        background-color: #11131C !important;
        border: 1px solid #2A2D3D !important;
        color: #F8FAFC !important;
        box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.4) !important;
    }
    div[role="tooltip"] *, div[data-baseweb="tooltip"] * {
        color: #F8FAFC !important;
    }

    /* Color the Streamlit Slider track and thumb to Indigo */
    div[data-testid="stSlider"] [class*="thumb"],
    div[data-testid="stSlider"] [role="slider"] {
        background-color: #6366F1 !important;
    }
    div[data-testid="stSlider"] [class*="track"] > div {
        background-color: #6366F1 !important;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
        background-color: #6366F1 !important;
    }
    div[data-testid="stSlider"] span {
        color: #A5B4FC !important;
    }
    
    /* Dropdown selectboxes styling */
    div[data-baseweb="select"], [data-baseweb="select"] div {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        color: #0F172A !important;
    }
    
    /* Standard Button Customization */
    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.3) !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(79, 70, 229, 0.5) !important;
    }

    /* Download Button Customization */
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.3) !important;
        margin-top: 10px;
    }
    div.stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(16, 185, 129, 0.5) !important;
        color: #FFFFFF !important;
    }
    
    /* Visual Cards - Native Streamlit Container Override */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(22, 24, 37, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(4px) !important;
    }
    
    /* Force padding adjustments on stContainer */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 15px !important;
    }
    
    .gradient-header {
        font-size: 2.2em;
        font-weight: 800;
        background: linear-gradient(to right, #A5B4FC, #6366F1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .code-box {
        background-color: #0E0F16 !important;
        border: 1px solid #1F2130 !important;
        border-radius: 8px;
        padding: 16px;
        font-family: 'Courier New', Courier, monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def verify_gcp_access(project_id):
    try:
        # Run gcloud projects describe to verify authentication
        subprocess.run(
            ["gcloud", "projects", "describe", project_id, "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        return True, "GCP Access Verified!"
    except Exception:
        return False, "Could not access project. Verify that you ran 'gcloud auth login' and 'gcloud auth application-default login' and that your project ID is correct."

def run_command_live(cmd, cwd, console_placeholder):
    try:
        process = subprocess.Popen(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True
        )
        log_text = ""
        for line in iter(process.stdout.readline, ""):
            log_text += line
            # Keep only the last 150 lines to prevent UI lag
            lines = log_text.splitlines()
            if len(lines) > 150:
                log_text = "\n".join(lines[-150:]) + "\n"
            console_placeholder.code(log_text, language="bash")
        
        process.stdout.close()
        rc = process.wait()
        return rc
    except Exception as e:
        console_placeholder.error(f"Execution failed: {e}")
        return -1

def get_dynamic_defaults(product, customer_name, industry):
    def clean_name(val):
        return "".join(c if c.isalnum() else "-" for c in val.lower()).strip("-")
        
    cust_clean = clean_name(customer_name) if customer_name else "demo"
    ind_clean = clean_name(industry) if industry else "general"
    
    # Target suffix
    suffix = f"{cust_clean}-{ind_clean}"[:30].strip("-")
    
    defaults = {}
    if product == "spanner":
        defaults = {
            "instance_id": f"spanner-instance-{suffix}",
            "database_id": f"spanner-db-{suffix}",
            "instance_config": "regional-us-central1",
            "node_count": 1,
            "processing_units": 0,
            "edition": "ENTERPRISE"
        }
    elif product == "alloydb":
        defaults = {
            "cluster_id": f"alloydb-cluster-{suffix}",
            "instance_id": f"alloydb-primary-{suffix}",
            "database_id": "postgres",
            "network_name": "default"
        }
    elif product == "cloudsql":
        defaults = {
            "instance_id": f"cloudsql-db-{suffix}",
            "database_id": "postgres",
            "database_version": "POSTGRES_15",
            "tier": "db-f1-micro",
            "db_username": "postgres",
            "db_password": f"postgres_pwd_{cust_clean[:10]}"
        }
    elif product == "bigtable":
        defaults = {
            "instance_id": f"bigtable-instance-{suffix}",
            "cluster_id": f"bigtable-cluster-{suffix}",
            "zone": "us-central1-a",
            "storage_type": "SSD"
        }
    elif product == "firestore":
        defaults = {
            "database_id": f"firestore-db-{suffix[:20]}",
            "type": "FIRESTORE_NATIVE",
            "location_id": "nam5"
        }
    elif product == "memorystore":
        defaults = {
            "instance_id": f"redis-instance-{suffix}",
            "tier": "BASIC",
            "memory_size_gb": 1,
            "network_name": "default"
        }
    return defaults

def prepare_tf_vars(params, target_db):
    db_configs = params.get("database_configs", {})
    db_config = db_configs.get(target_db, {})
    
    tf_vars = copy.deepcopy(db_config)
    tf_vars["project_id"] = params["project_id"]
    
    tf_dir = f"terraform/{target_db}"
    os.makedirs(tf_dir, exist_ok=True)
    tf_vars_path = os.path.join(tf_dir, "terraform.tfvars.json")
    
    with open(tf_vars_path, "w") as f:
        json.dump(tf_vars, f, indent=2)
    return tf_dir

def get_project_id():
    # Try environment variable first
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    if project:
        return project
    # Fallback: Try GCE Metadata server
    try:
        import requests
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
            timeout=1
        )
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        pass
    return ""

# --- Header ---
st.markdown('<div class="gradient-header">Database Demo Configurator</div>', unsafe_allow_html=True)
st.markdown("Configure and interactively launch database demos in your sandbox GCP project.")
st.markdown("---")

# --- Top Section: Inputs ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    with st.container(border=True):
        st.subheader("1. General Configuration")
        
        default_project = get_project_id()
        argolis_project = st.text_input(
            "GCP Project ID",
            value=default_project,
            placeholder="e.g., gopal-sandbox-project",
            help="The sandbox GCP project where database resources will be deployed."
        )
        
        is_auth_ok = False
        if argolis_project:
            with st.spinner("Checking GCP authentication..."):
                success, auth_msg = verify_gcp_access(argolis_project)
                if success:
                    st.success(f"✔️ {auth_msg}")
                    is_auth_ok = True
                else:
                    st.error(f"❌ {auth_msg}")
                    st.info("💡 Run these commands in your shell to authenticate:\n```bash\ngcloud auth login\ngcloud auth application-default login\n```")
        
        customer_name = st.text_input(
            "Customer Name",
            placeholder="e.g., Acme Retail Group",
            help="The client organization you are presenting to."
        )
        
        product = st.selectbox(
            "Target Database Product",
            options=["spanner", "alloydb", "cloudsql", "bigtable", "firestore", "memorystore"],
            format_func=lambda x: x.upper()
        )
        
        # Industry handling (with Other support)
        industry_options = ["Retail", "Financial Services", "Healthcare", "Gaming", "Cybersecurity", "Telecommunications", "Other (Enter Custom...)"]
        selected_industry = st.selectbox("Industry", options=industry_options)
        
        if selected_industry == "Other (Enter Custom...)":
            industry = st.text_input("Enter Custom Industry", placeholder="e.g., Manufacturing")
        else:
            industry = selected_industry

with col2:
    with st.container(border=True):
        st.subheader("2. Demo Scope & Scale")
        
        use_case = st.text_area(
            "Use Case Description",
            placeholder="Describe the application / business logic being simulated."
        )
        
        additional_context = st.text_area(
            "Additional Context / Notes",
            placeholder="Add special setup requirements or focus features."
        )
        
        dataset_size = st.select_slider(
            "Dataset Size / Scale Profile",
            options=["small", "medium", "large"],
            value="small",
            help="""Scale Profile Guide:
- Small: ~10MB (Fast provisioning; perfect for local validation / dry-runs)
- Medium: ~500MB (Frictionless scale for customer POCs / live demos)
- Large: ~5GB (Production-scale workloads showing concurrency and latency checks)"""
        )

# Session State resetting logic for Advanced Settings when active triggers change
trigger_key = f"{product}_{customer_name}_{industry}"
if "last_trigger_key" not in st.session_state or st.session_state.last_trigger_key != trigger_key:
    st.session_state.last_trigger_key = trigger_key
    # Force reset of the advanced keys to load the new dynamic defaults
    for k in ["tf_instance_id", "tf_database_id", "tf_cluster_id", "tf_instance_config", "tf_node_count", "tf_edition", "tf_network_name", "tf_database_version", "tf_tier", "tf_db_username", "tf_db_password", "tf_zone", "tf_storage_type", "tf_location_id", "tf_type", "tf_memory_size_gb"]:
        if k in st.session_state:
            del st.session_state[k]

# --- Read Default Parameters template from Workspace ---
PARAMS_TEMPLATE_PATH = "config/demo_parameters.json"

try:
    with open(PARAMS_TEMPLATE_PATH, "r") as f:
        params_template = json.load(f)
except Exception:
    params_template = {}

# --- Bottom Section: Outputs (Conditionally Visible) ---
if argolis_project and customer_name and is_auth_ok:
    st.markdown("---")
    
    # Map to standardized use-case config paths based on industry and product selection
    config_mappings = {
        ("retail", "spanner"): "config/use_cases/retail_marketing/use_case_config.json",
        ("retail", "bigtable"): "config/use_cases/retail_marketing/bigtable/use_case_config.json",
        ("financial services", "spanner"): "config/use_cases/financial_services_antimoney_laundering/use_case_config.json",
        ("cybersecurity", "spanner"): "config/use_cases/cybersecurity_fraud_detection/spanner/use_case_config.json",
        ("gaming", "alloydb"): "config/use_cases/gaming_analytics/use_case_config.json",
    }
    selected_key = (industry.lower(), product.lower())
    use_case_config_path = config_mappings.get(selected_key, "config/use_cases/retail_marketing/use_case_config.json")
    
    use_case_dir = os.path.dirname(use_case_config_path) if use_case_config_path else "config"
    use_case_params_path = os.path.join(use_case_dir, "active_parameters.json")
    
    # --- Persistence Logic: Load existing parameters for this specific use-case if present ---
    # Otherwise, start with a fresh template copy
    active_params = copy.deepcopy(params_template)
    if os.path.exists(use_case_params_path):
        try:
            with open(use_case_params_path, "r") as f:
                loaded_params = json.load(f)
                # Verify loaded params matches target database, else discard (stale config)
                if loaded_params.get("target_database") == product:
                    active_params = loaded_params
        except Exception:
            pass
            
    active_params["project_id"] = argolis_project
    active_params["target_database"] = product
    
    if "demo_context" not in active_params:
        active_params["demo_context"] = {}
    active_params["demo_context"]["customer_name"] = customer_name
    active_params["demo_context"]["industry"] = industry
    active_params["demo_context"]["use_case"] = use_case if use_case else "Database Demo"
    active_params["demo_context"]["use_case_config"] = use_case_config_path
    
    if "data_config" not in active_params:
        active_params["data_config"] = {}
    active_params["data_config"]["profile"] = dataset_size
    active_params["data_config"]["additional_context"] = additional_context
    
    # --- Advanced Database Settings Expandable Panel ---
    with st.expander("🛠️ Advanced Database Settings", expanded=False):
        st.markdown("Customize database resource identifiers, sizes, and credentials if needed.")
        
        dyn_defaults = get_dynamic_defaults(product, customer_name, industry)
        db_config_existing = active_params.get("database_configs", {}).get(product, {})
        
        # Spanner Inputs
        if product == "spanner":
            sp_instance_id = st.text_input(
                "Instance ID",
                value=db_config_existing.get("instance_id", dyn_defaults.get("instance_id")),
                key="tf_instance_id"
            )
            sp_database_id = st.text_input(
                "Database ID",
                value=db_config_existing.get("database_id", dyn_defaults.get("database_id")),
                key="tf_database_id"
            )
            sp_config = st.text_input(
                "Instance Config",
                value=db_config_existing.get("instance_config", dyn_defaults.get("instance_config")),
                key="tf_instance_config"
            )
            sp_edition = st.selectbox(
                "Spanner Edition",
                options=["ENTERPRISE", "ENTERPRISE_PLUS"],
                index=0 if db_config_existing.get("edition", dyn_defaults.get("edition")) == "ENTERPRISE" else 1,
                key="tf_edition"
            )
            sp_nodes = st.number_input(
                "Node Count",
                min_value=1,
                max_value=10,
                value=int(db_config_existing.get("node_count", dyn_defaults.get("node_count", 1))),
                key="tf_node_count"
            )
            
            active_params["database_configs"] = {
                "spanner": {
                    "instance_id": sp_instance_id,
                    "database_id": sp_database_id,
                    "instance_config": sp_config,
                    "edition": sp_edition,
                    "node_count": sp_nodes,
                    "processing_units": 0
                }
            }
            
        elif product == "alloydb":
            al_cluster_id = st.text_input(
                "Cluster ID",
                value=db_config_existing.get("cluster_id", dyn_defaults.get("cluster_id")),
                key="tf_cluster_id"
            )
            al_instance_id = st.text_input(
                "Primary Instance ID",
                value=db_config_existing.get("instance_id", dyn_defaults.get("instance_id")),
                key="tf_instance_id"
            )
            al_db_id = st.text_input(
                "Database ID",
                value=db_config_existing.get("database_id", dyn_defaults.get("database_id")),
                key="tf_database_id"
            )
            al_network = st.text_input(
                "VPC Network Name",
                value=db_config_existing.get("network_name", dyn_defaults.get("network_name")),
                key="tf_network_name"
            )
            
            active_params["database_configs"] = {
                "alloydb": {
                    "cluster_id": al_cluster_id,
                    "instance_id": al_instance_id,
                    "database_id": al_db_id,
                    "network_name": al_network
                }
            }
            
        elif product == "cloudsql":
            cs_instance_id = st.text_input(
                "Instance ID",
                value=db_config_existing.get("instance_id", dyn_defaults.get("instance_id")),
                key="tf_instance_id"
            )
            cs_db_id = st.text_input(
                "Database ID",
                value=db_config_existing.get("database_id", dyn_defaults.get("database_id")),
                key="tf_database_id"
            )
            cs_version = st.text_input(
                "Database Version",
                value=db_config_existing.get("database_version", dyn_defaults.get("database_version")),
                key="tf_database_version"
            )
            cs_tier = st.text_input(
                "Machine Tier",
                value=db_config_existing.get("tier", dyn_defaults.get("tier")),
                key="tf_tier"
            )
            cs_username = st.text_input(
                "Database Username",
                value=db_config_existing.get("db_username", dyn_defaults.get("db_username")),
                key="tf_db_username"
            )
            cs_password = st.text_input(
                "Database Password",
                value=db_config_existing.get("db_password", dyn_defaults.get("db_password")),
                key="tf_db_password",
                type="password"
            )
            
            active_params["database_configs"] = {
                "cloudsql": {
                    "instance_id": cs_instance_id,
                    "database_id": cs_db_id,
                    "database_version": cs_version,
                    "tier": cs_tier,
                    "db_username": cs_username,
                    "db_password": cs_password
                }
            }
            
        elif product == "bigtable":
            bt_instance_id = st.text_input(
                "Instance ID",
                value=db_config_existing.get("instance_id", dyn_defaults.get("instance_id")),
                key="tf_instance_id"
            )
            bt_cluster_id = st.text_input(
                "Cluster ID",
                value=db_config_existing.get("cluster_id", dyn_defaults.get("cluster_id")),
                key="tf_cluster_id"
            )
            bt_zone = st.text_input(
                "Zone",
                value=db_config_existing.get("zone", dyn_defaults.get("zone")),
                key="tf_zone"
            )
            bt_storage = st.selectbox(
                "Storage Type",
                options=["SSD", "HDD"],
                index=0 if db_config_existing.get("storage_type", dyn_defaults.get("storage_type")) == "SSD" else 1,
                key="tf_storage_type"
            )
            
            active_params["database_configs"] = {
                "bigtable": {
                    "instance_id": bt_instance_id,
                    "cluster_id": bt_cluster_id,
                    "zone": bt_zone,
                    "storage_type": bt_storage
                }
            }
            
        elif product == "firestore":
            fs_database_id = st.text_input(
                "Database ID",
                value=db_config_existing.get("database_id", dyn_defaults.get("database_id")),
                key="tf_database_id"
            )
            fs_type = st.text_input(
                "Database Type",
                value=db_config_existing.get("type", dyn_defaults.get("type")),
                key="tf_type"
            )
            fs_location = st.text_input(
                "Location ID",
                value=db_config_existing.get("location_id", dyn_defaults.get("location_id")),
                key="tf_location_id"
            )
            
            active_params["database_configs"] = {
                "firestore": {
                    "database_id": fs_database_id,
                    "type": fs_type,
                    "location_id": fs_location
                }
            }
            
        elif product == "memorystore":
            ms_instance_id = st.text_input(
                "Instance ID",
                value=db_config_existing.get("instance_id", dyn_defaults.get("instance_id")),
                key="tf_instance_id"
            )
            ms_tier = st.selectbox(
                "Service Tier",
                options=["BASIC", "STANDARD_HA"],
                index=0 if db_config_existing.get("tier", dyn_defaults.get("tier")) == "BASIC" else 1,
                key="tf_tier"
            )
            ms_memory = st.number_input(
                "Memory Capacity (GB)",
                min_value=1,
                max_value=10,
                value=int(db_config_existing.get("memory_size_gb", dyn_defaults.get("memory_size_gb", 1))),
                key="tf_memory_size_gb"
            )
            ms_network = st.text_input(
                "VPC Network Name",
                value=db_config_existing.get("network_name", dyn_defaults.get("network_name")),
                key="tf_network_name"
            )
            
            active_params["database_configs"] = {
                "memorystore": {
                    "instance_id": ms_instance_id,
                    "tier": ms_tier,
                    "memory_size_gb": ms_memory,
                    "network_name": ms_network
                }
            }
            
    # Filter Data Config Profiles: Keep only the selected profile inside active_params
    # (Leaving templates unchanged)
    if "data_config" in active_params and "profiles" in active_params["data_config"]:
        filtered_profiles = {}
        if dataset_size in active_params["data_config"]["profiles"]:
            filtered_profiles[dataset_size] = active_params["data_config"]["profiles"][dataset_size]
        active_params["data_config"]["profiles"] = filtered_profiles

    json_str = json.dumps(active_params, indent=2)
    
    # Save the custom active configurations inside the use-case specific directory
    os.makedirs(use_case_dir, exist_ok=True)
    with open(use_case_params_path, "w") as f:
        json.dump(active_params, f, indent=2)
        
    out_col1, out_col2 = st.columns([1, 1], gap="large")
    
    with out_col1:
        st.markdown("### 3. Generated Configurations")
        with st.container(border=True):
            st.subheader("`active_parameters.json` Preview")
            st.code(json_str, language="json")
            
            st.download_button(
                label="📥 Download active_parameters.json",
                data=json_str,
                file_name="active_parameters.json",
                mime="application/json"
            )
            
    with out_col2:
        st.markdown("### 4. Interactive Deployment Panel")
        
        # Clean use case name for state file
        use_case_clean = (use_case if use_case else "database_demo").lower().replace(" ", "_").replace("/", "_")
        
        # --- Step 1: Terraform Deployment ---
        with st.container(border=True):
            st.markdown("#### **Step 4.1: Provision Infrastructure (Terraform)**")
            st.markdown(f"Deploy the regional **{product.upper()}** resources inside `{argolis_project}`.")
            
            tf_console = st.empty()
            if st.button("🚀 Provision Infrastructure", key="btn_tf"):
                with st.spinner("Initializing and deploying resources..."):
                    tf_dir = prepare_tf_vars(active_params, product)
                    tf_console.info("Preparing local variables and running terraform apply...")
                    
                    # Run init & apply with isolated state file
                    cmd = f"terraform init && terraform apply -state=\"state_{use_case_clean}.tfstate\" -auto-approve"
                    rc = run_command_live(cmd, tf_dir, tf_console)
                    
                    if rc == 0:
                        # Capture TF output to retrieve the dynamic database host IP
                        try:
                            output_cmd = f"terraform output -json -state=\"state_{use_case_clean}.tfstate\""
                            out_proc = subprocess.run(
                                output_cmd,
                                shell=True,
                                cwd=tf_dir,
                                capture_output=True,
                                text=True
                            )
                            if out_proc.returncode == 0:
                                tf_outputs = json.loads(out_proc.stdout)
                                db_host_ip = tf_outputs.get("db_host_ip", {}).get("value")
                                if db_host_ip:
                                    # Update the local active params dict
                                    if "database_configs" not in active_params:
                                        active_params["database_configs"] = {}
                                    if product not in active_params["database_configs"]:
                                        active_params["database_configs"][product] = {}
                                    
                                    active_params["database_configs"][product]["host"] = db_host_ip
                                    
                                    # Save updated parameters back to active_parameters.json
                                    with open(use_case_params_path, "w") as f:
                                        json.dump(active_params, f, indent=2)
                                    tf_console.success(f"✔️ Infrastructure deployed successfully! Captured Database Host IP: {db_host_ip}")
                                else:
                                    tf_console.success("✔️ Infrastructure deployed successfully!")
                            else:
                                tf_console.success("✔️ Infrastructure deployed successfully! (Warning: Failed to read Terraform outputs)")
                        except Exception as out_err:
                            tf_console.success(f"✔️ Infrastructure deployed successfully! (Warning: Failed to capture DB Host IP: {out_err})")
                        st.success("✔️ Infrastructure deployed successfully!")
                    else:
                        st.error(f"❌ Terraform deployment failed with return code {rc}")
                        
        # --- Step 2: Schema & Ingestion Seeding ---
        with st.container(border=True):
            st.markdown("#### **Step 4.2: Seed Database Schema & Data**")
            st.markdown("Synthesize mock database records and load them directly into your database cluster.")
            
            ingest_console = st.empty()
            if st.button("📥 Ingest Schema & Data", key="btn_ingest"):
                with st.spinner("Seeding database..."):
                    success_flag = True
                    
                    # 1. Run Schema Generator (only if script exists)
                    schema_gen_script = f".agents/skills/{product}/step1_schema/scripts/generate_schema.py"
                    if os.path.exists(schema_gen_script):
                        ingest_console.info("Step 1: Running Schema DDL Generator...")
                        config_path = os.path.join(use_case_dir, "use_case_config.json")
                        schema_path = os.path.join(use_case_dir, "schema.sql")
                        indexes_path = os.path.join(use_case_dir, "indexes.sql")
                        columnar_path = os.path.join(use_case_dir, "columnar_config.sql")
                        cmd = f"python3 {schema_gen_script} --config {config_path} --output-schema {schema_path} --output-indexes {indexes_path} --alloydb-columnar {columnar_path}"
                        rc = run_command_live(cmd, ".", ingest_console)
                        if rc != 0:
                            st.error(f"❌ Schema DDL generation failed (code {rc})")
                            success_flag = False
                    
                    # 2. Run Data Generator (only if script exists)
                    if success_flag:
                        data_gen_script = f".agents/skills/{product}/step2_data/scripts/generate_data.py"
                        if os.path.exists(data_gen_script):
                            ingest_console.info("Step 2: Generating Mock Data simulation...")
                            config_path = os.path.join(use_case_dir, "use_case_config.json")
                            output_data_path = os.path.join(use_case_dir, "dummy_data.json")
                            cmd = f"python3 {data_gen_script} --config {config_path} --parameters {use_case_params_path} --output {output_data_path}"
                            rc = run_command_live(cmd, ".", ingest_console)
                            if rc != 0:
                                st.error(f"❌ Mock Data simulation failed (code {rc})")
                                success_flag = False
                                
                    # 3. Run Data Loader (always runs)
                    if success_flag:
                        loader_script = f".agents/skills/{product}/step3_load/scripts/load_data.py"
                        if os.path.exists(loader_script):
                            ingest_console.info("Step 3: Uploading schema & seeding records...")
                            cmd = f"python3 {loader_script} --parameters {use_case_params_path}"
                            rc = run_command_live(cmd, ".", ingest_console)
                            if rc != 0:
                                st.error(f"❌ Database ingestion failed (code {rc})")
                                success_flag = False
                        else:
                            st.error(f"Loader script '{loader_script}' not found!")
                            success_flag = False
                            
                    if success_flag:
                        st.success("✔️ Database schema and mock data successfully seeded!")
                        
        # --- Step 3: Teardown Infrastructure ---
        with st.container(border=True):
            st.markdown("#### **Step 4.3: Teardown Infrastructure**")
            st.markdown("Destroy all provisioned instances, saving GCP sandbox costs when you are done presenting.")
            
            destroy_console = st.empty()
            if st.button("🗑️ Destroy Infrastructure", key="btn_destroy"):
                with st.spinner("Tearing down infrastructure..."):
                    tf_dir = f"terraform/{product}"
                    if os.path.exists(tf_dir):
                        destroy_console.info("Running terraform destroy...")
                        cmd = f"terraform destroy -state=\"state_{use_case_clean}.tfstate\" -auto-approve"
                        rc = run_command_live(cmd, tf_dir, destroy_console)
                        if rc == 0:
                            st.success("✔️ Infrastructure destroyed successfully!")
                        else:
                            st.error(f"❌ Terraform destroy failed with return code {rc}")
                    else:
                        st.error(f"Terraform directory '{tf_dir}' not found.")
else:
    st.markdown("---")
    st.info("💡 **Please provide a 'GCP Project ID' and 'Customer Name' to generate configurations and unlock the interactive deployment panel.**")
