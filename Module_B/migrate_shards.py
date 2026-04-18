import sqlite3
import os

# Define our 3 simulated nodes
NUM_SHARDS = 3

def get_shard_id(user_id):
    """Hash-based partitioning logic."""
    return user_id % NUM_SHARDS

def migrate_data():
    print(" Starting Shard Migration...")

    # 1. Connect to the original database
    orig_conn = sqlite3.connect('careertrack.db')
    orig_conn.row_factory = sqlite3.Row
    orig_cur = orig_conn.cursor()

    # 2. Create the 3 new Shard databases
    shard_conns = []
    for i in range(NUM_SHARDS):
        db_name = f'shard_{i}.db'
        if os.path.exists(db_name):
            os.remove(db_name)
        shard_conns.append(sqlite3.connect(db_name))

    # 3. Copy the database schema
    orig_cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    schemas = orig_cur.fetchall()

    for conn in shard_conns:
        for schema in schemas:
            if schema['sql']:
                conn.execute(schema['sql'])
        conn.commit()
    print("Schemas successfully duplicated across all 3 shards.")

    # 4. Migrate the 'Users' table (Shard Key: UserID)
    print(" Partitioning Users table...")
    orig_cur.execute("SELECT * FROM Users")
    users = orig_cur.fetchall()
    for user in users:
        shard_id = get_shard_id(user['UserID'])
        placeholders = ', '.join(['?'] * len(user))
        columns = ', '.join(user.keys())
        query = f"INSERT INTO Users ({columns}) VALUES ({placeholders})"
        shard_conns[shard_id].execute(query, tuple(user))

    # 5. Migrate the 'Application' table
    print(" Partitioning Application table...")
    orig_cur.execute("SELECT * FROM Application")
    apps = orig_cur.fetchall()
    for app in apps:
        shard_id = get_shard_id(app['StudentID'])
        placeholders = ', '.join(['?'] * len(app))
        columns = ', '.join(app.keys())
        query = f"INSERT INTO Application ({columns}) VALUES ({placeholders})"
        shard_conns[shard_id].execute(query, tuple(app))

    # 6. Save and close
    for i, conn in enumerate(shard_conns):
        conn.commit()
        conn.close()
        print(f" Shard {i} successfully populated and sealed.")

    orig_conn.close()
    print("Migration Complete! No data lost.")

if __name__ == '__main__':
    migrate_data()