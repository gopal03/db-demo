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

## 4. Setup & Deployment Options

You can run this demo framework in one of two ways:

### Option A: Dedicated GCE Workstation VM (Recommended)
This approach runs the entire database framework inside a private Google Compute Engine VM. It is highly recommended because it:
* Bypasses all local corporate macOS Santa/Gatekeeper security blocks.
* Configures implicit metadata service account authentication (no credential files needed).
* Accesses AlloyDB/Cloud SQL instances directly using private VPC IPs (no public endpoints needed).
* Pre-installs `uv`, `golang`, and Google Cloud CLI components.

#### Step 1: Provision the Workstation VM (from local terminal)
```bash
cd terraform/workstation
terraform init
terraform apply -auto-approve
```
*This outputs a custom `ssh_connection_command` to connect to your workstation VM.*

#### Step 2: Connect and Tunnel Streamlit Ports
Run the SSH connection output in your terminal. This establishes a secure tunnel and forwards ports 8501 and 8504 to your local machine:
```bash
gcloud compute ssh db-workstation \
  --zone=us-central1-a \
  --tunnel-through-iap \
  -- -q -L 8501:localhost:8501 -L 8504:localhost:8504
```

#### Step 3: Launch Demos
Open your browser and go to `http://localhost:8504` to configure and launch your database demos.

---

### Option B: Local Laptop Setup

If you prefer to run the demo framework locally on your corporate machine:

#### Step 1: Clone the Repo
```bash
git clone https://github.com/gopal03/db-demo.git
cd db-demo
```

#### Step 2: Install UV Package Manager (Recommended)
For 100x faster package installation and virtualenv setups, install the `uv` tool globally:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Step 3: Launch Configurator Portal
Run the startup script. It checks if `uv` is available to instantly install virtual environments and dependencies; if not, it automatically falls back to standard `pip`:
```bash
./run_configurator.sh
```
Open `http://localhost:8504` in your browser.

#### Step 4: Authenticate GCP SDK
Ensure your local SDK credentials are active:
```bash
gcloud auth login
gcloud auth application-default login
```

---

## 5. Operational Presentation Workflow

1. **Configure & Plan:** In the Configurator Portal (`localhost:8504`), select your database product, GCP Project, and scale profile. Saving configuration generates a local `active_parameters.json` config.
2. **Provision Infrastructure (Terraform):** Click **🚀 Provision Infrastructure** in the Configurator panel to provision database instances.
3. **Ingest & Seed:** Click **📥 Seed & Plan Dashboard** to compile SQL DDL schemas, generate mock records, and seed the tables.
4. **Present:** Start the Demo Explorer Dashboard (Streamlit running on port `8501`) and share your screen to present the database benchmarks and explain plans.
5. **Teardown:** When done, click **🗑️ Destroy Infrastructure** to delete instances and prevent unnecessary sandbox costs.

---

## 6. Local Setup Troubleshooting (macOS Gatekeeper/Santa)

If you are running the framework locally (Option B) and your configurator console displays a `Failed to load plugin schemas` error during provisioning:
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
4. Return to the Configurator Portal UI (`localhost:8504`) to complete the **Seed & Plan** and presentation steps.

---

## 7. Workstation VM Troubleshooting

### 🔑 403 Permission Denied (GCP Authorization)
If Terraform fails with a `403 Permission Denied` (e.g., `compute.instances.create` or `compute.disks.create` forbidden):
1. **Refresh your Application Default Credentials (ADC):** Terraform reads separate local credentials from standard gcloud logins. Refresh them by running:
   ```bash
   gcloud auth application-default login
   ```
2. **Verify active CLI account:** Make sure your active shell identity is indeed the account authorized on your target sandbox:
   ```bash
   gcloud config get-value account
   ```

### 🌐 Network Resource "default" Not Found
If Terraform fails with `The referenced network resource cannot be found` (indicating your project does not have the pre-created `default` VPC):
1. **Find an existing VPC network name:**
   ```bash
   gcloud compute networks list --project=YOUR_PROJECT_ID
   ```
2. **Find the subnet name in your region (e.g., us-central1):**
   ```bash
   gcloud compute subnets list --project=YOUR_PROJECT_ID --network=YOUR_NETWORK_NAME
   ```
3. **Deploy using network variable overrides:**
   ```bash
   terraform apply \
     -var="project_id=YOUR_PROJECT_ID" \
     -var="network_name=YOUR_NETWORK_NAME" \
     -var="subnet_name=YOUR_SUBNET_NAME" \
     -auto-approve
   ```

---

## 8. Cleanup & Teardown

To avoid ongoing GCP billing charges, destroy all provisioned resources when you finish your presentation session.

Because the workstation VM and database clusters are modularly decoupled, they must be destroyed sequentially in their respective folders:

### Step 1: Destroy the Database Cluster first
Navigate to the directory of the active database you provisioned (e.g., AlloyDB) and run destroy:
```bash
cd terraform/alloydb
terraform destroy -var="project_id=YOUR_PROJECT_ID" -auto-approve
```

### Step 2: Destroy the Workstation VM second
Navigate to the workstation folder and run destroy:
```bash
cd ../workstation
terraform destroy -var="project_id=YOUR_PROJECT_ID" -auto-approve
```

*(Note: Always destroy the database cluster first to prevent active network peering dependencies from blocking the workstation NAT router and firewall teardown.)*
