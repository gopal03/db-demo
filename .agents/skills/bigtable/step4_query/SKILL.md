---
name: bigtable_step4_query
description: "Execute optimized Bigtable queries (prefix scans, filters, multi-version lookups) and generate value-driven talk tracks."
---



## 1. Core Bigtable Query Best Practices

Because Bigtable only indexes row keys, querying must be highly structured to ensure sub-10ms response times.

### A. Avoid Full Table Scans
* **Never** execute queries that require reading the entire table and filtering on the client side.
* Ensure all queries target a specific **row key**, a **list of row keys**, or a **contiguous range (prefix)**.

### B. Use Prefix and Range Scans
* To read related data, use a `RowRange` with a start and end key, or use a prefix filter.
* *Example (Python)*:
  ```python
  import google.cloud.bigtable.row_filters as filters
  
  # Read all rows for a specific device
  row_set = RowSet()
  row_set.add_row_range(RowRange(start_key=b"device_001#", end_key=b"device_001~"))
  rows = table.read_rows(row_set=row_set)
  ```

### C. Leverage Server-Side Filters
Filters allow Bigtable to discard unwanted data on the server before sending it over the network:
1. **`LatestCellsFilter` / `LatestVersionFilter`**: If you only care about the current state, restrict the query to return only the latest version of each cell.
2. **`ColumnQualifierRegexFilter`**: Retrieve only specific columns (e.g., only `temperature` and not `humidity`).
3. **`TimestampRangeFilter`**: Retrieve metrics within a specific time window.
4. **`StripValueFilter`**: Returns only the row keys and column names, omitting the values. Useful for checking existence or metadata.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Providing connection credentials.
2. **Bigtable Schema** (`schema.json`): Detailing the table structure.
3. **Schema Explanation** (`schema_explanation.md`): Detailing the designed query patterns.

---

## 3. Expected Outputs
The skill must produce:
1. **`run_queries.py`**: A Python script containing the demo queries showing off different Bigtable features.
2. **`talktrack.md`**: A customer-facing guide explaining:
   * What each query does.
   * Why the query is highly performant (e.g., "This is a prefix scan that avoids a table scan").
   * How Bigtable's architecture supports this pattern at petabyte scale.

---

## 4. Step-by-Step Instructions for the Agent

### Step 4.1: Identify Demo Query Scenarios
Design 3 distinct query scenarios to showcase:
1. **Single Row Lookup**: Showing sub-millisecond point-read latency (e.g., "Get current status of Device X").
2. **Time-Series Range Scan**: Showing high-throughput scan performance over a time window (e.g., "Get all metrics for Device X between 9:00 AM and 10:00 AM").
3. **Multi-Version Query**: Showing how Bigtable stores historical states in cells (e.g., "Get the last 5 changes to the configuration of Device X").

### Step 4.2: Write the Query Script (`run_queries.py`)
1. Implement the scenarios using the Google Cloud Bigtable Python SDK.
2. Explicitly use `row_filters` to limit the data returned.
3. Add print statements showing the execution time for each query.

### Step 4.3: Write the Talk Track (`talktrack.md`)
1. For each query, write a brief explanation of:
   * **The Business Value**: Why does the customer care about this query? (e.g., real-time dashboarding, audit history).
   * **The Technical Detail**: How does the row key design enable this query to run in milliseconds?
