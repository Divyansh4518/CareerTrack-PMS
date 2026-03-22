"""
Fix user passwords in the database
Run this script to reset admin and officer passwords
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

# Update admin password
admin_hash = hash_password('admin123')
cursor.execute("UPDATE Users SET PasswordHash = ? WHERE Username = 'admin'", (admin_hash,))

# Update officer password
officer_hash = hash_password('officer123')
cursor.execute("UPDATE Users SET PasswordHash = ? WHERE Username = 'officer'", (officer_hash,))

conn.commit()
conn.close()

print("✅ Passwords updated successfully!")
print("Admin: admin / admin123")
print("Officer: officer / officer123")
