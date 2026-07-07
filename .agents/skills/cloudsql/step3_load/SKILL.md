---
name: cloudsql_step3_load
description: "Provision Cloud SQL tables, bulk load mock data using a static psycopg2 loader, and apply secondary indexes."
---


## 1. Core Cloud SQL Bulk Loading Best Practices

Optimizing relational data loads for Cloud SQL requires managing transactional overhead and index creation.

### A. Disable Indexes During Ingestion
* Indexes significantly slow down large write operations because the engine must update the index tree for every inserted row.
* **Best Practice**: Create tables with primary keys only, load the data, and then run the `indexes.sql` script to create secondary indexes.

### B. Batching Writes
* Group inserts into batches (e.g. 500 rows per transaction) rather than inserting row-by-row.
* Uses standard bulk insert pipeline to optimize transaction size.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Providing connection configurations.
2. **Schema and Index scripts** (`schema.sql`, `indexes.sql`).
3. **Mock Data** (`dummy_data.json`).

---

## 3. Expected Outputs
The skill must produce:
1. **`run_load.sh`**: A shell script executing `schema.sql`, running the static loader, and executing `indexes.sql`.
2. **`loading_report.md`**: Loading duration and throughput summary.

---

## 4. How to Execute

Run the static loader script from the command line:

```bash
python3 .agents/skills/cloudsql/step3_load/scripts/load_data.py
```
