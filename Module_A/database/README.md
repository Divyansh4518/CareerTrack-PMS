# Module A: ACID-Compliant B+ Tree Storage Engine

> **Course:** Database Management Systems — IIT Gandhinagar  
> **Assignment:** 3 — Transaction Management & Recovery  
> **Project:** CareerTrack Placement Management System  

---

## Team Members

| Name | Roll No. | Contribution Area |
|------|----------|-------------------|
| Pramith Joy | 23110152 | B+ Tree storage engine (upsert logic, leaf-level updates), WAL-based crash recovery |
| Divyansh Saini | 23110101 | Write-Ahead Logging (WAL), transaction lifecycle management, WAL compaction design |
| Bhavitha Somireddy | 24110350 | Multi-table database architecture, transaction command integration (BEGIN/COMMIT/ROLLBACK) |
| Garv Singhal | 24110119 | Constraint validation engine (PK, FK, domain checks), consistency enforcement |
| Killada Eswara Valli | 24110165 | Concurrency control (isolation/locking strategy), ACID compliance test suite |

---

## Overview

This module implements a **custom, ACID-compliant database engine** where every relation is backed exclusively by an in-memory **B+ Tree** data structure. Unlike conventional database assignments that rely on SQLite or external engines for storage, our system uses B+ Trees as the **sole source of truth** — there are no shadow arrays, dictionaries, or external stores holding authoritative data.

