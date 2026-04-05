import requests
import concurrent.futures
import time

# --- CONFIGURATION ---
# Change these to match your local Flask setup
BASE_URL = "http://127.0.0.1:5000/api"
SESSION_TOKEN = "your_jwt_or_session_token_here" # Grab this from a successful login
HEADERS = {"Authorization": f"Bearer {SESSION_TOKEN}", "Content-Type": "application/json"}

def test_atomicity():
    """
    Tests ATOMICITY: All or nothing.
    We simulate a request that is designed to fail midway (e.g., missing required fields).
    If Atomicity works, the database and B+ tree should roll back entirely.
    """
    print("\n--- Starting Atomicity Test ---")
    
    # Example: Trying to apply for a job but sending intentionally corrupted data
    # to trigger the 'except' block in Bhavitha's API and force a rollback.
    bad_payload = {
        "student_id": 1,
        "job_id": 999,
        "status": "Applied",
        "intentionally_break_me": "This should cause an exception in the backend"
    }
    
    print("Sending intentionally failing request...")
    response = requests.post(f"{BASE_URL}/applications", json=bad_payload, headers=HEADERS)
    
    print(f"Server Response Code: {response.status_code}")
    if response.status_code == 500:
        print("✅ SUCCESS: Server caught the error. Now, verify your B+ tree and SQLite logs to ensure no partial data was saved!")
    else:
        print("❌ FAILED: The server accepted bad data or didn't throw a 500. Check your transaction wrappers.")

def simulate_concurrent_user(user_id, job_id):
    """Worker function for the isolation test."""
    payload = {
        "student_id": user_id,
        "job_id": job_id,
        "status": "Applied"
    }
    # Fire the request
    try:
        response = requests.post(f"{BASE_URL}/applications", json=payload, headers=HEADERS)
        return response.status_code
    except Exception as e:
        return str(e)

def test_isolation_and_concurrency(num_users=50):
    """
    Tests ISOLATION (Concurrency): Multiple users accessing at the exact same time.
    We simulate 50 students trying to apply for the exact same job at the exact same millisecond.
    """
    print(f"\n--- Starting Concurrency Test ({num_users} simultaneous requests) ---")
    
    target_job_id = 101 # A dummy job ID to hammer
    results = []
    
    start_time = time.time()
    
    # ThreadPoolExecutor spins up multiple threads to hit the API concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        # Schedule the requests
        futures = [executor.submit(simulate_concurrent_user, user_id, target_job_id) for user_id in range(1, num_users + 1)]
        
        # Collect the results as they finish
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    end_time = time.time()
    
    # Analyze results
    success_count = results.count(200) + results.count(201)
    error_count = len(results) - success_count
    
    print(f"Test completed in {end_time - start_time:.2f} seconds.")
    print(f"Successful applications: {success_count}")
    print(f"Failed/Rejected applications: {error_count}")
    
    if success_count == num_users:
        print("✅ SUCCESS: System handled high load without dropping requests.")
    else:
        print("⚠️ WARNING: Some requests failed. If this was a race condition check (like a limited slot job), ensure locks are working. If not, your server might be dropping connections.")

if __name__ == "__main__":
    print("Initializing ACID Stress Tester...")
    # Make sure your Flask server is running before executing this!
    
    # 1. Run Atomicity Test
    test_atomicity()
    
    time.sleep(2) # Brief pause
    
    # 2. Run Isolation/Concurrency Test
    test_isolation_and_concurrency(num_users=100) # Hammer it with 100 requests
    
    print("\n--- Testing Complete ---")
    print("To test DURABILITY: Manually kill your Flask server (Ctrl+C) right now, restart it, and verify the B+ Tree loads from the bptree_wal.log file correctly!")