---
name: cloudsql_step4_query
description: "Execute SQL queries against Cloud SQL, verify index scans, and generate a customer talk track using a static script."
---


## 1. Core Cloud SQL Query Best Practices

Query optimization in standard relational databases relies heavily on index utilization and avoiding sequential table scans.

### A. Query Plan Analysis
* Use `EXPLAIN` on SQL queries to verify that the query planner is using the indexes you created. Look for `Index Scan` nodes and avoid `Seq Scan` (sequential scans) on large tables.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Connection details.
2. **Queries Configuration** (`queries.json`): Housed inside the use case directory (e.g. `config/use_cases/<usecase>/cloudsql/queries.json`).

---

## 3. Expected Outputs
The skill must produce:
1. **`talktrack.md`**: A customer guide explaining the business scenario, SQL code, timing metrics, and execution plans.

---

## 4. How to Execute

Run the static query runner script from the command line:

```bash
python3 .agents/skills/cloudsql/step4_query/scripts/run_query.py
```
