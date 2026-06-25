---
name: step2_data_generation
description: "Simulate and generate realistic mock data that preserves logical paths and referential integrity for Spanner Graph tables."
---

# Step 2: Data Generation Skill

This skill governs the synthesis of high-fidelity graph data aligned with the schema defined in Step 1.

## Best Practices for Graph Data Synthesis

1. **Referential Integrity**:
   * Any edge row must link a valid source node primary key to a valid destination node primary key.
   * IDs must match exactly.

2. **Ensuring Path Connectivity**:
   * Do not generate purely random data.
   * Ensure specific, predictable paths exist to demonstrate the queries. For example, ensure that a compromised account can assume a role that has permissions to a gateway resource, which in turn has network flows to target databases.

3. **Data Formatting**:
   * Generate data in a clean format such as a single `config/dummy_data.json` containing key-value pairs where keys match the table names and values are lists of records.

## How to Execute

Run the script from the command line:

```bash
python3 .agents/skills/step2_data_generation/scripts/generate_data.py --config config/security_isv_blast_radius.json --output config/dummy_data.json
```
