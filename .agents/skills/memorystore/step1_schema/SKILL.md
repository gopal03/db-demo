---
name: memorystore_step1_schema
description: "Design an optimized Redis key space schema for Memorystore, selecting appropriate Redis data structures (Hashes, Sorted Sets, Sets) to support target queries."
---


## 1. Core Memorystore (Redis) Key Design Principles

Memorystore for Redis is an in-memory key-value database. Since there are no native tables or schemas, you must structure the data using Redis key conventions and data types.

### A. Key Namespacing
* Use a consistent, delimiter-based key prefixing scheme to represent relationships (typically using colons `:`).
  * *Example*: `customer:{customer_id}` (e.g. `customer:cust-0000045`).
* Key length: Keep key names short but descriptive. Long keys consume unnecessary memory.

### B. Selecting the Right Redis Data Type
1. **Hashes (`HSET`, `HGETALL`)**: Best for representing structured objects (e.g., profiles).
   * *Example*: `customer:cust-0000045` $\rightarrow$ Map of `{name: "John", email: "john@example.com", segment: "VIP"}`.
2. **Sorted Sets (`ZADD`, `ZRANGE`)**: Best for ordering values by a numeric score (ideal for time-series, log interactions, or timelines).
   * *Example*: `customer:cust-0000045:views` $\rightarrow$ Sorted Set where the **score** is the timestamp and the **member** is a serialized view event (e.g., `view_id#product_id#duration`).
3. **Sets (`SADD`, `SINTER`)**: Best for unique, unordered collections (e.g., unique product tags or purchases).
   * *Example*: `customer:cust-0000045:purchased_products` $\rightarrow$ Set of unique product IDs bought.
4. **Strings (`SET`, `GET`)**: Best for simple key-value lookups or storing pre-serialized JSON blobs.

### C. Relationship Modeling (Client-side Referencing)
* Since Redis does not support joins, model references as pointers. For example, a customer hash might contain a field `preferred_store_id: "store:stor-001"`. The client first reads the customer hash, retrieves the store key, and then reads the store hash.

---

## 2. Input Requirements
The agent expects:
1. **Use-case Configuration** (`use_case_config.json`): Detailing entities, parameters, and access queries.
2. **Demo Parameters** (`demo_parameters.json`): Connection parameters.

---

## 3. Expected Outputs
The skill must produce:
1. **`schema.json`**: A declarative JSON mapping out the Redis key spaces, prefixes, selected data types, and field mappings.
2. **`schema_explanation.md`**: Explaining the namespace design, data structure selection rationale, and join strategy.

---

## 4. Step-by-Step Instructions for the Agent

### Step 1.1: Map Entities to Redis Data Structures
Evaluate the use case entities and queries:
1. Map basic profiles (e.g., `Customers`, `Products`, `Stores`) to **Hashes** (`customer:{id}`, `product:{id}`, `store:{id}`).
2. Map time-series events (e.g., `CustomerViews`, `CustomerPurchases`) to **Sorted Sets** (`customer:{id}:views`, `customer:{id}:purchases`) using the event timestamp as the score.
3. Map flat relationships (e.g. `ProductInventory`) to **Hashes** using composite keys (`inventory:{product_id}:{store_id}`).

### Step 1.2: Document Key Mappings
1. Write the designed schemas and keyspace definitions into `schema.json`.
2. Detail how the fields inside Hashes and elements inside Sorted Sets will be structured.

### Step 1.3: Write Explanation
1. Save `schema.json` and `schema_explanation.md` to `config/use_cases/<use_case_name>/memorystore/`.
