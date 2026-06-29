import json
import argparse
import os
import sys

def load_params(params_path):
    with open(params_path, 'r') as f:
        return json.load(f)

def load_usecase(params):
    use_case_config = params.get('demo_context', {}).get('use_case_config')
    if not use_case_config:
        print("Error: 'demo_context.use_case_config' not found in parameters file.")
        sys.exit(1)
    if not os.path.exists(use_case_config):
        print(f"Error: Use case config file '{use_case_config}' not found.")
        sys.exit(1)
    with open(use_case_config, 'r') as f:
        return json.load(f)

def generate_ddl(config):
    ddl_statements = []
    node_pks = {}
    node_tables = {}

    # 1. Generate Node Tables
    for node in config['nodes']:
        table_name = node['table_name']
        node_tables[node['name']] = table_name
        key_cols = node['key']
        node_pks[node['name']] = key_cols

        cols = []
        for prop in node['properties']:
            null_clause = "" if prop.get('nullable', True) else " NOT NULL"
            cols.append(f"  {prop['name']} {prop['type']}{null_clause}")

        col_definitions = ",\n".join(cols)
        pk_definition = ", ".join(key_cols)
        ddl = f"CREATE TABLE {table_name} (\n{col_definitions}\n) PRIMARY KEY ({pk_definition});"
        ddl_statements.append(ddl)

    # 2. Generate Edge Tables
    for edge in config['edges']:
        table_name = edge['table_name']
        key_cols = edge['key']

        cols = []
        for prop in edge['properties']:
            null_clause = "" if prop.get('nullable', True) else " NOT NULL"
            cols.append(f"  {prop['name']} {prop['type']}{null_clause}")

        col_definitions = ",\n".join(cols)
        pk_definition = ", ".join(key_cols)

        source_node_name = edge['source']['node_name']
        source_table = node_tables[source_node_name]
        source_pks = node_pks[source_node_name]

        interleave_clause = ""
        if len(key_cols) >= len(source_pks) and key_cols[:len(source_pks)] == source_pks:
            interleave_clause = f",\n  INTERLEAVE IN PARENT {source_table} ON DELETE CASCADE"

        ddl = f"CREATE TABLE {table_name} (\n{col_definitions}\n) PRIMARY KEY ({pk_definition}){interleave_clause};"
        ddl_statements.append(ddl)

    # 3. Generate PROPERTY GRAPH Statement
    graph_name = config['graph_name']

    node_tables_gql = []
    for node in config['nodes']:
        table_name = node['table_name']
        key_cols = ", ".join(node['key'])
        label = node['name']
        node_tables_gql.append(f"    {table_name} KEY ({key_cols}) LABEL {label}")

    edge_tables_gql = []
    for edge in config['edges']:
        table_name = edge['table_name']
        key_cols = ", ".join(edge['key'])
        label = edge['name']

        source_node = edge['source']['node_name']
        source_table = node_tables[source_node]
        source_keys_edge = ", ".join(edge['source']['key_map'].keys())
        source_keys_node = ", ".join(edge['source']['key_map'].values())

        dest_node = edge['destination']['node_name']
        dest_table = node_tables[dest_node]
        dest_keys_edge = ", ".join(edge['destination']['key_map'].keys())
        dest_keys_node = ", ".join(edge['destination']['key_map'].values())

        edge_gql = (
            f"    {table_name}\n"
            f"      KEY ({key_cols})\n"
            f"      SOURCE KEY ({source_keys_edge}) REFERENCES {source_table} ({source_keys_node})\n"
            f"      DESTINATION KEY ({dest_keys_edge}) REFERENCES {dest_table} ({dest_keys_node})\n"
            f"      LABEL {label}"
        )
        edge_tables_gql.append(edge_gql)

    nodes_str = ",\n".join(node_tables_gql)
    edges_str = ",\n".join(edge_tables_gql)

    graph_ddl = (
        f"CREATE PROPERTY GRAPH {graph_name}\n"
        f"  NODE TABLES (\n{nodes_str}\n  )\n"
        f"  EDGE TABLES (\n{edges_str}\n  );"
    )
    ddl_statements.append(graph_ddl)

    return ddl_statements

def main():
    parser = argparse.ArgumentParser(description="Generate Spanner Graph DDL statements from parameters and use case config.")
    parser.add_argument('--parameters', default='config/spanner_parameters.json', help='Path to spanner parameters JSON')
    parser.add_argument('--output', default='config/generated_schema.sql', help='Path to output SQL file')
    args = parser.parse_args()

    # Load params and use case config
    params = load_params(args.parameters)
    demo_ctx = params.get('demo_context', {})
    print(f"Customer : {demo_ctx.get('customer_name', 'N/A')} | Industry: {demo_ctx.get('industry', 'N/A')}")
    print(f"Use Case : {demo_ctx.get('use_case', 'N/A')}")

    config = load_usecase(params)
    use_case_config_path = demo_ctx.get('use_case_config', '')
    print(f"Loading config from {use_case_config_path if use_case_config_path else 'N/A'}...")

    ddl_statements = generate_ddl(config)

    # Derive output path if default is used
    output_path = args.output
    if args.output == 'config/generated_schema.sql' and use_case_config_path:
        output_path = os.path.join(os.path.dirname(use_case_config_path), 'schema.sql')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        for stmt in ddl_statements:
            f.write(stmt + "\n\n")

    print(f"Generated {len(ddl_statements)} DDL statements -> {output_path}")
    print("\n--- Schema Preview (first 2 tables) ---")
    print("\n\n".join(ddl_statements[:2]))
    print("...\n[Remaining statements written to file]")

if __name__ == "__main__":
    main()
