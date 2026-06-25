CREATE TABLE Customers (
  customer_id STRING(36) NOT NULL,
  name STRING(100) NOT NULL,
  type STRING(50) NOT NULL,
  risk_score INT64 NOT NULL,
  country STRING(100) NOT NULL
) PRIMARY KEY (customer_id);

CREATE TABLE Accounts (
  account_id STRING(36) NOT NULL,
  bank_name STRING(100) NOT NULL,
  balance NUMERIC NOT NULL,
  currency STRING(3) NOT NULL
) PRIMARY KEY (account_id);

CREATE TABLE Merchants (
  merchant_id STRING(36) NOT NULL,
  name STRING(100) NOT NULL,
  category STRING(50) NOT NULL,
  risk_level STRING(20) NOT NULL
) PRIMARY KEY (merchant_id);

CREATE TABLE CustomerOwnsAccount (
  customer_id STRING(36) NOT NULL,
  account_id STRING(36) NOT NULL,
  opened_at TIMESTAMP
) PRIMARY KEY (customer_id, account_id),
  INTERLEAVE IN PARENT Customers ON DELETE CASCADE;

CREATE TABLE AccountTransfers (
  account_id STRING(36) NOT NULL,
  transfer_id STRING(36) NOT NULL,
  dest_account_id STRING(36) NOT NULL,
  amount NUMERIC NOT NULL,
  timestamp TIMESTAMP NOT NULL
) PRIMARY KEY (account_id, transfer_id),
  INTERLEAVE IN PARENT Accounts ON DELETE CASCADE;

CREATE TABLE AccountPaysMerchant (
  account_id STRING(36) NOT NULL,
  payment_id STRING(36) NOT NULL,
  merchant_id STRING(36) NOT NULL,
  amount NUMERIC NOT NULL,
  timestamp TIMESTAMP NOT NULL
) PRIMARY KEY (account_id, payment_id),
  INTERLEAVE IN PARENT Accounts ON DELETE CASCADE;

CREATE PROPERTY GRAPH AMLGraph
  NODE TABLES (
    Customers KEY (customer_id) LABEL Customer,
    Accounts KEY (account_id) LABEL Account,
    Merchants KEY (merchant_id) LABEL Merchant
  )
  EDGE TABLES (
    CustomerOwnsAccount
      KEY (customer_id, account_id)
      SOURCE KEY (customer_id) REFERENCES Customers (customer_id)
      DESTINATION KEY (account_id) REFERENCES Accounts (account_id)
      LABEL OwnsAccount,
    AccountTransfers
      KEY (account_id, transfer_id)
      SOURCE KEY (account_id) REFERENCES Accounts (account_id)
      DESTINATION KEY (dest_account_id) REFERENCES Accounts (account_id)
      LABEL Transfers,
    AccountPaysMerchant
      KEY (account_id, payment_id)
      SOURCE KEY (account_id) REFERENCES Accounts (account_id)
      DESTINATION KEY (merchant_id) REFERENCES Merchants (merchant_id)
      LABEL PaysMerchant
  );

