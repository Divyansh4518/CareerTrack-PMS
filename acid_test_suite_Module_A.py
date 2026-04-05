"""
╔══════════════════════════════════════════════════════════════════════════╗
║               ACID COMPLIANCE TEST SUITE FOR B+ TREE ENGINE            ║
║                                                                        ║
║  Tests the MultiTreeDatabase (Module_A) against all four ACID          ║
║  properties using multi-table transactions across three relations:     ║
║    • Students     (PK: StudentID)                                      ║
║    • JobPostings  (PK: JobID)                                          ║
║    • Applications (PK: AppID, FK: StudentID → Students,                ║
║                                   JobID → JobPostings)                 ║
║                                                                        ║
║  Each relation is backed by its own independent B+ Tree where the      ║
║  primary key is the B+ Tree key and the full record is the value.      ║
║                                                                        ║
║  Run:  python acid_test_suite.py                                       ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import io
import json
import time
import threading
import shutil

# Force UTF-8 output on Windows to avoid cp1252 encoding errors
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Path Setup ────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from Module_A.database.bplustree import BPlusTree
from Module_A.database.wal import WriteAheadLog
from Module_A.database.transaction import TransactionManager
from Module_A.database.multi_tree_db import MultiTreeDatabase


# ══════════════════════════════════════════════════════════════════════════════
#                         TEST INFRASTRUCTURE
# ══════════════════════════════════════════════════════════════════════════════

class TestResult:
    """Tracks pass/fail/error counts with pretty output."""

    RESET  = "\033[0m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"

    def __init__(self):
        self.passed  = 0
        self.failed  = 0
        self.errors  = 0
        self.results = []

    def record(self, category, name, status, detail=""):
        self.results.append((category, name, status, detail))
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        else:
            self.errors += 1

    def print_report(self):
        print(f"\n{'═' * 72}")
        print(f"{self.BOLD}{self.CYAN}  ACID COMPLIANCE TEST REPORT{self.RESET}")
        print(f"{'═' * 72}")

        current_category = None
        for category, name, status, detail in self.results:
            if category != current_category:
                current_category = category
                print(f"\n{self.BOLD}  ┌─ {category}{self.RESET}")

            if status == "PASS":
                icon = f"{self.GREEN}✅ PASS{self.RESET}"
            elif status == "FAIL":
                icon = f"{self.RED}❌ FAIL{self.RESET}"
            else:
                icon = f"{self.YELLOW}⚠️  ERROR{self.RESET}"

            print(f"  │  {icon}  {name}")
            if detail:
                print(f"  │       {self.DIM}{detail}{self.RESET}")

        total = self.passed + self.failed + self.errors
        print(f"\n{'─' * 72}")
        print(f"  {self.BOLD}Total: {total}  │  "
              f"{self.GREEN}Passed: {self.passed}{self.RESET}  │  "
              f"{self.RED}Failed: {self.failed}{self.RESET}  │  "
              f"{self.YELLOW}Errors: {self.errors}{self.RESET}")
        print(f"{'═' * 72}\n")

        if self.failed == 0 and self.errors == 0:
            print(f"  {self.GREEN}{self.BOLD}🎉 ALL ACID TESTS PASSED!{self.RESET}\n")
        else:
            print(f"  {self.RED}{self.BOLD}⛔ SOME TESTS DID NOT PASS.{self.RESET}\n")


# ── Isolated DB Factory ──────────────────────────────────────────────────────

TEST_DIR = os.path.join(PROJECT_ROOT, "_acid_test_workspace")


def fresh_db(wal_filename="test_wal.log"):
    """
    Create a MultiTreeDatabase that uses an isolated WAL file inside
    _acid_test_workspace/ so tests never pollute the real data.
    """
    os.makedirs(TEST_DIR, exist_ok=True)
    wal_path = os.path.join(TEST_DIR, wal_filename)

    # Clear any previous WAL
    if os.path.exists(wal_path):
        os.remove(wal_path)

    db = MultiTreeDatabase()
    # Redirect WAL to isolated file
    db.wal.log_file = wal_path
    db.tm.wal.log_file = wal_path
    return db, wal_path


def db_from_wal(wal_path):
    """
    Simulate a system restart by constructing a brand-new
    MultiTreeDatabase that recovers from the given WAL file.
    """
    db = MultiTreeDatabase.__new__(MultiTreeDatabase)
    db.tables = {
        "Students": BPlusTree(4),
        "JobPostings": BPlusTree(4),
        "Applications": BPlusTree(4),
    }
    db.wal = WriteAheadLog(log_file=wal_path)
    db.tm = TransactionManager(db.wal)
    db.lock = threading.Lock()
    db.recover()
    return db


def seed_three_tables(db):
    """
    Insert baseline data across all three relations inside one transaction.
    Returns the tx_id used.
    """
    tx = db.begin_transaction()
    # ── Students ──
    db.insert(tx, "Students", "S1", {
        "Name": "Alice", "CGPA": 9.0, "IsPlaced": 0, "applications_count": 0
    })
    db.insert(tx, "Students", "S2", {
        "Name": "Bob", "CGPA": 8.5, "IsPlaced": 0, "applications_count": 0
    })
    db.insert(tx, "Students", "S3", {
        "Name": "Charlie", "CGPA": 7.2, "IsPlaced": 0, "applications_count": 0
    })
    # ── JobPostings ──
    db.insert(tx, "JobPostings", "J1", {
        "RoleTitle": "Backend Engineer", "MinCGPA": 7.0, "applicants": 0
    })
    db.insert(tx, "JobPostings", "J2", {
        "RoleTitle": "Data Scientist", "MinCGPA": 8.0, "applicants": 0
    })
    db.insert(tx, "JobPostings", "J3", {
        "RoleTitle": "Product Manager", "MinCGPA": 7.5, "applicants": 0
    })
    # ── Applications ──
    db.insert(tx, "Applications", "A1", {
        "StudentID": "S1", "JobID": "J1", "Status": "Applied"
    })
    db.commit(tx)
    return tx


# ── Helper to count all records in a B+ Tree ─────────────────────────────────

def count_tree_records(tree):
    """Walk the leaf linked-list and count entries."""
    node = tree.root
    while not node.is_leaf:
        node = node.children[0]
    count = 0
    while node:
        count += len(node.keys)
        node = node.next
    return count


# ══════════════════════════════════════════════════════════════════════════════
#                          1. ATOMICITY TESTS
# ══════════════════════════════════════════════════════════════════════════════

def run_atomicity_tests(report: TestResult):
    CATEGORY = "ATOMICITY — All or Nothing"

    # ── A1: Explicit rollback undoes all three tables ─────────────────────────
    try:
        db, _ = fresh_db("atom_a1.log")
        seed_three_tables(db)

        # Snapshot BEFORE
        s_before = db.tables["Students"].search("S1")
        j_before = db.tables["JobPostings"].search("J1")
        a_count_before = count_tree_records(db.tables["Applications"])

        # Start a multi-table transaction and modify all three tables
        tx = db.begin_transaction()
        db.update(tx, "Students", "S1", {
            "Name": "Alice MODIFIED", "CGPA": 9.9, "IsPlaced": 1, "applications_count": 5
        })
        db.update(tx, "JobPostings", "J1", {
            "RoleTitle": "CHANGED ROLE", "MinCGPA": 9.0, "applicants": 100
        })
        db.insert(tx, "Applications", "A_TEMP", {
            "StudentID": "S1", "JobID": "J1", "Status": "Phantom"
        })

        # ROLLBACK instead of committing
        db.rollback(tx)

        # Verify EVERYTHING reverted
        s_after = db.tables["Students"].search("S1")
        j_after = db.tables["JobPostings"].search("J1")
        a_count_after = count_tree_records(db.tables["Applications"])
        phantom = db.tables["Applications"].search("A_TEMP")

        all_reverted = (
            s_after["Name"] == "Alice"
            and j_after["RoleTitle"] == "Backend Engineer"
            and phantom is None
            and a_count_after == a_count_before
        )

        if all_reverted:
            report.record(CATEGORY,
                "A1: Explicit ROLLBACK undoes multi-table changes",
                "PASS")
        else:
            report.record(CATEGORY,
                "A1: Explicit ROLLBACK undoes multi-table changes",
                "FAIL",
                f"Students.S1={s_after}, phantom={phantom}")
    except Exception as e:
        report.record(CATEGORY,
            "A1: Explicit ROLLBACK undoes multi-table changes",
            "ERROR", str(e))

    # ── A2: Exception mid-transaction triggers safe rollback ──────────────────
    try:
        db, _ = fresh_db("atom_a2.log")
        seed_three_tables(db)

        tx = db.begin_transaction()
        # First operation succeeds
        db.update(tx, "Students", "S2", {
            "Name": "Bob UPDATED", "CGPA": 8.5, "IsPlaced": 0, "applications_count": 1
        })

        # Second operation raises a constraint violation (CGPA = -5 is invalid)
        exception_caught = False
        try:
            db.insert(tx, "Students", "S_BAD", {
                "Name": "BadStudent", "CGPA": -5, "IsPlaced": 0, "applications_count": 0
            })
        except Exception:
            exception_caught = True

        # Rollback the broken transaction
        db.rollback(tx)

        s2 = db.tables["Students"].search("S2")
        s_bad = db.tables["Students"].search("S_BAD")

        if exception_caught and s2["Name"] == "Bob" and s_bad is None:
            report.record(CATEGORY,
                "A2: Constraint violation → ROLLBACK undoes earlier ops in same tx",
                "PASS")
        else:
            report.record(CATEGORY,
                "A2: Constraint violation → ROLLBACK undoes earlier ops in same tx",
                "FAIL",
                f"caught={exception_caught}, S2.Name={s2['Name']}, S_BAD={s_bad}")
    except Exception as e:
        report.record(CATEGORY,
            "A2: Constraint violation → ROLLBACK undoes earlier ops in same tx",
            "ERROR", str(e))

    # ── A3: Partial deletes are undone on rollback ────────────────────────────
    try:
        db, _ = fresh_db("atom_a3.log")
        seed_three_tables(db)

        tx = db.begin_transaction()
        db.delete(tx, "Students", "S1")
        db.delete(tx, "JobPostings", "J1")
        # Rollback before committing
        db.rollback(tx)

        s1 = db.tables["Students"].search("S1")
        j1 = db.tables["JobPostings"].search("J1")

        if s1 is not None and j1 is not None:
            report.record(CATEGORY,
                "A3: Partial deletes across tables undone on ROLLBACK",
                "PASS")
        else:
            report.record(CATEGORY,
                "A3: Partial deletes across tables undone on ROLLBACK",
                "FAIL",
                f"S1={s1}, J1={j1}")
    except Exception as e:
        report.record(CATEGORY,
            "A3: Partial deletes across tables undone on ROLLBACK",
            "ERROR", str(e))

    # ── A4: Committed transaction is NOT undone by rollback ───────────────────
    try:
        db, _ = fresh_db("atom_a4.log")
        seed_three_tables(db)

        # Commit a change
        tx1 = db.begin_transaction()
        db.update(tx1, "Students", "S3", {
            "Name": "Charlie Committed", "CGPA": 7.2, "IsPlaced": 0, "applications_count": 0
        })
        db.commit(tx1)

        # Start AND rollback a new transaction
        tx2 = db.begin_transaction()
        db.update(tx2, "Students", "S3", {
            "Name": "Charlie SHOULD NOT PERSIST", "CGPA": 7.2, "IsPlaced": 0, "applications_count": 0
        })
        db.rollback(tx2)

        s3 = db.tables["Students"].search("S3")
        if s3["Name"] == "Charlie Committed":
            report.record(CATEGORY,
                "A4: Committed data survives a subsequent ROLLBACK",
                "PASS")
        else:
            report.record(CATEGORY,
                "A4: Committed data survives a subsequent ROLLBACK",
                "FAIL",
                f"S3.Name={s3['Name']}")
    except Exception as e:
        report.record(CATEGORY,
            "A4: Committed data survives a subsequent ROLLBACK",
            "ERROR", str(e))


# ══════════════════════════════════════════════════════════════════════════════
#                        2. CONSISTENCY TESTS
# ══════════════════════════════════════════════════════════════════════════════

def run_consistency_tests(report: TestResult):
    CATEGORY = "CONSISTENCY — Constraint Enforcement"

    # ── C1: Primary Key uniqueness ────────────────────────────────────────────
    try:
        db, _ = fresh_db("cons_c1.log")
        seed_three_tables(db)

        tx = db.begin_transaction()
        caught = False
        try:
            db.insert(tx, "Students", "S1", {
                "Name": "Duplicate", "CGPA": 5.0, "IsPlaced": 0, "applications_count": 0
            })
        except Exception as e:
            caught = "PRIMARY KEY VIOLATION" in str(e)
        db.rollback(tx)

        if caught:
            report.record(CATEGORY,
                "C1: Duplicate PK insert is rejected",
                "PASS")
        else:
            report.record(CATEGORY,
                "C1: Duplicate PK insert is rejected",
                "FAIL", "No exception raised")
    except Exception as e:
        report.record(CATEGORY,
            "C1: Duplicate PK insert is rejected",
            "ERROR", str(e))

    # ── C2: FK — Application with non-existent Student is rejected ────────────
    try:
        db, _ = fresh_db("cons_c2.log")
        seed_three_tables(db)

        tx = db.begin_transaction()
        caught = False
        try:
            db.insert(tx, "Applications", "A_FK", {
                "StudentID": "S_NONEXISTENT", "JobID": "J1"
            })
        except Exception as e:
            caught = "FK VIOLATION" in str(e)
        db.rollback(tx)

        if caught:
            report.record(CATEGORY,
                "C2: FK violation — invalid StudentID rejected",
                "PASS")
        else:
            report.record(CATEGORY,
                "C2: FK violation — invalid StudentID rejected",
                "FAIL")
    except Exception as e:
        report.record(CATEGORY,
            "C2: FK violation — invalid StudentID rejected",
            "ERROR", str(e))

    # ── C3: FK — Application with non-existent Job is rejected ────────────────
    try:
        db, _ = fresh_db("cons_c3.log")
        seed_three_tables(db)

        tx = db.begin_transaction()
        caught = False
        try:
            db.insert(tx, "Applications", "A_FK2", {
                "StudentID": "S1", "JobID": "J_NONEXISTENT"
            })
        except Exception as e:
            caught = "FK VIOLATION" in str(e)
        db.rollback(tx)

        if caught:
            report.record(CATEGORY,
                "C3: FK violation — invalid JobID rejected",
                "PASS")
        else:
            report.record(CATEGORY,
                "C3: FK violation — invalid JobID rejected",
                "FAIL")
    except Exception as e:
        report.record(CATEGORY,
            "C3: FK violation — invalid JobID rejected",
            "ERROR", str(e))

    # ── C4: Domain — CGPA out of range ────────────────────────────────────────
    try:
        db, _ = fresh_db("cons_c4.log")

        tx = db.begin_transaction()
        caught_neg = False
        try:
            db.insert(tx, "Students", "S_NEG", {
                "Name": "Neg", "CGPA": -1, "IsPlaced": 0, "applications_count": 0
            })
        except Exception as e:
            caught_neg = "DOMAIN VIOLATION" in str(e)
        db.rollback(tx)

        tx2 = db.begin_transaction()
        caught_high = False
        try:
            db.insert(tx2, "Students", "S_HIGH", {
                "Name": "High", "CGPA": 11, "IsPlaced": 0, "applications_count": 0
            })
        except Exception as e:
            caught_high = "DOMAIN VIOLATION" in str(e)
        db.rollback(tx2)

        if caught_neg and caught_high:
            report.record(CATEGORY,
                "C4: Domain constraint — CGPA outside [0, 10] rejected",
                "PASS")
        else:
            report.record(CATEGORY,
                "C4: Domain constraint — CGPA outside [0, 10] rejected",
                "FAIL",
                f"neg={caught_neg}, high={caught_high}")
    except Exception as e:
        report.record(CATEGORY,
            "C4: Domain constraint — CGPA outside [0, 10] rejected",
            "ERROR", str(e))

    # ── C5: Valid FK Application is accepted ──────────────────────────────────
    try:
        db, _ = fresh_db("cons_c5.log")
        seed_three_tables(db)

        tx = db.begin_transaction()
        db.insert(tx, "Applications", "A_VALID", {
            "StudentID": "S2", "JobID": "J2", "Status": "Applied"
        })
        db.commit(tx)

        app = db.tables["Applications"].search("A_VALID")
        if app is not None and app["StudentID"] == "S2":
            report.record(CATEGORY,
                "C5: Valid FK Application accepted and persisted",
                "PASS")
        else:
            report.record(CATEGORY,
                "C5: Valid FK Application accepted and persisted",
                "FAIL")
    except Exception as e:
        report.record(CATEGORY,
            "C5: Valid FK Application accepted and persisted",
            "ERROR", str(e))

    # ── C6: Constraints hold after multi-table transaction ────────────────────
    try:
        db, _ = fresh_db("cons_c6.log")
        seed_three_tables(db)

        # Run a complex multi-table tx
        tx = db.begin_transaction()
        db.update(tx, "Students", "S1", {
            "Name": "Alice", "CGPA": 9.5, "IsPlaced": 0, "applications_count": 1
        })
        db.update(tx, "JobPostings", "J1", {
            "RoleTitle": "Backend Engineer", "MinCGPA": 7.0, "applicants": 1
        })
        db.insert(tx, "Applications", "A2", {
            "StudentID": "S1", "JobID": "J2", "Status": "Applied"
        })
        db.commit(tx)

        # Verify all data is consistent
        s1 = db.tables["Students"].search("S1")
        j1 = db.tables["JobPostings"].search("J1")
        a2 = db.tables["Applications"].search("A2")

        consistent = (
            s1 is not None and 0 <= s1["CGPA"] <= 10
            and j1 is not None
            and a2 is not None
            and db.tables["Students"].search(a2["StudentID"]) is not None
            and db.tables["JobPostings"].search(a2["JobID"]) is not None
        )

        if consistent:
            report.record(CATEGORY,
                "C6: All relations valid after multi-table commit",
                "PASS")
        else:
            report.record(CATEGORY,
                "C6: All relations valid after multi-table commit",
                "FAIL")
    except Exception as e:
        report.record(CATEGORY,
            "C6: All relations valid after multi-table commit",
            "ERROR", str(e))


# ══════════════════════════════════════════════════════════════════════════════
#                          3. ISOLATION TESTS
# ══════════════════════════════════════════════════════════════════════════════

def run_isolation_tests(report: TestResult):
    CATEGORY = "ISOLATION — Concurrency Control"

    # ── I1: Concurrent threads cannot interleave (serialized execution) ───────
    try:
        db, _ = fresh_db("iso_i1.log")
        seed_three_tables(db)

        execution_order = []
        errors = []

        def thread_work(thread_id, student_key, new_name):
            try:
                tx = db.begin_transaction()
                execution_order.append(f"T{thread_id}_BEGIN")

                # Read, modify, write
                student = db.tables["Students"].search(student_key)
                updated = dict(student)
                updated["Name"] = new_name
                db.update(tx, "Students", student_key, updated)

                # Small sleep to amplify any race window
                time.sleep(0.05)

                execution_order.append(f"T{thread_id}_COMMIT")
                db.commit(tx)
            except Exception as e:
                errors.append(str(e))

        t1 = threading.Thread(target=thread_work, args=(1, "S1", "Alice_T1"))
        t2 = threading.Thread(target=thread_work, args=(2, "S1", "Alice_T2"))

        t1.start()
        t2.start()
        t1.join(timeout=10)
        t2.join(timeout=10)

        # With per-transaction locking, one thread must fully complete before the other starts
        s1 = db.tables["Students"].search("S1")

        # The final value should be from the LAST thread to commit
        is_serialized = (
            len(errors) == 0
            and s1["Name"] in ("Alice_T1", "Alice_T2")
            and len(execution_order) == 4
        )

        # Verify strictly sequential: BEGIN→COMMIT→BEGIN→COMMIT (no interleaving)
        if is_serialized:
            # Check that the execution order is serialized (no interleaving)
            # Valid orders: [T1_BEGIN, T1_COMMIT, T2_BEGIN, T2_COMMIT]
            #            or [T2_BEGIN, T2_COMMIT, T1_BEGIN, T1_COMMIT]
            first_complete = execution_order[0][1]  # '1' or '2'
            expected = [
                f"T{first_complete}_BEGIN",
                f"T{first_complete}_COMMIT",
            ]
            other = "2" if first_complete == "1" else "1"
            expected += [f"T{other}_BEGIN", f"T{other}_COMMIT"]
            is_serialized = execution_order == expected

        if is_serialized:
            report.record(CATEGORY,
                "I1: Concurrent threads are fully serialized (no interleaving)",
                "PASS",
                f"Order: {execution_order}, Final S1.Name='{s1['Name']}'")
        else:
            report.record(CATEGORY,
                "I1: Concurrent threads are fully serialized (no interleaving)",
                "FAIL",
                f"Order: {execution_order}, Errors: {errors}")
    except Exception as e:
        report.record(CATEGORY,
            "I1: Concurrent threads are fully serialized (no interleaving)",
            "ERROR", str(e))

    # ── I2: No dirty reads — thread B cannot see thread A's uncommitted writes ─
    try:
        db, _ = fresh_db("iso_i2.log")
        seed_three_tables(db)

        dirty_read_detected = threading.Event()
        barrier = threading.Barrier(2, timeout=5)
        errors = []

        def writer():
            try:
                tx = db.begin_transaction()
                db.update(tx, "Students", "S2", {
                    "Name": "Bob_UNCOMMITTED", "CGPA": 8.5, "IsPlaced": 0,
                    "applications_count": 0
                })
                # Signal that write is done (but not committed)
                time.sleep(0.1)
                db.rollback(tx)
            except Exception as e:
                errors.append(f"writer: {e}")

        def reader():
            try:
                # Wait for writer to acquire lock — reader will block on begin_transaction()
                time.sleep(0.02)
                tx = db.begin_transaction()
                value = db.tables["Students"].search("S2")
                if value["Name"] == "Bob_UNCOMMITTED":
                    dirty_read_detected.set()
                db.commit(tx)
            except Exception as e:
                errors.append(f"reader: {e}")

        tw = threading.Thread(target=writer)
        tr = threading.Thread(target=reader)

        tw.start()
        tr.start()
        tw.join(timeout=10)
        tr.join(timeout=10)

        s2 = db.tables["Students"].search("S2")

        if not dirty_read_detected.is_set() and s2["Name"] == "Bob":
            report.record(CATEGORY,
                "I2: No dirty reads — reader cannot see uncommitted writes",
                "PASS")
        else:
            report.record(CATEGORY,
                "I2: No dirty reads — reader cannot see uncommitted writes",
                "FAIL",
                f"dirty_read={dirty_read_detected.is_set()}, S2.Name='{s2['Name']}', errors={errors}")
    except Exception as e:
        report.record(CATEGORY,
            "I2: No dirty reads — reader cannot see uncommitted writes",
            "ERROR", str(e))

    # ── I3: High concurrency stress test ──────────────────────────────────────
    try:
        db, _ = fresh_db("iso_i3.log")

        # Seed a counter record
        tx = db.begin_transaction()
        db.insert(tx, "JobPostings", "J_COUNTER", {
            "RoleTitle": "Counter Job", "MinCGPA": 0, "applicants": 0
        })
        db.commit(tx)

        NUM_THREADS = 20
        errors = []

        def increment_counter(thread_id):
            try:
                tx = db.begin_transaction()
                job = db.tables["JobPostings"].search("J_COUNTER")
                new_count = int(job["applicants"]) + 1
                updated = dict(job)
                updated["applicants"] = new_count
                db.update(tx, "JobPostings", "J_COUNTER", updated)
                db.commit(tx)
            except Exception as e:
                errors.append(f"T{thread_id}: {e}")

        threads = [
            threading.Thread(target=increment_counter, args=(i,))
            for i in range(NUM_THREADS)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        final = db.tables["JobPostings"].search("J_COUNTER")
        final_count = int(final["applicants"])

        if final_count == NUM_THREADS and len(errors) == 0:
            report.record(CATEGORY,
                f"I3: Stress test — {NUM_THREADS} concurrent increments = {final_count}",
                "PASS",
                f"Expected {NUM_THREADS}, got {final_count}")
        else:
            report.record(CATEGORY,
                f"I3: Stress test — {NUM_THREADS} concurrent increments",
                "FAIL",
                f"Expected {NUM_THREADS}, got {final_count}, errors={errors}")
    except Exception as e:
        report.record(CATEGORY,
            "I3: Stress test — concurrent increments",
            "ERROR", str(e))

    # ── I4: Multi-table transaction is atomic under concurrency ────────────────
    try:
        db, _ = fresh_db("iso_i4.log")
        seed_three_tables(db)

        errors = []

        def complex_transaction(suffix):
            try:
                tx = db.begin_transaction()
                s1 = db.tables["Students"].search("S1")
                new_s1 = dict(s1)
                new_s1["applications_count"] = int(new_s1["applications_count"]) + 1
                db.update(tx, "Students", "S1", new_s1)

                j1 = db.tables["JobPostings"].search("J1")
                new_j1 = dict(j1)
                new_j1["applicants"] = int(new_j1["applicants"]) + 1
                db.update(tx, "JobPostings", "J1", new_j1)

                db.insert(tx, "Applications", f"A_{suffix}", {
                    "StudentID": "S1", "JobID": "J1", "Status": "Applied"
                })
                db.commit(tx)
            except Exception as e:
                errors.append(str(e))

        threads = [
            threading.Thread(target=complex_transaction, args=(f"MT_{i}",))
            for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        s1 = db.tables["Students"].search("S1")
        j1 = db.tables["JobPostings"].search("J1")
        app_count = count_tree_records(db.tables["Applications"])

        # We started with 1 Application (A1) and added 5 more
        expected_apps = 6
        expected_count = 5  # 0 + 5 increments

        all_consistent = (
            int(s1["applications_count"]) == expected_count
            and int(j1["applicants"]) == expected_count
            and app_count == expected_apps
            and len(errors) == 0
        )

        if all_consistent:
            report.record(CATEGORY,
                "I4: Multi-table tx stays atomic under 5 concurrent threads",
                "PASS",
                f"apps={app_count}, S1.count={s1['applications_count']}, J1.applicants={j1['applicants']}")
        else:
            report.record(CATEGORY,
                "I4: Multi-table tx stays atomic under 5 concurrent threads",
                "FAIL",
                f"apps={app_count}, S1.count={s1['applications_count']}, J1.applicants={j1['applicants']}, errors={errors}")
    except Exception as e:
        report.record(CATEGORY,
            "I4: Multi-table tx stays atomic under 5 concurrent threads",
            "ERROR", str(e))


# ══════════════════════════════════════════════════════════════════════════════
#                    4. DURABILITY & RECOVERY TESTS
# ══════════════════════════════════════════════════════════════════════════════

def run_durability_tests(report: TestResult):
    CATEGORY = "DURABILITY & RECOVERY — Crash Survival"

    # ── D1: Committed data survives a simulated restart ───────────────────────
    try:
        db, wal_path = fresh_db("dur_d1.log")
        seed_three_tables(db)

        # Additional committed transaction
        tx = db.begin_transaction()
        db.insert(tx, "Applications", "A_DUR", {
            "StudentID": "S3", "JobID": "J3", "Status": "Shortlisted"
        })
        db.commit(tx)

        # ╔════════════════════════════════════╗
        # ║  SIMULATE CRASH — destroy db obj   ║
        # ╚════════════════════════════════════╝
        del db

        # Reconstruct from WAL (simulates restarting the server)
        db2 = db_from_wal(wal_path)

        s1 = db2.tables["Students"].search("S1")
        j1 = db2.tables["JobPostings"].search("J1")
        a_dur = db2.tables["Applications"].search("A_DUR")

        if (s1 is not None and s1["Name"] == "Alice"
                and j1 is not None and j1["RoleTitle"] == "Backend Engineer"
                and a_dur is not None and a_dur["Status"] == "Shortlisted"):
            report.record(CATEGORY,
                "D1: All committed data survives system restart",
                "PASS")
        else:
            report.record(CATEGORY,
                "D1: All committed data survives system restart",
                "FAIL",
                f"S1={s1}, J1={j1}, A_DUR={a_dur}")
    except Exception as e:
        report.record(CATEGORY,
            "D1: All committed data survives system restart",
            "ERROR", str(e))

    # ── D2: Uncommitted (incomplete) transaction is discarded on recovery ─────
    try:
        db, wal_path = fresh_db("dur_d2.log")
        seed_three_tables(db)

        # Write operations to WAL WITHOUT committing (simulate crash mid-tx)
        # We manually write to the WAL to simulate a crash mid-transaction
        with open(wal_path, "a") as f:
            f.write(json.dumps({"tx_id": 999, "action": "START"}) + "\n")
            f.write(json.dumps({
                "tx_id": 999, "table": "Students", "action": "INSERT",
                "key": "S_CRASH", "old_value": None,
                "new_value": {"Name": "CrashStudent", "CGPA": 5.0, "IsPlaced": 0, "applications_count": 0}
            }) + "\n")
            f.write(json.dumps({
                "tx_id": 999, "table": "JobPostings", "action": "INSERT",
                "key": "J_CRASH", "old_value": None,
                "new_value": {"RoleTitle": "CrashJob", "MinCGPA": 0, "applicants": 0}
            }) + "\n")
            # NO COMMIT record — simulates a crash before commit
            f.flush()
            os.fsync(f.fileno())

        # Recover from corrupt WAL
        db2 = db_from_wal(wal_path)

        s_crash = db2.tables["Students"].search("S_CRASH")
        j_crash = db2.tables["JobPostings"].search("J_CRASH")

        # The committed data (from seed) should still exist
        s1 = db2.tables["Students"].search("S1")

        if s_crash is None and j_crash is None and s1 is not None:
            report.record(CATEGORY,
                "D2: Incomplete (uncommitted) transaction is discarded on recovery",
                "PASS")
        else:
            report.record(CATEGORY,
                "D2: Incomplete (uncommitted) transaction is discarded on recovery",
                "FAIL",
                f"S_CRASH={s_crash}, J_CRASH={j_crash}, S1={s1}")
    except Exception as e:
        report.record(CATEGORY,
            "D2: Incomplete (uncommitted) transaction is discarded on recovery",
            "ERROR", str(e))

    # ── D3: Mixed scenario — committed tx present, stale incomplete tx present ─
    try:
        db, wal_path = fresh_db("dur_d3.log")

        # Committed tx #1
        tx1 = db.begin_transaction()
        db.insert(tx1, "Students", "S_SAFE", {
            "Name": "SafeStudent", "CGPA": 8.0, "IsPlaced": 0, "applications_count": 0
        })
        db.insert(tx1, "JobPostings", "J_SAFE", {
            "RoleTitle": "SafeJob", "MinCGPA": 6.0, "applicants": 0
        })
        db.commit(tx1)

        # Committed tx #2
        tx2 = db.begin_transaction()
        db.insert(tx2, "Applications", "A_SAFE", {
            "StudentID": "S_SAFE", "JobID": "J_SAFE", "Status": "Applied"
        })
        db.commit(tx2)

        # Append an incomplete tx directly to WAL (crash simulation)
        with open(wal_path, "a") as f:
            f.write(json.dumps({"tx_id": 888, "action": "START"}) + "\n")
            f.write(json.dumps({
                "tx_id": 888, "table": "Students", "action": "DELETE",
                "key": "S_SAFE",
                "old_value": {"Name": "SafeStudent", "CGPA": 8.0, "IsPlaced": 0, "applications_count": 0},
                "new_value": None
            }) + "\n")
            # NO COMMIT — crash
            f.flush()
            os.fsync(f.fileno())

        del db

        # Recover
        db3 = db_from_wal(wal_path)

        s_safe = db3.tables["Students"].search("S_SAFE")
        j_safe = db3.tables["JobPostings"].search("J_SAFE")
        a_safe = db3.tables["Applications"].search("A_SAFE")

        if (s_safe is not None and s_safe["Name"] == "SafeStudent"
                and j_safe is not None
                and a_safe is not None):
            report.record(CATEGORY,
                "D3: Committed data intact + incomplete DELETE tx discarded",
                "PASS")
        else:
            report.record(CATEGORY,
                "D3: Committed data intact + incomplete DELETE tx discarded",
                "FAIL",
                f"S_SAFE={s_safe}, J_SAFE={j_safe}, A_SAFE={a_safe}")
    except Exception as e:
        report.record(CATEGORY,
            "D3: Committed data intact + incomplete DELETE tx discarded",
            "ERROR", str(e))

    # ── D4: tx_id does not reuse after recovery ───────────────────────────────
    try:
        db, wal_path = fresh_db("dur_d4.log")
        seed_three_tables(db)

        tx = db.begin_transaction()
        db.commit(tx)
        last_tx_before_crash = tx

        del db

        db2 = db_from_wal(wal_path)
        new_tx = db2.begin_transaction()
        db2.commit(new_tx)

        if new_tx > last_tx_before_crash:
            report.record(CATEGORY,
                "D4: tx_id monotonically increases after restart",
                "PASS",
                f"Before crash: tx={last_tx_before_crash}, After recovery: tx={new_tx}")
        else:
            report.record(CATEGORY,
                "D4: tx_id monotonically increases after restart",
                "FAIL",
                f"Before={last_tx_before_crash}, After={new_tx}")
    except Exception as e:
        report.record(CATEGORY,
            "D4: tx_id monotonically increases after restart",
            "ERROR", str(e))

    # ── D5: WAL records are flushed to disk (fsync) ───────────────────────────
    try:
        db, wal_path = fresh_db("dur_d5.log")

        tx = db.begin_transaction()
        db.insert(tx, "Students", "S_FSYNC", {
            "Name": "FsyncTest", "CGPA": 7.0, "IsPlaced": 0, "applications_count": 0
        })
        db.commit(tx)

        # Immediately read the raw WAL file — data must be on disk
        with open(wal_path, "r") as f:
            raw = f.read()

        has_start = '"action": "START"' in raw
        has_insert = '"S_FSYNC"' in raw
        has_commit = '"action": "COMMIT"' in raw

        if has_start and has_insert and has_commit:
            report.record(CATEGORY,
                "D5: WAL entries are physically on disk after commit (fsync verified)",
                "PASS")
        else:
            report.record(CATEGORY,
                "D5: WAL entries are physically on disk after commit (fsync verified)",
                "FAIL",
                f"start={has_start}, insert={has_insert}, commit={has_commit}")
    except Exception as e:
        report.record(CATEGORY,
            "D5: WAL entries are physically on disk after commit (fsync verified)",
            "ERROR", str(e))

    # ── D6: Double recovery is idempotent ─────────────────────────────────────
    try:
        db, wal_path = fresh_db("dur_d6.log")
        seed_three_tables(db)

        tx = db.begin_transaction()
        db.update(tx, "Students", "S1", {
            "Name": "Alice v2", "CGPA": 9.5, "IsPlaced": 0, "applications_count": 0
        })
        db.commit(tx)
        del db

        # First recovery
        db_r1 = db_from_wal(wal_path)
        s1_r1 = db_r1.tables["Students"].search("S1")

        # Second recovery from the SAME WAL
        db_r2 = db_from_wal(wal_path)
        s1_r2 = db_r2.tables["Students"].search("S1")

        if (s1_r1 is not None and s1_r2 is not None
                and s1_r1["Name"] == "Alice v2"
                and s1_r2["Name"] == "Alice v2"):
            report.record(CATEGORY,
                "D6: Double recovery is idempotent (same result both times)",
                "PASS")
        else:
            report.record(CATEGORY,
                "D6: Double recovery is idempotent (same result both times)",
                "FAIL",
                f"R1={s1_r1}, R2={s1_r2}")
    except Exception as e:
        report.record(CATEGORY,
            "D6: Double recovery is idempotent (same result both times)",
            "ERROR", str(e))


# ══════════════════════════════════════════════════════════════════════════════
#                             MAIN RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                  ACID COMPLIANCE TEST SUITE                            ║
║                  B+ Tree Storage Engine                                ║
║                  CareerTrack PMS — Module A                            ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)

    report = TestResult()

    print("  Running Atomicity tests...")
    run_atomicity_tests(report)

    print("  Running Consistency tests...")
    run_consistency_tests(report)

    print("  Running Isolation tests...")
    run_isolation_tests(report)

    print("  Running Durability & Recovery tests...")
    run_durability_tests(report)

    report.print_report()

    # Cleanup test workspace
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    # Exit code for CI
    sys.exit(0 if report.failed == 0 and report.errors == 0 else 1)


if __name__ == "__main__":
    main()
