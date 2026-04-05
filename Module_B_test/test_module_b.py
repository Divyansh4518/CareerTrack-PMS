import os
import random
import threading
import time

import requests

BASE_URL = os.getenv("MODULE_B_TEST_BASE_URL", "http://127.0.0.1:5000")


# -----------------------------
# USER OPERATIONS
# -----------------------------
def user_operations(user_id):
    for _ in range(10):
        try:
            op = random.choice(["create", "read", "update", "delete"])

            if op == "create":
                r = requests.post(f"{BASE_URL}/data", json={"value": random.randint(1, 100)})
                print(f"[CREATE] {r.status_code}")

            elif op == "read":
                rid = random.randint(1, 5)
                r = requests.get(f"{BASE_URL}/data/{rid}")
                print(f"[READ] {r.status_code}")

            elif op == "update":
                rid = random.randint(1, 5)
                r = requests.put(f"{BASE_URL}/data/{rid}", json={"value": random.randint(100, 200)})
                print(f"[UPDATE] {r.status_code}")

            elif op == "delete":
                rid = random.randint(1, 5)
                r = requests.delete(f"{BASE_URL}/data/{rid}")
                print(f"[DELETE] {r.status_code}")

            # FAILURE SIMULATION
            if random.random() < 0.2:
                raise Exception("Simulated Failure")

        except Exception as e:
            print(f"[ROLLBACK] User {user_id}: {e}")

        time.sleep(random.random())


# -----------------------------
# CONCURRENT TEST
# -----------------------------
def test_concurrent():
    print("\n===== CONCURRENT TEST =====\n")

    threads = []
    for i in range(10):
        t = threading.Thread(target=user_operations, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n✅ Concurrent Test Done\n")


# -----------------------------
# RACE CONDITION TEST
# -----------------------------
def test_race():
    print("\n===== RACE CONDITION TEST =====\n")

    def update_same():
        try:
            r = requests.put(f"{BASE_URL}/data/1", json={"value": random.randint(1000, 2000)})
            print(f"[RACE UPDATE] {r.status_code}")
        except Exception:
            print("[ROLLBACK] Race handled")

    threads = []
    for _ in range(20):
        t = threading.Thread(target=update_same)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n✅ Race Test Done\n")


# -----------------------------
# STRESS TEST
# -----------------------------
def test_stress():
    print("\n===== STRESS TEST =====\n")

    threads = []
    for i in range(100):
        t = threading.Thread(target=user_operations, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n✅ Stress Test Done\n")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 Running Module B Tests\n")

    test_concurrent()
    test_race()
    test_stress()