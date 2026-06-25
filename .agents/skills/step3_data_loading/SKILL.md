---
name: step3_data_loading
description: "Provision Google Cloud Spanner instances and databases, deploy DDL schemas, and load dummy data efficiently."
---

# Step 3: Data Loading Skill

This skill handles provisioning and data ingestion on Cloud Spanner.

## Best Practices for Spanner Provisioning and Loading

1. **Auto-Provisioning**:
   * Verify the existence of the Spanner Instance before creation. If missing, create it using standard regional configuration (e.g. `regional-us-central1`).
   * Verify the database. If missing, create it and execute the generated DDL statements to set up the property graph schema.

2. **Efficient Loading via Mutations**:
   * Do not use standard row-by-row SQL `INSERT` statements as they add network round-trip overhead.
   * Use **Mutations** with `database.batch()` context managers.
   * Write data in logical dependency order: Nodes (Parents) first, followed by Edges (Children) that reference those nodes. This avoids foreign key violations and satisfies interleaving constraints.

3. **Data Type Handling**:
   * Parse timestamp strings into Python `datetime` objects with UTC timezone before submitting mutations.

## How to Execute

Run the script from the command line:

```bash
python3 .agents/skills/step3_data_loading/scripts/load_data.py --parameters config/spanner_parameters.json --schema config/generated_schema.sql --data config/dummy_data.json [--recreate]
```
