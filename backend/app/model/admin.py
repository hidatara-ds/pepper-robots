import sqlite3
from datetime import datetime
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class Admin:
    def __init__(self):
        # This class uses only static methods, no instance initialization needed
        pass
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def get_db_connection():
        """Get database connection"""
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def find_by_credentials(email, password):
        """Find admin by email and verify password"""
        conn = Admin.get_db_connection()
        try:
            admin = conn.execute(
                'SELECT * FROM Admin WHERE email = ?', (email,)
            ).fetchone()
            
            if not admin:
                return None
                
            # Verify password using bcrypt
            if Admin.verify_password(password, admin['password']):
                return dict(admin)
        finally:
            conn.close()
        
        return None
    
    @staticmethod
    def update_last_login(admin_id):
        """Update admin's last_login timestamp"""
        current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00')
        
        conn = Admin.get_db_connection()
        try:
            conn.execute(
                'UPDATE Admin SET last_login = ? WHERE admin_id = ?',
                (current_timestamp, admin_id)
            )
            conn.commit()
        finally:
            conn.close()
        
        return current_timestamp
    
    @staticmethod
    def find_by_email(email):
        """Find admin by email address only (for forgot password)"""
        conn = Admin.get_db_connection()
        try:
            admin = conn.execute(
                'SELECT * FROM Admin WHERE email = ?', (email,)
            ).fetchone()
            
            return dict(admin) if admin else None
        finally:
            conn.close()
    
    @staticmethod
    def update_password(admin_id, new_password):
        """Update admin password by admin_id (for reset password)"""
        try:
            current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00')
            hashed_password = Admin.hash_password(new_password)
            
            conn = Admin.get_db_connection()
            try:
                cursor = conn.execute(
                    'UPDATE Admin SET password = ?, updated_at = ? WHERE admin_id = ?',
                    (hashed_password, current_timestamp, admin_id)
                )
                conn.commit()
                
                # Return True if admin was found and updated
                return cursor.rowcount > 0
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error updating password: {e}")
            return False