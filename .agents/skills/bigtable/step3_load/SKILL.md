---
name: bigtable_step3_load
description: "Provision Bigtable instances, pre-split tables, and bulk load mock data using a static python loader."
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

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Providing project, instance, and cluster parameters.
2. **Bigtable Schema** (`schema.json`): Detailing table names, column families, and split points.
3. **Generated Mock Data** (`dummy_data.json`): The mutation payload generated in Step 2.

---

## 3. Expected Outputs
The skill must produce:
1. **`run_load.sh`**: A shell script that executes the provisioning (`create_tables.sh`) and runs the static loader script.
2. **`loading_report.md`**: A summary of the load, including:
   * Total rows and cells written.
   * Write throughput (rows/sec).

---

## 4. How to Execute

Run the static loader script from the command line:

```bash
python3 .agents/skills/bigtable/step3_load/scripts/load_data.py
```
