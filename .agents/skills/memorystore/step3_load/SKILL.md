---
name: memorystore_step3_load
description: "Provision connection parameters and bulk load mock datasets into Memorystore using a static Redis pipeline loader."
---


## 1. Core Memorystore Loading Best Practices

Bulk loading data into an in-memory database like Redis is heavily bottlenecked by network Round Trip Time (RTT). To achieve high write throughput, we must bypass individual network round-trips.

### A. Redis Pipelining
* **Never** execute commands (e.g. `hset`, `zadd`) one-by-one in a loop.
* Use **pipelines** to buffer commands in memory and send them to the server in a single batch.

---

## 2. Input Requirements
The agent expects:
1. **Demo Parameters** (`demo_parameters.json`): Providing project, host IP, port, and cluster connection details.
2. **Mock Data** (`dummy_data.json`).

---

## 3. Expected Outputs
The skill must produce:
1. **`run_load.sh`**: A shell script setting up environment pathways and executing `load_data.py`.
2. **`loading_report.md`**: Reporting write throughput (keys/sec) and total load duration.

---

## 4. How to Execute

Run the static loader script from the command line:

```bash
python3 .agents/skills/memorystore/step3_load/scripts/load_data.py
```