The engine supports full transaction semantics (`BEGIN`, `COMMIT`, `ROLLBACK`) across **three independent relations**, with Write-Ahead Logging for crash recovery and a global locking mechanism for isolation.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                  MultiTreeDatabase                   │
│                                                      │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Students │  │ JobPostings  │  │ Applications │   │
│  │ (B+Tree) │  │  (B+Tree)   │  │  (B+Tree)    │   │
│  └──────────┘  └──────────────┘  └──────────────┘   │
│         │              │                │            │
│         └──────────────┴────────────────┘            │
│                        │                             │
│              TransactionManager                      │
│                   │         │                        │
│           Undo Buffer    WAL (disk)                  │
│                                                      │
│           threading.Lock (per-transaction)            │
└──────────────────────────────────────────────────────┘
```

### File Structure

| File | Purpose |
|------|---------|
| `bplustree.py` | Core B+ Tree implementation with search, insert (upsert), delete, range query, and visualization |
| `multi_tree_db.py` | Multi-relation database engine — houses all three B+ Trees, enforces ACID properties |
| `transaction.py` | Transaction lifecycle manager — tracks active transactions and their undo buffers |
| `wal.py` | Write-Ahead Log — durable, append-only log with `fsync` guarantees |
| `bruteforce.py` | Linear scan baseline used for performance benchmarking (not part of the ACID engine) |

---

## Storage Design

### Three Independent Relations

Each relation is stored in its own `BPlusTree(order=4)` instance, initialized in `MultiTreeDatabase.__init__()`:

```python
self.tables = {
    "Students":     BPlusTree(4),   # PK: StudentID
    "JobPostings":  BPlusTree(4),   # PK: JobID
    "Applications": BPlusTree(4),   # PK: AppID
}
```

### B+ Tree Key-Value Mapping

- **Key** = Primary key of the record (e.g., `"S1"`, `"J2"`, `"APP_S1_J2"`)
- **Value** = Complete record stored as a Python dictionary

Example leaf entry:
```
Key: "S1" → Value: {"Name": "Alice", "CGPA": 9.0, "IsPlaced": 0, "applications_count": 0}
```

No data is stored outside these B+ Trees. The `TransactionManager.active_transactions` dictionary is purely transient bookkeeping (undo buffers for in-flight transactions) and is discarded on shutdown.

### Upsert Behavior

The B+ Tree's `insert()` method implements **upsert** semantics:

1. Before inserting, it calls `_update_leaf()` to walk to the target leaf node.
2. If the key already exists, the value is **overwritten in-place** — no duplicate entries are created.
3. If the key is new, standard B+ Tree insertion (with node splitting) proceeds.

This prevents the critical bug where duplicate keys would silently accumulate, particularly during WAL recovery replays where the same key may be re-inserted multiple times.

---

## Transaction Commands

All three commands operate across multiple relations within a single transaction:

### `BEGIN` → `begin_transaction()`
- Allocates a new monotonically increasing `tx_id`
- Acquires the **global lock** for the entire transaction lifetime
- Logs `START` to the WAL
- Returns the `tx_id` to the caller

### `COMMIT` → `commit(tx_id)`
- Writes a `COMMIT` record to the WAL (flushed with `fsync`)
- Clears the in-memory undo buffer for this transaction
- **Releases the global lock**

### `ROLLBACK` → `rollback(tx_id)`
- Iterates the undo buffer **in reverse order**
- Physically undoes each operation in the B+ Trees:
  - `INSERT` → deletes the inserted key (or restores the previous value)
  - `DELETE` → re-inserts the deleted record
  - `UPDATE` → restores the old value
- Writes a `ROLLBACK` record to the WAL
- **Releases the global lock**

---

## ACID Properties

### Atomicity

Every mutation (`insert`, `update`, `delete`) within a transaction is recorded in an in-memory undo buffer **before** the B+ Tree is modified. If anything fails mid-transaction, `rollback()` walks this buffer in reverse and physically undoes every operation. The WAL ensures that even in the case of a process crash, the recovery routine will simply **skip replaying** any transaction that lacks a `COMMIT` record.

**Key guarantee:** If a multi-table transaction modifies Students, JobPostings, and Applications, either all three changes persist or none do.

### Consistency

The `insert()` method enforces three layers of validation **before** any data reaches the B+ Tree:

| Constraint | Scope | Behavior |
|------------|-------|----------|
| **Primary Key Uniqueness** | All tables | Rejects `insert()` if the key already exists; callers must use `update()` for modifications |
| **Foreign Key Integrity** | Applications table | Validates that `StudentID` exists in the Students B+ Tree and `JobID` exists in the JobPostings B+ Tree |
| **Domain Constraints** | Students table | Rejects CGPA values outside the `[0, 10]` range |

If any constraint is violated, an exception is raised, and the caller is expected to `rollback()` the transaction. No partial state is left in the trees because the constraint check runs **before** the actual B+ Tree mutation.

### Isolation

Concurrency control is achieved through a **global `threading.Lock`** that enforces strict serialization:

- `begin_transaction()` → **acquires** the lock
- `commit()` / `rollback()` → **releases** the lock (in a `finally` block to guarantee release even on errors)
- All intermediate operations (`insert`, `update`, `delete`) run **without re-acquiring** the lock since it is already held

This provides **Serializable** isolation — the strongest level. No two transactions can interleave; each runs in complete isolation. This eliminates:
- Dirty reads (reading uncommitted data)
- Non-repeatable reads
- Phantom reads
- Lost updates

### Durability

Durability is achieved through Write-Ahead Logging:

1. **WAL-first protocol:** Every operation is written to `bptree_wal.log` **before** the in-memory B+ Tree is modified. The WAL uses `f.flush()` + `os.fsync()` to guarantee the entry reaches physical disk.

2. **Recovery on startup:** `MultiTreeDatabase.__init__()` calls `recover()` which:
   - Reads the entire WAL
   - Identifies which transactions have `COMMIT` records
   - Rebuilds all three B+ Trees from scratch by replaying **only committed** operations
   - Sets `next_tx_id` to avoid ID reuse

3. **Incomplete transactions are discarded:** Any transaction with a `START` but no `COMMIT` (indicating a crash mid-transaction) is simply never replayed.

---

## Crash Recovery Protocol

```
recover():
    1. Read all WAL entries from disk
    2. Scan for COMMIT and ROLLBACK markers
    3. committed_ids = {tx_ids with COMMIT} - {tx_ids with ROLLBACK}
    4. Re-initialize all three B+ Trees as empty
    5. Replay only operations from committed transactions
    6. Set next_tx_id = max(all seen tx_ids) + 1
