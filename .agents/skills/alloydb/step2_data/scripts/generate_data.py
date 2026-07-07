import json
import argparse
import os
import sys
import datetime
import random

# Curated values for mock data
MALE_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
SURNAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

PRODUCT_NAMES = {
    "Electronics": ["Pro Laptop 15", "Noise-Cancelling Headphones", "Smartwatch Series 5", "4K Ultra Monitor", "Wireless Charger Pad"],
    "Apparel": ["Classic Denim Jacket", "Slim Fit Chinos", "Activewear Running Shoes", "Leather Messenger Bag", "Merino Wool Sweater"],
    "Home": ["Ergonomic Office Chair", "Dimmable LED Desk Lamp", "Stainless Steel French Press", "Memory Foam Pillow", "Ceramic Dinnerware Set"],
    "Sports": ["Premium Yoga Mat", "Lightweight Tennis Racket", "Water-Resistant Backpack", "Adjustable Dumbbell Set", "Polarized Running Sunglasses"],
    "Beauty": ["Hydrating Face Serum", "Organic Argan Oil", "Volumizing Mascara", "Matte Lip Stain", "Mineral Sunscreen SPF 50"]
}

CITIES = {
    "USA": [("New York", "NY"), ("San Francisco", "CA"), ("Chicago", "IL"), ("Austin", "TX"), ("Miami", "FL")],
    "UK": [("London", "ENG"), ("Manchester", "ENG"), ("Edinburgh", "SCT"), ("Birmingham", "ENG")],
    "Germany": [("Munich", "BY"), ("Berlin", "BE"), ("Frankfurt", "HE"), ("Hamburg", "HH")],
    "Japan": [("Tokyo", "TYO"), ("Osaka", "OSA"), ("Kyoto", "KYT"), ("Fukuoka", "FUK")],
    "Singapore": [("Singapore", "SG")]
}

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "corp.example.com", "protonmail.com"]
SEGMENTS = ["High-Value", "Standard", "Budget", "VIP", "New User"]
LOYALTY_TIERS = ["Platinum", "Gold", "Silver", "Bronze", "None"]
CHANNELS = ["Web", "Mobile App", "In-Store", "Partner API"]
RISK_LEVELS = ["LOW", "MEDIUM", "HIGH"]
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "SGD"]
BANKS = ["Global Trust Bank", "Apex Capital Bank", "Sovereign Finance", "Nova Horizon Bank", "Summit Mutual"]
MERCHANT_CATEGORIES = ["Retail", "Entertainment", "Utilities", "Travel", "Dining", "Gaming/Casino"]

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def generate_value(prop_name, prop_type, context={}):
    name_lower = prop_name.lower()
    if context.get("nullable", True) and random.random() < 0.02:
        return None

    if "email" in name_lower:
        first = context.get("first_name", "user").lower()
        last = context.get("last_name", "name").lower()
        return f"{first}.{last}@{random.choice(EMAIL_DOMAINS)}"
    elif "name" in name_lower:
        if context.get("node_label") == "Customer":
            first = random.choice(MALE_NAMES if random.random() < 0.5 else FEMALE_NAMES)
            last = random.choice(SURNAMES)
            context["first_name"] = first
            context["last_name"] = last
            return f"{first} {last}"
        elif context.get("node_label") == "Product":
            cat = context.get("product_category", "Electronics")
            return random.choice(PRODUCT_NAMES.get(cat, PRODUCT_NAMES["Electronics"]))
        elif context.get("node_label") == "Store" or "store" in name_lower:
            city = context.get("city", "San Francisco")
            return f"Flagship Store {city}"
        elif "bank" in name_lower:
            return random.choice(BANKS)
        else:
            return f"Entity {random.randint(100, 999)}"
    elif "category" in name_lower:
        if context.get("node_label") == "Merchant":
            return random.choice(MERCHANT_CATEGORIES)
        cat = random.choice(list(PRODUCT_NAMES.keys()))
        context["product_category"] = cat
        return cat
    elif "segment" in name_lower:
        return random.choice(SEGMENTS)
    elif "tier" in name_lower or "loyalty" in name_lower:
        return random.choice(LOYALTY_TIERS)
    elif "channel" in name_lower:
        return random.choice(CHANNELS)
    elif "risk_score" in name_lower:
        return random.randint(1, 10)
    elif "risk_level" in name_lower:
        return random.choice(RISK_LEVELS)
    elif "currency" in name_lower:
        return random.choice(CURRENCIES)
    elif "country" in name_lower:
        country = random.choice(list(CITIES.keys()))
        context["country"] = country
        return country
    elif "city" in name_lower:
        country = context.get("country", "USA")
        city_list = CITIES.get(country, CITIES["USA"])
        city_info = random.choice(city_list)
        context["city"] = city_info[0]
        context["state"] = city_info[1]
        return city_info[0]
    elif "state" in name_lower:
        return context.get("state", "CA")
    elif "price" in name_lower or "amount" in name_lower or "balance" in name_lower:
        val = round(random.uniform(5.00, 1500.00), 2)
        if "INT" in prop_type.upper():
            return int(val)
        return str(val) if "NUMERIC" in prop_type.upper() else val
    elif "timestamp" in name_lower or "date" in name_lower or "_at" in name_lower:
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        mins_ago = random.randint(0, 59)
        dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=mins_ago)
        return dt.isoformat()

    type_upper = prop_type.upper()
    if "INT64" in type_upper or "BIGINT" in type_upper or "INT" in type_upper:
        return random.randint(10, 100000)
    elif "NUMERIC" in type_upper:
        return f"{round(random.uniform(1.00, 10000.00), 2)}"
    elif "FLOAT64" in type_upper or "DOUBLE" in type_upper:
        return random.uniform(1.0, 1000.0)
    elif "BOOL" in type_upper:
        return random.choice([True, False])
    elif "TIMESTAMP" in type_upper:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
    else:
        return f"Val-{random.randint(100, 999)}"

