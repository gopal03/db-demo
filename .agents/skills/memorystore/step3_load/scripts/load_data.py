import json
import os
import sys
import time
import datetime
import redis

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    params_path = "config/demo_parameters.json"
    if not os.path.exists(params_path):
        print(f"Error: Parameter file {params_path} not found.")
        sys.exit(1)
        
    params = load_json(params_path)
    use_case = params.get("demo_context", {}).get("use_case")
    
    if not use_case:
        print("Error: Active use case not specified in demo_parameters.json.")
        sys.exit(1)
        
    use_case_dir = os.path.join("config/use_cases", use_case.lower().replace(" ", "_"))
    
    redis_config = params.get("database_configs", {}).get("memorystore", {})
    host = redis_config.get("host", "127.0.0.1")
    port = redis_config.get("port", 6379)
    
    data_file = os.path.join(use_case_dir, "memorystore/dummy_data.json")
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found. Run Step 2 first.")
        sys.exit(1)
        
    data = load_json(data_file)
    
    print(f"Connecting to Memorystore (Redis) at {host}:{port}...")
    try:
        r = redis.Redis(host=host, port=port, decode_responses=True)
        r.ping()
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        sys.exit(1)
        
    print("Loading data via pipeline...")
    start_time = time.time()
    
    pipe = r.pipeline()
    total_commands = 0
    total_hashes = 0
    total_zsets = 0
    
    hashes = data.get("hashes", {})
    for key, fields in hashes.items():
        pipe.hset(key, mapping=fields)
        total_commands += 1
        total_hashes += 1
        
        if total_commands % 1000 == 0:
            pipe.execute()
            pipe = r.pipeline()
            
    zsets = data.get("sorted_sets", {})
    for key, members in zsets.items():
        mapping = {}
        for m in members:
            mapping[m["value"]] = m["score"]
        if mapping:
            pipe.zadd(key, mapping=mapping)
            total_commands += 1
            total_zsets += 1
            
            if total_commands % 1000 == 0:
                pipe.execute()
                pipe = r.pipeline()
                
    if len(pipe) > 0:
        pipe.execute()
        
    end_time = time.time()
    duration = end_time - start_time
    throughput = total_commands / duration if duration > 0 else 0
    
    print("\nData loading complete:")
    print(f"  - Total Hashes loaded: {total_hashes}")
    print(f"  - Total Sorted Sets loaded: {total_zsets}")
    print(f"  - Total Pipeline commands executed: {total_commands}")
    print(f"  - Total time: {duration:.2f} seconds")
    print(f"  - Throughput: {throughput:.2f} commands/second")
    
    report_file = os.path.join(use_case_dir, "memorystore/loading_report.md")
    with open(report_file, 'w') as f:
        f.write(f"""# Memorystore (Redis) Data Ingestion Report

* **Execution Date (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
* **Loader Script**: Static Redis Pipeline Loader
* **Target Endpoint**: {host}:{port}
* **Duration**: {duration:.2f} seconds
* **Throughput**: {throughput:.2f} pipeline commands/second

## Ingestion Metrics

| Metric | Count |
| :--- | :--- |
| **HSET Commands (Hashes)** | {total_hashes:,} |
| **ZADD Commands (Sorted Sets)** | {total_zsets:,} |
| **Total Commands Executed** | {total_commands:,} |
""")
        
    print(f"Ingestion report written to {report_file}")

if __name__ == "__main__":
    main()
