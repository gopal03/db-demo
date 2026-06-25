import json
import argparse
import os
import sys
import datetime
import random
import uuid

def load_params(params_path):
    with open(params_path, 'r') as f:
        return json.load(f)

def load_usecase(params):
    use_case_config = params.get('demo_context', {}).get('use_case_config')
    if not use_case_config or not os.path.exists(use_case_config):
        print(f"Error: Use case config '{use_case_config}' not found.")
        sys.exit(1)
    with open(use_case_config, 'r') as f:
        return json.load(f)

def get_data_counts(params):
    """Resolve the active data profile counts from parameters."""
    data_config = params.get('data_config', {})
    profile_name = data_config.get('profile', 'small')
    profiles = data_config.get('profiles', {})
    profile = profiles.get(profile_name, profiles.get('small', {}))
    print(f"Data Profile  : {profile_name} — {profile.get('description', '')}")
    return profile

def rand_str(prefix, n):
    return f"{prefix}-{str(n).zfill(7)}"

def generate_mock_data(counts):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    n_accounts = counts.get('accounts', 500)
    n_roles = counts.get('roles', 100)
    n_resources = counts.get('resources', 500)
    n_aar = counts.get('account_assumes_role', 2000)
    n_rhp = counts.get('role_has_permission', 5000)
    n_rnf = counts.get('resource_network_flow', 10000)

    account_types = ["IAM User", "Service Account", "Group", "Workload Identity"]
    role_scopes = ["Production-Infra", "Dev-Infra", "Data-Silo", "Network-Admin", "Billing"]
    resource_types = ["VM", "Kubernetes Pod", "Database", "GCS Bucket", "Pub/Sub Topic"]
    protocols = ["TCP", "UDP", "HTTPS"]
    permission_levels = ["Owner", "Editor", "Reader", "Admin"]

    print(f"Generating {n_accounts:,} Accounts...")
    accounts = [
        {"account_id": rand_str("acc", i), "name": f"user-{i}@corp.example.com", "type": random.choice(account_types)}
        for i in range(n_accounts)
    ]
    # Ensure the compromised account exists for queries
    accounts[0] = {"account_id": "acc-0000000", "name": "compromised-ops-user", "type": "IAM User"}

    print(f"Generating {n_roles:,} Roles...")
    roles = [
        {"role_id": rand_str("role", i), "name": f"Role-{i}", "scope": random.choice(role_scopes)}
        for i in range(n_roles)
    ]

    print(f"Generating {n_resources:,} Resources...")
    resources = [
        {"resource_id": rand_str("res", i), "name": f"resource-{i}", "type": random.choice(resource_types)}
        for i in range(n_resources)
    ]
    # Ensure specific resources exist for queries
    resources[0] = {"resource_id": "res-0000000", "name": "public-web-server", "type": "VM"}
    resources[1] = {"resource_id": "res-0000001", "name": "customer-db-prod", "type": "Database"}

    print(f"Generating {n_aar:,} AccountAssumesRole edges...")
    account_ids = [a["account_id"] for a in accounts]
    role_ids = [r["role_id"] for r in roles]
    resource_ids = [r["resource_id"] for r in resources]

    seen_aar = set()
    account_assumes_role = []
    # Seed known path: compromised-ops-user -> Role-0
    account_assumes_role.append({"account_id": "acc-0000000", "role_id": "role-0000000", "assumed_at": now})
    seen_aar.add(("acc-0000000", "role-0000000"))
    while len(account_assumes_role) < n_aar:
        acc = random.choice(account_ids)
        rol = random.choice(role_ids)
        if (acc, rol) not in seen_aar:
            seen_aar.add((acc, rol))
            account_assumes_role.append({"account_id": acc, "role_id": rol, "assumed_at": now})

    print(f"Generating {n_rhp:,} RoleHasPermission edges...")
    seen_rhp = set()
    role_has_permission = []
    # Seed known path: Role-0 -> public-web-server (Owner)
    role_has_permission.append({"role_id": "role-0000000", "resource_id": "res-0000000", "permission_level": "Owner"})
    seen_rhp.add(("role-0000000", "res-0000000"))
    while len(role_has_permission) < n_rhp:
        rol = random.choice(role_ids)
        res = random.choice(resource_ids)
        if (rol, res) not in seen_rhp:
            seen_rhp.add((rol, res))
            role_has_permission.append({"role_id": rol, "resource_id": res, "permission_level": random.choice(permission_levels)})

    print(f"Generating {n_rnf:,} ResourceNetworkFlow edges...")
    seen_rnf = set()
    resource_network_flow = []
    # Seed known path: public-web-server -> customer-db-prod
    resource_network_flow.append({"source_resource_id": "res-0000000", "dest_resource_id": "res-0000001", "port": 5432, "protocol": "TCP"})
    seen_rnf.add(("res-0000000", "res-0000001", 5432))
    while len(resource_network_flow) < n_rnf:
        src = random.choice(resource_ids)
        dst = random.choice(resource_ids)
        if src == dst:
            continue
        port = random.choice([22, 80, 443, 3306, 5432, 6379, 8080, 8443])
        if (src, dst, port) not in seen_rnf:
            seen_rnf.add((src, dst, port))
            resource_network_flow.append({"source_resource_id": src, "dest_resource_id": dst, "port": port, "protocol": random.choice(protocols)})

    return {
        "Accounts": accounts,
        "Roles": roles,
        "Resources": resources,
        "AccountAssumesRole": account_assumes_role,
        "RoleHasPermission": role_has_permission,
        "ResourceNetworkFlow": resource_network_flow
    }

def main():
    parser = argparse.ArgumentParser(description="Generate realistic mock graph data using profile from parameters.")
    parser.add_argument('--parameters', default='config/spanner_parameters.json', help='Path to spanner parameters JSON')
    parser.add_argument('--output', default='config/dummy_data.json', help='Path to output data JSON')
    args = parser.parse_args()

    params = load_params(args.parameters)
    demo_ctx = params.get('demo_context', {})
    print(f"Customer : {demo_ctx.get('customer_name', 'N/A')} | Industry: {demo_ctx.get('industry', 'N/A')}")
    print(f"Use Case : {demo_ctx.get('use_case', 'N/A')}\n")

    counts = get_data_counts(params)

    print("\nGenerating simulated security graph data...")
    data = generate_mock_data(counts)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    print(f"\nWriting data to {args.output} ...")
    with open(args.output, 'w') as f:
        json.dump(data, f)

    print("\nData generation complete:")
    for table, records in data.items():
        print(f"  - {table}: {len(records):,} records")

if __name__ == "__main__":
    main()
