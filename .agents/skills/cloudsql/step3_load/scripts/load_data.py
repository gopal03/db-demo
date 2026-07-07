import json
import os
import sys
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
    params_path = "config/demo_parameters.json"
    if not os.path.exists(params_path):
        print(f"Error: Parameter file {params_path} not found.")
        sys.exit(1)
        
    params = load_json(params_path)
    target_database = params.get("target_database", "cloudsql")
    use_case = params.get("demo_context", {}).get("use_case")
    
    if not use_case:
        print("Error: Active use case not specified in demo_parameters.json.")
        sys.exit(1)
        
    use_case_dir = os.path.join("config/use_cases", use_case.lower().replace(" ", "_"))
    
    db_config = params.get("database_configs", {}).get(target_database, {})
    host = db_config.get("host", "127.0.0.1")
    port = db_config.get("port", 5432)
    user = db_config.get("user", "postgres")
    password = db_config.get("password", "postgres")
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
            database=database_id
        )
        conn.autocommit = False
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
