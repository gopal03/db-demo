---
name: bigtable_step3_load
description: "Provision Bigtable instances, pre-split tables, and load mock data efficiently using bulk mutation APIs."
---



## 1. Core Bigtable Bulk Loading Best Practices

Writing data to Bigtable at scale requires optimizing the write path to prevent hotspotting the tablet servers and exceeding gRPC connection limits.

### A. Pre-Splitting Tables (Crucial for New Tables)
* By default, a new Bigtable table has only **one tablet** (managed by a single node).
* If you write a large volume of data immediately, all writes will hit that single node, causing a bottleneck until Bigtable automatically splits the tablet (which takes time).
* **Best Practice**: Pre-split the table when creating it. Define split points (row keys) based on the expected distribution of your row keys (e.g., split at `tenant_100`, `tenant_200`, etc.).
* *cbt example*:
  ```bash
  cbt createtable my-table "splits=tenant_100,tenant_200,tenant_300"
  ```

### B. Use Bulk Mutations (`MutateRows`)
* **Never** write rows one-by-one (`MutateRow`) in a loop.
* Use the **`MutateRows`** API, which batches multiple row mutations into a single gRPC request.
* **Batch Size Tuning**:
  * Recommended batch size: **100 to 500 rows** per batch.
  * Keep the total payload size per batch under **1 MB**.
  * Keep the number of individual cell mutations per batch under **100,000**.

### C. Parallelize Writes
* Use a pool of worker threads or asynchronous tasks to write multiple batches in parallel.
* Distribute the keys across batches so that different threads write to different tablet servers (ranges) simultaneously.

### D. Transient Error Handling (Backoff)
* Bulk loads can trigger rate-limiting or transient errors (`DEADLINE_EXCEEDED`, `UNAVAILABLE`).
* Implement **exponential backoff with jitter** to retry failed mutations within a batch. The Google Cloud Python client's `table.mutate_rows()` handles this automatically if configured correctly.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Providing project, instance, and cluster parameters.
2. **Bigtable Schema** (`schema.json`): Detailing table names, column families, and split points.
3. **Generated Mock Data** (`dummy_data.json`): The mutation payload generated in Step 2.

---

## 3. Expected Outputs
The skill must produce:
1. **`load_data.py`**: The python loading script utilizing the Google Cloud Bigtable SDK.
2. **`run_load.sh`**: A shell script that executes the provisioning (`create_tables.sh`) and runs the loader script.
3. **`loading_report.md`**: A summary of the load, including:
   * Total rows and cells written.
   * Write throughput (rows/sec).
   * Average latency per batch.

---

## 4. Step-by-Step Instructions for the Agent

### Step 3.1: Read Schema and Define Splits
1. Read `schema.json` and check if split points are defined.
2. If splits are not defined, analyze the `dummy_data.json` row keys to determine 3-5 logical split boundaries to prevent initial hotspotting.

### Step 3.2: Write the Provisioning Script
1. Generate `create_tables.sh` containing the `cbt` commands to create the table (with splits) and configure the column families and GC policies.

### Step 3.3: Write the Loader Script (`load_data.py`)
Write a Python script that:
1. Initializes the `bigtable.Client`.
2. Reads `dummy_data.json`.
3. Groups the mutations into batches of 200 rows.
4. Uses `table.mutate_rows(direct_rows)` to write the batches.
5. Implements basic timing to measure throughput.

### Step 3.4: Execute and Report
1. Propose running `run_load.sh` to provision and load the database.
2. Capture the script output and write the `loading_report.md`.