```

This is a **redo-only** recovery strategy. Since B+ Trees are purely in-memory, the WAL is the sole durable artifact. On restart, the entire database state is reconstructed from the WAL.

---

## ACID Compliance Test Suite

A comprehensive test suite (`acid_test_suite_Module_A.py`) validates all four ACID properties with **20 test cases** across multi-table transactions.

### Test Summary

| Category | Tests | What is Verified |
|----------|-------|-----------------|
| **Atomicity** (4 tests) | A1–A4 | Explicit rollback undoes multi-table changes; constraint violation mid-tx rolls back earlier ops; partial deletes undone; committed state survives subsequent rollback |
| **Consistency** (6 tests) | C1–C6 | PK uniqueness rejected; FK violation for invalid StudentID/JobID rejected; CGPA domain enforcement; valid FK accepted; all relations valid post-commit |
| **Isolation** (4 tests) | I1–I4 | Concurrent threads fully serialized (no interleaving); no dirty reads; 20-thread stress test (counter integrity); multi-table atomicity under 5 concurrent threads |
| **Durability** (6 tests) | D1–D6 | Committed data survives restart; uncommitted tx discarded; mixed recovery scenario; tx_id monotonic after restart; fsync verification; double recovery idempotent |

### Key Test Techniques

- **Isolated WAL files:** Each test uses its own temporary WAL file, preventing cross-contamination.
- **Crash simulation:** Durability tests inject raw WAL entries (START + operations, **no COMMIT**) directly into the log file, then instantiate a fresh `MultiTreeDatabase` to verify recovery correctly discards the incomplete transaction.
- **Thread contention:** Isolation tests spawn multiple `threading.Thread` instances that compete for the same keys, verifying that the global lock serializes execution and prevents data corruption.
- **Idempotency:** The D6 test recovers from the same WAL twice and asserts identical results both times.

### Running the Tests

```bash
python acid_test_suite_Module_A.py
```

Expected output:
```
ACID COMPLIANCE TEST REPORT

  ATOMICITY — All or Nothing
    PASS  A1: Explicit ROLLBACK undoes multi-table changes
    PASS  A2: Constraint violation → ROLLBACK undoes earlier ops in same tx
    PASS  A3: Partial deletes across tables undone on ROLLBACK
    PASS  A4: Committed data survives a subsequent ROLLBACK

  CONSISTENCY — Constraint Enforcement
    PASS  C1: Duplicate PK insert is rejected
    PASS  C2: FK violation — invalid StudentID rejected
    PASS  C3: FK violation — invalid JobID rejected
    PASS  C4: Domain constraint — CGPA outside [0, 10] rejected
    PASS  C5: Valid FK Application accepted and persisted
    PASS  C6: All relations valid after multi-table commit

  ISOLATION — Concurrency Control
    PASS  I1: Concurrent threads are fully serialized (no interleaving)
    PASS  I2: No dirty reads — reader cannot see uncommitted writes
    PASS  I3: Stress test — 20 concurrent increments = 20
    PASS  I4: Multi-table tx stays atomic under 5 concurrent threads

  DURABILITY & RECOVERY — Crash Survival
    PASS  D1: All committed data survives system restart
    PASS  D2: Incomplete (uncommitted) transaction is discarded on recovery
    PASS  D3: Committed data intact + incomplete DELETE tx discarded
    PASS  D4: tx_id monotonically increases after restart
    PASS  D5: WAL entries are physically on disk after commit (fsync verified)
    PASS  D6: Double recovery is idempotent (same result both times)

  Total: 20  |  Passed: 20  |  Failed: 0  |  Errors: 0

  ALL ACID TESTS PASSED!
```

---

## Dependencies

- **Python 3.10+**
- **No external packages required** — all ACID functionality is implemented using only the Python standard library (`threading`, `json`, `os`)
- `graphviz` (optional) — only needed for `visualize_tree()` in `bplustree.py`

---

## References

- A. Silberschatz, H. F. Korth, and S. Sudarshan, *Database System Concepts*, 7th Edition — Chapters 14 (Indexing), 15 (Transactions), 16 (Concurrency Control), 17 (Recovery System)
- R. Ramakrishnan and J. Gehrke, *Database Management Systems*, 3rd Edition — B+ Tree structure and WAL protocol
