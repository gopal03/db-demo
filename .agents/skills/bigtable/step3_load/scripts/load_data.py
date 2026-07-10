import json
import os
import sys
import time
import datetime
from google.cloud import bigtable
from google.rpc import code_pb2

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

import argparse

def main():
    parser = argparse.ArgumentParser(description="Generic Bigtable Loader.")
    parser.add_argument('--parameters', default='config/demo_parameters.json', help='Path to active_parameters.json')
    args = parser.parse_args()
    
    params_path = args.parameters
    if not os.path.exists(params_path):
        print(f"Error: Parameter file {params_path} not found.")
        sys.exit(1)
        
    params = load_json(params_path)
    project_id = params.get("project_id")
    use_case_dir = os.path.dirname(params_path)
    
    bt_config = params.get("database_configs", {}).get("bigtable", {})
    instance_id = bt_config.get("instance_id", "demo-instance-retail")
    
    data_file = os.path.join(use_case_dir, "dummy_data.json")
    if not os.path.exists(data_file):
        data_file = os.path.join(use_case_dir, "bigtable/dummy_data.json")
        if not os.path.exists(data_file):
            print(f"Error: Data file not found under {use_case_dir}.")
            sys.exit(1)
        
    data = load_json(data_file)
    
    print(f"Connecting to Bigtable project '{project_id}', instance '{instance_id}'...")
    client = bigtable.Client(project=project_id, admin=True)
    instance = client.instance(instance_id)
    
    if not instance.exists():
        print(f"Error: Bigtable instance '{instance_id}' does not exist. Please provision the instance first.")
        sys.exit(1)
        
    print("Loading data in batches...")
    start_time = time.time()
    total_rows = 0
    total_cells = 0
    
    for table_name, mutations in data.items():
        print(f"Loading table '{table_name}'...")
        table = instance.table(table_name)
        
        if not table.exists():
            print(f"Warning: Table '{table_name}' does not exist. Skipping.")
            continue
            
        batch_size = 200
        for i in range(0, len(mutations), batch_size):
            batch = mutations[i:i+batch_size]
            rows = []
            
            for mut in batch:
                row_key = mut["row_key"].encode("utf-8")
                row = table.direct_row(row_key)
                
                for cell in mut["cells"]:
                    family = cell["family"]
                    qualifier = cell["qualifier"].encode("utf-8")
                    val = cell["value"].encode("utf-8")
                    
                    ts_micros = cell.get("timestamp")
                    dt = None
                    if ts_micros is not None:
                        dt = datetime.datetime.fromtimestamp(ts_micros / 1000000, datetime.timezone.utc)
                        
                    row.set_cell(family, qualifier, val, timestamp=dt)
                    total_cells += 1
                
                rows.append(row)
                
            response = table.mutate_rows(rows)
            
            for idx, status in enumerate(response):
                if status.code != code_pb2.OK:
                    print(f"Error writing row {batch[idx]['row_key']}: {status.message} (code: {status.code})")
                    
            total_rows += len(rows)
            
    end_time = time.time()
    duration = end_time - start_time
    throughput = total_rows / duration if duration > 0 else 0
    
    print("\nData loading complete:")
    print(f"  - Total rows loaded: {total_rows}")
    print(f"  - Total cells loaded: {total_cells}")
    print(f"  - Total time: {duration:.2f} seconds")
    print(f"  - Throughput: {throughput:.2f} rows/second")
    
    report_file = os.path.join(use_case_dir, "bigtable/loading_report.md")
    with open(report_file, 'w') as f:
        f.write(f"""# Bigtable Data Ingestion Report

* **Execution Date (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
* **Loader Script**: Static Bigtable SDK Bulk Loader
* **Duration**: {duration:.2f} seconds
* **Throughput**: {throughput:.2f} rows/second

## Ingestion Metrics

| Metric | Count |
| :--- | :--- |
| **Total Rows Written** | {total_rows:,} |
| **Total Cells Written** | {total_cells:,} |
""")
        
    print(f"Ingestion report written to {report_file}")

if __name__ == "__main__":
    main()
