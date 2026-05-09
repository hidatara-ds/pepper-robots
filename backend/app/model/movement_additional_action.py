#!/usr/bin/env python3
"""
Movement Additional Action Model
Handles additional action operations for movement commands
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class MovementAdditionalAction:
    # Error message constants
    ACTION_NOT_FOUND = "Additional action not found"
    ACTION_CREATED_SUCCESSFULLY = "Additional action created successfully"
    ACTION_UPDATED_SUCCESSFULLY = "Additional action updated successfully"
    ACTION_DELETED_SUCCESSFULLY = "Additional action deleted successfully"
    MOVEMENT_COMMAND_ID_REQUIRED = "Movement command ID is required"
    ACTION_NAME_REQUIRED = "Action name is required"
    INVALID_ACTION_ID_FORMAT = "Invalid action ID format"
    ACTION_NAME_ALREADY_EXISTS = "Action name already exists for this command"
    
    # Common action types
    ACTION_TYPES = [
        "SPEAK", "PLAY_SOUND", "LED_ON", "LED_OFF", "WAIT", 
        "TAKE_PHOTO", "RECORD_VIDEO", "GESTURE_WAVE", "GESTURE_POINT",
        "DISPLAY_TEXT", "DISPLAY_IMAGE", "PLAY_ANIMATION"
    ]
    
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
    def generate_action_id() -> str:
        """Generate unique action ID using UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid_uuid(action_id: str) -> bool:
        """
        Validate if action_id is a valid UUID format
        
        Args:
            action_id: Action ID to validate
            
        Returns:
            True if valid UUID, False otherwise
        """
        try:
            uuid.UUID(action_id)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def action_name_exists_for_command(movement_command_id: str, action_name: str, 
                                      exclude_id: str = None) -> bool:
        """
        Check if action name already exists for a specific command
        
        Args:
            movement_command_id: Movement command ID
            action_name: Action name to check
            exclude_id: Action ID to exclude from check (for updates)
            
        Returns:
            True if name exists, False otherwise
        """
        try:
            conn = MovementAdditionalAction.get_db_connection()
            try:
                if exclude_id:
                    result = conn.execute("""
                        SELECT COUNT(*) as count FROM Movement_Additional_Action 
                        WHERE movement_command_id = ? 
                        AND LOWER(action_name) = LOWER(?) 
                        AND movement_additional_action_id != ? 
                        AND deleted_at IS NULL
                    """, (movement_command_id, action_name.strip(), exclude_id)).fetchone()
                else:
                    result = conn.execute("""
                        SELECT COUNT(*) as count FROM Movement_Additional_Action 
                        WHERE movement_command_id = ? 
                        AND LOWER(action_name) = LOWER(?) 
                        AND deleted_at IS NULL
                    """, (movement_command_id, action_name.strip())).fetchone()
                
                return result['count'] > 0
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error checking action name existence: {e}")
            return False
    
    @staticmethod
    def create_action(movement_command_id: str, action_name: str) -> Dict[str, Any]:
        """
        Create new additional action
        
        Args:
            movement_command_id: Movement command ID
            action_name: Name/type of the action
            
        Returns:
            Dict with action data or error info
        """
        result = {
            'success': False,
            'movement_additional_action_id': None,
            'message': '',
            'created_at': None
        }
        
        try:
            # Validate input
            if not movement_command_id or not movement_command_id.strip():
                result['message'] = MovementAdditionalAction.MOVEMENT_COMMAND_ID_REQUIRED
                return result
                
            if not action_name or not action_name.strip():
                result['message'] = MovementAdditionalAction.ACTION_NAME_REQUIRED
                return result
            
            # Check if action name already exists for this command
            if MovementAdditionalAction.action_name_exists_for_command(movement_command_id, action_name):
                result['message'] = MovementAdditionalAction.ACTION_NAME_ALREADY_EXISTS
                return result
            
            # Generate action ID and timestamp
            action_id = MovementAdditionalAction.generate_action_id()
            created_at = datetime.now().isoformat()
            updated_at = created_at
            
            # Insert action into database
            conn = MovementAdditionalAction.get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO Movement_Additional_Action (
                        movement_additional_action_id, movement_command_id, action_name, 
                        created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (action_id, movement_command_id.strip(), action_name.strip(), 
                      created_at, updated_at))
                conn.commit()
                
                result.update({
                    'success': True,
                    'movement_additional_action_id': action_id,
                    'message': MovementAdditionalAction.ACTION_CREATED_SUCCESSFULLY,
                    'created_at': created_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_action_by_id(action_id: str) -> Optional[Dict[str, Any]]:
        """
        Get additional action by ID
        
        Args:
            action_id: Action ID
            
        Returns:
            Action data dict or None if not found
        """
        try:
            conn = MovementAdditionalAction.get_db_connection()
            try:
                action = conn.execute("""
                    SELECT maa.*, mc.movement_type, ms.movement_name
                    FROM Movement_Additional_Action maa
                    LEFT JOIN Movement_Command mc ON maa.movement_command_id = mc.movement_command_id
                    LEFT JOIN Movement_Sequence ms ON mc.robot_movement_id = ms.movement_sequence_id
                    WHERE maa.movement_additional_action_id = ? AND maa.deleted_at IS NULL
                """, (action_id,)).fetchone()
                
                return dict(action) if action else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting additional action: {e}")
            return None
    
    @staticmethod
    def get_actions_by_command_id(movement_command_id: str) -> List[Dict[str, Any]]:
        """
        Get actions by movement command ID
        
        Args:
            movement_command_id: Movement command ID
            
        Returns:
            List of action dictionaries
        """
        try:
            conn = MovementAdditionalAction.get_db_connection()
            try:
                actions = conn.execute("""
                    SELECT maa.*, mc.movement_type, ms.movement_name
                    FROM Movement_Additional_Action maa
                    LEFT JOIN Movement_Command mc ON maa.movement_command_id = mc.movement_command_id
                    LEFT JOIN Movement_Sequence ms ON mc.robot_movement_id = ms.movement_sequence_id
                    WHERE maa.movement_command_id = ? AND maa.deleted_at IS NULL
                    ORDER BY maa.created_at ASC
                """, (movement_command_id,)).fetchall()
                
                return [dict(action) for action in actions]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting actions by command ID: {e}")
            return []
    
    @staticmethod
    def update_action(action_id: str, action_name: str = None) -> Dict[str, Any]:
        """
        Update additional action
        
        Args:
            action_id: Action ID
            action_name: Action name
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'updated_at': None
        }
        
        try:
            # Validate action_id format
            if not MovementAdditionalAction.is_valid_uuid(action_id):
                result['message'] = MovementAdditionalAction.INVALID_ACTION_ID_FORMAT
                return result
            
            # Check if action exists
            existing_action = MovementAdditionalAction.get_action_by_id(action_id)
            if not existing_action:
                result['message'] = MovementAdditionalAction.ACTION_NOT_FOUND
                return result
            
            # Check if action name already exists for this command (excluding current action)
            if (action_name and 
                MovementAdditionalAction.action_name_exists_for_command(
                    existing_action['movement_command_id'], action_name, action_id)):
                result['message'] = MovementAdditionalAction.ACTION_NAME_ALREADY_EXISTS
                return result
            
            # Prepare update data
            updated_at = datetime.now().isoformat()
            update_fields = []
            update_values = []
            
            if action_name is not None:
                update_fields.append("action_name = ?")
                update_values.append(action_name.strip())
            
            if not update_fields:
                result['message'] = "No fields to update"
                return result
            
            update_fields.append("updated_at = ?")
            update_values.append(updated_at)
            update_values.append(action_id)
            
            # Update action
            conn = MovementAdditionalAction.get_db_connection()
            try:
                query = f"UPDATE Movement_Additional_Action SET {', '.join(update_fields)} WHERE movement_additional_action_id = ?"
                conn.execute(query, update_values)
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': MovementAdditionalAction.ACTION_UPDATED_SUCCESSFULLY,
                    'updated_at': updated_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def soft_delete_action(action_id: str) -> Dict[str, Any]:
        """
        Soft delete additional action by setting deleted_at timestamp
        
        Args:
            action_id: Action ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'deleted_at': None
        }
        
        try:
            # Validate action_id format
            if not MovementAdditionalAction.is_valid_uuid(action_id):
                result['message'] = MovementAdditionalAction.INVALID_ACTION_ID_FORMAT
                return result
            
            # Check if action exists
            existing_action = MovementAdditionalAction.get_action_by_id(action_id)
            if not existing_action:
                result['message'] = MovementAdditionalAction.ACTION_NOT_FOUND
                return result
            
            deleted_at = datetime.now().isoformat()
            
            # Soft delete action
            conn = MovementAdditionalAction.get_db_connection()
            try:
                conn.execute("""
                    UPDATE Movement_Additional_Action 
                    SET deleted_at = ?, updated_at = ?
                    WHERE movement_additional_action_id = ?
                """, (deleted_at, deleted_at, action_id))
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': MovementAdditionalAction.ACTION_DELETED_SUCCESSFULLY,
                    'deleted_at': deleted_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_all_actions(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all additional actions with pagination
        
        Args:
            limit: Maximum number of actions to return
            offset: Number of actions to skip
            
        Returns:
            List of action dictionaries
        """
        try:
            conn = MovementAdditionalAction.get_db_connection()
            try:
                actions = conn.execute("""
                    SELECT maa.*, mc.movement_type, ms.movement_name
                    FROM Movement_Additional_Action maa
                    LEFT JOIN Movement_Command mc ON maa.movement_command_id = mc.movement_command_id
                    LEFT JOIN Movement_Sequence ms ON mc.robot_movement_id = ms.movement_sequence_id
                    WHERE maa.deleted_at IS NULL
                    ORDER BY ms.movement_name, mc.step_order, maa.action_name
                    LIMIT ? OFFSET ?
                """, (limit, offset)).fetchall()
                
                return [dict(action) for action in actions]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting all additional actions: {e}")
            return []
    
    @staticmethod
    def get_actions_by_sequence_id(movement_sequence_id: str) -> List[Dict[str, Any]]:
        """
        Get all actions for a movement sequence
        
        Args:
            movement_sequence_id: Movement sequence ID
            
        Returns:
            List of action dictionaries organized by command
        """
        try:
            conn = MovementAdditionalAction.get_db_connection()
            try:
                actions = conn.execute("""
                    SELECT maa.*, mc.movement_type, mc.step_order, ms.movement_name
                    FROM Movement_Additional_Action maa
                    INNER JOIN Movement_Command mc ON maa.movement_command_id = mc.movement_command_id
                    INNER JOIN Movement_Sequence ms ON mc.robot_movement_id = ms.movement_sequence_id
                    WHERE ms.movement_sequence_id = ? AND maa.deleted_at IS NULL
                    ORDER BY mc.step_order, maa.created_at
                """, (movement_sequence_id,)).fetchall()
                
                return [dict(action) for action in actions]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting actions by sequence ID: {e}")
            return []
    
    @staticmethod
    def search_actions(search_term: str) -> List[Dict[str, Any]]:
        """
        Search additional actions by action name
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching actions
        """
        try:
            conn = MovementAdditionalAction.get_db_connection()
            try:
                search_pattern = f"%{search_term.strip()}%"
                actions = conn.execute("""
                    SELECT maa.*, mc.movement_type, ms.movement_name
                    FROM Movement_Additional_Action maa
                    LEFT JOIN Movement_Command mc ON maa.movement_command_id = mc.movement_command_id
                    LEFT JOIN Movement_Sequence ms ON mc.robot_movement_id = ms.movement_sequence_id
                    WHERE maa.action_name LIKE ? AND maa.deleted_at IS NULL
                    ORDER BY maa.action_name
                """, (search_pattern,)).fetchall()
                
                return [dict(action) for action in actions]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error searching additional actions: {e}")
            return [] 