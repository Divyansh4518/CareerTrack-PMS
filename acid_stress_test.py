import requests
import concurrent.futures
import time

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:5000/api"
HEADERS = {"Content-Type": "application/json"}

VERIFY_URL = f"{BASE_URL}/debug/btrees/lookup"

# These are the seeded demo records in the in-memory B+ trees.
VALID_STUDENT_ID = "1"
VALID_JOB_ID = "1"

def authenticate():
    """Logs in to get the JWT session token."""
    print("🔑 Authenticating...")
    login_payload = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        if response.status_code == 200:
            token = response.json().get("session_token")
            HEADERS["Authorization"] = f"Bearer {token}"
            print("✅ Auth successful!\n")
            return True
        return False
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        return False

def verify_targets():
    """Confirms the test IDs exist in the running B+ trees before load testing."""
    print("🔎 Verifying B+ tree test records...")
    try:
        response = requests.get(
            VERIFY_URL,
            params={"student_id": VALID_STUDENT_ID, "job_id": VALID_JOB_ID},
            headers=HEADERS,
            timeout=5,
        )
        if response.status_code != 200:
            print(f"❌ Verification failed: HTTP {response.status_code}")
            return False

        data = response.json()
        if data.get("student_exists") and data.get("job_exists"):
            print(f"✅ Verified StudentID={VALID_STUDENT_ID} and JobID={VALID_JOB_ID} exist.\n")
            return True

        print(f"❌ Verification failed. Server reported: {data}")
        return False
    except Exception as e:
        print(f"❌ Verification Error: {e}")
        return False

def submit_application(req_num, is_poison=False):
    """Sends a request to the Mega-Transaction endpoint."""
    
    # Poison requests use a fake student ID. 
    # This should cause the API to throw an error mid-transaction and roll back.
    student_id = "FAKE_POISON_STUDENT" if is_poison else VALID_STUDENT_ID
    
    payload = {
        "StudentID": student_id,
        "JobID": VALID_JOB_ID,
        "RequestNum": req_num # Just for tracking
    }
    
    try:
        response = requests.post(f"{BASE_URL}/applications/apply", json=payload, headers=HEADERS)
        return {
            "req_num": req_num,
            "is_poison": is_poison,
            "status": response.status_code,
            "response": response.text
        }
    except Exception as e:
        return {"req_num": req_num, "is_poison": is_poison, "status": "ERROR", "response": str(e)}

def run_stress_test():
    if not authenticate():
        print("🛑 Halting: Cannot proceed without auth.")
        return

    if not verify_targets():
        print("🛑 Halting: Valid B+ tree targets were not verified.")
        return

    print("🚀 PHASE 1: Testing ISOLATION (Concurrency)...")
    results = []
    start_time = time.time()
    
    # Fire 30 valid requests at the exact same millisecond
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        valid_futures = [executor.submit(submit_application, i) for i in range(30)]
        for future in concurrent.futures.as_completed(valid_futures):
            results.append(future.result())
            
    print("\n☣️ PHASE 2: Testing ATOMICITY (Rollbacks)...")
    # Fire 5 poison requests that should crash and roll back
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        poison_futures = [executor.submit(submit_application, i, is_poison=True) for i in range(30, 35)]
        for future in concurrent.futures.as_completed(poison_futures):
            results.append(future.result())

    end_time = time.time()
    
    # --- Analyze ---
    valid_results = [r for r in results if not r["is_poison"]]
    poison_results = [r for r in results if r["is_poison"]]
    
    successful_valid = len([r for r in valid_results if r["status"] == 200])
    failed_valid = len(valid_results) - successful_valid
    
    print("\n📊 --- ACID TEST RESULTS ---")
    print(f"⏱️  Execution Time: {end_time - start_time:.2f} seconds")
    print(f"✅ Successful Concurrent Transactions (Isolation): {successful_valid}/30")
    if failed_valid > 0:
        print(f"⚠️  Failed Valid Transactions (Race conditions?): {failed_valid}")
        
    print("\n🧪 --- ROLLBACK VERIFICATION ---")
    for pr in poison_results:
        if pr['status'] == 500:
            print(f"✅ Poison #{pr['req_num']} cleanly rejected (Status 500). Rollback triggered!")
        else:
            print(f"❌ Poison #{pr['req_num']} behaved unexpectedly. Status: {pr['status']} - {pr['response']}")

if __name__ == "__main__":
    run_stress_test()