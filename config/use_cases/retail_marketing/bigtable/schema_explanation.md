# Bigtable Schema Design for Retail Marketing

This document explains the schema designed to support the Retail Marketing use case in Google Cloud Bigtable. Since Bigtable indexes data only by Row Key, the tables and keys are structured to avoid hotspotting while supporting high-throughput lookups and range scans.

## 1. Tables and Row Key Designs

### A. Table: `customers`
* **Purpose**: Stores customer profiles and retail preferences.
* **Row Key**: `customer_id` (e.g. `cust-0000045`)
  * *Rationale*: Point lookup is very fast. High cardinality of customer IDs prevents write hotspotting when creating new customers.
* **Column Families**:
  * `d` (descriptive data): Stores fields like `name`, `email`, `segment`, `loyalty_tier`, `signup_date`.
  * `p` (preferences): Stores `preferred_store_id`.
* **GC Policy**: `maxversions=1` for both families, as we only need the latest profile details.

### B. Table: `products`
* **Purpose**: Stores catalog information for products.
* **Row Key**: `product_id` (e.g. `prod-0000021`)
  * *Rationale*: Point lookup on product information. High cardinality.
* **Column Families**:
  * `d` (descriptive data): Stores `name`, `category`, `brand`, `price`.
* **GC Policy**: `maxversions=1`.

### C. Table: `stores`
* **Purpose**: Stores physical storefront information.
* **Row Key**: `store_id` (e.g. `stor-0000001`)
* **Column Families**:
  * `d` (descriptive data): Stores `name`, `city`, `state`, `zip_code`.
* **GC Policy**: `maxversions=1`.

### D. Table: `inventory`
* **Purpose**: Tracks inventory quantities at different stores.
* **Row Key**: `product_id#store_id` (e.g. `prod-0000021#stor-0000001`)
  * *Rationale*: Allows checking inventory for a product across all stores using a prefix scan (`prod-0000021#`), or a point lookup for a specific store.
* **Column Families**:
  * `d` (details): `quantity`, `aisle_location`.
* **GC Policy**: `maxversions=1`.

### E. Table: `customer_events`
* **Purpose**: Tracks customer interactions: views and purchases.
* **Row Key**: `customer_id#event_type#reversed_timestamp`
  * *Components*:
    1. `customer_id`: Prefix groups all interactions for a customer.
    2. `event_type`: Separates `view` from `purchase` (enabling scanning only views or only purchases).
    3. `reversed_timestamp`: Calculated as `Long.MAX_VALUE - timestamp_micros`. Ensures the most recent interactions appear first in scans.
  * *Rationale*: Prevents hotspotting because customer ID has high cardinality. Groups a customer's temporal events together, which matches the query patterns.
* **Column Families**:
  * `e` (event details):
    * For `view` events: `product_id`, `duration_seconds`, `device_type`.
    * For `purchase` events: `product_id`, `store_id`, `quantity`, `price_paid`.
* **GC Policy**: `maxversions=5`. Stores up to 5 versions of cell modifications if retried, keeping history clean.

---

## 2. How the Schema Satisfies the Demo Queries

### Query 1: Online Browsing to In-Store Purchases (Omnichannel Conversion)
* **Goal**: Identify customers who viewed a product online and purchased it at their preferred physical store.
* **Scan Pattern**:
  1. For a given customer (or scan all customers):
     * Read `customers` table to get the customer's profile and `preferred_store_id`.
     * Perform a prefix scan on `customer_events` for row keys starting with `customer_id#view#` to retrieve all product view events.
     * Perform a prefix scan on `customer_events` for row keys starting with `customer_id#purchase#` to retrieve all purchase events.
  2. Client-side join: Match `product_id` across views and purchases, and verify the purchase's `store_id` matches the customer's `preferred_store_id`.

### Query 2: High-Value Platinum Cart Abandonment
* **Goal**: Find Platinum loyalty customers who spent > 3 minutes viewing a product (> $100) but didn't buy it.
* **Scan Pattern**:
  1. Scan the `customers` table filtering for `loyalty_tier` = `Platinum`.
  2. For each Platinum customer:
     * Scan `customer_events` with prefix `customer_id#view#` to get all views. Filter on client side for `duration_seconds` > 180.
     * Lookup the viewed products in the `products` table to check if `price` > 100.
     * Scan `customer_events` with prefix `customer_id#purchase#` to check if there is a matching purchase for that `product_id`.

### Query 3: Cross-Category Product Affinity
* **Goal**: Find pairs of products from different categories purchased by the same customer.
* **Scan Pattern**:
  1. Scan all rows in `customer_events` or look for `customer_id#purchase#` row key segments.
  2. Group purchased `product_ids` per customer.
  3. Resolve the product categories from the `products` table.
  4. Perform counting/aggregation on client side.
