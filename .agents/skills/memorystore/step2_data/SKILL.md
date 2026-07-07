---
name: memorystore_step2_data
description: "Generates mock data payloads optimized for Memorystore Redis data structures."
---


## 1. Core Memorystore Data Generation Principles

Data generated for Memorystore must map to Redis commands and data types (Hashes, Sorted Sets).

### A. Key-Value Formatting
* The generated JSON structure should align with the designed Redis keys.
  * *Recommended JSON format*:
    ```json
    {
      "hashes": {
        "customer:cust-0000001": {
          "name": "Jane Doe",
          "email": "jane@example.com",
          "preferred_store_id": "store:stor-0000001"
        }
      },
      "sorted_sets": {
        "customer:cust-0000001:views": [
          {"score": 1782729600.0, "value": "view-0001#prod-0001#120#Desktop"}
        ]
      }
    }
    ```

### B. Timestamp Scores
* For Sorted Sets, timestamps must be converted to numeric scores (float representing Unix epochs in seconds or milliseconds) to allow range queries via `ZRANGEBYSCORE`.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Providing scale profiles and counts.
2. **Memorystore Schema** (`schema.json`): Defining key prefixes and Redis types.

---

## 3. Expected Outputs
The skill must produce:
1. **`dummy_data.json`**: The formatted Redis command/data JSON.
2. **`generate_data.py`**: The python generator script.
3. **`generation_report.md`**: Summarizing keys created.

---

## 4. Step-by-Step Instructions for the Agent

### Step 2.1: Analyze Scale Profile
1. Read the active profile and database limits from `demo_parameters.json`.

### Step 2.2: Implement `generate_data.py`
1. Write a python script that creates profiles (customers, products, stores) as dictionary hashes.
2. Create view and purchase timeline events as list structures containing a float epoch score and a delimited member string.
3. Write the output to `config/use_cases/<use_case_name>/memorystore/dummy_data.json`.

### Step 2.3: Generate report
1. Output `generation_report.md` summarizing key counts and sizes.
