CREATE TABLE Customers (
  customer_id STRING(36) NOT NULL,
  name STRING(100) NOT NULL,
  email STRING(100) NOT NULL,
  segment STRING(50) NOT NULL,
  loyalty_tier STRING(50) NOT NULL,
  signup_date TIMESTAMP NOT NULL
) PRIMARY KEY (customer_id);

CREATE TABLE Products (
  product_id STRING(36) NOT NULL,
  name STRING(100) NOT NULL,
  category STRING(100) NOT NULL,
  brand STRING(100) NOT NULL,
  price NUMERIC NOT NULL
) PRIMARY KEY (product_id);

CREATE TABLE Stores (
  store_id STRING(36) NOT NULL,
  name STRING(100) NOT NULL,
  city STRING(100) NOT NULL,
  state STRING(100) NOT NULL,
  zip_code STRING(20) NOT NULL
) PRIMARY KEY (store_id);

CREATE TABLE CustomerPreferredStore (
  customer_id STRING(36) NOT NULL,
  store_id STRING(36) NOT NULL,
  assigned_at TIMESTAMP NOT NULL
) PRIMARY KEY (customer_id, store_id),
  INTERLEAVE IN PARENT Customers ON DELETE CASCADE;

CREATE TABLE CustomerViews (
  customer_id STRING(36) NOT NULL,
  view_id STRING(36) NOT NULL,
  product_id STRING(36) NOT NULL,
  duration_seconds INT64 NOT NULL,
  device_type STRING(50) NOT NULL,
  timestamp TIMESTAMP NOT NULL
) PRIMARY KEY (customer_id, view_id),
  INTERLEAVE IN PARENT Customers ON DELETE CASCADE;

CREATE TABLE ProductInventory (
  product_id STRING(36) NOT NULL,
  store_id STRING(36) NOT NULL,
  quantity INT64 NOT NULL,
  aisle_location STRING(50) NOT NULL
) PRIMARY KEY (product_id, store_id),
  INTERLEAVE IN PARENT Products ON DELETE CASCADE;

CREATE TABLE CustomerPurchases (
  customer_id STRING(36) NOT NULL,
  purchase_id STRING(36) NOT NULL,
  product_id STRING(36) NOT NULL,
  store_id STRING(36) NOT NULL,
  quantity INT64 NOT NULL,
  price_paid NUMERIC NOT NULL,
  timestamp TIMESTAMP NOT NULL
) PRIMARY KEY (customer_id, purchase_id),
  INTERLEAVE IN PARENT Customers ON DELETE CASCADE;

CREATE PROPERTY GRAPH RetailMarketingGraph
  NODE TABLES (
    Customers KEY (customer_id) LABEL Customer,
    Products KEY (product_id) LABEL Product,
    Stores KEY (store_id) LABEL Store
  )
  EDGE TABLES (
    CustomerPreferredStore
      KEY (customer_id, store_id)
      SOURCE KEY (customer_id) REFERENCES Customers (customer_id)
      DESTINATION KEY (store_id) REFERENCES Stores (store_id)
      LABEL PrefersStore,
    CustomerViews
      KEY (customer_id, view_id)
      SOURCE KEY (customer_id) REFERENCES Customers (customer_id)
      DESTINATION KEY (product_id) REFERENCES Products (product_id)
      LABEL Views,
    ProductInventory
      KEY (product_id, store_id)
      SOURCE KEY (product_id) REFERENCES Products (product_id)
      DESTINATION KEY (store_id) REFERENCES Stores (store_id)
      LABEL Inventory,
    CustomerPurchases
      KEY (customer_id, purchase_id)
      SOURCE KEY (customer_id) REFERENCES Customers (customer_id)
      DESTINATION KEY (product_id) REFERENCES Products (product_id)
      LABEL Purchased
  );

