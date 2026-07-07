---
name: alloydb_step3_load
description: "Provision AlloyDB tables, configure Columnar Engine, and bulk load mock data using a static psycopg2 loader."
---


## 1. Core AlloyDB Loading Best Practices

Efficiently provisioning and loading data into AlloyDB requires managing PostgreSQL transactions and connection performance.

### A. DDL Provisioning
* Execute `schema.sql` first to create the table structure.
* Do **not** create optional indexes (only primary keys and unique keys) prior to loading data, as index updates degrade load throughput. Create non-primary indexes after the load completes.

### B. Bulk Loading Techniques
* **Batch Inserts**: Uses a static bulk loader script to combine multiple `INSERT` statements into single network round-trips.
* **Transaction Control**: Perform the entire load for a table within a single transaction (or batches of 500 rows) and commit at the end.

### C. Columnar Engine Activation
* After loading tables, register them with the Columnar Engine using the columnar configuration script (`columnar_config.sql`).
* Force a refresh of the columnar store to populate the in-memory cache:
  ```sql
  SELECT google_columnar_engine.refresh_resources();
  ```

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): AlloyDB cluster/instance parameters, credentials, and connection settings.
2. **DDL Scripts** (`schema.sql`, `columnar_config.sql`).
3. **Generated Mock Data** (`dummy_data.json`).

---

## 3. Expected Outputs
The skill must produce:
1. **`run_load.sh`**: A shell script that executes table provisioning, runs the static loader script, creates indexes, and configures the Columnar Engine.
2. **`loading_report.md`**: Execution time, row throughput, and latency.

---

## 4. How to Execute

Run the static loader script from the command line:

```bash
python3 .agents/skills/alloydb/step3_load/scripts/load_data.py
```
