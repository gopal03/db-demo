#!/bin/bash
# Exit on error
set -e

INSTANCE_ID=${1:-"demo-instance-retail"}

echo "Creating Bigtable tables for instance: $INSTANCE_ID..."

# Helper to check and create tables
create_table_with_splits() {
  local table_name=$1
  local splits=$2
  if cbt -instance "$INSTANCE_ID" ls | grep -q "^${table_name}$"; then
    echo "Table '${table_name}' already exists. Skipping creation."
  else
    echo "Creating table '${table_name}' with splits: ${splits}"
    cbt -instance "$INSTANCE_ID" createtable "$table_name" "splits=${splits}"
  fi
}

create_table_no_splits() {
  local table_name=$1
  if cbt -instance "$INSTANCE_ID" ls | grep -q "^${table_name}$"; then
    echo "Table '${table_name}' already exists. Skipping creation."
  else
    echo "Creating table '${table_name}'..."
    cbt -instance "$INSTANCE_ID" createtable "$table_name"
  fi
}

# 1. Customers Table
create_table_with_splits "customers" "cust-0000100,cust-0000200,cust-0000300,cust-0000400"
cbt -instance "$INSTANCE_ID" createfamily customers d || true
cbt -instance "$INSTANCE_ID" setgcpolicy customers d maxversions=1
cbt -instance "$INSTANCE_ID" createfamily customers p || true
cbt -instance "$INSTANCE_ID" setgcpolicy customers p maxversions=1

# 2. Products Table
create_table_with_splits "products" "prod-0000100,prod-0000200,prod-0000300,prod-0000400"
cbt -instance "$INSTANCE_ID" createfamily products d || true
cbt -instance "$INSTANCE_ID" setgcpolicy products d maxversions=1

# 3. Stores Table
create_table_no_splits "stores"
cbt -instance "$INSTANCE_ID" createfamily stores d || true
cbt -instance "$INSTANCE_ID" setgcpolicy stores d maxversions=1

# 4. Inventory Table
create_table_with_splits "inventory" "prod-0000100,prod-0000200,prod-0000300,prod-0000400"
cbt -instance "$INSTANCE_ID" createfamily inventory d || true
cbt -instance "$INSTANCE_ID" setgcpolicy inventory d maxversions=1

# 5. Customer Events Table
create_table_with_splits "customer_events" "cust-0000100,cust-0000200,cust-0000300,cust-0000400"
cbt -instance "$INSTANCE_ID" createfamily customer_events e || true
cbt -instance "$INSTANCE_ID" setgcpolicy customer_events e maxversions=5

echo "Table provisioning completed successfully."
