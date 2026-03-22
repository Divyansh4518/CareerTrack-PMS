"""
Debug script to check password hashing and database users
"""

import sqlite3
import hashlib

def hash_password(password):
    """Hash a password using SHA-256"""
    salt = "careertrack_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Connect to database
conn = sqlite3.connect('careertrack.db')
cursor = conn.cursor()

# Check what users exist
cursor.execute("SELECT UserID, Username, PasswordHash, Role FROM Users")
users = cursor.fetchall()

print("=" * 80)
print("USERS IN DATABASE:")
print("=" * 80)
for user in users:
    print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[3]}")
    print(f"Stored Hash: {user[2][:50]}...")
    print()

# Test password hashing
print("=" * 80)
print("TESTING PASSWORD HASHING:")
print("=" * 80)

test_passwords = {
    'admin': 'admin123',
    'officer': 'officer123'
}

for username, password in test_passwords.items():
    generated_hash = hash_password(password)
    print(f"\nUsername: {username}")
    print(f"Password: {password}")
    print(f"Generated Hash: {generated_hash}")
    
    # Check if it matches database
    cursor.execute("SELECT PasswordHash FROM Users WHERE Username = ?", (username,))
    result = cursor.fetchone()
    if result:
        stored_hash = result[0]
        print(f"Stored Hash:    {stored_hash}")
        print(f"Match: {'✅ YES' if stored_hash == generated_hash else '❌ NO'}")
    else:
        print(f"User not found in database!")

conn.close()

print("\n" + "=" * 80)
print("Now let's create the correct hash and update the database...")
print("=" * 80)

# Now fix the passwords
conn = sqlite3.connect('careertrack.db')
cursor = conn.cursor()

# Delete existing users
cursor.execute("DELETE FROM Users WHERE Username IN ('admin', 'officer')")

# Insert with correct hashes
admin_hash = hash_password('admin123')
officer_hash = hash_password('officer123')

cursor.execute("""
    INSERT INTO Users (Username, PasswordHash, Role, Email, IsActive)
    VALUES (?, ?, ?, ?, 1)
""", ('admin', admin_hash, 'Admin', 'admin@careertrack.com'))

cursor.execute("""
    INSERT INTO Users (Username, PasswordHash, Role, Email, IsActive)
    VALUES (?, ?, ?, ?, 1)
""", ('officer', officer_hash, 'PlacementOfficer', 'officer@careertrack.com'))

conn.commit()
conn.close()

print("\n✅ Users recreated with correct password hashes!")
print("\nYou can now login with:")
print("Username: admin")
print("Password: admin123")
print("\nOR")
print("Username: officer")
print("Password: officer123")
