# Bully Election Algorithm – Simulation in Python

This project simulates the **Bully Algorithm** for leader election in a distributed asynchronous system using Python threads.

## 📌 Description

Each node is implemented as a thread. Nodes can:
- Detect missing leaders
- Initiate elections
- Respond to other nodes
- Elect the highest active ID as the leader

The simulation includes:
- Asynchronous behavior with random delays
- Failure of specific nodes (via `DISABLED_NODES`)
- COORDINATOR messages from the elected leader
- Message count and election time metrics

## ⚙️ How to Run

```bash
python bully_simulation.py
