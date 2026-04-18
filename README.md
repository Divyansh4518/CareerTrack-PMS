# 🎓 CareerTrack - Placement Management System 

A robust, database-driven software solution designed to automate and manage the college placement process efficiently. Developed as part of the Database Management Systems (CS 432) course at **IIT Gandhinagar**.

---

## 📌 Project Overview
Many institutions handle placement activities manually, leading to data duplication, delayed communication, and inconsistent records. CareerTrack provides a centralized, automated platform to manage student details, track company job postings, and seamlessly process job applications from end to end.

## 🛠️ Project Structure & Architecture

```text
CareerTrack-PMS/
│
├── Module_A/                 # Storage Engine Implementation
│   ├── database/
│   │   ├── bplustree.py      # Core B+ Tree data structure & engine
│   │   ├── multi_tree_db.py  # Multi-relation DB manager (Assignment 3)
│   │   ├── transaction.py    # ACID Transaction Manager
│   │   └── wal.py            # Write-Ahead Logging for Crash Recovery
│   └── acid_tester.py        # ACID Compliance test suite
│
├── Module_B/                 # Secure Web Application & Sharding
│   ├── app.py                # Main Flask application entry point
│   ├── db_router.py          # Hash-based query router (Assignment 4)
│   ├── migrate_shards.py     # Script to partition data into 3 nodes
│   ├── test_router.py        # Scatter-gather sharding test suite
│   ├── sql/                  # core_tables.sql, indexes.sql
│   └── templates/            # HTML/CSS UI rendering files
│
├── Report/                   # Final Submission Assets & PDFs
├── Diagrams/                 # ER Diagrams
└── README.md                 # Project documentation
```

---

## 🚀 Assignment 4: Database Sharding & Horizontal Scaling
*Final Capstone Phase*

To handle massive datasets, the CareerTrack database was transitioned from a monolithic architecture to a horizontally scaled distributed system. 
* **Hash-Based Partitioning:** Migrated user and application data across 3 simulated nodes (`shard_0.db`, `shard_1.db`, `shard_2.db`) using the modulo hash of the `UserID`.
* **Query Routing:** Built a dynamic API router (`db_router.py`) to instantly route single-lookup queries to the correct node in $O(1)$ time.
* **Scatter-Gather Execution:** Implemented cross-shard range queries that query all nodes concurrently and merge the results in memory.
* **Scalability Analysis:** Analyzed CAP Theorem trade-offs, demonstrating improved system Availability and Partition Tolerance.

---

## 🔒 Assignment 3: ACID Transactions & Crash Recovery
We upgraded the custom B+ Tree storage engine to act as a fully ACID-compliant database:
* **Atomicity & Isolation:** Implemented `BEGIN`, `COMMIT`, and `ROLLBACK` semantics with a global threading lock to prevent dirty reads.
* **Durability (WAL):** Engineered a Write-Ahead Log (`bptree_wal.log`) that persists operations to disk *before* modifying the in-memory tree.
* **Crash Recovery:** Built a recovery sequence that replays committed transactions from the WAL to rebuild the exact database state after a simulated system failure.
* **Stress Testing:** Executed multi-threaded race-condition testing to verify isolation under heavy load.

---

## 🌐 Assignment 2: Web API & Storage Mechanics
We brought the CareerTrack system to life using a modern backend architecture:
* **B+ Tree Storage Engine:** Developed a pure Python simulation of a B+ Tree, mathematically proving $O(\log N)$ time complexity for search, insert, and delete operations.
* **Flask Web Application:** Built a RESTful Web API using Python and migrated the initial schema to SQLite.
* **Role-Based Access Control (RBAC):** Implemented secure session handling, restricting specific endpoints based on user roles (Admin, Placement Officer, Student).
* **Audit Logging:** Engineered an `audit.py` interceptor that strictly logs all system access attempts.

---

## 📁 Assignment 1: Database Design & Normalization
* **Schema:** Contains 12 normalized tables (1NF, 2NF, 3NF) eliminating redundancy.
* **Entity Relationships:** Modeled using strict Silberschatz/Chen ER notation, correctly handling 1:1, 1:M, and M:N cardinalities.
* **Data Integrity:** Enforced via Primary Keys, Foreign Keys, Unique constraints, and cascaded updates/deletions.

---

## 👨‍💻 Team Big Data (Contributions)
* **Pramith Joy (23110152):** Core B+ Tree storage engine, algorithmic complexity analysis, transaction management (Module A).
* **Bhavitha Somireddy (24110350):** Flask backend architecture, REST API routing, failure handling logic.
* **Killada Eswara Valli (24110165):** Frontend UI integration, HTML templates, stress testing simulation.
* **Garv Singhal (24110119):** Security framework design (RBAC), audit logging, and documentation formatting.
* **Divyansh Saini (23110101):** SQLite database migration, schema modularization, query indexing, and shard deployment.

*Developed for Semester II (2025-2026).*