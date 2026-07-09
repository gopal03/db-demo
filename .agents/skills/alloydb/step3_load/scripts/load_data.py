import json
import os
import sys
import argparse
import time
import datetime
import psycopg2
from psycopg2 import extras

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_insert_query(table_name, record):
    columns = list(record.keys())
    placeholders = [f"%({col})s" for col in columns]
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
    return query

def main():
    parser = argparse.ArgumentParser(description="AlloyDB PostgreSQL Data Loader.")
    parser.add_argument('--parameters', default='config/demo_parameters.json', help='Path to parameters config file')
    args = parser.parse_args()
    
    params_path = args.parameters
    if not os.path.exists(params_path):
        print(f"Error: Parameter file {params_path} not found.")
        sys.exit(1)
        
    params = load_json(params_path)
    target_database = params.get("target_database", "alloydb")
    
    # Resolve use case directory relative to parameter file
    use_case_dir = os.path.dirname(params_path)
    
    db_config = params.get("database_configs", {}).get(target_database, {})
    host = db_config.get("host", "127.0.0.1")
    port = db_config.get("port", 5432)
    user = db_config.get("user", "postgres")
    password = db_config.get("password", "alloydb_password_123")
    database_id = db_config.get("database_id", "postgres")
    
    data_file = os.path.join(use_case_dir, f"{target_database}/dummy_data.json")
    if not os.path.exists(data_file):
        data_file = os.path.join(use_case_dir, "dummy_data.json")
        if not os.path.exists(data_file):
            print(f"Error: Data file not found under {use_case_dir}.")
            sys.exit(1)
        
    data = load_json(data_file)
    
    print(f"Connecting to {target_database.upper()} at {host}:{port} (db: {database_id})...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database_id,
            sslmode="require"
        )
        conn.autocommit = False
    except psycopg2.OperationalError as e:
        err_msg = str(e)
        if "does not exist" in err_msg:
            print(f"Database '{database_id}' does not exist. Creating it dynamically...")
            try:
                sys_conn = psycopg2.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database="postgres",
                    sslmode="require"
                )
                sys_conn.autocommit = True
                with sys_conn.cursor() as sys_cur:
                    sys_cur.execute(f'CREATE DATABASE "{database_id}"')
                sys_conn.close()
                print(f"Database '{database_id}' created successfully. Reconnecting...")
                
                # Retry main connection
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database_id,
                    sslmode="require"
                )
                conn.autocommit = False
            except Exception as create_err:
                print(f"Failed to create database '{database_id}': {create_err}")
                sys.exit(1)
        else:
            print(f"Error connecting to database: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
        
    print("Loading data in transactions...")
    start_time = time.time()
    total_rows = 0
    
    with conn.cursor() as cur:
        for table_name, records in data.items():
            if not records:
                continue
            print(f"Loading table '{table_name}' ({len(records)} records)...")
            
            query = get_insert_query(table_name, records[0])
            
            batch_size = 500
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                try:
                    extras.execute_batch(cur, query, batch)
                except Exception as e:
                    print(f"Error executing batch insert for table {table_name}: {e}")
                    conn.rollback()
                    sys.exit(1)
            
            total_rows += len(records)
            
        conn.commit()
        
    conn.close()
    
    end_time = time.time()
    duration = end_time - start_time
    throughput = total_rows / duration if duration > 0 else 0
    
    print("\nData loading complete:")
    print(f"  - Total rows loaded: {total_rows}")
    print(f"  - Total time: {duration:.2f} seconds")
    print(f"  - Throughput: {throughput:.2f} rows/second")
    
    report_file = os.path.join(use_case_dir, f"{target_database}/loading_report.md")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w') as f:
        f.write(f"""# {target_database.upper()} Data Ingestion Report

* **Execution Date (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
* **Loader Script**: Static PostgreSQL psycopg2 Bulk Loader
* **Duration**: {duration:.2f} seconds
* **Throughput**: {throughput:.2f} rows/second

## Ingestion Metrics

| Metric | Count |
| :--- | :--- |
| **Total Rows Written** | {total_rows:,} |
""")
        
    print(f"Ingestion report written to {report_file}")

if __name__ == "__main__":
    main()
