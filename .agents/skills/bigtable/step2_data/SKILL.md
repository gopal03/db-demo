---
name: bigtable_step2_data
description: "Generates realistic mock data for Bigtable tables based on a provided schema and demo parameters."
---


## 1. Core Bigtable Data Generation Principles

Unlike relational databases where data is generated as flat tables, Bigtable data must be structured to match its multi-dimensional map model: **`Table -> Row Key -> Column Family -> Column Qualifier -> Timestamp -> Value`**.

### A. Row Key Construction
The data generator must dynamically construct the row keys using the exact formula defined in Step 1.
* **Delimiter Joins**: Join segments using the designated delimiter (e.g., `#`, `:`).
* **Integer Padding**: If a segment is a numeric ID (e.g., `123`), pad it with leading zeroes (e.g., `0000000123`) to ensure lexicographical sorting matches numerical sorting.
* **Reversed Timestamps**: If the schema requires reversed timestamps, calculate them using:
  $$\text{Reversed Timestamp} = \text{Long.MAX\_VALUE} - \text{Current Timestamp in Microseconds}$$

### B. Timestamps (Microseconds)
* Bigtable cell timestamps are stored in **microseconds** (not milliseconds).
* The data generator must ensure all generated timestamps are 16-digit integers (e.g., `1782729600000000` for June 29, 2026).

### C. Simulating Time-Series and Cell Versioning
* If the table is a time-series or tracking table, generate multiple data points (cells) for the same row key or across consecutive row keys with varying timestamps.
* For column families with a `maxversions` GC policy, you can simulate writing multiple versions of the same cell to demonstrate historical queries.

### D. Structured Output Format
To make loading easy, the generator should output a structured JSON mutation file named `dummy_data.json` under the use-case directory (e.g., `config/use_cases/<use_case_name>/bigtable/`).

**Recommended JSON Structure**:
```json
[
  {
    "row_key": "company_123#device_000045#20260629",
    "cells": [
      {
        "family": "d",
        "qualifier": "device_name",
        "value": "Thermostat-A",
        "timestamp": 1782729600000000
      },
      {
        "family": "m",
        "qualifier": "temperature",
        "value": "72.5",
        "timestamp": 1782729600000000
      }
    ]
  }
]
```

---

## 2. Input Requirements
The agent expects the following inputs:
1. **Demo Parameters** (`demo_parameters.json`): To read the active scale profile (e.g., `small` = 500 rows) and database configurations.
2. **Bigtable Schema** (`schema.json`): To know the target tables and column families.
3. **Schema Explanation** (`schema_explanation.md`): To understand the row key formula.

---

## 3. Expected Outputs
The skill must produce:
1. **`dummy_data.json`**: The structured JSON mutation file containing the generated rows.
2. **`generate_data.py`**: The python script used to generate this data (saved in `scripts/` or the skill folder for reproducibility).
3. **`generation_report.md`**: A summary showing the number of rows generated, the range of row keys, and sample mutations.

---

## 4. Step-by-Step Instructions for the Agent

### Step 2.1: Read Configuration and Profile
1. Open `demo_parameters.json` and identify the active data profile (e.g., `small`, `medium`).
2. Read the `rows_per_table` parameter for the active profile.

### Step 2.2: Implement the Row Key Formatter
1. Write a helper function in your generator script that takes the entity attributes and formats them into a byte-compatible string row key, applying delimiters, padding, and timestamp reversals.

### Step 2.3: Generate the Mock Data
1. Generate realistic values using a library (or standard random distributions).
2. Ensure data types are converted to strings (as Bigtable stores values as raw bytes, strings are the most portable format for demo loading).
3. Generate multiple cells per row as defined by the column families.

### Step 2.4: Write Outputs
1. Save the generated JSON to `config/use_cases/<use_case_name>/bigtable/dummy_data.json`.
2. Save the generator script to `config/use_cases/<use_case_name>/bigtable/generate_data.py` (or inside the skill's script directory if making it reusable).
3. Output the markdown report.

