import sqlite3
from db_router import get_shard_id, get_db_connection

def test_single_lookup(user_id):
    print(f"\n[SINGLE LOOKUP] Searching for UserID: {user_id}")
    shard_id = get_shard_id(user_id)
    print(f"ROUTING: Hash calculated. Directing query to shard_{shard_id}.db...")
    
    # The router automatically connects to the right database
    conn = get_db_connection(user_id)
    user = conn.execute("SELECT * FROM Users WHERE UserID = ?", (user_id,)).fetchone()
    
    if user:
        print(f"SUCCESS: Retrieved {user['Username']} directly from Shard {shard_id}.")
    else:
        print(f"FAILED: User not found in Shard {shard_id}.")
    conn.close()

def test_range_query(min_id, max_id):
    print(f"\n[SCATTER-GATHER RANGE QUERY] Searching for UserIDs between {min_id} and {max_id}")
    print("ROUTING: Querying ALL shards and merging the results in memory...")
    
    all_users = []
    # Query each shard independently
    for i in range(3):
        conn = sqlite3.connect(f'shard_{i}.db')
        conn.row_factory = sqlite3.Row
        users = conn.execute("SELECT * FROM Users WHERE UserID BETWEEN ? AND ?", (min_id, max_id)).fetchall()
        print(f"   -> Shard {i} returned {len(users)} records.")
        all_users.extend(users)
        conn.close()
        
    print(f"MERGED RESULT: Successfully combined {len(all_users)} total users from across the distributed system.")

if __name__ == '__main__':
    print("========================================")
    print("CAREERTRACK SHARDING ROUTER TEST")
    print("========================================")
    
    # Test specific users mapping to different shards
    test_single_lookup(1)
    test_single_lookup(2)
    test_single_lookup(3)
    
    # Test a query that requires merging data from all databases
    test_range_query(1, 10)