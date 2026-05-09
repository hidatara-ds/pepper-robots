#!/usr/bin/env python3
"""
Language Model
Handles language operations with voice configurations
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class Language:
    # Error message constants
    LANGUAGE_NOT_FOUND = "Language not found"
    LANGUAGE_CREATED_SUCCESSFULLY = "Language created successfully"
    LANGUAGE_UPDATED_SUCCESSFULLY = "Language updated successfully"
    LANGUAGE_DELETED_SUCCESSFULLY = "Language deleted successfully"
    LANGUAGE_ID_REQUIRED = "Language ID is required"
    
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
    def create_language(language_id: str, voice_1: str = None, voice_2: str = None, 
                       voice_3: str = None, voice_4: str = None, voice_5: str = None) -> Dict[str, Any]:
        """
        Create new language with voice configurations
        
        Args:
            language_id: Language identifier (e.g., "en", "indo")
            voice_1: Voice configuration 1
            voice_2: Voice configuration 2
            voice_3: Voice configuration 3
            voice_4: Voice configuration 4
            voice_5: Voice configuration 5
            
        Returns:
            Dict with language data or error info
        """
        result = {
            'success': False,
            'language_id': None,
            'message': '',
            'created_at': None
        }
        
        try:
            # Validate input
            if not language_id or not language_id.strip():
                result['message'] = Language.LANGUAGE_ID_REQUIRED
                return result
            
            language_id = language_id.strip()
            created_at = datetime.now().isoformat()
            
            # Insert language into database
            conn = Language.get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO Language (
                        language_id, voice_1, voice_2, voice_3, voice_4, voice_5
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (language_id, voice_1, voice_2, voice_3, voice_4, voice_5))
                conn.commit()
                
                result.update({
                    'success': True,
                    'language_id': language_id,
                    'message': Language.LANGUAGE_CREATED_SUCCESSFULLY,
                    'created_at': created_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_language_by_id(language_id: str) -> Optional[Dict[str, Any]]:
        """
        Get language by language_id
        
        Args:
            language_id: Language ID
            
        Returns:
            Language data dict or None if not found
        """
        try:
            conn = Language.get_db_connection()
            try:
                language = conn.execute("""
                    SELECT * FROM Language 
                    WHERE language_id = ?
                """, (language_id,)).fetchone()
                
                return dict(language) if language else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting language: {e}")
            return None
    
    @staticmethod
    def update_language(language_id: str, voice_1: str = None, voice_2: str = None,
                       voice_3: str = None, voice_4: str = None, voice_5: str = None) -> Dict[str, Any]:
        """
        Update language voice configurations
        
        Args:
            language_id: Language ID
            voice_1: Voice configuration 1
            voice_2: Voice configuration 2
            voice_3: Voice configuration 3
            voice_4: Voice configuration 4
            voice_5: Voice configuration 5
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Check if language exists
            existing_language = Language.get_language_by_id(language_id)
            if not existing_language:
                result['message'] = Language.LANGUAGE_NOT_FOUND
                return result
            
            # Prepare update data
            update_fields = []
            update_values = []
            
            if voice_1 is not None:
                update_fields.append("voice_1 = ?")
                update_values.append(voice_1)
            
            if voice_2 is not None:
                update_fields.append("voice_2 = ?")
                update_values.append(voice_2)
                
            if voice_3 is not None:
                update_fields.append("voice_3 = ?")
                update_values.append(voice_3)
                
            if voice_4 is not None:
                update_fields.append("voice_4 = ?")
                update_values.append(voice_4)
                
            if voice_5 is not None:
                update_fields.append("voice_5 = ?")
                update_values.append(voice_5)
            
            if not update_fields:
                result['message'] = "No fields to update"
                return result
            
            update_values.append(language_id)
            
            # Update language
            conn = Language.get_db_connection()
            try:
                query = f"UPDATE Language SET {', '.join(update_fields)} WHERE language_id = ?"
                conn.execute(query, update_values)
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': Language.LANGUAGE_UPDATED_SUCCESSFULLY
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def delete_language(language_id: str) -> Dict[str, Any]:
        """
        Delete language (hard delete since this table doesn't have soft delete)
        
        Args:
            language_id: Language ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Check if language exists
            existing_language = Language.get_language_by_id(language_id)
            if not existing_language:
                result['message'] = Language.LANGUAGE_NOT_FOUND
                return result
            
            # Delete language
            conn = Language.get_db_connection()
            try:
                conn.execute("DELETE FROM Language WHERE language_id = ?", (language_id,))
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': Language.LANGUAGE_DELETED_SUCCESSFULLY
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_all_languages() -> List[Dict[str, Any]]:
        """
        Get all languages
        
        Returns:
            List of language dictionaries
        """
        try:
            conn = Language.get_db_connection()
            try:
                languages = conn.execute("""
                    SELECT * FROM Language 
                    ORDER BY language_id
                """).fetchall()
                
                return [dict(language) for language in languages]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting all languages: {e}")
            return []
    
    @staticmethod
    def get_voice_by_language_and_number(language_id: str, voice_number: int) -> Optional[str]:
        """
        Get specific voice configuration by language and voice number
        
        Args:
            language_id: Language ID
            voice_number: Voice number (1-5)
            
        Returns:
            Voice configuration string or None if not found
        """
        try:
            if voice_number < 1 or voice_number > 5:
                return None
                
            language = Language.get_language_by_id(language_id)
            if not language:
                return None
            
            voice_field = f"voice_{voice_number}"
            return language.get(voice_field)
            
        except Exception as e:
            print(f"Error getting voice: {e}")
            return None 