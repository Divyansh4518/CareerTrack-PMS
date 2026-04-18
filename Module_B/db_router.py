import mysql.connector
import json

def load_metadata():
    """Loads the central metadata catalog."""
    with open('metadata.json', 'r') as f:
        return json.load(f)

def get_shard_id(user_id):
    """Calculates the hash based on metadata."""
    metadata = load_metadata()
    return user_id % metadata['num_shards']

def get_db_connection(user_id):
    """Routes to the correct MySQL shard on the IITGN network."""
    metadata = load_metadata()
    shard_id = str(get_shard_id(user_id))
    port = metadata['nodes'][shard_id]
    
    conn = mysql.connector.connect(
        host=metadata['host'],
        port=port,
        user=metadata['user'],
        password=metadata['password'],
        database=metadata['database']
    )
    return conn