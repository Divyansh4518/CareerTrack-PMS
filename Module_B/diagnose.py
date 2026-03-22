"""
Comprehensive diagnostic for login issues
Run this on your computer to identify the problem
"""

import sqlite3
import hashlib
import os

def hash_password(password):
    salt = 'careertrack_salt_2026'
    return hashlib.sha256((password + salt).encode()).hexdigest()

print("=" * 80)
print("CAREERTRACK PMS - COMPREHENSIVE DIAGNOSTICS")
print("=" * 80)

# Check database file location
db_path = os.path.join(os.path.dirname(__file__), 'careertrack.db')
print(f"\n1. DATABASE FILE:")
print(f"   Path: {db_path}")
print(f"   Exists: {os.path.exists(db_path)}")
if os.path.exists(db_path):
    print(f"   Size: {os.path.getsize(db_path)} bytes")
else:
    print("   ❌ DATABASE FILE NOT FOUND!")
    print("   Run: python db.py")
    exit(1)

# Connect and check users
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n2. USERS IN DATABASE:")
    cursor.execute('SELECT UserID, Username, PasswordHash, Role, Email, IsActive FROM Users ORDER BY Username')
    users = cursor.fetchall()
    
    if not users:
        print("   ❌ NO USERS FOUND!")
        print("   Run: python debug_passwords.py")
        exit(1)
    
    print(f"   Total users: {len(users)}")
    print()
    
    for user in users:
        user_id, username, password_hash, role, email, is_active = user
        print(f"   Username: {username}")
        print(f"   Role: {role}")
        print(f"   Email: {email}")
        print(f"   Active: {'Yes' if is_active else 'No'}")
        print(f"   Password Hash: {password_hash[:50]}...")
        
        # Determine expected password
        if username == 'admin':
            expected_password = 'admin123'
        elif username == 'officer':
            expected_password = 'officer123'
        else:
            expected_password = None
        
        if expected_password:
            correct_hash = hash_password(expected_password)
            matches = password_hash == correct_hash
            
            print(f"   Expected password: {expected_password}")
            print(f"   Hash matches: {'✅ YES' if matches else '❌ NO'}")
            
            if not matches:
                print(f"   Current hash:  {password_hash}")
                print(f"   Expected hash: {correct_hash}")
                print(f"   ⚠️  PASSWORD HASH IS WRONG!")
        
        print()
    
    # Test authentication
    print(f"\n3. TESTING AUTHENTICATION:")
    
    test_cases = [
        ('admin', 'admin123'),
        ('officer', 'officer123'),
        ('admin', 'wrongpassword'),
    ]
    
    for username, password in test_cases:
        print(f"\n   Testing: {username} / {password}")
        
        cursor.execute("""
            SELECT UserID, Username, PasswordHash, Role, Email, IsActive
            FROM Users
            WHERE Username = ?
        """, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            print(f"   ❌ User '{username}' not found in database")
            continue
        
        user_id, db_username, stored_hash, role, email, is_active = user
        
        if not is_active:
            print(f"   ❌ Account is deactivated")
            continue
        
        provided_hash = hash_password(password)
        matches = stored_hash == provided_hash
        
        if matches:
            print(f"   ✅ Authentication would SUCCEED")
            print(f"   Role: {role}")
        else:
            print(f"   ❌ Authentication would FAIL")
            print(f"   Stored hash:   {stored_hash[:40]}...")
            print(f"   Provided hash: {provided_hash[:40]}...")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("4. RECOMMENDED ACTIONS:")
    print("=" * 80)
    
    # Check if any passwords are wrong
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT Username, PasswordHash FROM Users WHERE Username IN (?, ?)', ('admin', 'officer'))
    users = cursor.fetchall()
    conn.close()
    
    admin_wrong = False
    officer_wrong = False
    
    for username, stored_hash in users:
        if username == 'admin':
            admin_wrong = stored_hash != hash_password('admin123')
        elif username == 'officer':
            officer_wrong = stored_hash != hash_password('officer123')
    
    if admin_wrong or officer_wrong:
        print("\n⚠️  PASSWORD HASHES ARE INCORRECT!")
        print("\nFIX IT BY RUNNING:")
        print("   python debug_passwords.py")
        print("\nThis will reset the passwords to:")
        print("   admin / admin123")
        print("   officer / officer123")
    else:
        print("\n✅ ALL PASSWORD HASHES ARE CORRECT!")
        print("\nIf login still fails in browser:")
        print("1. Clear browser cache (Ctrl+Shift+Delete)")
        print("2. Try Incognito/Private mode")
        print("3. Check browser console (F12) for JavaScript errors")
        print("4. Make sure Flask app is running")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTICS COMPLETE")
print("=" * 80)
