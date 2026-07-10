import streamlit as st
import json
import os
import sys
import datetime
from decimal import Decimal
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components


# Add .agents/skills to sys.path to allow importing from skills
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".agents/skills")))
from lib.db_adapters import get_database_adapter

# --- Configuration & Paths ---
PARAMS_FILE = "config/demo_parameters.json"

st.set_page_config(
    layout="wide",
    page_title="Demo Console",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- Premium Dynamic CSS Theme Engine ---
def apply_industry_theme(industry):
    themes = {
        "Gaming": {
            "bg": "#0B0C10", "card_bg": "rgba(30, 31, 46, 0.6)", "border": "rgba(255, 255, 255, 0.08)",
            "accent": "#FFD700", "sidebar": "#12131C", "text": "#E0E0E0", "btn_grad": "linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%)"
        },
        "Financial Services": {
            "bg": "#0A1128", "card_bg": "rgba(16, 29, 66, 0.7)", "border": "rgba(0, 204, 150, 0.15)",
            "accent": "#00CC96", "sidebar": "#001F54", "text": "#F4F7F6", "btn_grad": "linear-gradient(135deg, #00CC96 0%, #008080 100%)"
        },
        "Retail": {
            "bg": "#18122B", "card_bg": "rgba(44, 30, 90, 0.6)", "border": "rgba(225, 90, 151, 0.2)",
            "accent": "#E15A97", "sidebar": "#393053", "text": "#F1F0F4", "btn_grad": "linear-gradient(135deg, #E15A97 0%, #A22E60 100%)"
        },
        "Healthcare": {
            "bg": "#0F2027", "card_bg": "rgba(32, 58, 67, 0.7)", "border": "rgba(75, 159, 239, 0.2)",
            "accent": "#4B9FEF", "sidebar": "#203A43", "text": "#EAF2F8", "btn_grad": "linear-gradient(135deg, #4B9FEF 0%, #1D63B8 100%)"
        }
    }
    t = themes.get(industry, themes["Gaming"])
    
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {t['bg']};
            color: {t['text']};
            font-family: 'Inter', 'Outfit', sans-serif;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {t['sidebar']} !important;
            border-right: 1px solid {t['border']};
        }}
        .glass-card {{
            background: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }}
        .metric-value {{
            font-size: 2.2em;
            font-weight: bold;
            color: {t['accent']};
            margin-bottom: 4px;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
        }}
        .metric-value.alert {{
            color: #FF4B4B;
            text-shadow: 0 0 10px rgba(255, 75, 75, 0.4);
        }}
        .metric-label {{
            font-size: 0.85em;
            color: #8E90A6;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stButton>button {{
            background: {t['btn_grad']} !important;
            color: #0B0C10 !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            padding: 10px 20px !important;
            transition: all 0.3s ease !important;
        }}
        .stButton>button:hover {{
            box-shadow: 0 0 15px {t['accent']}50 !important;
            transform: translateY(-2px) !important;
        }}
        h1, h2, h3 {{
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }}
        code {{
            color: #FF79C6 !important;
            background-color: #1E1F29 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---

def load_parameters():
    if not os.path.exists(PARAMS_FILE):
        return None
    with open(PARAMS_FILE, 'r') as f:
        data = json.load(f)
        
    # Check if this active use case has a customized active_parameters.json file
    use_case_config_path = data.get("demo_context", {}).get("use_case_config")
    if use_case_config_path:
        use_case_dir = os.path.dirname(use_case_config_path)
        active_params_path = os.path.join(use_case_dir, "active_parameters.json")
        if os.path.exists(active_params_path):
            try:
                with open(active_params_path, 'r') as f:
                    data = json.load(f)
            except Exception:
                pass
    
    # Adapt nested demo_parameters.json / active_parameters.json to flat keys used by app.py
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
    if not params:
        st.error("⚠️ Active demo configuration not found! Please open the **Configurator Portal** (port 8504) first to configure, deploy, and seed your database.")
        st.stop()
        
    demo_ctx = params.get("demo_context", {})
    apply_industry_theme(demo_ctx.get("industry", "Gaming"))
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
            st.code(f"Project: {params.get('project_id')}")
            st.code(f"Target DB: {params.get('target_database', 'spanner')}")
        
    target_database = params.get("target_database", "spanner")
    try:
        database = get_database_adapter(target_database, params)
        db_online = database.is_online()
        conn_error = None
    except Exception as e:
        database = None
        db_online = False
        conn_error = str(e)
    
    # Check Connection Status
    if not db_online:
        with st.sidebar:
            st.error("Database connection: OFFLINE")
            if conn_error:
                st.caption(f"Error: {conn_error}")
            st.caption("Please check your database parameters or provision the instance.")
    else:
        with st.sidebar:
            st.success("Database connection: ONLINE")

    # --- MENU OPTION 1: DEMO CONSOLE ---
    if menu == "🎮 Demo Console":
        st.title(f"🛡️ {demo_ctx.get('use_case', 'Spanner Graph Console')}")
        st.markdown(f"#### Customer Presentation Engine — Prepared for **{demo_ctx.get('customer_name')}**")
        st.markdown("---")
        
        if not db_online:
            st.warning("⚠️ No database connection found. Please go to the **Control Panel** to set up and seed your database.")
            if conn_error:
                st.error(f"Details: {conn_error}")
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
            
            count = database.get_row_count(table_name)
                
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
                
                # Execute query via adapter
                try:
                    df = database.execute_query(selected_query)
                    if not df.empty:
                        with tab_viz:
                            st.info(f"🗣️ **Sales Talk Track**: {selected_query['talk_track']}")
                            if use_case_config.get("graph_name"):
                                html = render_dynamic_graph(df)
                                components.html(html, height=500, scrolling=True)
                            else:
                                # Relational datasets: Render charts dynamically
                                num_cols = df.select_dtypes(include=['number']).columns.tolist()
                                str_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                                if num_cols and str_cols:
                                    st.bar_chart(df, x=str_cols[0], y=num_cols[0])
                                elif len(num_cols) >= 2:
                                    st.scatter_chart(df, x=num_cols[0], y=num_cols[1])
                                else:
                                    st.dataframe(df, use_container_width=True)
                                    
                        with tab_data:
                            st.dataframe(df, use_container_width=True)
                            
                        with tab_code:
                            query_code = selected_query.get("sql") or selected_query.get("gql") or ""
                            st.code(query_code, language="sql")
                    else:
                        st.warning("No records matched this threat scenario. (Database is clean!)")
                except Exception as e:
                    st.error(f"Failed to execute scenario query: {e}")



    # --- MENU OPTION 3: SANDBOX ---
    elif menu == "🛠️ Sandbox (Custom GQL)":
        st.title("🛠️ Graph Sandbox Console")
        st.markdown("Execute raw, custom Spanner GQL queries directly and visualize results dynamically.")
        st.markdown("---")
        
        if not db_online:
            st.warning("⚠️ No database connection found. Connect in the Control Panel.")
            if conn_error:
                st.error(f"Details: {conn_error}")
            st.stop()
            
        default_query = "SELECT * FROM Players LIMIT 10;"
        sandbox_label = "SQL Query"
        if target_database == "spanner":
            default_query = "GRAPH AMLGraph\nMATCH (a:Account)-[t:Transfers]->(b:Account)\nRETURN a.account_id, b.account_id, t.amount\nLIMIT 10"
            sandbox_label = "GQL Query"
        elif target_database == "memorystore":
            default_query = "*"
            sandbox_label = "Redis Key Pattern"
            
        custom_gql = st.text_area(sandbox_label, value=default_query, height=150)
        
        if st.button("Execute Sandbox Query"):
            try:
                # Execute custom search/query via adapter
                df = database.execute_query({"sql": custom_gql, "redis_pattern": custom_gql, "collection": custom_gql, "table_id": custom_gql})
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    
                    if use_case_config.get("graph_name"):
                        st.subheader("Dynamic Graph Rendering")
                        html = render_dynamic_graph(df)
                        components.html(html, height=500, scrolling=True)
                else:
                    st.info("Query returned no records.")
            except Exception as e:
                st.error(f"Execution Error: {e}")

if __name__ == "__main__":
    main()
