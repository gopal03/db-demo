---
name: cloudsql_step1_schema
description: "Translate a database-agnostic use-case configuration into an optimized relational schema (SQL DDL) for Cloud SQL (PostgreSQL/MySQL) using a static generator."
---


## 1. Core Cloud SQL Schema Design Principles

Cloud SQL is a fully managed service for relational databases (PostgreSQL, MySQL, SQL Server). Schema design focuses on traditional relational modeling, indexing, and normalization.

### A. Relational Database Modeling
1. **Normalization (3NF)**: Design tables to reduce redundancy. Split entities into distinct tables and link them via foreign keys.
2. **Primary Keys**: Every table must have a primary key. Use auto-incrementing integers (`SERIAL`/`AUTO_INCREMENT`) or UUIDs.
3. **Data Types**: Choose size-appropriate datatypes:
   * `INT`/`BIGINT` for integers.
   * `VARCHAR(N)` for strings.
   * `DECIMAL(12,2)` for precise financial decimals.
   * `TIMESTAMPTZ` for timezone-aware timestamps.
4. **Foreign Keys**: Define foreign keys to enforce referential integrity.

---

## 2. Input Requirements
The agent expects:
1. **Use-case Configuration** (`use_case_config.json`): Specifying tables, attributes, relationships, and queries.
2. **Demo Parameters** (`demo_parameters.json`): Connection parameters and engine choice.

---

## 3. Expected Outputs
The skill must produce the following files in the use-case directory (e.g., `config/use_cases/<use_case_name>/cloudsql/`):
1. **`schema.sql`**: A SQL DDL script to create tables, keys, and foreign keys.
2. **`indexes.sql`**: A SQL script to create secondary indexes.
3. **`schema_explanation.md`**: Explaining the design, indexing strategies, and normalization choices.

---

## 4. How to Execute

Run the static generator script from the command line:

```bash
python3 .agents/skills/cloudsql/step1_schema/scripts/generate_schema.py \
  --config config/use_cases/<use_case_name>/use_case_config.json \
  --output-schema config/use_cases/<use_case_name>/cloudsql/schema.sql \
  --output-indexes config/use_cases/<use_case_name>/cloudsql/indexes.sql
```
