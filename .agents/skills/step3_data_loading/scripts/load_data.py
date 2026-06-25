import json
import argparse
import datetime
import os
import sys
from decimal import Decimal
from google.cloud import spanner
from google.cloud import spanner_admin_instance_v1

def load_params(params_path):
    with open(params_path, 'r') as f:
        return json.load(f)

def parse_ddl_file(schema_path):
    with open(schema_path, 'r') as f:
        content = f.read()
    statements = [stmt.strip() for stmt in content.split('\n\n') if stmt.strip()]
    return statements

def provision_spanner(client, params, ddl_statements, recreate=False):
    project_id = params['project_id']
    instance_id = params['instance_id']
    database_id = params['database_id']
    config_name = params.get('instance_config', 'regional-us-central1')
    edition_str = params.get('edition', 'ENTERPRISE').upper()
    node_count = params.get('node_count', 1)
    processing_units = params.get('processing_units', 0)

    from google.cloud import spanner_admin_instance_v1
    InstancePB = spanner_admin_instance_v1.types.Instance
    edition_enum = getattr(InstancePB.Edition, edition_str, InstancePB.Edition.ENTERPRISE)

    instance = client.instance(instance_id)

    if not instance.exists():
        print(f"Provisioning Spanner Instance '{instance_id}' [{edition_str} edition]...")
        instance_pb = InstancePB(
            name=f"projects/{project_id}/instances/{instance_id}",
            config=f"projects/{project_id}/instanceConfigs/{config_name}",
            display_name=instance_id,
            edition=edition_enum
        )
        if processing_units > 0:
            instance_pb.processing_units = processing_units
        else:
            instance_pb.node_count = node_count

        api = client.instance_admin_api
        op = api.create_instance(
            parent=f"projects/{project_id}",
            instance_id=instance_id,
            instance=instance_pb
        )
        print("Waiting for instance provisioning...")
        op.result()
        print(f"Instance '{instance_id}' ({edition_str}) provisioned successfully.")
    else:
        print(f"Instance '{instance_id}' already exists.")

    # Database
    database = instance.database(database_id)
    if database.exists() and recreate:
        print(f"Dropping existing database '{database_id}'...")
        database.drop()

    if not database.exists():
        print(f"Creating database '{database_id}'...")
        op = database.create()
        op.result()
        print(f"Database '{database_id}' created.")

        print("Deploying Graph schema...")
        cleaned_ddl = [stmt.rstrip(';') for stmt in ddl_statements if stmt.strip()]
        op = database.update_ddl(cleaned_ddl)
        op.result()
        print("Property graph schema deployed successfully.")
    else:
        print(f"Database '{database_id}' already exists. Skipping DDL deployment.")

    return database

def load_table_data(database, table_name, records, column_types=None, batch_size=1000):
    if not records:
        return
    if column_types is None:
        column_types = {}
    print(f"Loading {len(records):,} records into '{table_name}'...")
    keys = list(records[0].keys())

    # Stream in batches
    for start in range(0, len(records), batch_size):
        batch_records = records[start:start + batch_size]
        values = []
        for rec in batch_records:
            row = []
            for k, v in rec.items():
                col_type = column_types.get(k, '').upper()
                if 'NUMERIC' in col_type:
                    row.append(Decimal(str(v)) if v is not None else None)
                # Generic detection of ISO-8601 string timestamps
                elif isinstance(v, str) and len(v) >= 19 and (v.endswith('Z') or '+' in v or ('-' in v and v.count('-') >= 2 and 'T' in v)):
                    try:
                        row.append(datetime.datetime.fromisoformat(v.replace("Z", "+00:00")))
                    except ValueError:
                        row.append(v)
                else:
                    row.append(v)
            values.append(row)

        with database.batch() as batch:
            batch.insert_or_update(table=table_name, columns=keys, values=values)

    print(f"  ✓ '{table_name}' loaded.")

def main():
    parser = argparse.ArgumentParser(description="Provision Spanner and load graph data using parameters file.")
    parser.add_argument('--parameters', default='config/spanner_parameters.json', help='Path to spanner parameters JSON')
    parser.add_argument('--schema', default='config/generated_schema.sql', help='Path to generated schema SQL')
    parser.add_argument('--data', default='config/dummy_data.json', help='Path to mock data JSON')
    parser.add_argument('--recreate', action='store_true', help='Drop and recreate the database if it exists')
    args = parser.parse_args()

    # 1. Load parameters
    params = load_params(args.parameters)
    demo_ctx = params.get('demo_context', {})
    print(f"\nCustomer : {demo_ctx.get('customer_name', 'N/A')} | Industry: {demo_ctx.get('industry', 'N/A')}")
    print(f"Use Case : {demo_ctx.get('use_case', 'N/A')}")
    print(f"Project  : {params['project_id']} | Instance: {params['instance_id']} | DB: {params['database_id']}\n")

    # Derive DDL and Data paths dynamically if default values are used
    use_case_config_path = demo_ctx.get('use_case_config', '')
    use_case_dir = os.path.dirname(use_case_config_path) if use_case_config_path else ''

    schema_path = args.schema
    if args.schema == 'config/generated_schema.sql' and use_case_dir:
        schema_path = os.path.join(use_case_dir, 'schema.sql')

    data_path = args.data
    if args.data == 'config/dummy_data.json' and use_case_dir:
        data_path = os.path.join(use_case_dir, 'dummy_data.json')

    # 2. Parse DDL
    if not os.path.exists(schema_path):
        print(f"Error: Schema DDL file {schema_path} not found. Run generate_schema.py first.")
        sys.exit(1)
    ddl_statements = parse_ddl_file(schema_path)

    # 3. Load data
    if not os.path.exists(data_path):
        print(f"Error: Data file {data_path} not found. Run generate_data.py first.")
        sys.exit(1)
    with open(data_path, 'r') as f:
        data = json.load(f)

    # 4. Connect and provision
    print(f"Connecting to GCP project '{params['project_id']}'...")
    client = spanner.Client(project=params['project_id'])

    try:
        database = provision_spanner(client, params, ddl_statements, args.recreate)
    except Exception as e:
        print(f"Failed to provision: {e}")
        sys.exit(1)

    # 5. Load in dependency order dynamically: nodes first, then edges
    try:
        # Load the use-case config to identify table names
        use_case_config_path = params.get('demo_context', {}).get('use_case_config')
        if not use_case_config_path or not os.path.exists(use_case_config_path):
            print(f"Error: Use-case config file '{use_case_config_path}' not found.")
            sys.exit(1)
        with open(use_case_config_path, 'r') as f:
            use_case_config = json.load(f)

        node_tables = [node['table_name'] for node in use_case_config.get('nodes', [])]
        edge_tables = [edge['table_name'] for edge in use_case_config.get('edges', [])]

        # Build column types map dynamically from use-case config
        table_types = {}
        for node in use_case_config.get('nodes', []):
            table_types[node['table_name']] = {prop['name']: prop['type'] for prop in node.get('properties', [])}
        for edge in use_case_config.get('edges', []):
            table_types[edge['table_name']] = {prop['name']: prop['type'] for prop in edge.get('properties', [])}

        print("Ingesting Node Tables...")
        for table in node_tables:
            if table in data:
                load_table_data(database, table, data[table], table_types.get(table, {}))

        print("\nIngesting Edge Tables...")
        for table in edge_tables:
            if table in data:
                load_table_data(database, table, data[table], table_types.get(table, {}))

        print("\nAll data successfully loaded into Spanner Graph!")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