def generate_prefix_id(label, index):
    prefix = label[:4].lower()
    return f"{prefix}-{str(index).zfill(7)}"

def inject_custom_seeding_paths(graph_name, dataset, rows_per_table):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if graph_name == "RetailMarketingGraph":
        print(" [Seeding] Injecting specific paths for Retail Marketing Demo...")
        customers = dataset.get("Customers", [])
        products = dataset.get("Products", [])
        stores = dataset.get("Stores", [])
        
        if len(customers) >= 3:
            customers[0] = {"customer_id": "cust-0000000", "name": "James Smith", "email": "james.smith@corp.example.com", "segment": "VIP", "loyalty_tier": "Platinum", "signup_date": now}
            customers[1] = {"customer_id": "cust-0000001", "name": "Mary Johnson", "email": "mary.johnson@gmail.com", "segment": "Standard", "loyalty_tier": "Gold", "signup_date": now}
            customers[2] = {"customer_id": "cust-0000002", "name": "John Davis", "email": "john.davis@yahoo.com", "segment": "High-Value", "loyalty_tier": "Platinum", "signup_date": now}
        
        if len(products) >= 6:
            products[0] = {"product_id": "prod-0000000", "name": "Ultra-Wide Monitor 34", "category": "Electronics", "brand": "ApexTech", "price": "599.99"}
            products[1] = {"product_id": "prod-0000001", "name": "Ergonomic Office Chair", "category": "Home", "brand": "FlexiSit", "price": "249.50"}
            products[2] = {"product_id": "prod-0000002", "name": "Classic Running Shoes", "category": "Sports", "brand": "RunMax", "price": "120.00"}
            products[3] = {"product_id": "prod-0000003", "name": "Wireless Charging Pad", "category": "Electronics", "brand": "ApexTech", "price": "45.00"}
            products[4] = {"product_id": "prod-0000004", "name": "Smart Watch Series 6", "category": "Electronics", "brand": "ApexTech", "price": "349.00"}
            products[5] = {"product_id": "prod-0000005", "name": "Premium Leather Jacket", "category": "Apparel", "brand": "FitWare", "price": "299.00"}
            
        if len(stores) >= 1:
            stores[0] = {"store_id": "store-0000000", "name": "Downtown Flagship Store", "city": "San Francisco", "state": "CA", "zip_code": "94105"}

        prefers_store = dataset.get("CustomerPreferredStore", [])
        views = dataset.get("CustomerViews", [])
        inventory = dataset.get("ProductInventory", [])
        purchases = dataset.get("CustomerPurchases", [])
        
        prefers_store.insert(0, {"customer_id": "cust-0000000", "store_id": "store-0000000", "assigned_at": now})
        views.insert(0, {"customer_id": "cust-0000000", "view_id": "view-0000001", "product_id": "prod-0000000", "duration_seconds": 120, "device_type": "Desktop", "timestamp": now})
        views.insert(1, {"customer_id": "cust-0000000", "view_id": "view-0000002", "product_id": "prod-0000004", "duration_seconds": 180, "device_type": "Mobile", "timestamp": now})
        
        inventory.insert(0, {"product_id": "prod-0000000", "store_id": "store-0000000", "quantity": 12, "aisle_location": "Aisle A4"})
        inventory.insert(1, {"product_id": "prod-0000004", "store_id": "store-0000000", "quantity": 8, "aisle_location": "Aisle B2"})
        
        purchases.insert(0, {"customer_id": "cust-0000000", "purchase_id": "purch-0000001", "product_id": "prod-0000002", "store_id": "store-0000000", "quantity": 1, "price_paid": "120.00", "timestamp": now})
        purchases.insert(1, {"customer_id": "cust-0000001", "purchase_id": "purch-0000002", "product_id": "prod-0000002", "store_id": "store-0000000", "quantity": 1, "price_paid": "120.00", "timestamp": now})
        purchases.insert(2, {"customer_id": "cust-0000001", "purchase_id": "purch-0000003", "product_id": "prod-0000003", "store_id": "store-0000000", "quantity": 1, "price_paid": "45.00", "timestamp": now})
        
        views.insert(2, {"customer_id": "cust-0000002", "view_id": "view-0000003", "product_id": "prod-0000004", "duration_seconds": 240, "device_type": "Tablet", "timestamp": now})
        purchases.insert(3, {"customer_id": "cust-0000002", "purchase_id": "purch-0000004", "product_id": "prod-0000005", "store_id": "store-0000000", "quantity": 1, "price_paid": "299.00", "timestamp": now})

