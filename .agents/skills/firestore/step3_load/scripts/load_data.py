import json
import os
import sys
import time
import datetime
from google.cloud import firestore

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def extract_operations(collection_ref, items, ops_list):
    for item in items:
        doc_id = item.get("doc_id")
        data = item.get("data", {})
        
        if doc_id:
            doc_ref = collection_ref.document(doc_id)
        else:
            doc_ref = collection_ref.document()
            
        ops_list.append((doc_ref, data))
        
        subcollections = item.get("subcollections", {})
        for sub_name, sub_items in subcollections.items():
            sub_col_ref = doc_ref.collection(sub_name)
            extract_operations(sub_col_ref, sub_items, ops_list)

import argparse

def main():
    parser = argparse.ArgumentParser(description="Generic Firestore Loader.")
    parser.add_argument('--parameters', default='config/demo_parameters.json', help='Path to active_parameters.json')
    args = parser.parse_args()
    
    params_path = args.parameters
    if not os.path.exists(params_path):
        print(f"Error: Parameter file {params_path} not found.")
        sys.exit(1)
        
    params = load_json(params_path)
    project_id = params.get("project_id")
    use_case_dir = os.path.dirname(params_path)
    
    fs_config = params.get("database_configs", {}).get("firestore", {})
    database_id = fs_config.get("database_id", "(default)")
    
    data_file = os.path.join(use_case_dir, "dummy_data.json")
    if not os.path.exists(data_file):
        data_file = os.path.join(use_case_dir, "firestore/dummy_data.json")
        if not os.path.exists(data_file):
            print(f"Error: Data file not found under {use_case_dir}.")
            sys.exit(1)
        
    data = load_json(data_file)
    
    print(f"Connecting to Firestore project '{project_id}', database '{database_id}'...")
    db = firestore.Client(project=project_id, database=database_id)
    
    ops_list = []
    for collection_name, items in data.items():
        col_ref = db.collection(collection_name)
        extract_operations(col_ref, items, ops_list)
        
    print(f"Prepared {len(ops_list)} document operations to write.")
    
    print("Loading data in batches...")
    start_time = time.time()
    
    batch_size = 450
    total_written = 0
    
    batch = db.batch()
    for idx, (doc_ref, doc_data) in enumerate(ops_list):
        batch.set(doc_ref, doc_data)
        total_written += 1
        
        if total_written % batch_size == 0:
            print(f"Committing batch of {batch_size}...")
            batch.commit()
            batch = db.batch()
            
    if total_written % batch_size != 0:
        print(f"Committing final batch of {total_written % batch_size}...")
        batch.commit()
        
    end_time = time.time()
    duration = end_time - start_time
    throughput = total_written / duration if duration > 0 else 0
    
    print("\nData loading complete:")
    print(f"  - Total documents loaded: {total_written}")
    print(f"  - Total time: {duration:.2f} seconds")
    print(f"  - Throughput: {throughput:.2f} docs/second")
    
    report_file = os.path.join(use_case_dir, "firestore/loading_report.md")
    with open(report_file, 'w') as f:
        f.write(f"""# Firestore Data Ingestion Report

* **Execution Date (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
* **Loader Script**: Static Firestore SDK Batch Loader
* **Duration**: {duration:.2f} seconds
* **Throughput**: {throughput:.2f} documents/second

## Ingestion Metrics

| Metric | Count |
| :--- | :--- |
| **Total Documents Written** | {total_written:,} |
""")
        
    print(f"Ingestion report written to {report_file}")

if __name__ == "__main__":
    main()
