import mysql.connector
from db_router import get_shard_id, get_db_connection, load_metadata

def test_single_lookup(user_id):
    print(f"\n[SINGLE LOOKUP] Searching for UserID: {user_id}")
    shard_id = get_shard_id(user_id)
    metadata = load_metadata()
    port = metadata['nodes'][str(shard_id)]
    print(f"ROUTING: Directing query to MySQL Shard {shard_id} (Port {port})...")
    
    try:
        conn = get_db_connection(user_id)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()
        
        if user:
            print(f"SUCCESS: Retrieved {user['Username']} directly from MySQL Shard {shard_id}.")
        else:
            print(f"FAILED: User not found in MySQL Shard {shard_id}.")
        conn.close()
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

def test_range_query(min_id, max_id):
    print(f"\n[SCATTER-GATHER RANGE QUERY] Searching for UserIDs between {min_id} and {max_id}")
    print("ROUTING: Querying ALL MySQL shards and merging the results in memory...")
    
    all_users = []
    metadata = load_metadata()
    for i in range(3):
        port = metadata['nodes'][str(i)]
        try:
            conn = mysql.connector.connect(
                host=metadata['host'],
                port=port,
                user=metadata['user'],
                password=metadata['password'],
                database=metadata['database']
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Users WHERE UserID BETWEEN %s AND %s", (min_id, max_id))
            users = cursor.fetchall()
            print(f"   -> Shard {i} (Port {port}) returned {len(users)} records.")
            all_users.extend(users)
            conn.close()
        except Exception as e:
            print(f"   -> Shard {i} CONNECTION ERROR: {e}")
        
    print(f"MERGED RESULT: Successfully combined {len(all_users)} total users from the cluster.")

def test_join_query(student_id):
    print(f"\n[JOIN QUERY] Fetching Applications for StudentID: {student_id}")
    shard_id = get_shard_id(student_id)
    print(f"ROUTING: Directing JOIN query to MySQL Shard {shard_id}...")
    
    try:
        conn = get_db_connection(student_id)
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT users.Username, application.Status 
            FROM users 
            JOIN application ON users.UserID = application.StudentID 
            WHERE users.UserID = %s
        """
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        
        if results:
            print(f"SUCCESS: Found {len(results)} applications for student {student_id} on Shard {shard_id}.")
        else:
            print(f"FAILED: No applications found for student {student_id}.")
        conn.close()
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == '__main__':
    print("========================================")
    print("CAREERTRACK MySQL SHARDING ROUTER TEST")
    print("========================================")
    
    test_single_lookup(1)
    test_range_query(1, 10)
    test_join_query(1)