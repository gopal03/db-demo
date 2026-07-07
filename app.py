import streamlit as st
import json
import os
import sys
import datetime
from decimal import Decimal
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
from google.cloud import spanner
from google.cloud import spanner_admin_instance_v1

# Add .agents/skills to sys.path to allow importing from skills
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".agents/skills")))

# --- Configuration & Paths ---
PARAMS_FILE = "config/demo_parameters.json"

st.set_page_config(
    layout="wide",
    page_title="Spanner Graph Demo Console",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- Premium Dark Glassmorphism CSS ---
st.markdown("""
<style>
    /* Main Canvas */
    .stApp {
        background-color: #0B0C10;
        color: #E0E0E0;
        font-family: 'Inter', 'Outfit', sans-serif;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #12131C !important;
        border-right: 1px solid #1F202E;
    }
    
    /* Translucent Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 31, 46, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    
    /* Metrics / Telemetry */
    .metric-value {
        font-size: 2.2em;
        font-weight: bold;
        color: #FFD700; /* Gold */
        margin-bottom: 4px;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    .metric-value.alert {
        color: #FF4B4B; /* Glowing Crimson */
        text-shadow: 0 0 10px rgba(255, 75, 75, 0.4);
    }
    .metric-label {
        font-size: 0.85em;
        color: #8E90A6;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%) !important;
        color: #0B0C10 !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    /* Code Blocks */
    code {
        color: #FF79C6 !important;
        background-color: #1E1F29 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_resource
def get_spanner_client(project_id):
    return spanner.Client(project=project_id)

def load_parameters():
    if not os.path.exists(PARAMS_FILE):
        # Fallback default
        return {
            "project_id": "YOUR_PROJECT_ID",
            "instance_id": "spanner-graph-demo-instance",
            "database_id": "spanner-graph-demo-db",
            "demo_context": {
                "customer_name": "Acme Corp",
                "industry": "General",
                "use_case": "Demo",
                "use_case_config": ""
            }
        }
    with open(PARAMS_FILE, 'r') as f:
        data = json.load(f)
    
    # Adapt nested demo_parameters.json to flat keys used by app.py
    if "database_configs" in data and "spanner" in data["database_configs"]:
        spanner_cfg = data["database_configs"]["spanner"]
        data["instance_id"] = spanner_cfg.get("instance_id", "spanner-graph-demo-instance")
        data["database_id"] = spanner_cfg.get("database_id", "spanner-graph-demo-db")
    else:
        # Fallback defaults if database_configs structure is missing
        data["instance_id"] = data.get("instance_id", "spanner-graph-demo-instance")
        data["database_id"] = data.get("database_id", "spanner-graph-demo-db")
        
    return data

def save_parameters(params):
    os.makedirs(os.path.dirname(PARAMS_FILE), exist_ok=True)
    with open(PARAMS_FILE, 'w') as f:
        json.dump(params, f, indent=2)

def load_use_case_config(config_path):
    if not config_path or not os.path.exists(config_path):
        return None
    with open(config_path, 'r') as f:
        return json.load(f)

def get_database_connection(client, instance_id, database_id):
    try:
        instance = client.instance(instance_id)
        if not instance.exists():
            return None
        database = instance.database(database_id)
        if not database.exists():
            return None
        return database
    except Exception:
        # Suppress API and IAM auth errors, degrading gracefully to OFFLINE
        return None

# --- Dynamic Graph Parser & Renderer (Generic Heuristic) ---
def render_dynamic_graph(df, height="500px"):
    net = Network(height=height, width="100%", bgcolor="#12131C", font_color="white", notebook=False)
    
    # Identify node columns based on headers
    node_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if any(term in col_lower for term in ['id', 'account', 'customer', 'merchant', 'source', 'destination', 'intermediary', 'hop', 'user', 'device', 'workload', 'datastore', 'vuln', 'identity', 'gateway', 'database']):
            node_cols.append(col)
            
    if not node_cols:
        # Fallback: treat the first and last column as nodes
        node_cols = [df.columns[0], df.columns[-1]] if len(df.columns) > 1 else [df.columns[0]]

    added_nodes = set()
    
    for _, row in df.iterrows():
        path_nodes = []
        for col in node_cols:
            node_val = str(row[col])
            if not node_val or node_val.lower() == 'none' or node_val.lower() == 'null':
                continue
            
            # Determine color/shape based on ID characteristics
            color = "#FFD700"  # Default Gold
            shape = "dot"
            
            node_val_lower = node_val.lower()
            if 'cust' in node_val_lower or 'user' in node_val_lower or '@' in node_val_lower or 'rostov' in node_val_lower:
                color = "#FF4B4B" if 'compromised' in node_val_lower or 'rostov' in node_val_lower else "#00CC96"
                shape = "dot"
            elif 'merch' in node_val_lower or 'casino' in node_val_lower:
                color = "#E15A97"
                shape = "hexagon"
            elif 'res-' in node_val_lower or 'srv' in node_val_lower or 'db' in node_val_lower or 'gateway' in node_val_lower:
                color = "#4B9FEF"
                shape = "square"
                
            if node_val not in added_nodes:
                net.add_node(node_val, label=node_val, color=color, shape=shape)
                added_nodes.add(node_val)
            path_nodes.append(node_val)
            
        # Draw edges sequentially along the path
        for i in range(len(path_nodes) - 1):
            src = path_nodes[i]
            dst = path_nodes[i+1]
            if src != dst:
                net.add_edge(src, dst, color="#8E90A6", width=2)
                
    # Physics Layout Engine
    net.force_atlas_2based(
        gravity=-40,
        central_gravity=0.01,
        spring_length=120,
        spring_strength=0.08,
        damping=0.4
    )
    
    net.set_options("""
    {
      "interaction": {
        "navigationButtons": true
      }
    }
    """)
    
    try:
        path = "temp_graph.html"
        net.save_graph(path)
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        return html
    except Exception as e:
        return f"<div>Error rendering graph: {e}</div>"

# --- Main Application Controller ---
def main():
    params = load_parameters()
    demo_ctx = params.get("demo_context", {})
    active_config_path = demo_ctx.get("use_case_config", "")
    
    # 1. Sidebar Control
    with st.sidebar:
        st.markdown(f"### 🛡️ {demo_ctx.get('customer_name', 'Acme Corp')}")
        st.caption(f"Industry: {demo_ctx.get('industry', 'N/A')}")
        st.caption(f"Use Case: {demo_ctx.get('use_case', 'N/A')}")
        st.markdown("---")
        
        # Navigation with Lock/Unlock
        show_admin_option = st.query_params.get("admin") == "true"
        unlock_admin = st.checkbox("Unlock Developer Tools", value=show_admin_option)
        
        if unlock_admin:
            menu = st.radio("Navigation", ["🎮 Demo Console", "🛠️ Sandbox (Custom GQL)"])
        else:
            menu = "🎮 Demo Console"
        
        if unlock_admin:
            st.markdown("---")
            st.markdown("### Database Status")
            st.code(f"Project: {params['project_id']}")
            st.code(f"Instance: {params['instance_id']}")
            st.code(f"DB: {params['database_id']}")
        
    client = get_spanner_client(params["project_id"])
    database = get_database_connection(client, params["instance_id"], params["database_id"])
    
    # Check Connection Status
    if database is None:
        with st.sidebar:
            st.error("Database connection: OFFLINE")
            st.caption("Please check your Spanner parameters or provision the database.")
    else:
        with st.sidebar:
            st.success("Database connection: ONLINE")

    # --- MENU OPTION 1: DEMO CONSOLE ---
    if menu == "🎮 Demo Console":
        st.title(f"🛡️ {demo_ctx.get('use_case', 'Spanner Graph Console')}")
        st.markdown(f"#### Customer Presentation Engine — Prepared for **{demo_ctx.get('customer_name')}**")
        st.markdown("---")
        
        if database is None:
            st.warning("⚠️ No database connection found. Please go to the **Control Panel** to set up and seed your database.")
            st.stop()
            
        use_case_config = load_use_case_config(active_config_path)
        if not use_case_config:
            st.error("⚠️ Active use-case configuration file could not be loaded. Verify the path in the Control Panel.")
            st.stop()
            
        # Dynamic KPI telemetry cards
        st.subheader("📊 Live Graph Footprint")
        cols = st.columns(len(use_case_config.get("nodes", [])))
        for idx, node in enumerate(use_case_config.get("nodes", [])):
            table_name = node["table_name"]
            label_name = node["name"]
            
            # Fetch row count dynamically using standard SQL via Spanner
            try:
                with database.snapshot() as snapshot:
                    result = list(snapshot.execute_sql(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result[0][0]
            except Exception:
                count = "-"
                
            with cols[idx]:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-label">{label_name}s (Nodes)</div>
                    <div class="metric-value">{(f"{count:,}" if isinstance(count, int) else count)}</div>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("---")
        
        # Scenario Selector
        st.subheader("🔍 Suspicious Activity Scenarios")
        queries = use_case_config.get("queries", [])
        
        if not queries:
            st.info("No pre-configured scenario queries found in the config file.")
        else:
            scenario_names = [q["title"] for q in queries]
            selected_scenario_title = st.selectbox("Select Compliance Scenario", scenario_names)
            selected_query = next((q for q in queries if q["title"] == selected_scenario_title), None)
            
            if selected_query:
                st.markdown(f"*{selected_query['description']}*")
                
                tab_viz, tab_data, tab_code = st.tabs(["Graph Visualization", "Tabular Data", "GQL Query"])
                
                # Execute query
                try:
                    with database.snapshot() as snapshot:
                        results = snapshot.execute_sql(selected_query["gql"])
                        rows = list(results)
                        headers = [field.name for field in results.fields] if results.fields else []
                        
                    if rows:
                        df = pd.DataFrame(rows, columns=headers)
                        
                        with tab_viz:
                            st.info(f"🗣️ **Sales Talk Track**: {selected_query['talk_track']}")
                            html = render_dynamic_graph(df)
                            components.html(html, height=500, scrolling=True)
                            
                        with tab_data:
                            st.dataframe(df, use_container_width=True)
                            
                        with tab_code:
                            st.code(selected_query["gql"], language="sql")
                    else:
                        st.warning("No records matched this threat scenario. (Database is clean!)")
                except Exception as e:
                    st.error(f"Failed to execute scenario query: {e}")



    # --- MENU OPTION 3: SANDBOX ---
    elif menu == "🛠️ Sandbox (Custom GQL)":
        st.title("🛠️ Graph Sandbox Console")
        st.markdown("Execute raw, custom Spanner GQL queries directly and visualize results dynamically.")
        st.markdown("---")
        
        if database is None:
            st.warning("⚠️ No database connection found. Connect in the Control Panel.")
            st.stop()
            
        custom_gql = st.text_area("GQL Query", value="GRAPH AMLGraph\nMATCH (a:Account)-[t:Transfers]->(b:Account)\nRETURN a.account_id, b.account_id, t.amount\nLIMIT 10", height=150)
        
        if st.button("Execute Sandbox Query"):
            try:
                with database.snapshot() as snapshot:
                    results = snapshot.execute_sql(custom_gql)
                    rows = list(results)
                    headers = [field.name for field in results.fields] if results.fields else []
                    
                if rows:
                    df = pd.DataFrame(rows, columns=headers)
                    st.dataframe(df, use_container_width=True)
                    
                    st.subheader("Dynamic Graph Rendering")
                    html = render_dynamic_graph(df)
                    components.html(html, height=500, scrolling=True)
                else:
                    st.info("Query returned no records.")
            except Exception as e:
                st.error(f"Execution Error: {e}")

if __name__ == "__main__":
    main()
