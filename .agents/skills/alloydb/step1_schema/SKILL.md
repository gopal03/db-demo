---
name: alloydb_step1_schema
description: "Translate a database-agnostic use-case configuration into an optimized AlloyDB schema (PostgreSQL DDL) and Columnar Engine recommendations using a static generator."
---


## 1. Core AlloyDB Schema Design Principles

AlloyDB is a fully managed, PostgreSQL-compatible database engine designed for enterprise workloads. It combines PostgreSQL compatibility with advanced GCP-native storage and compute optimizations, most notably the **AlloyDB Columnar Engine**.

### A. Table and Index Design Best Practices
1. **Primary Keys**: Explicitly define primary keys for all tables. Use `UUID` or `BIGSERIAL` (auto-incrementing integers) for identifiers.
2. **Data Types**: Use correct PostgreSQL types (`VARCHAR`, `BIGINT`, `NUMERIC`, `TIMESTAMPTZ`).
3. **Foreign Keys**: Define explicit foreign key constraints to maintain referential integrity.
4. **Deferred Indexing**: Index creation is handled post-data-ingestion in Step 3.

### B. AlloyDB Columnar Engine Configuration
AlloyDB includes a Columnar Engine that stores selected columns or tables in an in-memory columnar format, speeding up analytical queries by orders of magnitude.
* **Auto-Columnarization**: The static script automatically registers all tables in a `columnar_config.sql` script to load them into the Columnar store.

---

## 2. Input Requirements
The agent expects the following inputs:
1. **Use-case Configuration** (`use_case_config.json`): Specifying tables, attributes, relationships, and queries.
2. **Demo Parameters** (`demo_parameters.json`): Specifying active scale profiles and AlloyDB connection details.

---

## 3. Expected Outputs
The skill must produce the following files in the use-case directory (e.g., `config/use_cases/<use_case_name>/alloydb/`):
1. **`schema.sql`**: A DDL script containing the PostgreSQL statements to create tables and primary/foreign keys.
2. **`indexes.sql`**: A SQL script to create index structures for foreign keys.
3. **`columnar_config.sql`**: A SQL script containing commands to register analytical tables with the Columnar Engine.
4. **`schema_explanation.md`**: Explaining the design, indexing strategies, and columnar selections.

---

## 4. How to Execute

Run the static generator script from the command line:

```bash
python3 .agents/skills/alloydb/step1_schema/scripts/generate_schema.py \
  --config config/use_cases/<use_case_name>/use_case_config.json \
  --output-schema config/use_cases/<use_case_name>/alloydb/schema.sql \
  --output-indexes config/use_cases/<use_case_name>/alloydb/indexes.sql \
  --alloydb-columnar config/use_cases/<use_case_name>/alloydb/columnar_config.sql
```
