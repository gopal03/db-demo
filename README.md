# GCP Database Demo Engine

A unified demo engineering framework designed for Google Cloud Customer Engineers (CEs) to easily configure, provision, seed, and present interactive database demos to customers. 

This repository allows you to deploy and showcase a variety of real-world use cases (e.g., Gaming analytics, Cybersecurity graph blast radius, Retail marketing vector search) across Google Cloud's database portfolio.

---

## 1. Supported Databases & Use Cases

| GCP Database | Demo Use Case / Industry | Key Feature Showcase |
| :--- | :--- | :--- |
| **Spanner** | Cybersecurity / Financial AML | **Spanner Graph** GQL lateral traversals and threat path tracking. |
| **AlloyDB** | Gaming Analytics / Retail | **Columnar Engine** query acceleration & vector similarity search. |
| **Cloud SQL** | Relational transactions ledger | Primary instance vs read replica latency comparisons. |
| **Bigtable** | IoT Fleet Telemetry | Time-series streaming data ingestion. |
| **Memorystore** | Cache Acceleration | Redis cache hit vs database read latency metrics. |
| **Firestore** | Document / Catalog Store | Native document collections search. |

---

## 2. Key Portals & Dashboards

The codebase exposes two visual Streamlit applications:

### ⚙️ 1. The Configurator Portal (`configurator.py`)
The CE control center. Use this portal to:
* Verify active GCP `gcloud` login permissions.
* Enter customer name and automatically calculate clean resource default names.
* Modify machine tiers, regions, and VPC networks in **Advanced Settings**.
* Trigger infrastructure provisioning (Terraform), mock data generation, and table seeding.
* Tear down instances when the demo is complete to save Argolis sandbox resource costs.

### 🛡️ 2. The Demo Explorer Console (`app.py`)
The client-facing screen presented during client meetings. It displays:
* Custom metrics dashboards (node counts, active transactions).
* Pre-configured business scenarios with **Sales Talk Tracks** explaining the database value proposition.
* Real-time query execution latencies and explain plans.
* Dynamic visualizations (e.g., Pyvis network graphs for graph traversals, charting grids for products/telemetry).

---

## 3. Local Machine Setup & Pre-requisites

This demo framework is designed to run locally on your corporate machine, leveraging your private Argolis sandbox project access.

### Step 3.1: Clone the Repository
Clone the codebase to your local directory (we recommend outside `~/Downloads` due to macOS Santa security policy):
```bash
git clone https://github.com/gopal03/db-demo.git
cd db-demo
```

### Step 3.2: Initialize Python Virtual Environment
Set up a clean environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3.3: Authenticate GCP Credentials
Establish active credentials so that Terraform and python clients can access your sandbox Argolis project:
```bash
gcloud auth login
gcloud auth application-default login
```

### Step 3.4: Launch the Configurator Portal
Run the launcher script to spin up the Streamlit configurator server:
```bash
./run_configurator.sh
```
The portal will open in your browser automatically at `http://localhost:8504`.

---

## 4. Operational Workflow for CEs

1. **Configure & Plan:** In the Configurator Portal, fill out client details, choose your database product, and select your scale profile (Small: ~10MB, Medium: ~500MB, Large: ~5GB). Saving updates creates a local `active_parameters.json` config file inside the use-case directory.
2. **Provision Infrastructure (Terraform):** Click **🚀 Provision Infrastructure** in the panel to spin up your databases.
3. **Ingest & Seed:** Click **📥 Seed & Plan Dashboard** to compile SQL DDL schemas, generate thousands of mock records, and seed the database tables.
4. **Present:** Start the Demo Explorer Dashboard using Streamlit (`streamlit run app.py` on port `8501`) and share your screen to present queries and talk tracks to the customer.
5. **Teardown:** When done, click **🗑️ Destroy Infrastructure** in the Configurator to delete GCP resources and prevent Argolis cost leaks.

---

## 5. Troubleshooting (macOS Santa Block)

On Google corporate laptops, macOS **Santa** security policy blocks the execution of downloaded binaries (like the Terraform Google provider) when executed from quarantined paths or inside sandboxed terminals.

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
