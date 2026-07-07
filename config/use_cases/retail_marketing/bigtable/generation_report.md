# Bigtable Data Generation Report

* **Generation Date (UTC)**: 2026-07-01T21:59:44.979812+00:00
* **Scale Profile**: small
* **Base Target Size**: 500 rows

## Summary of Generated Rows

* **Table `customers`**: 500 rows
* **Table `products`**: 100 rows
* **Table `stores`**: 10 rows
* **Table `inventory`**: 300 rows
* **Table `customer_events`**: 1,305 rows (Views & Purchases)

## Configured Test Scenarios

1. **Scenario 1 (Omnichannel Conversion)**:
   * Customer: `cust-0000000` (VIP/Platinum)
   * Preferred Store: `stor-0000005`
   * Event flow: Viewed product `prod-0000000` online, then purchased it in store `stor-0000005`.
2. **Scenario 2 (Cart Abandonment)**:
   * Customer: `cust-0000000` (Platinum)
   * Event flow: Spent 240 seconds viewing product `prod-0000001` (Price: $232.09). No purchase was recorded.
3. **Scenario 3 (Product Affinity)**:
   * Customer: `cust-0000001`
   * Event flow: Purchased `prod-0000002` (Category: `Beauty`) and `prod-0000003` (Category: `Sports`).
