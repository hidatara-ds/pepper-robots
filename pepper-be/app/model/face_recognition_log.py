#!/usr/bin/env python3
"""
Face Recognition Log Model
Handles face recognition log operations
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class FaceRecognitionLog:
    # Error message constants
    LOG_NOT_FOUND = "Face recognition log not found"
    LOG_CREATED_SUCCESSFULLY = "Face recognition log created successfully"
    LOG_UPDATED_SUCCESSFULLY = "Face recognition log updated successfully"
    LOG_DELETED_SUCCESSFULLY = "Face recognition log deleted successfully"
    USER_ID_REQUIRED = "User ID is required"
    INVALID_LOG_ID_FORMAT = "Invalid log ID format"
    INVALID_MATCH_PERCENTAGE = "Match percentage must be between 0 and 100"
    
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
    def generate_log_id() -> str:
        """Generate unique log ID using UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid_uuid(log_id: str) -> bool:
        """
        Validate if log_id is a valid UUID format
        
        Args:
            log_id: Log ID to validate
            
        Returns:
            True if valid UUID, False otherwise
        """
        try:
            uuid.UUID(log_id)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def create_recognition_log(user_id: str, match_percentage: float = None, 
                             image_input_path: str = None, is_valid: bool = True) -> Dict[str, Any]:
        """
        Create new face recognition log
        
        Args:
            user_id: User ID
            match_percentage: Recognition match percentage (0-100)
            image_input_path: Path to input image
            is_valid: Whether the recognition is valid
            
        Returns:
            Dict with log data or error info
        """
        result = {
            'success': False,
            'face_recognition_log_id': None,
            'message': '',
            'recognized_at': None
        }
        
        try:
            # Validate input
            if not user_id or not user_id.strip():
                result['message'] = FaceRecognitionLog.USER_ID_REQUIRED
                return result
            
            # Validate match percentage if provided
            if match_percentage is not None:
                if not (0 <= match_percentage <= 100):
                    result['message'] = FaceRecognitionLog.INVALID_MATCH_PERCENTAGE
                    return result
            
            # Generate log ID and timestamp
            log_id = FaceRecognitionLog.generate_log_id()
            recognized_at = datetime.now().isoformat()
            updated_at = recognized_at
            
            # Insert log into database
            conn = FaceRecognitionLog.get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO Face_Recognition_Log (
                        face_recognition_log_id, user_id, match_percentage, 
                        image_input_path, is_valid, recognized_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (log_id, user_id.strip(), match_percentage, image_input_path, 
                      1 if is_valid else 0, recognized_at, updated_at))
                conn.commit()
                
                result.update({
                    'success': True,
                    'face_recognition_log_id': log_id,
                    'message': FaceRecognitionLog.LOG_CREATED_SUCCESSFULLY,
                    'recognized_at': recognized_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_log_by_id(log_id: str) -> Optional[Dict[str, Any]]:
        """
        Get recognition log by log_id
        
        Args:
            log_id: Log ID
            
        Returns:
            Log data dict or None if not found
        """
        try:
            conn = FaceRecognitionLog.get_db_connection()
            try:
                log = conn.execute("""
                    SELECT frl.*, u.name as user_name
                    FROM Face_Recognition_Log frl
                    LEFT JOIN User u ON frl.user_id = u.user_id
                    WHERE frl.face_recognition_log_id = ? AND frl.deleted_at IS NULL
                """, (log_id,)).fetchone()
                
                if log:
                    log_dict = dict(log)
                    # Convert is_valid back to boolean
                    log_dict['is_valid'] = bool(log_dict['is_valid'])
                    return log_dict
                
                return None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting recognition log: {e}")
            return None
    
    @staticmethod
    def get_logs_by_user_id(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recognition logs by user_id
        
        Args:
            user_id: User ID
            limit: Maximum number of logs to return
            
        Returns:
            List of log dictionaries
        """
        try:
            conn = FaceRecognitionLog.get_db_connection()
            try:
                logs = conn.execute("""
                    SELECT frl.*, u.name as user_name
                    FROM Face_Recognition_Log frl
                    LEFT JOIN User u ON frl.user_id = u.user_id
                    WHERE frl.user_id = ? AND frl.deleted_at IS NULL
                    ORDER BY frl.recognized_at DESC
                    LIMIT ?
                """, (user_id, limit)).fetchall()
                
                result = []
                for log in logs:
                    log_dict = dict(log)
                    # Convert is_valid back to boolean
                    log_dict['is_valid'] = bool(log_dict['is_valid'])
                    result.append(log_dict)
                
                return result
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting logs by user: {e}")
            return []
    
    @staticmethod
    def update_recognition_log(log_id: str, match_percentage: float = None, 
                             is_valid: bool = None) -> Dict[str, Any]:
        """
        Update recognition log
        
        Args:
            log_id: Log ID
            match_percentage: Recognition match percentage
            is_valid: Whether the recognition is valid
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'updated_at': None
        }
        
        try:
            # Validate log_id format
            if not FaceRecognitionLog.is_valid_uuid(log_id):
                result['message'] = FaceRecognitionLog.INVALID_LOG_ID_FORMAT
                return result
            
            # Check if log exists
            existing_log = FaceRecognitionLog.get_log_by_id(log_id)
            if not existing_log:
                result['message'] = FaceRecognitionLog.LOG_NOT_FOUND
                return result
            
            # Validate match percentage if provided
            if match_percentage is not None:
                if not (0 <= match_percentage <= 100):
                    result['message'] = FaceRecognitionLog.INVALID_MATCH_PERCENTAGE
                    return result
            
            # Prepare update data
            updated_at = datetime.now().isoformat()
            update_fields = []
            update_values = []
            
            if match_percentage is not None:
                update_fields.append("match_percentage = ?")
                update_values.append(match_percentage)
            
            if is_valid is not None:
                update_fields.append("is_valid = ?")
                update_values.append(1 if is_valid else 0)
            
            if not update_fields:
                result['message'] = "No fields to update"
                return result
            
            update_fields.append("updated_at = ?")
            update_values.append(updated_at)
            update_values.append(log_id)
            
            # Update log
            conn = FaceRecognitionLog.get_db_connection()
            try:
                query = f"UPDATE Face_Recognition_Log SET {', '.join(update_fields)} WHERE face_recognition_log_id = ?"
                conn.execute(query, update_values)
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': FaceRecognitionLog.LOG_UPDATED_SUCCESSFULLY,
                    'updated_at': updated_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def soft_delete_log(log_id: str) -> Dict[str, Any]:
        """
        Soft delete recognition log by setting deleted_at timestamp
        
        Args:
            log_id: Log ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'deleted_at': None
        }
        
        try:
            # Validate log_id format
            if not FaceRecognitionLog.is_valid_uuid(log_id):
                result['message'] = FaceRecognitionLog.INVALID_LOG_ID_FORMAT
                return result
            
            # Check if log exists
            existing_log = FaceRecognitionLog.get_log_by_id(log_id)
            if not existing_log:
                result['message'] = FaceRecognitionLog.LOG_NOT_FOUND
                return result
            
            deleted_at = datetime.now().isoformat()
            
            # Soft delete log
            conn = FaceRecognitionLog.get_db_connection()
            try:
                conn.execute("""
                    UPDATE Face_Recognition_Log 
                    SET deleted_at = ?, updated_at = ?
                    WHERE face_recognition_log_id = ?
                """, (deleted_at, deleted_at, log_id))
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': FaceRecognitionLog.LOG_DELETED_SUCCESSFULLY,
                    'deleted_at': deleted_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_all_logs(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all recognition logs with pagination
        
        Args:
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of log dictionaries
        """
        try:
            conn = FaceRecognitionLog.get_db_connection()
            try:
                logs = conn.execute("""
                    SELECT frl.*, u.name as user_name
                    FROM Face_Recognition_Log frl
                    LEFT JOIN User u ON frl.user_id = u.user_id
                    WHERE frl.deleted_at IS NULL
                    ORDER BY frl.recognized_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset)).fetchall()
                
                result = []
                for log in logs:
                    log_dict = dict(log)
                    # Convert is_valid back to boolean
                    log_dict['is_valid'] = bool(log_dict['is_valid'])
                    result.append(log_dict)
                
                return result
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting all logs: {e}")
            return []
    
    @staticmethod
    def get_recognition_statistics() -> Dict[str, Any]:
        """
        Get face recognition statistics
        
        Returns:
            Dict with various statistics
        """
        try:
            conn = FaceRecognitionLog.get_db_connection()
            try:
                # Total recognitions
                total = conn.execute("""
                    SELECT COUNT(*) as count FROM Face_Recognition_Log 
                    WHERE deleted_at IS NULL
                """).fetchone()['count']
                
                # Valid recognitions
                valid = conn.execute("""
                    SELECT COUNT(*) as count FROM Face_Recognition_Log 
                    WHERE is_valid = 1 AND deleted_at IS NULL
                """).fetchone()['count']
                
                # Today's recognitions
                today = datetime.now().date().isoformat()
                today_count = conn.execute("""
                    SELECT COUNT(*) as count FROM Face_Recognition_Log 
                    WHERE DATE(recognized_at) = ? AND deleted_at IS NULL
                """, (today,)).fetchone()['count']
                
                # Average match percentage
                avg_match = conn.execute("""
                    SELECT AVG(match_percentage) as avg_match FROM Face_Recognition_Log 
                    WHERE match_percentage IS NOT NULL AND deleted_at IS NULL
                """).fetchone()['avg_match']
                
                return {
                    'total_recognitions': total,
                    'valid_recognitions': valid,
                    'invalid_recognitions': total - valid,
                    'today_recognitions': today_count,
                    'average_match_percentage': round(avg_match, 2) if avg_match else 0,
                    'success_rate': round((valid / total * 100), 2) if total > 0 else 0
                }
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting recognition statistics: {e}")
            return {
                'total_recognitions': 0,
                'valid_recognitions': 0,
                'invalid_recognitions': 0,
                'today_recognitions': 0,
                'average_match_percentage': 0,
                'success_rate': 0
            } 