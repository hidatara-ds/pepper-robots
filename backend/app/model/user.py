#!/usr/bin/env python3
"""
User Model
Handles user operations
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
import re

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class User:
    # Error message constants
    NAME_ALREADY_EXISTS = "Name already exists"
    USER_NOT_FOUND = "User not found"
    USER_DOESNT_EXIST = "User doesn't exists"
    NAME_CANNOT_BE_EMPTY = "Name cannot be empty"
    USER_DELETED_SUCCESSFULLY = "User deleted successfully"
    NAME_IS_REQUIRED = "Name is required"
    USER_CREATED_SUCCESSFULLY = "User created successfully"
    USER_UPDATED_SUCCESSFULLY = "User updated successfully"
    USER_NAME_UPDATED_SUCCESSFULLY = "User name updated successfully"
    USER_ALREADY_DELETED = "User already deleted"
    INVALID_USER_ID_FORMAT = "Invalid user ID format"
    USER_AND_RELATED_DATA_SOFT_DELETED = "User and related data soft deleted successfully"
    INVALID_PAGE_NUMBER = "Invalid page number"
    INVALID_LIMIT_NUMBER = "Invalid limit number"
    
    # SQL query constants
    CHECK_DUPLICATE_NAME_QUERY = 'SELECT user_id FROM User WHERE LOWER(name) = LOWER(?) AND user_id != ? AND deleted_at IS NULL'
    CHECK_NAME_EXISTS_QUERY = 'SELECT COUNT(*) as count FROM User WHERE LOWER(name) = LOWER(?) AND deleted_at IS NULL'
    GET_USER_BY_ID_QUERY = 'SELECT * FROM User WHERE user_id = ? AND deleted_at IS NULL'
    GET_USER_BY_NAME_QUERY = 'SELECT * FROM User WHERE LOWER(name) = LOWER(?) AND deleted_at IS NULL'
    
    def __init__(self):
        # This class uses only static methods, no instance initialization needed
        pass
    
    @staticmethod
    def get_db_connection():
        """Get database connection"""
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def generate_user_id() -> str:
        """Generate unique user ID using UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid_uuid(user_id: str) -> bool:
        """
        Validate if user_id is a valid UUID format
        
        Args:
            user_id: User ID to validate
            
        Returns:
            True if valid UUID, False otherwise
        """
        try:
            uuid.UUID(user_id)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def create_user(name: str) -> Dict[str, Any]:
        """
        Create new user with face data
        
        Args:
            name: User's name
            
        Returns:
            Dict with user data or error info
        """
        result = {
            'success': False,
            'user_id': None,
            'message': '',
            'created_at': None
        }
        
        try:
            # Validate input
            if not name or not name.strip():
                result['message'] = User.NAME_IS_REQUIRED
                return result
            
            name = name.strip()
            
            # Check if name already exists
            if User.name_exists(name):
                result['message'] = User.NAME_ALREADY_EXISTS
                return result
            
            # Generate user ID and timestamp
            user_id = User.generate_user_id()
            created_at = datetime.now().isoformat()
            
            # Insert user into database
            conn = User.get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO User (user_id, name, is_active, created_at)
                    VALUES (?, ?, ?, ?)
                """, (user_id, name, True, created_at))
                conn.commit()
                
                result.update({
                    'success': True,
                    'user_id': user_id,
                    'message': User.USER_CREATED_SUCCESSFULLY,
                    'created_at': created_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def name_exists(name: str) -> bool:
        """
        Check if user name already exists
        
        Args:
            name: Name to check
            
        Returns:
            True if name exists, False otherwise
        """
        try:
            conn = User.get_db_connection()
            try:
                result = conn.execute(
                    User.CHECK_NAME_EXISTS_QUERY,
                    (name.strip(),)
                ).fetchone()
                
                return result['count'] > 0
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error checking name existence: {e}")
            return False
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by user_id
        
        Args:
            user_id: User ID
            
        Returns:
            User data dict or None if not found
        """
        try:
            conn = User.get_db_connection()
            try:
                user = conn.execute(
                    User.GET_USER_BY_ID_QUERY,
                    (user_id,)
                ).fetchone()
                
                return dict(user) if user else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @staticmethod
    def get_user_by_name(name: str) -> Optional[Dict[str, Any]]:
        """
        Get user by name
        
        Args:
            name: User's name
            
        Returns:
            User data dict or None if not found
        """
        try:
            conn = User.get_db_connection()
            try:
                user = conn.execute(
                    User.GET_USER_BY_NAME_QUERY,
                    (name.strip(),)
                ).fetchone()
                
                return dict(user) if user else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting user by name: {e}")
            return None
    
    @staticmethod
    def get_all_users(include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get all users
        
        Args:
            include_inactive: Whether to include inactive users
            
        Returns:
            List of user data dicts
        """
        try:
            conn = User.get_db_connection()
            try:
                query = 'SELECT * FROM User WHERE deleted_at IS NULL'
                if not include_inactive:
                    query += ' AND is_active = 1'
                query += ' ORDER BY created_at DESC'
                
                users = conn.execute(query).fetchall()
                return [dict(user) for user in users]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    @staticmethod
    def get_active_identities(page: int = 1, limit: int = 20):
        """
        Get paginated list of active users with active face data

        Args:
            page: Page number (default 1)
            limit: Items per page (default 20)

        Returns:
            Tuple of (data list, pagination dict) or error dict
        """
        if page < 1:
            return {
                "success": False,
                "message": User.INVALID_PAGE_NUMBER
            }, None
        if limit < 1:
            return {
                "success": False,
                "message": User.INVALID_LIMIT_NUMBER
            }, None

        offset = (page - 1) * limit

        conn = User.get_db_connection()
        try:
            total_query = '''
                SELECT COUNT(*)
                FROM User u
                WHERE u.is_active = 1
                AND EXISTS (
                    SELECT 1 FROM Face_Data f WHERE f.user_id = u.user_id AND f.is_active = 1
                )
            '''
            total_items = conn.execute(total_query).fetchone()[0]

            query = '''
                SELECT u.user_id, u.name, u.created_at, f.image_path, f.face_image_base64
                FROM User u
                JOIN Face_Data f ON u.user_id = f.user_id
                WHERE u.is_active = 1 AND f.is_active = 1
                GROUP BY u.user_id
                ORDER BY u.created_at DESC
                LIMIT ? OFFSET ?
            '''
            results = conn.execute(query, (limit, offset)).fetchall()

            data = [
                {
                    "user_id": row["user_id"],
                    "name": row["name"],
                    "created_at": row["created_at"],
                    "image_path": row["image_path"],
                    "face_image_base64": row["face_image_base64"]
                }
                for row in results
            ]

            total_pages = (total_items + limit - 1) // limit if limit else 1

            pagination = {
                "currentPage": page,
                "totalPages": total_pages,
                "totalItems": total_items,
                "itemsPerPage": limit
            }

            return data, pagination
        finally:
            conn.close()
    
    @staticmethod
    def update_user(user_id: str, name: str = None, is_active: bool = None) -> Dict[str, Any]:
        """
        Update user data
        
        Args:
            user_id: User ID
            name: New name (optional)
            is_active: New active status (optional)
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Check if user exists
            existing_user = User.get_user_by_id(user_id)
            if not existing_user:
                result['message'] = User.USER_NOT_FOUND
                return result
            
            # Validate name if provided
            if name is not None:
                name = name.strip()
                if not name:
                    result['message'] = User.NAME_CANNOT_BE_EMPTY
                    return result
                
                # Check if new name already exists (excluding current user)
                conn = User.get_db_connection()
                try:
                    existing_name = conn.execute(
                        User.CHECK_DUPLICATE_NAME_QUERY,
                        (name, user_id)
                    ).fetchone()
                    
                    if existing_name:
                        result['message'] = User.NAME_ALREADY_EXISTS
                        return result
                        
                finally:
                    conn.close()
            
            # Update user
            updated_at = datetime.now().isoformat()
            update_fields = ['updated_at = ?']
            update_values = [updated_at]
            
            if name is not None:
                update_fields.append('name = ?')
                update_values.append(name)
            
            if is_active is not None:
                update_fields.append('is_active = ?')
                update_values.append(is_active)
            
            update_values.append(user_id)
            
            conn = User.get_db_connection()
            try:
                cursor = conn.execute(
                    f'UPDATE User SET {", ".join(update_fields)} WHERE user_id = ?',
                    update_values
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    result.update({
                        'success': True,
                        'message': User.USER_UPDATED_SUCCESSFULLY
                    })
                else:
                    result['message'] = User.USER_NOT_FOUND
                    
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def hard_delete_user(user_id: str) -> Dict[str, Any]:
        """
        HARD DELETE user - FOR ROLLBACK OPERATIONS ONLY
        Permanently removes user record and related data from database
        
        Args:
            user_id: User ID to delete permanently
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Validate UUID format
            if not User.is_valid_uuid(user_id):
                result['message'] = User.INVALID_USER_ID_FORMAT
                return result
            
            conn = User.get_db_connection()
            try:
                # Start transaction by beginning explicit transaction
                conn.execute('BEGIN TRANSACTION')
                
                # First, delete all related Face_Data records (cascade delete)
                face_cursor = conn.execute('DELETE FROM Face_Data WHERE user_id = ?', (user_id,))
                face_deleted_count = face_cursor.rowcount
                
                # Then delete the user record
                user_cursor = conn.execute('DELETE FROM User WHERE user_id = ?', (user_id,))
                user_deleted_count = user_cursor.rowcount
                
                # Commit the transaction
                conn.commit()
                
                if user_deleted_count > 0:
                    result.update({
                        'success': True,
                        'message': f'User permanently deleted (Face records: {face_deleted_count})'
                    })
                    print(f"ROLLBACK: Hard deleted user {user_id} and {face_deleted_count} face records")
                else:
                    result['message'] = User.USER_NOT_FOUND
                    
            except Exception as e:
                # Rollback transaction on error
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
            print(f"Error hard deleting user {user_id}: {e}")
        
        return result
    
    @staticmethod
    def delete_user(user_id: str) -> Dict[str, Any]:
        """
        SOFT DELETE user (mark as deleted) - FOR NORMAL OPERATIONS
        Marks user and related face data as deleted without removing from database
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Check if user exists
            existing_user = User.get_user_by_id(user_id)
            if not existing_user:
                result['message'] = User.USER_NOT_FOUND
                return result
            
            deleted_at = datetime.now().isoformat()
            
            conn = User.get_db_connection()
            try:
                # Start transaction
                conn.execute('BEGIN TRANSACTION')
                
                # Soft delete related Face_Data records
                conn.execute('''
                    UPDATE Face_Data 
                    SET is_active = 0, deleted_at = ?, updated_at = ?
                    WHERE user_id = ? AND deleted_at IS NULL
                ''', (deleted_at, deleted_at, user_id))
                
                # Soft delete user
                cursor = conn.execute('''
                    UPDATE User 
                    SET deleted_at = ?, is_active = 0, updated_at = ?
                    WHERE user_id = ?
                ''', (deleted_at, deleted_at, user_id))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    result.update({
                        'success': True,
                        'message': User.USER_AND_RELATED_DATA_SOFT_DELETED
                    })
                else:
                    result['message'] = User.USER_NOT_FOUND
                    
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_all_active_users() -> List[Dict[str, Any]]:
        """
        Get all active users
        
        Returns:
            List of active users
        """
        try:
            conn = User.get_db_connection()
            try:
                query = """
                    SELECT u.*
                    FROM User u
                    WHERE u.deleted_at IS NULL AND u.is_active = 1
                    ORDER BY u.created_at DESC
                """
                
                users = conn.execute(query).fetchall()
                return [dict(user) for user in users]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting active users: {e}")
            return []
    
    @staticmethod
    def get_user_statistics() -> Dict[str, Any]:
        """
        Get user statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            conn = User.get_db_connection()
            try:
                # Total users
                total_users = conn.execute(
                    'SELECT COUNT(*) as count FROM User WHERE deleted_at IS NULL'
                ).fetchone()['count']
                
                # Active users
                active_users = conn.execute(
                    'SELECT COUNT(*) as count FROM User WHERE deleted_at IS NULL AND is_active = 1'
                ).fetchone()['count']
                
                return {
                    'total_users': total_users,
                    'active_users': active_users
                }
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    @staticmethod
    def update_user_name(user_id: str, name: str) -> Dict[str, Any]:
        """
        Update user name with validation
        
        Args:
            user_id: User ID
            name: New name for the user
            
        Returns:
            Dict with success status, updated name, updated_at, or error info
        """
        result = {
            'success': False,
            'status': 400,
            'message': '',
            'name': None,
            'updated_at': None
        }
        
        try:
            # Validate UUID format
            if not User.is_valid_uuid(user_id):
                result['message'] = User.USER_DOESNT_EXIST
                return result
            
            # Validate name
            if not name or not name.strip():
                result['message'] = User.NAME_CANNOT_BE_EMPTY
                return result
            
            name = name.strip()
            
            # Check if user exists
            existing_user = User.get_user_by_id(user_id)
            if not existing_user:
                result['message'] = User.USER_DOESNT_EXIST
                return result
            
            # Check if name already exists for other users (excluding current user)
            conn = User.get_db_connection()
            try:
                duplicate_user = conn.execute(
                    User.CHECK_DUPLICATE_NAME_QUERY,
                    (name, user_id)
                ).fetchone()
                
                if duplicate_user:
                    result['message'] = User.NAME_ALREADY_EXISTS
                    return result
                
                # Update user name and timestamp
                updated_at = datetime.now().isoformat()
                
                cursor = conn.execute(
                    'UPDATE User SET name = ?, updated_at = ? WHERE user_id = ?',
                    (name, updated_at, user_id)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    result.update({
                        'success': True,
                        'status': 200,
                        'message': User.USER_NAME_UPDATED_SUCCESSFULLY,
                        'name': name,
                        'updated_at': updated_at
                    })
                else:
                    result['message'] = User.USER_DOESNT_EXIST
                    
            finally:
                conn.close()
                
        except Exception as e:
            result.update({
                'status': 500,
                'message': f"Database error: {str(e)}"
            })
        
        return result
    
    @staticmethod
    def soft_delete_user(user_id: str) -> Dict[str, Any]:
        """
        Soft delete user
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with success status, deleted_at, or error info
        """
        result = {
            'success': False,
            'status': 400,
            'message': '',
            'deleted_at': None
        }
        
        try:
            # Validate UUID format
            if not User.is_valid_uuid(user_id):
                result['message'] = User.USER_DOESNT_EXIST
                return result
            
            # Check if user exists (including already deleted users)
            conn = User.get_db_connection()
            try:
                existing_user = conn.execute(
                    'SELECT user_id, deleted_at FROM User WHERE user_id = ?',
                    (user_id,)
                ).fetchone()
                
                if not existing_user:
                    result['message'] = User.USER_DOESNT_EXIST
                    return result
                
                # Set deletion timestamp
                deleted_at = datetime.now().isoformat()
                
                # If user is already deleted, still return success with original deleted_at
                if existing_user['deleted_at']:
                    result.update({
                        'success': True,
                        'status': 200,
                        'message': User.USER_ALREADY_DELETED,
                        'deleted_at': existing_user['deleted_at']
                    })
                    return result
                
                # Soft delete user
                conn.execute(
                    'UPDATE User SET is_active = ?, deleted_at = ? WHERE user_id = ?',
                    (False, deleted_at, user_id)
                )
                
                conn.commit()
                
                result.update({
                    'success': True,
                    'status': 200,
                    'message': User.USER_DELETED_SUCCESSFULLY,
                    'deleted_at': deleted_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result.update({
                'status': 500,
                'message': f"Database error: {str(e)}"
            })
        
        return result 