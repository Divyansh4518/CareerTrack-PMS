import threading
from .wal import WriteAheadLog
from .transaction import TransactionManager
from .bplustree import BPlusTree # From Assignment 2

class MultiTreeDatabase:
    def __init__(self):
        # The 3 Required Relations
        self.tables = {
            "Students": BPlusTree(4),
            "JobPostings": BPlusTree(4),
            "Applications": BPlusTree(4)
        }
        self.wal = WriteAheadLog()
        self.tm = TransactionManager(self.wal)
        self.lock = threading.Lock() # Global lock for isolation (held per-transaction)
        self.recover()

    def begin_transaction(self):
        """Begin a new transaction. Acquires the global lock for the full transaction lifetime."""
        self.lock.acquire()
        try:
            return self.tm.begin()
        except Exception:
            self.lock.release()
            raise

    def insert(self, tx_id, table_name, key, value):
        """Insert a record into a table within the current transaction.
        
        Validates:
         - Primary key uniqueness (rejects duplicates; use update() for existing keys)
         - Foreign key integrity for Applications (StudentID & JobID must exist)
         - Domain constraints (e.g. CGPA must be 0-10)
        """
        tree = self.tables[table_name]

        # ---- Consistency: Primary Key uniqueness ----
        existing = tree.search(key)
        if existing is not None:
            raise Exception(
                f"PRIMARY KEY VIOLATION: Key '{key}' already exists in '{table_name}'. "
                f"Use update() to modify existing records."
            )

        # ---- Consistency: Foreign Key checks for Applications ----
        if table_name == "Applications":
            student_id = value.get("StudentID")
            job_id = value.get("JobID")
            if student_id is not None and self.tables["Students"].search(student_id) is None:
                raise Exception(
                    f"FK VIOLATION: StudentID '{student_id}' does not exist in Students."
                )
            if job_id is not None and self.tables["JobPostings"].search(job_id) is None:
                raise Exception(
                    f"FK VIOLATION: JobID '{job_id}' does not exist in JobPostings."
                )

        # ---- Consistency: Domain constraints ----
        if table_name == "Students":
            cgpa = value.get("CGPA")
            if cgpa is not None and not (0 <= cgpa <= 10):
                raise Exception(
                    f"DOMAIN VIOLATION: CGPA must be between 0 and 10, got {cgpa}."
                )

        old_value = None  # Guaranteed None since we checked uniqueness above
        self.tm.register_operation(tx_id, table_name, "INSERT", key, old_value, value)
        tree.insert(key, value) # The value is the full record dictionary

    def update(self, tx_id, table_name, key, value):
        """Update an existing record in a table within the current transaction.
        
        Raises an exception if the key does not exist.
        """
        tree = self.tables[table_name]
        old_value = tree.search(key)
        if old_value is None:
            raise Exception(
                f"UPDATE FAILED: Key '{key}' does not exist in '{table_name}'."
            )

        # ---- Consistency: Domain constraints ----
        if table_name == "Students":
            cgpa = value.get("CGPA")
            if cgpa is not None and not (0 <= cgpa <= 10):
                raise Exception(
                    f"DOMAIN VIOLATION: CGPA must be between 0 and 10, got {cgpa}."
                )

        self.tm.register_operation(tx_id, table_name, "UPDATE", key, old_value, value)
        tree.insert(key, value)  # BPlusTree.insert() now upserts

    def delete(self, tx_id, table_name, key):
        tree = self.tables[table_name]
        old_value = tree.search(key)
        if old_value is not None:
            self.tm.register_operation(tx_id, table_name, "DELETE", key, old_value, None)
            tree.delete(key)

    def commit(self, tx_id):
        """Commit the transaction and release the global lock."""
        try:
            self.tm.commit(tx_id)
        finally:
            self.lock.release()

    def rollback(self, tx_id):
        """Rollback the transaction, undo all changes, and release the global lock."""
        try:
            undo_ops = self.tm.get_undo_log(tx_id)
            for op in undo_ops:
                tree = self.tables[op["table"]]
                if op["operation"] == "INSERT":
                    if op["old_value"] is None:
                        tree.delete(op["key"]) 
                    else:
                        tree.insert(op["key"], op["old_value"]) 
                elif op["operation"] == "DELETE":
                    tree.insert(op["key"], op["old_value"])
                elif op["operation"] == "UPDATE":
                    tree.insert(op["key"], op["old_value"])
            self.tm.rollback_complete(tx_id)
        finally:
            self.lock.release()

    def recover(self):
        """
        Crash recovery from WAL.
        Rebuild in-memory trees by replaying operations from committed transactions only.
        """
        # Recovery runs at init before any external access, no lock needed here.
        logs = self.wal.read_log()
        if not logs:
            return

        # Rebuild tables from scratch using only committed WAL entries.
        self.tables = {
            "Students": BPlusTree(4),
            "JobPostings": BPlusTree(4),
            "Applications": BPlusTree(4)
        }

        committed_tx_ids = set()
        rolled_back_tx_ids = set()
        max_tx_id = 0

        for entry in logs:
            tx_id = entry.get("tx_id")
            if isinstance(tx_id, int):
                max_tx_id = max(max_tx_id, tx_id)

            action = entry.get("action")
            if action == "COMMIT" and tx_id is not None:
                committed_tx_ids.add(tx_id)
            elif action == "ROLLBACK" and tx_id is not None:
                rolled_back_tx_ids.add(tx_id)

        replayable_tx_ids = committed_tx_ids - rolled_back_tx_ids

        for entry in logs:
            tx_id = entry.get("tx_id")
            if tx_id not in replayable_tx_ids:
                continue

            action = entry.get("action")
            if action not in {"INSERT", "DELETE", "UPDATE"}:
                continue

            table_name = entry.get("table")
            if table_name not in self.tables:
                continue

            key = entry.get("key")
            old_value = entry.get("old_value")
            new_value = entry.get("new_value")
            tree = self.tables[table_name]

            if action in {"INSERT", "UPDATE"}:
                tree.insert(key, new_value)
            elif action == "DELETE":
                if old_value is not None:
                    tree.delete(key)

        # Avoid tx_id reuse after a restart.
        self.tm.next_tx_id = max_tx_id + 1