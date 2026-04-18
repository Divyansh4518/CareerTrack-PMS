import mysql.connector

# Dr. Meena's Shard Ports
shards = {
    0: 3307,
    1: 3308,
    2: 3309
}

# The dummy data we want to insert. 
# Notice how User 1 maps to Shard 1, User 2 to Shard 2, and User 3 to Shard 0.
dummy_users = [
    (1, 'admin'),
    (2, 'officer'),
    (3, 'student_john')
]

dummy_apps = [
    (101, 1, 'Pending'),
    (102, 1, 'Accepted'),
    (201, 2, 'Rejected'),
    (301, 3, 'Under Review')
]

def setup_shards():
    for shard_id, port in shards.items():
        print(f"Connecting to Shard {shard_id} on Port {port}...")
        try:
            conn = mysql.connector.connect(
                host="10.0.116.184",
                port=port,
                user="Big_Data",
                password="password@123",
                database="Big_Data"
            )
            cursor = conn.cursor()
            
            # 1. Create the Tables (LOWERCASE)
            cursor.execute("CREATE TABLE IF NOT EXISTS users (UserID INT PRIMARY KEY, Username VARCHAR(50))")
            cursor.execute("CREATE TABLE IF NOT EXISTS application (AppID INT PRIMARY KEY, StudentID INT, Status VARCHAR(50))")
            
            # 2. Clear existing data
            cursor.execute("DELETE FROM application")
            cursor.execute("DELETE FROM users")
            
            # 3. Insert Users that belong to THIS shard (LOWERCASE)
            for user in dummy_users:
                if user[0] % 3 == shard_id:
                    cursor.execute("INSERT INTO users (UserID, Username) VALUES (%s, %s)", user)
                    print(f"   -> Inserted User {user[0]} into Shard {shard_id}")
            
            # 4. Insert Applications for Users in THIS shard (LOWERCASE)
            for app in dummy_apps:
                if app[1] % 3 == shard_id:
                    cursor.execute("INSERT INTO application (AppID, StudentID, Status) VALUES (%s, %s, %s)", app)
            
            conn.commit()
            conn.close()
            print(f"✅ Shard {shard_id} setup complete!\n")
            
        except Exception as e:
            print(f"❌ ERROR on Shard {shard_id}: {e}\n")

if __name__ == '__main__':
    setup_shards()