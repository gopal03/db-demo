---
name: alloydb_step2_data
description: "Generates realistic relational mock data for AlloyDB tables while maintaining relational integrity using a static schema-driven script."
---


## 1. Core AlloyDB Data Generation Principles

AlloyDB, as a PostgreSQL database, requires strict adherence to relational schema rules (primary keys, foreign keys, constraints).

### A. Referential Integrity
* Ensure all child tables (containing foreign keys) only reference valid primary keys in parent tables.
* The static script automatically parses the schema config and links keys properly.

### B. Output Format (JSON)
* Generates data as a structured JSON file mapping table names to arrays of row objects which is parsed and loaded via the loader script.

---

## 2. Input Requirements
The agent expects the following inputs:
1. **Demo Parameters** (`demo_parameters.json`): Providing project, database configuration, and scale profile.
2. **Use Case Configuration** (`use_case_config.json`): Specifying target tables and relations.

---

## 3. Expected Outputs
The skill must produce:
1. **`dummy_data.json`**: The structured JSON data payload.
2. **`generation_report.md`**: A summary of rows generated per table.

---

## 4. How to Execute

Run the static generator script from the command line:

```bash
python3 .agents/skills/alloydb/step2_data/scripts/generate_data.py \
  --config config/use_cases/<use_case_name>/use_case_config.json \
  --output config/use_cases/<use_case_name>/alloydb/dummy_data.json
```
