import sqlite3
import os

class DatabaseManager:
    """
    Manages SQLite database connections and operations for History and Bookmarks.
    """
    def __init__(self, db_path="database/searcher.db"):
        self.db_path = db_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self.init_db()
        
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create History table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create Bookmarks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    title TEXT,
                    added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create Passwords table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    UNIQUE(url, username)
                )
            ''')
            conn.commit()
            
    # --- History Operations ---
    
    def add_history(self, url, title):
        if url == "about:blank" or not url:
            return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO history (url, title) VALUES (?, ?)", (url, title))
            conn.commit()
            
    def get_history(self, limit=100):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_time FROM history ORDER BY visit_time DESC LIMIT ?", (limit,))
            return cursor.fetchall()
            
    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history")
            conn.commit()
            
    # --- Bookmark Operations ---
            
    def add_bookmark(self, url, title):
        if url == "about:blank" or not url:
            return False
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO bookmarks (url, title) VALUES (?, ?)", (url, title))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Already bookmarked
            return False
            
    def get_bookmarks(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, added_time FROM bookmarks ORDER BY added_time DESC")
            return cursor.fetchall()
            
    def remove_bookmark(self, url):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookmarks WHERE url = ?", (url,))
            conn.commit()
            
    def is_bookmarked(self, url):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM bookmarks WHERE url = ?", (url,))
            return cursor.fetchone() is not None
            
    # --- Password Operations (Basic) ---
    
    def save_password(self, url, username, password):
        # Very basic plain-text/base64 storage for Phase 3. 
        # In a real browser, this would use OS-level encryption (Keyring/Credential Manager).
        import base64
        encoded_pw = base64.b64encode(password.encode('utf-8')).decode('utf-8')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO passwords (url, username, password) 
                    VALUES (?, ?, ?)
                ''', (url, username, encoded_pw))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving password: {e}")
            return False
            
    def get_passwords(self):
        import base64
        results = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, url, username, password FROM passwords")
            for row in cursor.fetchall():
                pid, url, user, encoded_pw = row
                try:
                    decoded_pw = base64.b64decode(encoded_pw.encode('utf-8')).decode('utf-8')
                    results.append((pid, url, user, decoded_pw))
                except Exception:
                    pass
        return results
        
    def remove_password(self, pid):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM passwords WHERE id = ?", (pid,))
            conn.commit()
