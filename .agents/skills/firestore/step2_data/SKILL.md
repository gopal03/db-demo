---
name: firestore_step2_data
description: "Generates document-oriented mock data for Firestore, embedding nested fields and denormalized properties."
---


## 1. Core Firestore Data Generation Principles

Data generated for Firestore must reflect document nesting, subcollection structures, and denormalization.

### A. Document Hierarchy
* Organize data into collections.
* For subcollections, structure the output to clearly map the hierarchy.
  * *Recommended JSON schema*:
    ```json
    {
      "customers": [
        {
          "doc_id": "cust-0000001",
          "data": {
            "name": "Jane Doe",
            "email": "jane.doe@example.com"
          },
          "subcollections": {
            "views": [
              {
                "doc_id": "view-0000001",
                "data": {
                  "product_id": "prod-0000001",
                  "timestamp": "2026-06-29T12:00:00Z"
                }
              }
            ]
          }
        }
      ]
    }
    ```

### B. Denormalized Fields
* When generating data for a document, fetch the relevant values from related entities (e.g. products) and write them directly into the document cells (e.g., embedding `product_name` and `price` inside a purchase document).

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Providing the scale profiles and row boundaries.
2. **Firestore Schema** (`schema.json`): Defining collections, hierarchies, and denormalized fields.

---

## 3. Expected Outputs
The skill must produce:
1. **`dummy_data.json`**: The structured document dataset.
2. **`generate_data.py`**: The python generator script.
3. **`generation_report.md`**: Summary of documents created.

---

## 4. Step-by-Step Instructions for the Agent

### Step 2.1: Read Configuration
1. Open `demo_parameters.json` and read the `rows_per_table` value for the active profile to scale document counts.

### Step 2.2: Implement `generate_data.py`
1. Write a script that first generates independent entities (e.g. products, stores).
2. Generate customers. In memory, keep a cache of products and stores.
3. When generating subcollections (like `views`) or dependent collections (like `purchases`), perform the denormalization by looking up product properties from memory and embedding them inside the record.
4. Save the nested output JSON structure to `config/use_cases/<use_case_name>/firestore/dummy_data.json`.

### Step 2.3: Output Report
1. Save `generation_report.md` with counts of root documents and sub-documents generated.
