"""
Test the authentication directly to see what's happening
"""

import sqlite3
import hashlib
from auth_utils import authenticate_user, hash_password, verify_password

print("=" * 80)
print("TESTING AUTHENTICATION SYSTEM")
print("=" * 80)

# Test 1: Check hash_password function
print("\n1. Testing hash_password function:")
password = "admin123"
hashed = hash_password(password)
print(f"   Password: {password}")
print(f"   Hashed: {hashed}")

# Test 2: Check database connection
print("\n2. Checking database users:")
conn = sqlite3.connect('careertrack.db')
cursor = conn.cursor()
cursor.execute("SELECT Username, PasswordHash, Role FROM Users WHERE Username = 'admin'")
result = cursor.fetchone()

if result:
    print(f"   Username: {result[0]}")
    print(f"   Role: {result[2]}")
    print(f"   Stored Hash: {result[1]}")
    print(f"   Generated Hash: {hashed}")
    print(f"   Match: {'✅ YES' if result[1] == hashed else '❌ NO'}")
else:
    print("   ❌ Admin user not found in database!")

conn.close()

# Test 3: Test verify_password function
print("\n3. Testing verify_password function:")
if result:
    stored_hash = result[1]
    is_valid = verify_password(stored_hash, "admin123")
    print(f"   Verify 'admin123': {'✅ PASS' if is_valid else '❌ FAIL'}")
    
    is_invalid = verify_password(stored_hash, "wrongpassword")
    print(f"   Verify 'wrongpassword': {'✅ PASS (should be False)' if not is_invalid else '❌ FAIL (should be False)'}")

# Test 4: Test authenticate_user function
print("\n4. Testing authenticate_user function:")
result = authenticate_user("admin", "admin123")
if result:
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Authentication successful!")
        print(f"   Session token: {result.get('session_token', 'N/A')[:30]}...")
        print(f"   Username: {result.get('username', 'N/A')}")
        print(f"   Role: {result.get('role', 'N/A')}")
else:
    print("   ❌ Authentication failed - returned None")

# Test 5: Try wrong password
print("\n5. Testing with wrong password:")
result = authenticate_user("admin", "wrongpassword")
if result:
    print(f"   ❌ Should have failed but got: {result}")
else:
    print("   ✅ Correctly rejected wrong password")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
