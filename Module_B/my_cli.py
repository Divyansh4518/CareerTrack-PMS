import mysql.connector
import json

def run_cli():
    print("--- CareerTrack Shard CLI (Team Big_Data) ---")
    port = input("Enter Shard Port (3307, 3308, or 3309): ")
    
    try:
        conn = mysql.connector.connect(
            host="10.0.116.184",
            port=int(port),
            user="Big_Data",
            password="password@123",
            database="Big_Data"
        )
        cursor = conn.cursor(dictionary=True)
        print(f"✅ Connected to Shard on Port {port}\n")
        
        while True:
            query = input("mysql> ")
            if query.lower() in ['exit', 'quit']: break
            
            try:
                cursor.execute(query)
                if query.lower().startswith("select"):
                    results = cursor.fetchall()
                    for row in results: print(row)
                else:
                    conn.commit()
                    print("Query OK.")
            except Exception as e:
                print(f"Error: {e}")
                
        conn.close()
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    run_cli()