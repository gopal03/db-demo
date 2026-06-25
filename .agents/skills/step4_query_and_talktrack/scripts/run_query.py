import json
import argparse
import sys
import os
from google.cloud import spanner

def load_params(params_path):
    with open(params_path, 'r') as f:
        return json.load(f)

def load_usecase(params):
    use_case_config = params.get('demo_context', {}).get('use_case_config')
    if not use_case_config or not os.path.exists(use_case_config):
        print(f"Error: use_case_config '{use_case_config}' not found in parameters or on disk.")
        sys.exit(1)
    with open(use_case_config, 'r') as f:
        return json.load(f)

def run_spanner_query(database, sql):
    rows = []
    headers = []
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(sql)
        for row in results:
            if not headers and results.fields:
                headers = [field.name for field in results.fields]
            rows.append(list(row))
        if not headers and results.fields:
            headers = [field.name for field in results.fields]
    return headers, rows

def format_table(headers, rows):
    if not rows:
        return "(no results)"
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))

    header_line = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in widths)
    row_lines = [" | ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)) for row in rows]
    return f"{header_line}\n{separator}\n" + "\n".join(row_lines)

def main():
    parser = argparse.ArgumentParser(description="Execute Spanner Graph GQL queries with talk tracks.")
    parser.add_argument('--parameters', default='config/spanner_parameters.json', help='Path to spanner parameters JSON')
    parser.add_argument('--query', default=None, help='Specific query ID to run (e.g. q1_blast_radius)')
    args = parser.parse_args()

    params = load_params(args.parameters)
    demo_ctx = params.get('demo_context', {})

    print(f"\n{'='*60}")
    print(f"  Spanner Graph Demo — {demo_ctx.get('use_case', 'Demo')}")
    print(f"  Customer : {demo_ctx.get('customer_name', 'N/A')}")
    print(f"  Industry : {demo_ctx.get('industry', 'N/A')}")
    print(f"  Database : {params['instance_id']} / {params['database_id']}")
    print(f"{'='*60}\n")

    usecase = load_usecase(params)

    # Connect to Spanner
    client = spanner.Client(project=params['project_id'])
    instance = client.instance(params['instance_id'])
    if not instance.exists():
        print(f"Error: Spanner Instance '{params['instance_id']}' not found.")
        sys.exit(1)
    database = instance.database(params['database_id'])
    if not database.exists():
        print(f"Error: Database '{params['database_id']}' not found. Run load_data.py first.")
        sys.exit(1)

    queries = usecase.get('queries', [])
    if args.query:
        queries = [q for q in queries if q['id'] == args.query]
        if not queries:
            print(f"Error: Query ID '{args.query}' not found.")
            sys.exit(1)

    for idx, q in enumerate(queries):
        print(f"=== {idx+1}. {q['title']} ===")
        print(f"Description: {q['description']}")
        print(f"\nGQL Query:\n{q['gql']}\n")
        try:
            headers, rows = run_spanner_query(database, q['gql'])
            print("Results:")
            print(format_table(headers, rows))
        except Exception as e:
            print(f"Query Error: {e}")
        print(f"\n🗣️  Talk Track:\n{q['talk_track']}")
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
