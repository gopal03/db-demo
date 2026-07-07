import json
import os
import sys
import datetime
import random

def current_micros():
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000000)

MAX_LONG = 9223372036854775807 # 2^63 - 1

def reverse_timestamp(micros):
    return MAX_LONG - micros

# Heuristic name/label choices
MALE_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
SURNAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
SEGMENTS = ["High-Value", "Standard", "Budget", "VIP", "New User"]
LOYALTY_TIERS = ["Platinum", "Gold", "Silver", "Bronze", "None"]
CATEGORIES = ["Electronics", "Apparel", "Home", "Sports", "Beauty"]
BRANDS = ["ApexTech", "FlexiSit", "RunMax", "FitWare", "ZenLiving", "GlowBody"]
PRODUCT_NAMES = {
    "Electronics": ["Pro Laptop 15", "Noise-Cancelling Headphones", "Smartwatch Series 5", "4K Ultra Monitor", "Wireless Charger Pad"],
    "Apparel": ["Classic Denim Jacket", "Slim Fit Chinos", "Activewear Running Shoes", "Leather Messenger Bag", "Merino Wool Sweater"],
    "Home": ["Ergonomic Office Chair", "Dimmable LED Desk Lamp", "Stainless Steel French Press", "Memory Foam Pillow", "Ceramic Dinnerware Set"],
    "Sports": ["Premium Yoga Mat", "Lightweight Tennis Racket", "Water-Resistant Backpack", "Adjustable Dumbbell Set", "Polarized Running Sunglasses"],
    "Beauty": ["Hydrating Face Serum", "Organic Argan Oil", "Volumizing Mascara", "Matte Lip Stain", "Mineral Sunscreen SPF 50"]
}
CITIES = [("New York", "NY", "10001"), ("San Francisco", "CA", "94105"), ("Chicago", "IL", "60601"), ("Austin", "TX", "78701"), ("Miami", "FL", "33101")]
DEVICE_TYPES = ["Desktop", "Mobile", "Tablet", "SmartTV"]

def rand_id(prefix, n):
    return f"{prefix}-{str(n).zfill(7)}"

