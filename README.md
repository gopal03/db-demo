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
* Bypasses all local corporate macOS security blocks by executing Terraform and database binaries entirely inside the Cloud VM.
* Configures implicit metadata service account authentication (no credential files needed).
* Accesses AlloyDB/Cloud SQL instances directly using private VPC IPs (no public endpoints needed).
* Pre-installs `uv` and Google Cloud CLI components.

To launch the workstation VM, set up the environment, and establish connection tunnels automatically, execute the following steps in your local Mac terminal:

#### Step 1: Authenticate to your GCP Environment
Run these commands locally to ensure your CLI is authenticated to your target sandbox project:
```bash
gcloud auth login
gcloud auth application-default login
```

#### Step 2: Run the One-Click Launcher Script
Execute the launcher script from the root of the cloned repository:
```bash
./launch_workstation.sh
```
*This script will provision the VM, wait for configuration to complete, start port-forwarding, and display clickable links to launch the portals in your browser.*

#### Step 3: Open the Portals
Once the script prints the launch links, click them to open the dashboards:
* **Configurator Portal:** [http://localhost:8504](http://localhost:8504)
* **Demo Console:** [http://localhost:8501](http://localhost:8501)

---

## 5. Operational Presentation Workflow

### Path A: Interactive Browser Portal (Recommended)
1. **Configure & Plan:** In the Configurator Portal (`localhost:8504`), select your database product, GCP Project, and scale profile. Clicking **"Save Configuration"** updates your environment.
2. **Provision Infrastructure (Terraform):** Click **🚀 Provision Infrastructure** to deploy resources dynamically.
3. **Compile Schema & Data Plan:** Under **Step 4.2.1**, click **"📝 Compile Schema & Data Plan"** to write DDL schemas and mock records to the VM disk, then preview the generated SQL on-screen.
4. **Apply Schema & Seed Database:** Under **Step 4.2.2**, click **"🚀 Apply Schema & Seed Database"** (enabled after compile) to execute the schema and load the records.
5. **Present:** Open the Demo Explorer Dashboard (`http://localhost:8501`) to present benchmark metrics and interactive sandbox query traversals.
6. **Teardown:** When done, click **🗑️ Destroy Infrastructure** (or use advanced settings) to terminate instances.

### Path B: Two-Script CLI Workflow
If you prefer executing the database seeding and console launches directly inside the VM terminal (after configuring your parameters in the browser):
1. **Configure Parameters:** Open the Configurator Portal (`localhost:8504`), select your database product, GCP Project, and scale profile, then click **"Save Configuration"** to generate the active parameters file on the VM.
2. **Provision and Compile:** Run the setup script to deploy Terraform infrastructure and compile DDL schemas/data on disk:
   ```bash
   ./setup_demo.sh
   ```
3. **Review:** Inspect the compiled schema at `config/use_cases/<use_case>/schema.sql`.
4. **Seed and Launch:** Once reviewed, run the execution script to seed the database and start the Streamlit presentation dashboard in the background:
   ```bash
   ./run_demo.sh
   ```
5. **Present:** Open `http://localhost:8501` to view your live, seeded presentation console.

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

### Step 2: Delete the Workstation VM second
Run the following command from your local terminal to delete the VM instance:
```bash
gcloud compute instances delete db-workstation --zone=us-central1-a --project=YOUR_PROJECT_ID --quiet
```
*(Note: Always destroy the database cluster first to prevent active network peering dependencies from blocking the workstation NAT router and firewall teardown.)*
