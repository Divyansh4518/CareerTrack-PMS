class TransactionManager:
    def __init__(self, wal):
        self.wal = wal
        self.active_transactions = {} 
        self.next_tx_id = 1

    def begin(self):
        tx_id = self.next_tx_id
        self.next_tx_id += 1
        self.active_transactions[tx_id] = []
        self.wal.log_start(tx_id)
        return tx_id

    def register_operation(self, tx_id, table_name, operation, key, old_value, new_value):
        if tx_id not in self.active_transactions:
            raise Exception(f"Transaction {tx_id} is not active.")
        
        # Log to WAL first (Durability)
        self.wal.log_operation(tx_id, table_name, operation, key, old_value, new_value)
        
        # Add to memory buffer (Atomicity)
        self.active_transactions[tx_id].append({
            "table": table_name,
            "operation": operation,
            "key": key,
            "old_value": old_value
        })

    def commit(self, tx_id):
        if tx_id in self.active_transactions:
            self.wal.log_commit(tx_id)
            del self.active_transactions[tx_id]

    def get_undo_log(self, tx_id):
        if tx_id in self.active_transactions:
            return reversed(self.active_transactions[tx_id])
        return []

    def rollback_complete(self, tx_id):
        if tx_id in self.active_transactions:
            self.wal.log_rollback(tx_id)
            del self.active_transactions[tx_id]