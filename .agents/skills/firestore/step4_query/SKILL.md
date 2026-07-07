---
name: firestore_step4_query
description: "Execute optimized NoSQL queries against Firestore, perform client-side joins, and construct a customer-facing guide."
---


## 1. Core Firestore Query Best Practices

Firestore queries are designed to scale automatically with the size of the result set, not the size of the database. Understanding query limits is essential.

### A. Query Constraints and Filtering
* **No Joins**: Firestore does not support native joins. Join operations must be performed on the client side (e.g. fetching a customer document, then querying their views subcollection, and matching results in Python code).
* **No Server-Side Aggregations**: Standard group by or multi-document aggregations are not supported on the server (except basic `COUNT()`, `SUM()`, and `AVG()` aggregates which are now supported natively but restricted). Advanced analysis requires loading documents and aggregating in the client code.
* **Equality and Inequality**: A query can have inequality filters (`<`, `>`, `<=`, `>=`) on only one field. If you filter on multiple fields, one of them must be an equality match (`==`).

### B. Index Matching
* If a query fails with an error stating that a composite index is missing, the error message will contain a direct URL to create that index in the Google Cloud Console. Click it or deploy the index via your `firestore.indexes.json` configuration file.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Connection details.
2. **Firestore Schema** (`schema.json`): Detailing collections and attributes.

---

## 3. Expected Outputs
The skill must produce:
1. **`run_queries.py`**: A python script executing point reads, composite queries, and client-side join logic to solve the use-case query scenarios.
2. **`talktrack.md`**: A customer guide explaining:
   * The query logic.
   * How Firestore's index-scaling architecture guarantees rapid, predictable latency.
   * A walkthrough of how the client-side join was implemented to solve relational queries.

---

## 4. Step-by-Step Instructions for the Agent

### Step 4.1: Model the Queries
Convert the use-case queries into Firestore query patterns:
1. **Point Lookup**: Retrieve a single document by its path (e.g. `db.collection('customers').document(customerId).get()`).
2. **Compound Filter Query**: Query a collection using multiple `.where()` filters. Ensure a composite index is active if filtering on multiple fields or adding a sort.
3. **Client-Side Join Query**: Query a customer document, query a separate collection (e.g., `purchases`) filtering by that customer's ID, and merge the datasets in memory.

### Step 4.2: Write the Query Script (`run_queries.py`)
1. Write the Python queries using `google.cloud.firestore`.
2. Print the query code, the execution results, and the measured roundtrip latency.

### Step 4.3: Write the Talk Track (`talktrack.md`)
1. Explain how NoSQL databases scale lookup and search performance independently of total database volume.
2. Discuss the trade-offs of client-side joining versus server-side joins.
