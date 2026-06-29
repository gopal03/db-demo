---
name: step1_schema_generation
description: "Translate the JSON configuration of a Spanner Graph use-case into best-practice SQL DDL statements."
---

# Step 1: Schema Generation Skill

This skill governs the translation of a graph use case configuration (e.g. `config/security_isv_blast_radius.json`) into optimal Google Standard SQL DDL for Cloud Spanner Graph.

## Best Practices for Spanner Graph DDL

1. **Table Definitions**:
   * Define node tables and edge tables explicitly as standard tables.
   * Use specific types: `STRING(36)` for UUIDs/IDs, `TIMESTAMP` for dates. Avoid unsized `STRING` unless necessary.
   * Primary Keys: Ensure all node tables have clear primary keys. Edge tables must have primary keys that uniquely identify each edge (often a composite key of source ID, destination ID, and an optional discriminator like port or timestamp).

2. **Interleaving Edge Tables**:
   * For optimal graph query traversal performance, interleave the edge tables inside the parent source node table.
   * The primary key of the edge table must be prefixed with the parent node table's primary key.
   * Append `INTERLEAVE IN PARENT <SourceNodeTable> ON DELETE CASCADE`.

3. **Property Graph Definition**:
   * Use `CREATE PROPERTY GRAPH <GraphName>` statement.
   * Inside `NODE TABLES`, define each node table with its `KEY` and `LABEL`.
   * Inside `EDGE TABLES`, define each edge table with its `KEY`, `SOURCE KEY ... REFERENCES ...`, `DESTINATION KEY ... REFERENCES ...`, and `LABEL`.
   * Keep property configurations clean and consistent.

## How to Execute

Run the script from the command line:

```bash
python3 .agents/skills/step1_schema_generation/scripts/generate_schema.py --config config/security_isv_blast_radius.json --output config/generated_schema.sql
```
