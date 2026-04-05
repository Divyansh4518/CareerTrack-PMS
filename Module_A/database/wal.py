import json
import os

class WriteAheadLog:
    def __init__(self, log_file="bptree_wal.log"):
        self.log_file = log_file

    def log_start(self, tx_id):
        self._write({"tx_id": tx_id, "action": "START"})

    def log_operation(self, tx_id, table_name, operation, key, old_value, new_value):
        self._write({
            "tx_id": tx_id,
            "table": table_name,
            "action": operation, # "INSERT", "DELETE", or "UPDATE"
            "key": key,
            "old_value": old_value,
            "new_value": new_value
        })

    def log_commit(self, tx_id):
        self._write({"tx_id": tx_id, "action": "COMMIT"})

    def log_rollback(self, tx_id):
        self._write({"tx_id": tx_id, "action": "ROLLBACK"})

    def _write(self, entry):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno()) 

    def read_log(self):
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r") as f:
            return [json.loads(line) for line in f if line.strip()]