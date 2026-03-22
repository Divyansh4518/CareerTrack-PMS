import sqlite3

def test_indexing():
    # Connect to your local database
    conn = sqlite3.connect('careertrack.db')
    cursor = conn.cursor()
    
    print("===========================================")
    print("🔍 SQLITE INDEXING PERFORMANCE TEST")
    print("===========================================\n")
    
    # Ask SQLite how it plans to execute this search
    cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM application WHERE Status = 'Shortlisted';")
    plan = cursor.fetchall()
    
    print("Query: SELECT * FROM application WHERE Status = 'Shortlisted';\n")
    print("Execution Plan:")
    for row in plan:
        explanation = row[3]
        print(f"-> {explanation}")
        
        if "SCAN" in explanation:
            print("\n⚠️ RESULT: Full table SCAN detected (O(N) time).")
            print("Action: You need to apply indexes.sql to optimize this!")
        elif "SEARCH" in explanation or "INDEX" in explanation:
            print("\n✅ RESULT: B-Tree INDEX SEARCH detected.")
            print("Performance: Query is optimized to O(log N) time complexity!")

    conn.close()

if __name__ == "__main__":
    test_indexing()