---
name: cloudsql_step2_data
description: "Generates relational mock data for Cloud SQL tables, ensuring referential integrity and query seed matches using a static schema-driven script."
---


## 1. Core Cloud SQL Data Generation Principles

Data generated for Cloud SQL must align with the constraints defined in the relational database DDL.

### A. Referential Integrity
* Ensure all child tables (join tables) only contain foreign key values that exist in the parent entity tables.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Providing the scale profile and row boundaries.
2. **Use Case Configuration** (`use_case_config.json`): Specifying target tables and relations.

---

## 3. Expected Outputs
The skill must produce:
1. **`dummy_data.json`**: The JSON payload mapping tables to rows.
2. **`generation_report.md`**: Summarizing row count stats.

---

## 4. How to Execute

Run the static generator script from the command line:

```bash
python3 .agents/skills/cloudsql/step2_data/scripts/generate_data.py \
  --config config/use_cases/<use_case_name>/use_case_config.json \
  --output config/use_cases/<use_case_name>/cloudsql/dummy_data.json
```
