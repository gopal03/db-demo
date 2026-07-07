---
name: firestore_step3_load
description: "Bulk load mock document structures into Google Cloud Firestore using a static WriteBatch loader script."
---


## 1. Core Firestore Loading Best Practices

Firestore bulk loading requires careful management of batch sizes and write throughput to avoid rate limiting.

### A. Firestore Write Batches
* You can write multiple documents in a single transaction using **`WriteBatch`**.
* **Limit**: A single `WriteBatch` can contain a maximum of **500 operations** (creates, updates, or deletes). Exceeding this limit will cause the batch to fail.
* **Best Practice**: Group document writes in chunks of 450 to leave a safety margin.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Credentials and database ID.
2. **Schema & Indexes** (`schema.json`, `firestore.indexes.json`).
3. **Mock Data** (`dummy_data.json`).

---

## 3. Expected Outputs
The skill must produce:
1. **`run_load.sh`**: A shell script to deploy composite indexes (using `gcloud firestore indexes import`) and execute the static loader script.
2. **`loading_report.md`**: Reporting total loaded documents and execution metrics.

---

## 4. How to Execute

Run the static loader script from the command line:

```bash
python3 .agents/skills/firestore/step3_load/scripts/load_data.py
```
