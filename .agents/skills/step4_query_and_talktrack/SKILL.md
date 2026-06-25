---
name: step4_query_and_talktrack
description: "Create a few queries and talk track on how best to demonstrate Spanner Graph solution."
---

# Step 4: Query and Talk Track Skill

This skill governs running GQL queries on Spanner Graph and presenting them alongside a customer-facing sales talk track.

## Best Practices for Demonstrating Spanner Graph

1. **Focus on Query Simplicity**:
   * Contrast the Spanner Graph GQL query with equivalent SQL (which would require multiple joins or recursive CTEs).
   * Emphasize readability of the `MATCH (node)-[edge]->(node)` structure.

2. **Structure the Talk Track**:
   * Start with the **Problem** (e.g. "We need to find what systems are compromised").
   * Explain the **GQL Query** (e.g. "We match the Account, Role, and Resource directly").
   * Explain the **Value** (e.g. "Spanner Graph performs this highly connected lookup at Cloud scale with transactional consistency").

## How to Execute

Run the script from the command line:

```bash
python3 .agents/skills/step4_query_and_talktrack/scripts/run_query.py --parameters config/spanner_parameters.json --usecase config/security_isv_blast_radius.json [--query <query_id>]
```
