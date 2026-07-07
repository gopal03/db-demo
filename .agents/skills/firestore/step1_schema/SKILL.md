---
name: firestore_step1_schema
description: "Translate a database-agnostic use-case configuration into a document-oriented Firestore schema model, specifying collections, subcollections, and composite index configurations."
---


## 1. Core Firestore Schema Design Principles

Firestore is a serverless, NoSQL document database. Data is organized into **Documents** and **Collections**. Firestore has no native schema enforcement, making structural design and indexing crucial.

### A. Document modeling options
1. **Subcollections vs. Root Collections**:
   * **Subcollections**: Best for data that is owned by a parent document and only read in that context (e.g., `customers/cust_123/views/view_456`).
   * **Root Collections**: Best when you need to query entities independently of their parent (e.g., querying all purchases across all customers). In this case, store the parent ID as a field inside the document.
2. **Denormalization**:
   * To avoid multiple client-side lookups (since Firestore does not support `JOIN` operations), duplicate static, small fields. For example, store `product_name` and `price_paid` directly inside a purchase document instead of just referencing `product_id`.
3. **Document Limits**: Keep individual documents under the **1 MB limit**. For high-write entities, avoid storing arrays that grow unboundedly inside a single document; use subcollections instead.

### B. Indexing requirements
1. **Single-field Indexes**: Firestore automatically creates indexes for every field in a document.
2. **Composite Indexes**: If a query filters on multiple fields (e.g., `WHERE loyalty_tier == 'Platinum' AND signup_date > '2026-01-01'`) or combines filtering and sorting, you must define a **composite index**.
3. **Index Configurations**: Define these in a `firestore.indexes.json` file to deploy them automatically via the Firebase CLI.

---

## 2. Input Requirements
The agent expects:
1. **Use-case Configuration** (`use_case_config.json`): Detailing entities, attributes, and access queries.
2. **Demo Parameters** (`demo_parameters.json`): Connection parameters.

---

## 3. Expected Outputs
The skill must produce:
1. **`schema.json`**: A declarative JSON mapping out the collection paths, document fields, and denormalized structures.
2. **`firestore.indexes.json`**: A configuration file defining the composite indexes required for the use case.
3. **`schema_explanation.md`**: Explaining the collection structure, denormalization strategy, and index justifications.

---

## 4. Step-by-Step Instructions for the Agent

### Step 1.1: Design Collections
Evaluate the primary queries in `use_case_config.json`:
1. If a query requires searching across all instances of an entity (e.g., listing all product purchases to evaluate affinity), design it as a **Root Collection** (e.g., a top-level `purchases` collection).
2. If an entity is tightly bound to a parent (e.g., user views), design it as a **Subcollection** (e.g. `customers/{customerId}/views`).

### Step 1.2: Apply Denormalization
1. For transaction-like collections (e.g. `purchases`), copy vital attributes (such as `product_name`, `product_category`, and `price`) from the original entity to prevent multi-hop client-side fetching.

### Step 1.3: Specify Composite Indexes
1. Examine queries that filter on multiple properties. Write the required composite index definitions into `firestore.indexes.json`.
   * *Example index entry format*:
     ```json
     {
       "indexes": [
         {
           "collectionGroup": "customers",
           "queryScope": "COLLECTION",
           "fields": [
             { "fieldPath": "loyalty_tier", "order": "ASCENDING" },
             { "fieldPath": "signup_date", "order": "DESCENDING" }
           ]
         }
       ]
     }
     ```

### Step 1.4: Write Outputs
1. Save `schema.json`, `firestore.indexes.json`, and `schema_explanation.md` to `config/use_cases/<use_case_name>/firestore/`.
