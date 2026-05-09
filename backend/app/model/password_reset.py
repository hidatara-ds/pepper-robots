import sqlite3
import uuid
from datetime import datetime, timedelta
import os

class PasswordReset:
    
    @staticmethod
    def get_db_connection():
        """Get database connection"""
        conn = sqlite3.connect('pepper_robot.db')
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        conn.execute('PRAGMA foreign_keys = ON')
        return conn
    
    @staticmethod
    def generate_reset_token():
        """Generate a unique reset token"""
        return str(uuid.uuid4()).replace('-', '')
    
    @staticmethod
    def create_reset_token(admin_id, expires_minutes=15):
        """
        Create a new password reset token for an admin
        
        Args:
            admin_id (str): Admin ID to create token for
            expires_minutes (int): Token expiry time in minutes (default 15)
            
        Returns:
            str: Generated token if successful, None if failed
        """
        try:
            token = PasswordReset.generate_reset_token()
            expires_at = (datetime.now() + timedelta(minutes=expires_minutes)).strftime('%Y-%m-%d %H:%M:%S')
            
            conn = PasswordReset.get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO password_reset_tokens (admin_id, token, expires_at) VALUES (?, ?, ?)',
                    (admin_id, token, expires_at)
                )
                conn.commit()
                return token
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error creating reset token: {e}")
            return None
    
    @staticmethod
    def get_reset_token(token):
        """
        Get reset token details by token string
        
        Args:
            token (str): Reset token to lookup
            
        Returns:
            dict: Token data if found and not used, None otherwise
        """
        try:
            conn = PasswordReset.get_db_connection()
            try:
                result = conn.execute(
                    'SELECT * FROM password_reset_tokens WHERE token = ? AND is_used = 0',
                    (token,)
                ).fetchone()
                
                return dict(result) if result else None
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting reset token: {e}")
            return None
    
    @staticmethod
    def is_token_valid(token):
        """
        Check if token exists and is not expired
        
        Args:
            token (str): Reset token to validate
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            reset_data = PasswordReset.get_reset_token(token)
            if not reset_data:
                return False
            
            # Check if token is expired
            expires_at = datetime.strptime(reset_data['expires_at'], '%Y-%m-%d %H:%M:%S')
            is_not_expired = datetime.now() < expires_at
            
            return is_not_expired
            
        except Exception as e:
            print(f"Error validating token: {e}")
            return False
    
    @staticmethod
    def mark_token_used(token):
        """
        Mark token as used to prevent reuse
        
        Args:
            token (str): Reset token to mark as used
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = PasswordReset.get_db_connection()
            try:
                cursor = conn.execute(
                    'UPDATE password_reset_tokens SET is_used = 1 WHERE token = ?',
                    (token,)
                )
                conn.commit()
                return cursor.rowcount > 0
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error marking token as used: {e}")
            return False
    
    @staticmethod
    def invalidate_all_tokens_for_admin(admin_id):
        """
        Mark all tokens for an admin as used (for security after password change)
        
        Args:
            admin_id (str): Admin ID to invalidate tokens for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = PasswordReset.get_db_connection()
            try:
                conn.execute(
                    'UPDATE password_reset_tokens SET is_used = 1 WHERE admin_id = ? AND is_used = 0',
                    (admin_id,)
                )
                conn.commit()
                return True
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error invalidating tokens for admin: {e}")
            return False
    
    @staticmethod
    def cleanup_expired_tokens():
        """
        Remove expired tokens from database (maintenance function)
        
        Returns:
            int: Number of tokens cleaned up
        """
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            conn = PasswordReset.get_db_connection()
            try:
                cursor = conn.execute(
                    'DELETE FROM password_reset_tokens WHERE expires_at < ?',
                    (current_time,)
                )
                conn.commit()
                return cursor.rowcount
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error cleaning up expired tokens: {e}")
            return 0
    
    @staticmethod
    def get_token_stats():
        """
        Get statistics about password reset tokens (for monitoring)
        
        Returns:
            dict: Token statistics
        """
        try:
            conn = PasswordReset.get_db_connection()
            try:
                # Count total tokens
                total_tokens = conn.execute(
                    'SELECT COUNT(*) as count FROM password_reset_tokens'
                ).fetchone()['count']
                
                # Count active (unused and not expired) tokens
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                active_tokens = conn.execute(
                    'SELECT COUNT(*) as count FROM password_reset_tokens WHERE is_used = 0 AND expires_at > ?',
                    (current_time,)
                ).fetchone()['count']
                
                # Count expired tokens
                expired_tokens = conn.execute(
                    'SELECT COUNT(*) as count FROM password_reset_tokens WHERE expires_at < ?',
                    (current_time,)
                ).fetchone()['count']
                
                # Count used tokens
                used_tokens = conn.execute(
                    'SELECT COUNT(*) as count FROM password_reset_tokens WHERE is_used = 1'
                ).fetchone()['count']
                
                return {
                    'total_tokens': total_tokens,
                    'active_tokens': active_tokens,
                    'expired_tokens': expired_tokens,
                    'used_tokens': used_tokens
                }
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting token stats: {e}")
            return {
                'total_tokens': 0,
                'active_tokens': 0,
                'expired_tokens': 0,
                'used_tokens': 0
            } 