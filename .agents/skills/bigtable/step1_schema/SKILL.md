---
name: bigtable_step1_schema
description: "Translate a database-agnostic use-case configuration into an optimized Bigtable schema (tables, column families, and GC policies) using GCP best practices."
---


## 1. Core Bigtable Schema Design Principles

Bigtable is a sparse, distributed, persistent multi-dimensional sorted map. It has only **one index**: the **Row Key**. Poor schema design (especially Row Key design) will result in hotspots, poor performance, and difficult data migrations.

### A. Row Key Design Best Practices
1. **Query-Driven Design**: Design row keys strictly based on how the application will read the data. The most efficient queries retrieve data by:
   * A single row key.
   * A row key prefix (starting range).
   * A contiguous range of row keys (start key to end key).
2. **Avoid Hotspotting (Write Distribution)**:
   * **NEVER** start a row key with a timestamp or sequential ID. This forces all writes to go to a single tablet server (hotspotting).
   * Precede timestamps or sequential IDs with a **high-cardinality value** (e.g., `device_id`, `user_id`, or `customer_id`).
   * If using sequential IDs, reverse them (e.g., `12345` $\rightarrow$ `54321`) to distribute writes.
3. **Multi-Segment Row Keys**:
   * Combine multiple fields using a delimiter (typically `#`, `:`, or `/`).
   * Place the most general/broadest query filter first, followed by more granular fields, and finally the timestamp (e.g., `tenant_id#device_type#device_id#timestamp`).
4. **Lexicographical Sorting**:
   * Bigtable sorts keys alphabetically/by byte value.
   * **Pad integers** with leading zeroes (e.g., `03` instead of `3`) so they sort numerically (`03` < `20`, whereas lexicographically `20` < `3`).
   * If the query pattern requires retrieving the **most recent data first**, use a **reversed timestamp** (`Long.MAX_VALUE - timestamp`).
5. **Keep Keys Short**: Row keys must be under 4KB, but ideally should be kept under 100 bytes to conserve memory and reduce network overhead.
6. **Use Human-Readable Strings**: Avoid hashing row keys. Human-readable keys make debugging with tools like **Key Visualizer** much easier.
7. **Reverse Domain Names**: If storing domain-based data, reverse them (e.g., `com.google.maps`) to group related domains together.

### B. Column Family & GC Policy Best Practices
1. **Minimize Column Families**: Keep the number of column families small (typically 1 to 3, absolute maximum of 100). Group columns that are queried together or share the same lifecycle.
2. **Short Names**: Use short, clean names for column families (e.g., `f`, `m`, `stat`) to save disk space (family names are stored with every cell value).
3. **Define Garbage Collection (GC) Policies**:
   * Every column family must have a GC policy to prevent unbounded growth.
   * **Age-based**: Delete cells older than $N$ days (e.g., `maxage=30d`).
   * **Version-based**: Keep only the last $N$ versions of a cell (e.g., `maxversions=3`).
   * **Union/Intersection**: Combine them (e.g., keep up to 3 versions, but delete anything older than 30 days).

---

## 2. Input Requirements
The agent expects the following inputs:
1. **Use-case Configuration** (`use_case_config.json`): Specifying entities, attributes, relationships, and primary query patterns.
2. **Demo Parameters** (`demo_parameters.json`): Providing the `project_id` and the `bigtable` configuration blocks.

---

## 3. Expected Outputs
The skill must produce the following files in the use-case directory (e.g., `config/use_cases/<use_case_name>/bigtable/`):
1. **`schema.json`**: A declarative JSON representation of the Bigtable tables, column families, and GC policies.
2. **`create_tables.sh`**: A shell script containing `cbt` CLI commands to provision the tables and set up GC policies.
3. **`schema_explanation.md`**: A markdown document explaining:
   * The designed Row Key structure and why it avoids hotspotting.
   * The column families and their GC policies.
   * How the primary query patterns are satisfied using row key prefix scans or lookups.

---

## 4. Step-by-Step Instructions for the Agent

### Step 4.1: Analyze Use Case and Queries
1. Read the `use_case_config.json` to identify:
   * The core entities (e.g., `users`, `events`, `metrics`).
   * The write frequency (is it high-throughput time-series?).
   * The primary read queries (e.g., "Get last 50 metrics for device X", "Get all events for tenant Y on date Z").

### Step 4.2: Design the Row Key(s)
1. For each table, construct a row key formula:
   * *Example (Time-Series)*: `[high_cardinality_id]#[metric_type]#[reversed_timestamp]`
   * *Example (Multi-Tenant)*: `[tenant_id]#[entity_type]#[entity_id]`
2. Verify:
   * Does it start with a timestamp? (If yes, reject and prepend a high-cardinality ID).
   * Does it support the primary queries using prefix scans?
   * Are integers padded?
   * Is it under 100 bytes?

### Step 4.3: Define Column Families and GC Policies
1. Group the entity's attributes into 1-3 column families.
   * *Example*: `d` (for static/infrequently changing descriptive data), `m` (for rapidly changing metrics/measures).
2. Assign a GC policy to each family based on the use case (e.g., keep metrics for 30 days; keep only the latest version of descriptive data).

### Step 4.4: Generate the Schema Files
1. Create the `bigtable/` subdirectory under the active use-case folder.
2. Write the `schema.json` file.
3. Write the `create_tables.sh` script using `cbt` commands.
   * *Example `cbt` command*:
     ```bash
     cbt createtable my-table
     cbt createfamily my-table m
     cbt setgcpolicy my-table m maxage=30d
     ```
4. Write `schema_explanation.md` detailing the design decisions.

