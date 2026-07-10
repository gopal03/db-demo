import os
import json
import pandas as pd

class SpannerAdapter:
    def __init__(self, params):
        self.project_id = params.get("project_id")
        spanner_cfg = params.get("database_configs", {}).get("spanner", {})
        self.instance_id = spanner_cfg.get("instance_id")
        self.database_id = spanner_cfg.get("database_id")
        
        if not self.instance_id or not self.database_id:
            raise ValueError("Spanner connection properties (instance_id, database_id) are missing in parameters!")
            
        from google.cloud import spanner
        self.client = spanner.Client(project=self.project_id)
        instance = self.client.instance(self.instance_id)
        if not instance.exists():
            raise ConnectionError(f"Spanner instance '{self.instance_id}' does not exist in project '{self.project_id}'!")
        db = instance.database(self.database_id)
        if not db.exists():
            raise ConnectionError(f"Spanner database '{self.database_id}' does not exist in instance '{self.instance_id}'!")
        self.db_conn = db

    def is_online(self):
        return self.db_conn is not None

    def get_row_count(self, table_name):
        if not self.is_online():
            return "-"
        try:
            with self.db_conn.snapshot() as snapshot:
                result = list(snapshot.execute_sql(f"SELECT COUNT(*) FROM {table_name}"))
                return result[0][0]
        except Exception:
            return "-"

    def execute_query(self, query_config):
        if not self.is_online():
            return pd.DataFrame()
        query_text = query_config.get("gql") or query_config.get("sql")
        with self.db_conn.snapshot() as snapshot:
            results = snapshot.execute_sql(query_text)
            rows = list(results)
            headers = [field.name for field in results.fields] if results.fields else []
            return pd.DataFrame(rows, columns=headers)

class PostgresAdapter:
    def __init__(self, target_database, params):
        import psycopg2
        db_cfg = params.get("database_configs", {}).get(target_database, {})
        host = db_cfg.get("host")
        port = db_cfg.get("port", 5432)
        user = db_cfg.get("user")
        password = db_cfg.get("password")
        database_id = db_cfg.get("database_id")
        
        if not host or not user or not password or not database_id:
            raise ValueError(f"Postgres ({target_database.upper()}) connection properties (host, user, password, database_id) are missing in parameters!")
            
        self.db_conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database_id,
            sslmode="require" if target_database == "alloydb" else "prefer"
        )

    def is_online(self):
        return self.db_conn is not None

    def get_row_count(self, table_name):
        if not self.is_online():
            return "-"
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                return cursor.fetchone()[0]
        except Exception:
            return "-"

    def execute_query(self, query_config):
        if not self.is_online():
            return pd.DataFrame()
        query_text = query_config.get("sql") or query_config.get("gql")
        with self.db_conn.cursor() as cursor:
            cursor.execute(query_text)
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description] if cursor.description else []
            return pd.DataFrame(rows, columns=headers)

class RedisAdapter:
    def __init__(self, params):
        import redis
        db_cfg = params.get("database_configs", {}).get("memorystore", {})
        host = db_cfg.get("host")
        port = db_cfg.get("port", 6379)
        
        if not host:
            raise ValueError("Redis (Memorystore) connection properties (host) are missing in parameters!")
            
        self.db_conn = redis.Redis(host=host, port=port, decode_responses=True)
        self.db_conn.ping()

    def is_online(self):
        return self.db_conn is not None

    def get_row_count(self, table_name):
        if not self.is_online():
            return "-"
        try:
            return len(self.db_conn.keys(f"{table_name}:*"))
        except Exception:
            return "-"

    def execute_query(self, query_config):
        if not self.is_online():
            return pd.DataFrame()
        pattern = query_config.get("redis_pattern") or "*"
        keys = self.db_conn.keys(pattern)
        data = []
        for k in keys[:50]:
            val_type = self.db_conn.type(k)
            if val_type == "hash":
                data.append({"key": k, **self.db_conn.hgetall(k)})
            else:
                data.append({"key": k, "value": self.db_conn.get(k)})
        return pd.DataFrame(data)

class FirestoreAdapter:
    def __init__(self, params):
        from google.cloud import firestore
        db_cfg = params.get("database_configs", {}).get("firestore", {})
        database_id = db_cfg.get("database_id")
        
        if not database_id:
            raise ValueError("Firestore connection properties (database_id) are missing in parameters!")
            
        self.db_conn = firestore.Client(
            project=params.get("project_id"),
            database=database_id
        )

    def is_online(self):
        return self.db_conn is not None

    def get_row_count(self, collection_name):
        if not self.is_online():
            return "-"
        try:
            return self.db_conn.collection(collection_name).count().get()[0][0].value
        except Exception:
            return "-"

    def execute_query(self, query_config):
        if not self.is_online():
            return pd.DataFrame()
        col = query_config.get("collection")
        docs = self.db_conn.collection(col).limit(50).stream()
        data = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        return pd.DataFrame(data)

class BigtableAdapter:
    def __init__(self, params):
        from google.cloud import bigtable
        db_cfg = params.get("database_configs", {}).get("bigtable", {})
        instance_id = db_cfg.get("instance_id")
        
        if not instance_id:
            raise ValueError("Bigtable connection properties (instance_id) are missing in parameters!")
            
        client = bigtable.Client(project=params.get("project_id"), admin=True)
        instance = client.instance(instance_id)
        if not instance.exists():
            raise ConnectionError(f"Bigtable instance '{instance_id}' does not exist!")
        self.db_conn = instance

    def is_online(self):
        return self.db_conn is not None

    def get_row_count(self, table_id):
        if not self.is_online():
            return "-"
        try:
            table = self.db_conn.table(table_id)
            return sum(1 for _ in table.read_rows())
        except Exception:
            return "-"

    def execute_query(self, query_config):
        if not self.is_online():
            return pd.DataFrame()
        table_id = query_config.get("table_id")
        table = self.db_conn.table(table_id)
        rows = table.read_rows(limit=50)
        data = []
        for r in rows:
            row_data = {"row_key": r.row_key.decode()}
            for family_id, family in r.cells.items():
                for column, cells in family.items():
                    col_name = f"{family_id}:{column.decode()}"
                    row_data[col_name] = cells[0].value.decode()
            data.append(row_data)
        return pd.DataFrame(data)

def get_database_adapter(target_database, params):
    """
    Factory to retrieve the matching database connection adapter.
    """
    if target_database == "spanner":
        return SpannerAdapter(params)
    elif target_database in ["alloydb", "cloudsql"]:
        return PostgresAdapter(target_database, params)
    elif target_database == "memorystore":
        return RedisAdapter(params)
    elif target_database == "firestore":
        return FirestoreAdapter(params)
    elif target_database == "bigtable":
        return BigtableAdapter(params)
    else:
        raise ValueError(f"Unsupported database target: {target_database}")
