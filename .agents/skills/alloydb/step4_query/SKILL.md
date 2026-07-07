---
name: alloydb_step4_query
description: "Execute SQL queries against AlloyDB, verify Columnar Engine execution, and generate a customer talk track using a static script."
---


## 1. Core AlloyDB Query Best Practices

AlloyDB combines relational capability with columnar analytics. For the best demo experience, it is vital to show how the Columnar Engine accelerates queries.

### A. Verifying Columnar Execution
* Standard PostgreSQL queries will automatically execute against the Columnar Engine if the optimizer determines it is faster.
* Use `EXPLAIN` on a query and verify that the plan contains a **`Custom Scan (columnar)`** node.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Connection details.
2. **Queries Configuration** (`queries.json`): Housed inside the use case directory (e.g. `config/use_cases/<usecase>/alloydb/queries.json`).

---

## 3. Expected Outputs
The skill must produce:
1. **`talktrack.md`**: A customer guide explaining the business scenario, SQL code, timing metrics, and execution plans.

---

## 4. How to Execute

Run the static query runner script from the command line:

```bash
python3 .agents/skills/alloydb/step4_query/scripts/run_query.py
```
