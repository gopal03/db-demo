import json
import os
import sys
import time
import psycopg2

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

import argparse

def main():
    parser = argparse.ArgumentParser(description="Cloud SQL Query Runner.")
    parser.add_argument('--parameters', default='config/demo_parameters.json', help='Path to active_parameters.json')
    args = parser.parse_args()
    
    params_path = args.parameters
    if not os.path.exists(params_path):
        print(f"Error: Parameter file {params_path} not found.")
        sys.exit(1)
        
    params = load_json(params_path)
    target_database = params.get("target_database", "cloudsql")
    use_case_dir = os.path.dirname(params_path)
    
    queries_file = os.path.join(use_case_dir, "queries.json")
    if not os.path.exists(queries_file):
        queries_file = os.path.join(use_case_dir, f"{target_database}/queries.json")
        if not os.path.exists(queries_file):
            print(f"Error: Queries file not found. Expected: {queries_file}")
            sys.exit(1)
            
    queries_data = load_json(queries_file)
    
    db_config = params.get("database_configs", {}).get(target_database, {})
    host = db_config.get("host", "127.0.0.1")
    port = db_config.get("port", 5432)
    user = db_config.get("user", "postgres")
    password = db_config.get("password", "postgres")
    database_id = db_config.get("database_id", "postgres")
    
    print(f"Connecting to {target_database.upper()} at {host}:{port}...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database_id,
            sslmode="require"
        )
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
        
    print("\nRunning Demo Queries...")
    
    talktrack_content = f"# Customer Talk Track for {target_database.upper()}\n\n"
    
    with conn.cursor() as cur:
        for q in queries_data:
            q_id = q.get("id")
            title = q.get("title")
            sql = q.get("sql")
            description = q.get("description", "")
            business_value = q.get("business_value", "")
            
            print(f"\n========================================\nQuery: {title}\n========================================")
            print(f"SQL:\n{sql}\n")
            
            print("Query Execution Plan:")
            try:
                cur.execute(f"EXPLAIN {sql}")
                plan = cur.fetchall()
                plan_str = "\n".join([row[0] for row in plan])
                print(plan_str)
                print("-" * 40)
            except Exception as e:
                print(f"Error executing EXPLAIN: {e}")
                conn.rollback()
                continue
                
            start_time = time.time()
            try:
                cur.execute(sql)
                rows = cur.fetchall()
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                print(f"Results ({len(rows)} rows, Latency: {latency_ms:.2f} ms):")
                for row in rows[:5]:
                    print(row)
                if len(rows) > 5:
                    print(f"... and {len(rows) - 5} more rows.")
            except Exception as e:
                print(f"Error executing query: {e}")
                conn.rollback()
                continue
                
            talktrack_content += f"## {title}\n\n"
            talktrack_content += f"> {description}\n\n"
            talktrack_content += f"### SQL Statement\n```sql\n{sql}\n```\n\n"
            talktrack_content += f"### Execution Plan\n```text\n{plan_str}\n```\n\n"
            talktrack_content += f"### Latency\n* **Measured Latency**: {latency_ms:.2f} ms\n\n"
            talktrack_content += f"### Talk Track & Business Value\n{business_value}\n\n---\n\n"
            
    conn.close()
    
    talktrack_file = os.path.join(use_case_dir, f"{target_database}/talktrack.md")
    with open(talktrack_file, 'w') as f:
        f.write(talktrack_content)
        
    print(f"\nDemo queries execution completed. Talk track written to {talktrack_file}")

if __name__ == "__main__":
    main()
