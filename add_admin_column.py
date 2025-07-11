import sqlite3
import os

# Pfad zur Datenbank
db_path = 'instance/database.db'

# Alternativ, falls die Datenbank im Root-Verzeichnis ist
if not os.path.exists(db_path):
    db_path = 'database.db'

try:
    # Verbindung zur Datenbank
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Prüfe, ob die Spalte bereits existiert
    cursor.execute("PRAGMA table_info(user)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_admin' not in columns:
        # Füge die is_admin Spalte hinzu
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        print("✓ is_admin Spalte wurde hinzugefügt")
        
        # Setze einen existierenden User als Admin (ersten User)
        cursor.execute("UPDATE user SET is_admin = 1 WHERE id = 1")
        print("✓ Erster User wurde als Admin gesetzt")
        
        conn.commit()
    else:
        print("✓ is_admin Spalte existiert bereits")
        
    # Zeige alle User
    cursor.execute("SELECT id, username, is_admin FROM user")
    users = cursor.fetchall()
    print("\nAktuelle User:")
    for user in users:
        admin_status = "Admin" if user[2] else "Normal"
        print(f"  ID: {user[0]}, Username: {user[1]}, Status: {admin_status}")
        
except sqlite3.Error as e:
    print(f"Fehler: {e}")
    
finally:
    if conn:
        conn.close()
