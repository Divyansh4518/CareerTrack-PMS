"""
Test the login API endpoint directly
"""

import requests
import json

print("=" * 80)
print("TESTING LOGIN API ENDPOINT")
print("=" * 80)

url = "http://localhost:5000/api/auth/login"

# Test data
test_credentials = [
    {"username": "admin", "password": "admin123"},
    {"username": "officer", "password": "officer123"},
    {"username": "admin", "password": "wrongpassword"},
]

for cred in test_credentials:
    print(f"\nTesting with username='{cred['username']}', password='{cred['password']}'")
    print("-" * 80)
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(cred)
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Flask server!")
        print("   Make sure the Flask app is running: python app.py")
        break
    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n" + "=" * 80)
