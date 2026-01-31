#!/usr/bin/env python3
"""
Configuration Model
Handles configuration operations
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class Configuration:
    # Error message constants
    CONFIGURATION_NOT_FOUND = "Configuration not found"
    CONFIGURATION_CREATED_SUCCESSFULLY = "Configuration created successfully"
    CONFIGURATION_UPDATED_SUCCESSFULLY = "Configuration updated successfully"
    CONFIGURATION_DELETED_SUCCESSFULLY = "Configuration deleted successfully"
    ADMIN_ID_REQUIRED = "Admin ID is required"
    INVALID_CONFIG_ID_FORMAT = "Invalid configuration ID format"
    
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
    def generate_config_id() -> str:
        """Generate unique configuration ID using UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid_uuid(config_id: str) -> bool:
        """
        Validate if config_id is a valid UUID format
        
        Args:
            config_id: Configuration ID to validate
            
        Returns:
            True if valid UUID, False otherwise
        """
        try:
            uuid.UUID(config_id)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def create_configuration(admin_id: str, mobile_app_language: str = "indo", pepper_mode_id: str = None) -> Dict[str, Any]:
        """
        Create new configuration
        
        Args:
            admin_id: Admin ID
            mobile_app_language: Mobile app language (default: "indo")
            pepper_mode_id: Pepper mode ID
            
        Returns:
            Dict with configuration data or error info
        """
        result = {
            'success': False,
            'config_id': None,
            'message': '',
            'created_at': None
        }
        
        try:
            # Validate input
            if not admin_id or not admin_id.strip():
                result['message'] = Configuration.ADMIN_ID_REQUIRED
                return result
            
            # Generate config ID and timestamp
            config_id = Configuration.generate_config_id()
            created_at = datetime.now().isoformat()
            updated_at = created_at
            
            # Insert configuration into database
            conn = Configuration.get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO Configuration (
                        config_id, admin_id, mobile_app_language, pepper_mode_id, 
                        created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (config_id, admin_id, mobile_app_language, pepper_mode_id, created_at, updated_at))
                conn.commit()
                
                result.update({
                    'success': True,
                    'config_id': config_id,
                    'message': Configuration.CONFIGURATION_CREATED_SUCCESSFULLY,
                    'created_at': created_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_configuration_by_id(config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration by config_id
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Configuration data dict or None if not found
        """
        try:
            conn = Configuration.get_db_connection()
            try:
                config = conn.execute("""
                    SELECT * FROM Configuration 
                    WHERE config_id = ? AND deleted_at IS NULL
                """, (config_id,)).fetchone()
                
                return dict(config) if config else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting configuration: {e}")
            return None
    
    @staticmethod
    def get_configuration_by_admin_id(admin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration by admin_id
        
        Args:
            admin_id: Admin ID
            
        Returns:
            Configuration data dict or None if not found
        """
        try:
            conn = Configuration.get_db_connection()
            try:
                config = conn.execute("""
                    SELECT * FROM Configuration 
                    WHERE admin_id = ? AND deleted_at IS NULL
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (admin_id,)).fetchone()
                
                return dict(config) if config else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting configuration by admin: {e}")
            return None
    
    @staticmethod
    def update_configuration(config_id: str, mobile_app_language: str = None, pepper_mode_id: str = None) -> Dict[str, Any]:
        """
        Update configuration
        
        Args:
            config_id: Configuration ID (UUID or integer string)
            mobile_app_language: Mobile app language
            pepper_mode_id: Pepper mode ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'updated_at': None
        }
        
        try:
            # Validate config_id format - support both UUID and integer
            config_id_str = str(config_id)
            if not (Configuration.is_valid_uuid(config_id_str) or config_id_str.isdigit()):
                result['message'] = Configuration.INVALID_CONFIG_ID_FORMAT
                return result
            
            # Check if configuration exists
            existing_config = Configuration.get_configuration_by_id(config_id)
            if not existing_config:
                result['message'] = Configuration.CONFIGURATION_NOT_FOUND
                return result
            
            # Prepare update data
            updated_at = datetime.now().isoformat()
            update_fields = []
            update_values = []
            
            if mobile_app_language is not None:
                update_fields.append("mobile_app_language = ?")
                update_values.append(mobile_app_language)
            
            if pepper_mode_id is not None:
                update_fields.append("pepper_mode_id = ?")
                update_values.append(pepper_mode_id)
            
            if not update_fields:
                result['message'] = "No fields to update"
                return result
            
            update_fields.append("updated_at = ?")
            update_values.append(updated_at)
            update_values.append(config_id)
            
            # Update configuration
            conn = Configuration.get_db_connection()
            try:
                query = f"UPDATE Configuration SET {', '.join(update_fields)} WHERE config_id = ?"
                conn.execute(query, update_values)
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': Configuration.CONFIGURATION_UPDATED_SUCCESSFULLY,
                    'updated_at': updated_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def soft_delete_configuration(config_id: str) -> Dict[str, Any]:
        """
        Soft delete configuration by setting deleted_at timestamp
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'deleted_at': None
        }
        
        try:
            # Validate config_id format
            if not Configuration.is_valid_uuid(config_id):
                result['message'] = Configuration.INVALID_CONFIG_ID_FORMAT
                return result
            
            # Check if configuration exists
            existing_config = Configuration.get_configuration_by_id(config_id)
            if not existing_config:
                result['message'] = Configuration.CONFIGURATION_NOT_FOUND
                return result
            
            deleted_at = datetime.now().isoformat()
            
            # Soft delete configuration
            conn = Configuration.get_db_connection()
            try:
                conn.execute("""
                    UPDATE Configuration 
                    SET deleted_at = ?, updated_at = ?
                    WHERE config_id = ?
                """, (deleted_at, deleted_at, config_id))
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': Configuration.CONFIGURATION_DELETED_SUCCESSFULLY,
                    'deleted_at': deleted_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_all_configurations() -> List[Dict[str, Any]]:
        """
        Get all active configurations
        
        Returns:
            List of configuration dictionaries
        """
        try:
            conn = Configuration.get_db_connection()
            try:
                configs = conn.execute("""
                    SELECT c.*, a.email as admin_email
                    FROM Configuration c
                    LEFT JOIN Admin a ON c.admin_id = a.admin_id
                    WHERE c.deleted_at IS NULL
                    ORDER BY c.created_at DESC
                """).fetchall()
                
                return [dict(config) for config in configs]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting all configurations: {e}")
            return [] 