---
name: memorystore_step4_query
description: "Execute optimized keyspace lookups and range queries against Memorystore (Redis), implement client-side joins, and write a customer talk track."
---


## 1. Core Memorystore Query Best Practices

Redis is single-threaded; queries must run in $O(1)$ or $O(\log N)$ time to prevent blocking the engine.

### A. Avoid Blocking Commands
* **Never** use the `KEYS *` command in a production or live demo environment. It is an $O(N)$ blocking operation that scans the entire database, causing latency spikes.
* **Best Practice**: Target keys directly using their namespace structure. To scan or iterate, use `SCAN` which incrementally returns keys.

### B. Fast Lookups and Ranges
* **Hashes (`HGETALL` / `HMGET`)**: Fetch specific object fields in $O(1)$ time.
* **Sorted Sets (`ZRANGEBYSCORE`)**: Query range events chronologically (e.g. all views between two epochs) in $O(\log N + M)$ where $M$ is the number of elements returned.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Connection properties.
2. **Key Schema** (`schema.json`): Outlining key namespace patterns.

---

## 3. Expected Outputs
The skill must produce:
1. **`run_queries.py`**: A python script executing keyspace scans, hashed reads, and sorted set ranges.
2. **`talktrack.md`**: A customer guide explaining:
   * The query logic and command sequence.
   * How Redis's in-memory single-threaded execution guarantees sub-millisecond response times.
   * Caching/lookaside strategies.

---

## 4. Step-by-Step Instructions for the Agent

### Step 4.1: Convert Use-Case Queries to Redis Command Paths
1. **Point Lookup**: Fetch customer profile details using `HGETALL customer:{customerId}`.
2. **Interactions Timeline**: Fetch views for a customer using `ZRANGEBYSCORE customer:{customerId}:views -inf +inf` (or specify epoch bounds).
3. **Cross-Entity Join (Client-side)**: Fetch the customer's preferred store from the customer hash, then fetch the store hash details, and join them in Python.

### Step 4.2: Write the Query Script (`run_queries.py`)
1. Implement the queries using `redis`.
2. Measure roundtrip latency (expecting < 1ms for individual operations).
3. Print query commands, results, and timing.

### Step 4.3: Write the Talk Track (`talktrack.md`)
1. Explain how memory-first databases solve OLTP scalability challenges.
2. Document the exact command flow and key structures.
