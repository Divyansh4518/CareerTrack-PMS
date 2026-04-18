import sqlite3

NUM_SHARDS = 3
GLOBAL_DB = 'careertrack.db'

def get_shard_id(user_id):
    """Calculates the hash to find the correct shard."""
    return user_id % NUM_SHARDS

def get_db_connection(user_id=None):
    """
    Routes to the correct shard if user_id is provided.
    Otherwise, defaults to the global database for non-sharded tables.
    """
    if user_id is not None:
        shard_id = get_shard_id(user_id)
        db_name = f'shard_{shard_id}.db'
        conn = sqlite3.connect(db_name)
    else:
        # Connect to the main DB for tables like JobPosting or Company
        conn = sqlite3.connect(GLOBAL_DB)
    
    conn.row_factory = sqlite3.Row
    return conn