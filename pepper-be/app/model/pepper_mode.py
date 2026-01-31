#!/usr/bin/env python3
"""
Pepper Mode Model
Handles pepper mode operations
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class PepperMode:
    # Error message constants
    PEPPER_MODE_NOT_FOUND = "Pepper mode not found"
    PEPPER_MODE_CREATED_SUCCESSFULLY = "Pepper mode created successfully"
    PEPPER_MODE_UPDATED_SUCCESSFULLY = "Pepper mode updated successfully"
    PEPPER_MODE_DELETED_SUCCESSFULLY = "Pepper mode deleted successfully"
    LANGUAGE_REQUIRED = "Language is required"
    VOICE_REQUIRED = "Voice is required"
    INVALID_PEPPER_MODE_ID_FORMAT = "Invalid pepper mode ID format"
    
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
    def generate_pepper_mode_id() -> str:
        """Generate unique pepper mode ID using UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid_uuid(pepper_mode_id: str) -> bool:
        """
        Validate if pepper_mode_id is a valid UUID format
        
        Args:
            pepper_mode_id: Pepper mode ID to validate
            
        Returns:
            True if valid UUID, False otherwise
        """
        try:
            uuid.UUID(pepper_mode_id)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def create_pepper_mode(language: str, voice: str) -> Dict[str, Any]:
        """
        Create new pepper mode
        
        Args:
            language: Language setting
            voice: Voice setting
            
        Returns:
            Dict with pepper mode data or error info
        """
        result = {
            'success': False,
            'pepper_mode_id': None,
            'message': '',
            'created_at': None
        }
        
        try:
            # Validate input
            if not language or not language.strip():
                result['message'] = PepperMode.LANGUAGE_REQUIRED
                return result
                
            if not voice or not voice.strip():
                result['message'] = PepperMode.VOICE_REQUIRED
                return result
            
            # Generate pepper mode ID and timestamp
            pepper_mode_id = PepperMode.generate_pepper_mode_id()
            created_at = datetime.now().isoformat()
            updated_at = created_at
            
            # Insert pepper mode into database
            conn = PepperMode.get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO Pepper_Mode (
                        pepper_mode_id, language, voice, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (pepper_mode_id, language.strip(), voice.strip(), created_at, updated_at))
                conn.commit()
                
                result.update({
                    'success': True,
                    'pepper_mode_id': pepper_mode_id,
                    'message': PepperMode.PEPPER_MODE_CREATED_SUCCESSFULLY,
                    'created_at': created_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_pepper_mode_by_id(pepper_mode_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pepper mode by pepper_mode_id
        
        Args:
            pepper_mode_id: Pepper mode ID
            
        Returns:
            Pepper mode data dict or None if not found
        """
        try:
            conn = PepperMode.get_db_connection()
            try:
                pepper_mode = conn.execute("""
                    SELECT * FROM Pepper_Mode 
                    WHERE pepper_mode_id = ? AND deleted_at IS NULL
                """, (pepper_mode_id,)).fetchone()
                
                return dict(pepper_mode) if pepper_mode else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting pepper mode: {e}")
            return None
    
    @staticmethod
    def update_pepper_mode(pepper_mode_id: str, language: str = None, voice: str = None) -> Dict[str, Any]:
        """
        Update pepper mode
        
        Args:
            pepper_mode_id: Pepper mode ID
            language: Language setting
            voice: Voice setting
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'updated_at': None
        }
        
        try:
            # Validate pepper_mode_id format
            if not PepperMode.is_valid_uuid(pepper_mode_id):
                result['message'] = PepperMode.INVALID_PEPPER_MODE_ID_FORMAT
                return result
            
            # Check if pepper mode exists
            existing_mode = PepperMode.get_pepper_mode_by_id(pepper_mode_id)
            if not existing_mode:
                result['message'] = PepperMode.PEPPER_MODE_NOT_FOUND
                return result
            
            # Prepare update data
            updated_at = datetime.now().isoformat()
            update_fields = []
            update_values = []
            
            if language is not None:
                update_fields.append("language = ?")
                update_values.append(language.strip())
            
            if voice is not None:
                update_fields.append("voice = ?")
                update_values.append(voice.strip())
            
            if not update_fields:
                result['message'] = "No fields to update"
                return result
            
            update_fields.append("updated_at = ?")
            update_values.append(updated_at)
            update_values.append(pepper_mode_id)
            
            # Update pepper mode
            conn = PepperMode.get_db_connection()
            try:
                query = f"UPDATE Pepper_Mode SET {', '.join(update_fields)} WHERE pepper_mode_id = ?"
                conn.execute(query, update_values)
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': PepperMode.PEPPER_MODE_UPDATED_SUCCESSFULLY,
                    'updated_at': updated_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def soft_delete_pepper_mode(pepper_mode_id: str) -> Dict[str, Any]:
        """
        Soft delete pepper mode by setting deleted_at timestamp
        
        Args:
            pepper_mode_id: Pepper mode ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'deleted_at': None
        }
        
        try:
            # Validate pepper_mode_id format
            if not PepperMode.is_valid_uuid(pepper_mode_id):
                result['message'] = PepperMode.INVALID_PEPPER_MODE_ID_FORMAT
                return result
            
            # Check if pepper mode exists
            existing_mode = PepperMode.get_pepper_mode_by_id(pepper_mode_id)
            if not existing_mode:
                result['message'] = PepperMode.PEPPER_MODE_NOT_FOUND
                return result
            
            deleted_at = datetime.now().isoformat()
            
            # Soft delete pepper mode
            conn = PepperMode.get_db_connection()
            try:
                conn.execute("""
                    UPDATE Pepper_Mode 
                    SET deleted_at = ?, updated_at = ?
                    WHERE pepper_mode_id = ?
                """, (deleted_at, deleted_at, pepper_mode_id))
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': PepperMode.PEPPER_MODE_DELETED_SUCCESSFULLY,
                    'deleted_at': deleted_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_all_pepper_modes() -> List[Dict[str, Any]]:
        """
        Get all active pepper modes
        
        Returns:
            List of pepper mode dictionaries
        """
        try:
            conn = PepperMode.get_db_connection()
            try:
                modes = conn.execute("""
                    SELECT * FROM Pepper_Mode 
                    WHERE deleted_at IS NULL
                    ORDER BY created_at DESC
                """).fetchall()
                
                return [dict(mode) for mode in modes]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting all pepper modes: {e}")
            return []
    
    @staticmethod
    def get_pepper_modes_by_language(language: str) -> List[Dict[str, Any]]:
        """
        Get pepper modes by language
        
        Args:
            language: Language to filter by
            
        Returns:
            List of pepper mode dictionaries
        """
        try:
            conn = PepperMode.get_db_connection()
            try:
                modes = conn.execute("""
                    SELECT * FROM Pepper_Mode 
                    WHERE language = ? AND deleted_at IS NULL
                    ORDER BY created_at DESC
                """, (language,)).fetchall()
                
                return [dict(mode) for mode in modes]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting pepper modes by language: {e}")
            return [] 