def load_params():
    path = "config/demo_parameters.json"
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def main():
    params = load_params()
    profile_name = params.get("data_config", {}).get("profile", "small")
    profile = params.get("data_config", {}).get("profiles", {}).get(profile_name, {})
    rows_per_table = profile.get("rows_per_table", 500)
    
    print(f"Generating mock data for Bigtable demo...")
    print(f"Profile: {profile_name} ({rows_per_table} rows)")
    
    # 1. Generate Stores
    n_stores = 10
    stores = []
    store_ids = []
    for i in range(n_stores):
        sid = rand_id("stor", i)
        store_ids.append(sid)
        city, state, zip_c = CITIES[i % len(CITIES)]
        stores.append({
            "row_key": sid,
            "cells": [
                {"family": "d", "qualifier": "name", "value": f"Flagship Store {city}"},
                {"family": "d", "qualifier": "city", "value": city},
                {"family": "d", "qualifier": "state", "value": state},
                {"family": "d", "qualifier": "zip_code", "value": zip_c}
            ]
        })
        
    # 2. Generate Products
    n_products = 100
    products = []
    product_ids = []
    product_prices = {}
    product_categories = {}
    
    for i in range(n_products):
        pid = rand_id("prod", i)
        product_ids.append(pid)
        category = random.choice(CATEGORIES)
        brand = random.choice(BRANDS)
        prod_name = random.choice(PRODUCT_NAMES[category]) + f" {random.randint(1, 9)}"
        # Seed cheap/expensive range
        price = round(random.uniform(10.0, 99.0) if i > 10 else random.uniform(120.0, 800.0), 2)
        
        product_prices[pid] = price
        product_categories[pid] = category
        
        products.append({
            "row_key": pid,
            "cells": [
                {"family": "d", "qualifier": "name", "value": prod_name},
                {"family": "d", "qualifier": "category", "value": category},
                {"family": "d", "qualifier": "brand", "value": brand},
                {"family": "d", "qualifier": "price", "value": str(price)}
            ]
        })
        
    # 3. Generate Customers
    customers = []
    customer_ids = []
    customer_loyalty = {}
    customer_store = {}
    
    for i in range(rows_per_table):
        cid = rand_id("cust", i)
        customer_ids.append(cid)
        first = random.choice(MALE_NAMES if random.random() < 0.5 else FEMALE_NAMES)
        last = random.choice(SURNAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'example.com'])}"
        
        segment = random.choice(SEGMENTS)
        loyalty = random.choice(LOYALTY_TIERS)
        if i == 0:
            segment = "VIP"
            loyalty = "Platinum"
        elif i == 1:
            segment = "Standard"
            loyalty = "Gold"
            
        customer_loyalty[cid] = loyalty
        preferred_store = random.choice(store_ids)
        customer_store[cid] = preferred_store
        
        signup_dt = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=random.randint(30, 365))).isoformat()
        
        customers.append({
            "row_key": cid,
            "cells": [
                {"family": "d", "qualifier": "name", "value": name},
                {"family": "d", "qualifier": "email", "value": email},
                {"family": "d", "qualifier": "segment", "value": segment},
                {"family": "d", "qualifier": "loyalty_tier", "value": loyalty},
                {"family": "d", "qualifier": "signup_date", "value": signup_dt},
                {"family": "p", "qualifier": "preferred_store_id", "value": preferred_store}
            ]
        })
        
    # 4. Generate Inventory
    inventory = []
    for pid in product_ids:
        allocated_stores = random.sample(store_ids, 3)
        for sid in allocated_stores:
            qty = random.randint(5, 100)
            aisle = f"Aisle {random.choice(['A','B','C','D'])}{random.randint(1,9)}"
            inventory.append({
                "row_key": f"{pid}#{sid}",
                "cells": [
                    {"family": "d", "qualifier": "quantity", "value": str(qty)},
                    {"family": "d", "qualifier": "aisle_location", "value": aisle}
                ]
            })
            
    # 5. Generate Customer Events (Views & Purchases)
    customer_events = []
    now_micros = current_micros()
    
    # --- SEED SCENARIO 1 (Omnichannel conversion) ---
    c0 = customer_ids[0]
    p0 = product_ids[0]
    s0 = customer_store[c0]
    
    # View
    v_time_1 = now_micros - 10000000 # 10s ago
    customer_events.append({
        "row_key": f"{c0}#view#{reverse_timestamp(v_time_1)}",
        "cells": [
            {"family": "e", "qualifier": "product_id", "value": p0},
            {"family": "e", "qualifier": "duration_seconds", "value": "120"},
            {"family": "e", "qualifier": "device_type", "value": "Desktop"},
            {"family": "e", "qualifier": "timestamp", "value": datetime.datetime.fromtimestamp(v_time_1/1000000, datetime.timezone.utc).isoformat()}
        ]
    })
    # Purchase at Preferred Store
    p_time_1 = now_micros - 5000000 # 5s ago
    customer_events.append({
        "row_key": f"{c0}#purchase#{reverse_timestamp(p_time_1)}",
        "cells": [
            {"family": "e", "qualifier": "product_id", "value": p0},
            {"family": "e", "qualifier": "store_id", "value": s0},
            {"family": "e", "qualifier": "quantity", "value": "1"},
            {"family": "e", "qualifier": "price_paid", "value": str(product_prices[p0])},
            {"family": "e", "qualifier": "timestamp", "value": datetime.datetime.fromtimestamp(p_time_1/1000000, datetime.timezone.utc).isoformat()}
        ]
    })
    
    # --- SEED SCENARIO 2 (Cart Abandonment) ---
    p1 = product_ids[1]
    if product_prices[p1] <= 100:
        product_prices[p1] = 150.00
        # Sync inside product record
        for prod in products:
            if prod["row_key"] == p1:
                for cell in prod["cells"]:
                    if cell["qualifier"] == "price":
                        cell["value"] = "150.0"
                        
    v_time_2 = now_micros - 20000000
    customer_events.append({
        "row_key": f"{c0}#view#{reverse_timestamp(v_time_2)}",
        "cells": [
            {"family": "e", "qualifier": "product_id", "value": p1},
            {"family": "e", "qualifier": "duration_seconds", "value": "240"},
            {"family": "e", "qualifier": "device_type", "value": "Mobile"},
            {"family": "e", "qualifier": "timestamp", "value": datetime.datetime.fromtimestamp(v_time_2/1000000, datetime.timezone.utc).isoformat()}
        ]
    })
    # Note: No purchase seeded for c0 with p1
    
    # --- SEED SCENARIO 3 (Product Affinity) ---
    c1 = customer_ids[1]
    p2 = product_ids[2]
    p3 = product_ids[3]
    if product_categories[p2] == product_categories[p3]:
        for cat in CATEGORIES:
            if cat != product_categories[p2]:
                product_categories[p3] = cat
                break
        for prod in products:
            if prod["row_key"] == p3:
                for cell in prod["cells"]:
                    if cell["qualifier"] == "category":
                        cell["value"] = product_categories[p3]
                        
    p_time_2 = now_micros - 30000000
    customer_events.append({
        "row_key": f"{c1}#purchase#{reverse_timestamp(p_time_2)}",
        "cells": [
            {"family": "e", "qualifier": "product_id", "value": p2},
            {"family": "e", "qualifier": "store_id", "value": customer_store[c1]},
            {"family": "e", "qualifier": "quantity", "value": "1"},
            {"family": "e", "qualifier": "price_paid", "value": str(product_prices[p2])},
            {"family": "e", "qualifier": "timestamp", "value": datetime.datetime.fromtimestamp(p_time_2/1000000, datetime.timezone.utc).isoformat()}
        ]
    })
    p_time_3 = now_micros - 25000000
    customer_events.append({
        "row_key": f"{c1}#purchase#{reverse_timestamp(p_time_3)}",
        "cells": [
            {"family": "e", "qualifier": "product_id", "value": p3},
            {"family": "e", "qualifier": "store_id", "value": customer_store[c1]},
            {"family": "e", "qualifier": "quantity", "value": "1"},
            {"family": "e", "qualifier": "price_paid", "value": str(product_prices[p3])},
            {"family": "e", "qualifier": "timestamp", "value": datetime.datetime.fromtimestamp(p_time_3/1000000, datetime.timezone.utc).isoformat()}
        ]
    })
    
    # Generate background random events
    n_random_events = 1300
    for _ in range(n_random_events):
        cid = random.choice(customer_ids)
        pid = random.choice(product_ids)
        event_type = random.choice(["view", "purchase"])
        evt_time = now_micros - random.randint(1000000, 100000000000)
        
        if event_type == "view":
            dur = random.randint(5, 300)
            dev = random.choice(DEVICE_TYPES)
            customer_events.append({
                "row_key": f"{cid}#view#{reverse_timestamp(evt_time)}",
                "cells": [
                    {"family": "e", "qualifier": "product_id", "value": pid},
                    {"family": "e", "qualifier": "duration_seconds", "value": str(dur)},
                    {"family": "e", "qualifier": "device_type", "value": dev},
                    {"family": "e", "qualifier": "timestamp", "value": datetime.datetime.fromtimestamp(evt_time/1000000, datetime.timezone.utc).isoformat()}
                ]
            })
        else:
            qty = random.randint(1, 3)
            sid = random.choice(store_ids)
            price = round(product_prices[pid] * qty, 2)
            customer_events.append({
                "row_key": f"{cid}#purchase#{reverse_timestamp(evt_time)}",
                "cells": [
                    {"family": "e", "qualifier": "product_id", "value": pid},
                    {"family": "e", "qualifier": "store_id", "value": sid},
                    {"family": "e", "qualifier": "quantity", "value": str(qty)},
                    {"family": "e", "qualifier": "price_paid", "value": str(price)},
                    {"family": "e", "qualifier": "timestamp", "value": datetime.datetime.fromtimestamp(evt_time/1000000, datetime.timezone.utc).isoformat()}
                ]
            })
            
    # Serialize to file
    output_data = {
        "customers": customers,
        "products": products,
        "stores": stores,
        "inventory": inventory,
        "customer_events": customer_events
    }
    
    out_dir = "config/use_cases/retail_marketing/bigtable"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "dummy_data.json")
    print(f"Writing mock data to {out_file}...")
    with open(out_file, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    # Write report
    report_file = os.path.join(out_dir, "generation_report.md")
    print(f"Writing generation report to {report_file}...")
    with open(report_file, 'w') as f:
        f.write(f"""# Bigtable Data Generation Report

* **Generation Date (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
* **Scale Profile**: {profile_name}
* **Base Target Size**: {rows_per_table} rows

## Summary of Generated Rows

* **Table `customers`**: {len(customers):,} rows
* **Table `products`**: {len(products):,} rows
* **Table `stores`**: {len(stores):,} rows
* **Table `inventory`**: {len(inventory):,} rows
* **Table `customer_events`**: {len(customer_events):,} rows (Views & Purchases)

## Configured Test Scenarios

1. **Scenario 1 (Omnichannel Conversion)**:
   * Customer: `{c0}` (VIP/Platinum)
   * Preferred Store: `{s0}`
   * Event flow: Viewed product `{p0}` online, then purchased it in store `{s0}`.
2. **Scenario 2 (Cart Abandonment)**:
   * Customer: `{c0}` (Platinum)
   * Event flow: Spent 240 seconds viewing product `{p1}` (Price: ${product_prices[p1]}). No purchase was recorded.
3. **Scenario 3 (Product Affinity)**:
   * Customer: `{c1}`
   * Event flow: Purchased `{p2}` (Category: `{product_categories[p2]}`) and `{p3}` (Category: `{product_categories[p3]}`).
""")
        
    print("Mock data generation successfully completed.")

if __name__ == "__main__":
    main()
