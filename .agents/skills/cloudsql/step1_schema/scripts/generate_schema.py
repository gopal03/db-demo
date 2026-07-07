import json
import argparse
import os
import sys

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def map_type(agnostic_type):
    t_upper = agnostic_type.upper()
    if "STRING(36)" in t_upper:
        return "VARCHAR(36)"
    elif "STRING" in t_upper:
        if "(" in t_upper:
            length = t_upper.split("(")[1].split(")")[0]
            return f"VARCHAR({length})"
        return "TEXT"
    elif "INT64" in t_upper or "BIGINT" in t_upper:
        return "BIGINT"
    elif "INT" in t_upper:
        return "INTEGER"
    elif "NUMERIC" in t_upper or "DECIMAL" in t_upper:
        return "NUMERIC(12, 2)"
    elif "FLOAT64" in t_upper or "DOUBLE" in t_upper:
        return "DOUBLE PRECISION"
    elif "BOOL" in t_upper:
        return "BOOLEAN"
    elif "TIMESTAMP" in t_upper:
        return "TIMESTAMPTZ"
    else:
        return "VARCHAR(100)"

def generate_ddl(config):
    statements = []
    
    for node in config.get("nodes", []):
        table_name = node["table_name"]
        pk_cols = node["key"]
        
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        columns_sql = []
        for prop in node.get("properties", []):
            name = prop["name"]
            p_type = map_type(prop["type"])
            nullable = "NULL" if prop.get("nullable", True) else "NOT NULL"
            columns_sql.append(f"    {name} {p_type} {nullable}")
            
        columns_sql.append(f"    PRIMARY KEY ({', '.join(pk_cols)})")
        sql += ",\n".join(columns_sql) + "\n);"
        statements.append(sql)
        
    for edge in config.get("edges", []):
        table_name = edge["table_name"]
        pk_cols = edge["key"]
        src = edge["source"]
        dst = edge["destination"]
        
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        columns_sql = []
        
        for prop in edge.get("properties", []):
            name = prop["name"]
            p_type = map_type(prop["type"])
            nullable = "NULL" if prop.get("nullable", True) else "NOT NULL"
            columns_sql.append(f"    {name} {p_type} {nullable}")
            
        src_table = None
        for node in config.get("nodes", []):
            if node["name"] == src["node_name"]:
                src_table = node["table_name"]
                break
                
        fk_src_cols = list(src["key_map"].keys())
        ref_src_cols = list(src["key_map"].values())
        columns_sql.append(f"    FOREIGN KEY ({', '.join(fk_src_cols)}) REFERENCES {src_table}({', '.join(ref_src_cols)}) ON DELETE CASCADE")
        
        dst_table = None
        for node in config.get("nodes", []):
            if node["name"] == dst["node_name"]:
                dst_table = node["table_name"]
                break
                
        fk_dst_cols = list(dst["key_map"].keys())
        ref_dst_cols = list(dst["key_map"].values())
        columns_sql.append(f"    FOREIGN KEY ({', '.join(fk_dst_cols)}) REFERENCES {dst_table}({', '.join(ref_dst_cols)}) ON DELETE CASCADE")
        
        columns_sql.append(f"    PRIMARY KEY ({', '.join(pk_cols)})")
        sql += ",\n".join(columns_sql) + "\n);"
        statements.append(sql)
        
    return "\n\n".join(statements)

def generate_indexes(config):
    statements = []
    for edge in config.get("edges", []):
        table_name = edge["table_name"]
        
        src_cols = list(edge["source"]["key_map"].keys())
        idx_src_name = f"idx_{table_name}_{'_'.join(src_cols)}"
        statements.append(f"CREATE INDEX IF NOT EXISTS {idx_src_name} ON {table_name} ({', '.join(src_cols)});")
        
        dst_cols = list(edge["destination"]["key_map"].keys())
        idx_dst_name = f"idx_{table_name}_{'_'.join(dst_cols)}"
        statements.append(f"CREATE INDEX IF NOT EXISTS {idx_dst_name} ON {table_name} ({', '.join(dst_cols)});")
        
    return "\n".join(statements)

def main():
    parser = argparse.ArgumentParser(description="Static SQL DDL Generator for Postgres.")
    parser.add_argument('--config', required=True, help='Path to use_case_config.json')
    parser.add_argument('--output-schema', required=True, help='Path to output schema.sql')
    parser.add_argument('--output-indexes', required=True, help='Path to output indexes.sql')
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        print(f"Error: Config file {args.config} not found.")
        sys.exit(1)
        
    config = load_json(args.config)
    
    schema_sql = generate_ddl(config)
    os.makedirs(os.path.dirname(args.output_schema), exist_ok=True)
    with open(args.output_schema, 'w') as f:
        f.write(schema_sql + "\n")
    print(f"Schema written to {args.output_schema}")
    
    indexes_sql = generate_indexes(config)
    os.makedirs(os.path.dirname(args.output_indexes), exist_ok=True)
    with open(args.output_indexes, 'w') as f:
        f.write(indexes_sql + "\n")
    print(f"Indexes written to {args.output_indexes}")

if __name__ == "__main__":
    main()