def generate_dataset(config, rows_per_table):
    dataset = {}
    node_id_pool = {}

    print(f"\nGenerating mock dataset for database: {config['graph_name']}")
    print(f"Target scale: {rows_per_table:,} rows per main table.")

    for node in config.get("nodes", []):
        label = node["name"]
        table_name = node["table_name"]
        pk_cols = node["key"]
        
        print(f" -> Generating table: {table_name}...")
        records = []
        node_pks = []

        for idx in range(rows_per_table):
            record = {}
            context = {"node_label": label, "nullable": False}
            
            for pk in pk_cols:
                if len(pk_cols) == 1:
                    pk_val = generate_prefix_id(label, idx)
                else:
                    pk_val = f"{label[:3].lower()}-{idx}-{random.randint(1000, 9999)}"
                record[pk] = pk_val
            
            for prop in node.get("properties", []):
                if prop["name"] in record:
                    continue
                context["nullable"] = prop.get("nullable", True)
                record[prop["name"]] = generate_value(prop["name"], prop["type"], context)
            
            records.append(record)
            node_pks.append({pk: record[pk] for pk in pk_cols})
            
        dataset[table_name] = records
        node_id_pool[label] = node_pks

    edge_scale_multiplier = {
        "PrefersStore": 1,
        "CustomerPreferredStore": 1,
        "Purchased": 4,
        "CustomerPurchases": 4,
        "Transfers": 5,
        "PaysMerchant": 3,
        "Views": 6,
        "CustomerViews": 6,
        "Inventory": 2,
        "ProductInventory": 2
    }

    for edge in config.get("edges", []):
        label = edge["name"]
        table_name = edge["table_name"]
        pk_cols = edge["key"]
        src_node = edge["source"]["node_name"]
        dst_node = edge["destination"]["node_name"]
        
        multiplier = edge_scale_multiplier.get(label, 4)
        n_edges = rows_per_table * multiplier
        
        print(f" -> Generating table: {table_name} (creating {n_edges:,} records)...")
        records = []
        seen_edges = set()

        src_pks = node_id_pool.get(src_node, [])
        dst_pks = node_id_pool.get(dst_node, [])

        if not src_pks or not dst_pks:
            continue

        for idx in range(min(10, rows_per_table)):
            record = {}
            context = {"node_label": label, "nullable": False}
            
            src_node_pk = src_pks[idx]
            for edge_k, node_k in edge["source"]["key_map"].items():
                record[edge_k] = src_node_pk[node_k]
                
            dst_node_pk = dst_pks[(idx + 1) % len(dst_pks)]
            for edge_k, node_k in edge["destination"]["key_map"].items():
                record[edge_k] = dst_node_pk[node_k]

            edge_pk_vals = []
            for pk in pk_cols:
                if pk in record:
                    edge_pk_vals.append(record[pk])
                else:
                    if "timestamp" in pk.lower() or "date" in pk.lower() or "_at" in pk.lower():
                        val = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=idx)).isoformat()
                    else:
                        val = f"tx-{idx}-{random.randint(1000, 9999)}"
                    record[pk] = val
                    edge_pk_vals.append(val)
            
            edge_tuple = tuple(edge_pk_vals)
            if edge_tuple not in seen_edges:
                for prop in edge.get("properties", []):
                    if prop["name"] in record:
                        continue
                    context["nullable"] = prop.get("nullable", True)
                    record[prop["name"]] = generate_value(prop["name"], prop["type"], context)
                
                records.append(record)
                seen_edges.add(edge_tuple)

        attempts = 0
        max_attempts = n_edges * 10
        
        while len(records) < n_edges and attempts < max_attempts:
            attempts += 1
            record = {}
            context = {"node_label": label, "nullable": False}
            
            src_node_pk = random.choice(src_pks)
            dst_node_pk = random.choice(dst_pks)
            
            for edge_k, node_k in edge["source"]["key_map"].items():
                record[edge_k] = src_node_pk[node_k]
                
            for edge_k, node_k in edge["destination"]["key_map"].items():
                record[edge_k] = dst_node_pk[node_k]
                
            edge_pk_vals = []
            for pk in pk_cols:
                if pk in record:
                    edge_pk_vals.append(record[pk])
                else:
                    if "timestamp" in pk.lower() or "date" in pk.lower() or "_at" in pk.lower():
                        dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=random.randint(0, 30), minutes=random.randint(0, 1440))
                        val = dt.isoformat()
                    else:
                        val = f"dis-{random.randint(100000, 999999)}"
                    record[pk] = val
                    edge_pk_vals.append(val)
            
            edge_tuple = tuple(edge_pk_vals)
            
            if edge_tuple not in seen_edges:
                for prop in edge.get("properties", []):
                    if prop["name"] in record:
                        continue
                    context["nullable"] = prop.get("nullable", True)
                    record[prop["name"]] = generate_value(prop["name"], prop["type"], context)
                
                records.append(record)
                seen_edges.add(edge_tuple)

        dataset[table_name] = records

    inject_custom_seeding_paths(config['graph_name'], dataset, rows_per_table)

    return dataset

def main():
    parser = argparse.ArgumentParser(description="Generic Relational Data Generator.")
    parser.add_argument('--config', required=True, help='Path to the use_case_config.json')
    parser.add_argument('--parameters', default='config/demo_parameters.json', help='Path to demo_parameters.json')
    parser.add_argument('--output', required=True, help='Path to output JSON file')
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: Config {args.config} not found.")
        sys.exit(1)
        
    use_case_config = load_json(args.config)
    
    rows_per_table = 500
    if os.path.exists(args.parameters):
        try:
            params = load_json(args.parameters)
            profile_name = params.get("data_config", {}).get("profile", "small")
            rows_per_table = params.get("data_config", {}).get("profiles", {}).get(profile_name, {}).get("rows_per_table", 500)
            print(f"Loaded scale profile '{profile_name}' with {rows_per_table} rows per table.")
        except Exception as e:
            print(f"Warning: Failed to load parameters: {e}. Defaulting to 500 rows.")

    mock_data = generate_dataset(use_case_config, rows_per_table)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    print(f"Writing dataset to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(mock_data, f, indent=2)

    print("\nData generation complete:")
    for table_name, records in mock_data.items():
        print(f"  - {table_name}: {len(records):,} records generated.")

if __name__ == "__main__":
    main()
