# GCP Database Demo Engine

A unified, extensible demo engineering framework designed to easily configure, provision, seed, and present database demos on Google Cloud across any database product, industry vertical, or business use case.

Rather than being locked to a fixed set of demos, this engine acts as a **pluggable platform**. Developers can define any custom schema, relational table structures, and analytical query scenarios using simple JSON declarations, and the engine handles the data generation, infrastructure vars, and console presentation automatically.

---

## 1. Supported Databases & Workloads

The framework is designed to demonstrate any database capabilities—such as graph queries, vector similarity search, relational transactions, high-throughput time-series ingestion, and cache acceleration—across any target schema. The pre-packaged use cases are provided as out-of-the-box examples:
* **Spanner:** Relational workloads and graph traversals (e.g. Spanner Graph).
* **AlloyDB for PostgreSQL:** Vector similarity search (pgvector), hybrid transactional/analytical processing (HTAP), and Columnar Engine analytics.
* **Cloud SQL (PostgreSQL/MySQL):** Transactional ledgers and replication performance.
* **Bigtable:** High-throughput time-series streams and IoT telemetry metrics.
* **Memorystore (Redis):** In-memory cache hit performance and session stores.
* **Firestore:** Hierarchical document databases and search catalogs.

---

## 2. Key Portals & Dashboards

The codebase exposes two Streamlit applications:

### ⚙️ 1. The Configurator Portal (`configurator.py`)
The configuration control center. Use this portal to:
* Verify active GCP `gcloud` login permissions.
* Enter customer name and automatically calculate clean resource default names.
* Modify machine tiers, regions, and VPC networks in **Advanced Settings**.
* Trigger infrastructure provisioning (Terraform), mock data generation, and table seeding.
* Tear down instances when the demo is complete to save sandbox resource costs.

### 🛡️ 2. The Demo Explorer Console (`app.py`)
The client-facing screen presented during client meetings. It displays:
* Custom metrics dashboards (node counts, active transactions).
* Pre-configured business scenarios with **Sales Talk Tracks** explaining the database value proposition.
* Real-time query execution latencies and explain plans.
* Dynamic visualizations (e.g., Pyvis network graphs for graph traversals, charting grids for products/telemetry).

---

## 3. Extensibility: Creating a Custom Use Case

The engine is fully pluggable. To add a new use-case (e.g. *Retail Fraud*, *Healthcare Telemetry*, *Smart Grid Logging*):

1. **Create a Use Case Folder:** Create a new folder under `config/use_cases/your_use_case_name/`.
2. **Define the Schema & Queries (`use_case_config.json`):** Add a JSON file declaring the tables, columns, data relationships, and the SQL/GQL queries you want to run.
3. **Register the Mapping:** Add your new industry and database mapping to the `config_mappings` dictionary inside `configurator.py`.

Once configured, the portal will automatically synthesize mock records matching your column definitions, seed the database, and display the custom presentation screens in the dashboard console.

---

## 4. Local Machine Setup & Pre-requisites

The demo engine is designed to run locally on your machine, leveraging your private Google Cloud credentials.

### Step 4.1: Clone the Repository
Clone the codebase to your local directory 
```bash
git clone https://github.com/gopal03/db-demo.git
cd db-demo
```

### Step 4.2: Initialize Python Virtual Environment
Set up a clean environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 4.3: Authenticate GCP Credentials
Establish active credentials so that Terraform and python clients can access your sandbox project:
```bash
gcloud auth login
gcloud auth application-default login
```

### Step 4.4: Launch the Configurator Portal
Run the launcher script to spin up the Streamlit configurator server:
```bash
./run_configurator.sh
```
The portal will open in your browser automatically at `http://localhost:8504`.

---

## 5. Operational Presentation Workflow

1. **Configure & Plan:** In the Configurator Portal, fill out client details, choose your database product, and select your scale profile (Small: ~10MB, Medium: ~500MB, Large: ~5GB). Saving updates creates a local `active_parameters.json` config file inside the use-case directory.
2. **Provision Infrastructure (Terraform):** Click **🚀 Provision Infrastructure** in the panel to spin up your databases.
3. **Ingest & Seed:** Click **📥 Seed & Plan Dashboard** to compile SQL DDL schemas, generate thousands of mock records, and seed the database tables.
4. **Present:** Start the Demo Explorer Dashboard using Streamlit (`streamlit run app.py` on port `8501`) and share your screen to present queries and talk tracks to the customer.
5. **Teardown:** When done, click **🗑️ Destroy Infrastructure** in the Configurator to delete GCP resources and prevent unnecessary sandbox costs.

---

## 6. Troubleshooting 

If your configurator console displays a `Failed to load plugin schemas` error during provisioning:
1. Open your host terminal (outside the IDE sandboxed terminal).
2. Navigate to the target folder:
   ```bash
   cd terraform/alloydb  # Or terraform/spanner, etc.
   ```
3. Run the Terraform command directly:
   ```bash
   terraform init
   terraform apply -auto-approve
   ```
4. Once completed, return to the Configurator Portal UI to complete the **Seed & Plan** and presentation steps.
