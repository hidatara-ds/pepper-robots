#!/usr/bin/env python3
"""
Kamus Bahasa Model
Handles dictionary/translation operations
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class KamusBahasa:
    # Error message constants
    ENTRY_NOT_FOUND = "Dictionary entry not found"
    ENTRY_CREATED_SUCCESSFULLY = "Dictionary entry created successfully"
    ENTRY_UPDATED_SUCCESSFULLY = "Dictionary entry updated successfully"
    ENTRY_DELETED_SUCCESSFULLY = "Dictionary entry deleted successfully"
    TEXT_INDO_REQUIRED = "Indonesian text is required"
    TEXT_ENGLISH_REQUIRED = "English text is required"
    
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
    def create_entry(text_indo: str, text_english: str, is_custom: bool = False) -> Dict[str, Any]:
        """
        Create new dictionary entry
        
        Args:
            text_indo: Indonesian text
            text_english: English text
            is_custom: Whether this is a custom entry
            
        Returns:
            Dict with entry data or error info
        """
        result = {
            'success': False,
            'kamus_bahasa_id': None,
            'message': '',
            'created_at': None
        }
        
        try:
            # Validate input
            if not text_indo or not text_indo.strip():
                result['message'] = KamusBahasa.TEXT_INDO_REQUIRED
                return result
                
            if not text_english or not text_english.strip():
                result['message'] = KamusBahasa.TEXT_ENGLISH_REQUIRED
                return result
            
            # Create timestamp
            created_at = datetime.now().isoformat()
            updated_at = created_at
            
            # Insert entry into database
            conn = KamusBahasa.get_db_connection()
            try:
                cursor = conn.execute("""
                    INSERT INTO Kamus_Bahasa (
                        text_indo, text_english, is_custom, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (text_indo.strip(), text_english.strip(), 1 if is_custom else 0, 
                      created_at, updated_at))
                conn.commit()
                
                # Get the inserted ID
                entry_id = cursor.lastrowid
                
                result.update({
                    'success': True,
                    'kamus_bahasa_id': entry_id,
                    'message': KamusBahasa.ENTRY_CREATED_SUCCESSFULLY,
                    'created_at': created_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_entry_by_id(entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get dictionary entry by ID
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Entry data dict or None if not found
        """
        try:
            conn = KamusBahasa.get_db_connection()
            try:
                entry = conn.execute("""
                    SELECT * FROM Kamus_Bahasa 
                    WHERE kamus_bahasa_id = ? AND deleted_at IS NULL
                """, (entry_id,)).fetchone()
                
                if entry:
                    entry_dict = dict(entry)
                    # Convert is_custom back to boolean
                    entry_dict['is_custom'] = bool(entry_dict['is_custom'])
                    return entry_dict
                
                return None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting dictionary entry: {e}")
            return None
    
    @staticmethod
    def search_entries(search_term: str, language: str = "both") -> List[Dict[str, Any]]:
        """
        Search dictionary entries
        
        Args:
            search_term: Term to search for
            language: Which language to search ("indo", "english", "both")
            
        Returns:
            List of matching entries
        """
        try:
            conn = KamusBahasa.get_db_connection()
            try:
                search_pattern = f"%{search_term.strip()}%"
                
                if language == "indo":
                    query = """
                        SELECT * FROM Kamus_Bahasa 
                        WHERE text_indo LIKE ? AND deleted_at IS NULL
                        ORDER BY text_indo
                    """
                    params = (search_pattern,)
                elif language == "english":
                    query = """
                        SELECT * FROM Kamus_Bahasa 
                        WHERE text_english LIKE ? AND deleted_at IS NULL
                        ORDER BY text_english
                    """
                    params = (search_pattern,)
                else:  # both
                    query = """
                        SELECT * FROM Kamus_Bahasa 
                        WHERE (text_indo LIKE ? OR text_english LIKE ?) AND deleted_at IS NULL
                        ORDER BY text_indo
                    """
                    params = (search_pattern, search_pattern)
                
                entries = conn.execute(query, params).fetchall()
                
                result = []
                for entry in entries:
                    entry_dict = dict(entry)
                    # Convert is_custom back to boolean
                    entry_dict['is_custom'] = bool(entry_dict['is_custom'])
                    result.append(entry_dict)
                
                return result
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error searching dictionary entries: {e}")
            return []
    
    @staticmethod
    def update_entry(entry_id: int, text_indo: str = None, text_english: str = None, 
                    is_custom: bool = None) -> Dict[str, Any]:
        """
        Update dictionary entry
        
        Args:
            entry_id: Entry ID
            text_indo: Indonesian text
            text_english: English text
            is_custom: Whether this is a custom entry
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'updated_at': None
        }
        
        try:
            # Check if entry exists
            existing_entry = KamusBahasa.get_entry_by_id(entry_id)
            if not existing_entry:
                result['message'] = KamusBahasa.ENTRY_NOT_FOUND
                return result
            
            # Prepare update data
            updated_at = datetime.now().isoformat()
            update_fields = []
            update_values = []
            
            if text_indo is not None:
                update_fields.append("text_indo = ?")
                update_values.append(text_indo.strip())
            
            if text_english is not None:
                update_fields.append("text_english = ?")
                update_values.append(text_english.strip())
                
            if is_custom is not None:
                update_fields.append("is_custom = ?")
                update_values.append(1 if is_custom else 0)
            
            if not update_fields:
                result['message'] = "No fields to update"
                return result
            
            update_fields.append("updated_at = ?")
            update_values.append(updated_at)
            update_values.append(entry_id)
            
            # Update entry
            conn = KamusBahasa.get_db_connection()
            try:
                query = f"UPDATE Kamus_Bahasa SET {', '.join(update_fields)} WHERE kamus_bahasa_id = ?"
                conn.execute(query, update_values)
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': KamusBahasa.ENTRY_UPDATED_SUCCESSFULLY,
                    'updated_at': updated_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def soft_delete_entry(entry_id: int) -> Dict[str, Any]:
        """
        Soft delete dictionary entry by ID
        Sets deleted_at timestamp.
        
        Args:
            entry_id: Entry ID to soft-delete
            
        Returns:
            Dict with success status, message, and deleted_at timestamp
        """
        result = {
            'success': False,
            'message': '',
            'deleted_at': None
        }
        
        try:
            # First, check if the entry exists and is not already deleted
            conn = KamusBahasa.get_db_connection()
            try:
                existing_entry = conn.execute("""
                    SELECT kamus_bahasa_id 
                    FROM Kamus_Bahasa 
                    WHERE kamus_bahasa_id = ? AND deleted_at IS NULL
                """, (entry_id,)).fetchone()
                
                if not existing_entry:
                    result['message'] = KamusBahasa.ENTRY_NOT_FOUND
                    return result
                
                # If entry exists, perform the soft delete
                deleted_at = datetime.now().isoformat()
                
                conn.execute("""
                    UPDATE Kamus_Bahasa 
                    SET deleted_at = ?
                    WHERE kamus_bahasa_id = ?
                """, (deleted_at, entry_id))
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': KamusBahasa.ENTRY_DELETED_SUCCESSFULLY,
                    'deleted_at': deleted_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_all_entries(is_custom_only: bool = False, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all dictionary entries with pagination
        
        Args:
            is_custom_only: Whether to get only custom entries
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of entry dictionaries
        """
        try:
            conn = KamusBahasa.get_db_connection()
            try:
                if is_custom_only:
                    query = """
                        SELECT * FROM Kamus_Bahasa 
                        WHERE is_custom = 1 AND deleted_at IS NULL
                        ORDER BY text_indo
                        LIMIT ? OFFSET ?
                    """
                else:
                    query = """
                        SELECT * FROM Kamus_Bahasa 
                        WHERE deleted_at IS NULL
                        ORDER BY text_indo
                        LIMIT ? OFFSET ?
                    """
                
                entries = conn.execute(query, (limit, offset)).fetchall()
                
                result = []
                for entry in entries:
                    entry_dict = dict(entry)
                    # Convert is_custom back to boolean
                    entry_dict['is_custom'] = bool(entry_dict['is_custom'])
                    result.append(entry_dict)
                
                return result
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting all dictionary entries: {e}")
            return []

    @staticmethod
    def get_text_list_with_language() -> List[Dict[str, Any]]:
        """
        Get dictionary entries formatted for /kamus/list endpoint
        Returns text based on Configuration.mobile_app_language setting
        """
        try:
            conn = KamusBahasa.get_db_connection()
            try:
                config = conn.execute("""
                    SELECT mobile_app_language 
                    FROM Configuration 
                    WHERE deleted_at IS NULL 
                    ORDER BY created_at DESC
                    LIMIT 1
                """).fetchone()
                
                language = config['mobile_app_language'] if config else "indo"
                text_field = "text_indo" if language == "indo" else "text_english"
                
                query = f"""
                    SELECT kamus_bahasa_id, {text_field} as text, is_custom, created_at
                    FROM Kamus_Bahasa 
                    WHERE deleted_at IS NULL
                    ORDER BY created_at DESC
                """
                
                entries = conn.execute(query).fetchall()
                
                result = []
                for row in entries:
                    entry_dict = dict(row)
                    # Convert is_custom to boolean
                    entry_dict['is_custom'] = bool(entry_dict['is_custom'])
                    result.append(entry_dict)
                
                return result
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting text list with language: {e}")
            return []

    @staticmethod
    def check_text_exists(text: str) -> bool:
        """
        Check if text already exists in Kamus_Bahasa table (case-insensitive).
        """
        try:
            conn = KamusBahasa.get_db_connection()
            try:
                text_lower = text.lower().strip()
                existing = conn.execute("""
                    SELECT 1 FROM Kamus_Bahasa 
                    WHERE (LOWER(text_indo) = ? OR LOWER(text_english) = ?) AND deleted_at IS NULL
                """, (text_lower, text_lower)).fetchone()
                return existing is not None
            finally:
                conn.close()
        except Exception as e:
            print(f"Error checking text exists: {e}")
            return False

    @staticmethod
    def create_entry_with_translation(input_text: str) -> Dict[str, Any]:
        """
        Create new dictionary entry with auto-translation for /kamus/add endpoint.
        """
        result = {'success': False, 'message': ''}
        try:
            from app.utils.translation_helper import TranslationHelper
            
            if not input_text or not input_text.strip():
                result['message'] = "Text cannot be empty"
                return result
            
            text = input_text.strip()
            
            if KamusBahasa.check_text_exists(text):
                result['message'] = "Text already exists"
                return result
            
            translation_result = TranslationHelper.process_text_for_kamus(text)
            text_indo = translation_result['text_indo']
            text_english = translation_result['text_english']
            
            created_at = datetime.now().isoformat()
            
            conn = KamusBahasa.get_db_connection()
            try:
                cursor = conn.execute("""
                    INSERT INTO Kamus_Bahasa (text_indo, text_english, is_custom, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (text_indo, text_english, 1, created_at, created_at))
                conn.commit()
                
                entry_id = cursor.lastrowid
                
                config = conn.execute("SELECT mobile_app_language FROM Configuration WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 1").fetchone()
                language = config['mobile_app_language'] if config else "indo"
                response_text = text_indo if language == "indo" else text_english
                
                result.update({
                    'success': True, 'kamus_bahasa_id': entry_id, 'text': response_text,
                    'is_custom': True, 'created_at': created_at,
                    'message': KamusBahasa.ENTRY_CREATED_SUCCESSFULLY
                })
            finally:
                conn.close()
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result 

    @staticmethod
    def update_entry_with_translation(entry_id: int, input_text: str) -> Dict[str, Any]:
        """
        Update existing dictionary entry with auto-translation for /kamus/edit endpoint.
        
        Args:
            entry_id: ID of the entry to update
            input_text: New text input (can be Indonesian or English)
            
        Returns:
            Dict with success status, entry data, and message
        """
        result = {'success': False, 'message': ''}
        
        try:
            from app.utils.translation_helper import TranslationHelper
            
            # Validate input text
            if not input_text or not input_text.strip():
                result['message'] = "Text cannot be empty"
                return result
            
            text = input_text.strip()
            
            # Check if entry exists
            existing_entry = KamusBahasa.get_entry_by_id(entry_id)
            if not existing_entry:
                result['message'] = "Dictionary entry not found"
                return result
            
            # Check if new text already exists in other entries (excluding current entry)
            conn = KamusBahasa.get_db_connection()
            try:
                text_lower = text.lower().strip()
                existing_text = conn.execute("""
                    SELECT 1 FROM Kamus_Bahasa 
                    WHERE (LOWER(text_indo) = ? OR LOWER(text_english) = ?) 
                    AND deleted_at IS NULL 
                    AND kamus_bahasa_id != ?
                """, (text_lower, text_lower, entry_id)).fetchone()
                
                if existing_text:
                    result['message'] = "Text already exists in another entry"
                    return result
                
                # Process text with auto-translation
                translation_result = TranslationHelper.process_text_for_kamus(text)
                text_indo = translation_result['text_indo']
                text_english = translation_result['text_english']
                
                # Update entry in database
                updated_at = datetime.now().isoformat()
                
                conn.execute("""
                    UPDATE Kamus_Bahasa 
                    SET text_indo = ?, text_english = ?, updated_at = ?
                    WHERE kamus_bahasa_id = ? AND deleted_at IS NULL
                """, (text_indo, text_english, updated_at, entry_id))
                conn.commit()
                
                # Get configuration for response text selection
                config = conn.execute("""
                    SELECT mobile_app_language 
                    FROM Configuration 
                    WHERE deleted_at IS NULL 
                    ORDER BY created_at DESC
                    LIMIT 1
                """).fetchone()
                
                language = config['mobile_app_language'] if config else "indo"
                response_text = text_indo if language == "indo" else text_english
                
                # Build success response
                result.update({
                    'success': True,
                    'kamus_bahasa_id': entry_id,
                    'text': response_text,
                    'is_custom': bool(existing_entry['is_custom']),
                    'created_at': existing_entry['created_at'],
                    'message': KamusBahasa.ENTRY_UPDATED_SUCCESSFULLY
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result