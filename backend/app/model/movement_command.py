#!/usr/bin/env python3
"""
Movement Command Model
Handles movement command operations
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class MovementCommand:
    # Error message constants
    COMMAND_NOT_FOUND = "Movement command not found"
    COMMAND_CREATED_SUCCESSFULLY = "Movement command created successfully"
    COMMAND_UPDATED_SUCCESSFULLY = "Movement command updated successfully"
    COMMAND_DELETED_SUCCESSFULLY = "Movement command deleted successfully"
    ROBOT_MOVEMENT_ID_REQUIRED = "Robot movement ID is required"
    MOVEMENT_TYPE_REQUIRED = "Movement type is required"
    INVALID_COMMAND_ID_FORMAT = "Invalid command ID format"
    STEP_ORDER_REQUIRED = "Step order is required"
    
    # Movement type constants
    MOVEMENT_TYPES = [
        "FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT",
        "HEAD_UP", "HEAD_DOWN", "HEAD_LEFT", "HEAD_RIGHT",
        "ARM_UP", "ARM_DOWN", "WAVE", "POINT", "GESTURE"
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
    def generate_command_id() -> str:
        """Generate unique command ID using UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid_uuid(command_id: str) -> bool:
        """
        Validate if command_id is a valid UUID format
        
        Args:
            command_id: Command ID to validate
            
        Returns:
            True if valid UUID, False otherwise
        """
        try:
            uuid.UUID(command_id)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_movement_type(movement_type: str) -> bool:
        """
        Validate if movement_type is valid
        
        Args:
            movement_type: Movement type to validate
            
        Returns:
            True if valid movement type, False otherwise
        """
        return movement_type.upper() in MovementCommand.MOVEMENT_TYPES
    
    @staticmethod
    def create_command(robot_movement_id: str, movement_type: str, step_order: int,
                      movement_additional_action_id: str = None) -> Dict[str, Any]:
        """
        Create new movement command
        
        Args:
            robot_movement_id: Robot movement ID (references movement sequence)
            movement_type: Type of movement
            step_order: Order of this step in the sequence
            movement_additional_action_id: Additional action ID (optional)
            
        Returns:
            Dict with command data or error info
        """
        result = {
            'success': False,
            'movement_command_id': None,
            'message': '',
            'created_at': None
        }
        
        try:
            # Validate input
            if not robot_movement_id or not robot_movement_id.strip():
                result['message'] = MovementCommand.ROBOT_MOVEMENT_ID_REQUIRED
                return result
                
            if not movement_type or not movement_type.strip():
                result['message'] = MovementCommand.MOVEMENT_TYPE_REQUIRED
                return result
            
            if step_order is None or step_order < 1:
                result['message'] = MovementCommand.STEP_ORDER_REQUIRED
                return result
            
            # Validate movement type
            if not MovementCommand.is_valid_movement_type(movement_type):
                result['message'] = f"Invalid movement type. Valid types: {', '.join(MovementCommand.MOVEMENT_TYPES)}"
                return result
            
            # Generate command ID and timestamp
            command_id = MovementCommand.generate_command_id()
            created_at = datetime.now().isoformat()
            updated_at = created_at
            
            # Insert command into database
            conn = MovementCommand.get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO Movement_Command (
                        movement_command_id, robot_movement_id, movement_type, 
                        movement_additional_action_id, step_order, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (command_id, robot_movement_id.strip(), movement_type.upper(), 
                      movement_additional_action_id, step_order, created_at, updated_at))
                conn.commit()
                
                result.update({
                    'success': True,
                    'movement_command_id': command_id,
                    'message': MovementCommand.COMMAND_CREATED_SUCCESSFULLY,
                    'created_at': created_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_command_by_id(command_id: str) -> Optional[Dict[str, Any]]:
        """
        Get movement command by ID
        
        Args:
            command_id: Command ID
            
        Returns:
            Command data dict or None if not found
        """
        try:
            conn = MovementCommand.get_db_connection()
            try:
                command = conn.execute("""
                    SELECT mc.*, ms.movement_name, maa.action_name
                    FROM Movement_Command mc
                    LEFT JOIN Movement_Sequence ms ON mc.robot_movement_id = ms.movement_sequence_id
                    LEFT JOIN Movement_Additional_Action maa ON mc.movement_additional_action_id = maa.movement_additional_action_id
                    WHERE mc.movement_command_id = ? AND mc.deleted_at IS NULL
                """, (command_id,)).fetchone()
                
                return dict(command) if command else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting movement command: {e}")
            return None
    
    @staticmethod
    def get_commands_by_movement_id(robot_movement_id: str) -> List[Dict[str, Any]]:
        """
        Get commands by robot movement ID (sequence ID)
        
        Args:
            robot_movement_id: Robot movement ID
            
        Returns:
            List of command dictionaries ordered by step_order
        """
        try:
            conn = MovementCommand.get_db_connection()
            try:
                commands = conn.execute("""
                    SELECT mc.*, ms.movement_name, maa.action_name
                    FROM Movement_Command mc
                    LEFT JOIN Movement_Sequence ms ON mc.robot_movement_id = ms.movement_sequence_id
                    LEFT JOIN Movement_Additional_Action maa ON mc.movement_additional_action_id = maa.movement_additional_action_id
                    WHERE mc.robot_movement_id = ? AND mc.deleted_at IS NULL
                    ORDER BY mc.step_order ASC
                """, (robot_movement_id,)).fetchall()
                
                return [dict(command) for command in commands]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting commands by movement ID: {e}")
            return []
    
    @staticmethod
    def update_command(command_id: str, movement_type: str = None, step_order: int = None,
                      movement_additional_action_id: str = None) -> Dict[str, Any]:
        """
        Update movement command
        
        Args:
            command_id: Command ID
            movement_type: Movement type
            step_order: Step order
            movement_additional_action_id: Additional action ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'updated_at': None
        }
        
        try:
            # Validate command_id format
            if not MovementCommand.is_valid_uuid(command_id):
                result['message'] = MovementCommand.INVALID_COMMAND_ID_FORMAT
                return result
            
            # Check if command exists
            existing_command = MovementCommand.get_command_by_id(command_id)
            if not existing_command:
                result['message'] = MovementCommand.COMMAND_NOT_FOUND
                return result
            
            # Validate movement type if provided
            if movement_type and not MovementCommand.is_valid_movement_type(movement_type):
                result['message'] = f"Invalid movement type. Valid types: {', '.join(MovementCommand.MOVEMENT_TYPES)}"
                return result
            
            # Validate step order if provided
            if step_order is not None and step_order < 1:
                result['message'] = MovementCommand.STEP_ORDER_REQUIRED
                return result
            
            # Prepare update data
            updated_at = datetime.now().isoformat()
            update_fields = []
            update_values = []
            
            if movement_type is not None:
                update_fields.append("movement_type = ?")
                update_values.append(movement_type.upper())
            
            if step_order is not None:
                update_fields.append("step_order = ?")
                update_values.append(step_order)
                
            if movement_additional_action_id is not None:
                update_fields.append("movement_additional_action_id = ?")
                update_values.append(movement_additional_action_id)
            
            if not update_fields:
                result['message'] = "No fields to update"
                return result
            
            update_fields.append("updated_at = ?")
            update_values.append(updated_at)
            update_values.append(command_id)
            
            # Update command
            conn = MovementCommand.get_db_connection()
            try:
                query = f"UPDATE Movement_Command SET {', '.join(update_fields)} WHERE movement_command_id = ?"
                conn.execute(query, update_values)
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': MovementCommand.COMMAND_UPDATED_SUCCESSFULLY,
                    'updated_at': updated_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def soft_delete_command(command_id: str) -> Dict[str, Any]:
        """
        Soft delete movement command by setting deleted_at timestamp
        
        Args:
            command_id: Command ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'deleted_at': None
        }
        
        try:
            # Validate command_id format
            if not MovementCommand.is_valid_uuid(command_id):
                result['message'] = MovementCommand.INVALID_COMMAND_ID_FORMAT
                return result
            
            # Check if command exists
            existing_command = MovementCommand.get_command_by_id(command_id)
            if not existing_command:
                result['message'] = MovementCommand.COMMAND_NOT_FOUND
                return result
            
            deleted_at = datetime.now().isoformat()
            
            # Soft delete command
            conn = MovementCommand.get_db_connection()
            try:
                conn.execute("""
                    UPDATE Movement_Command 
                    SET deleted_at = ?, updated_at = ?
                    WHERE movement_command_id = ?
                """, (deleted_at, deleted_at, command_id))
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': MovementCommand.COMMAND_DELETED_SUCCESSFULLY,
                    'deleted_at': deleted_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_all_commands(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all movement commands with pagination
        
        Args:
            limit: Maximum number of commands to return
            offset: Number of commands to skip
            
        Returns:
            List of command dictionaries
        """
        try:
            conn = MovementCommand.get_db_connection()
            try:
                commands = conn.execute("""
                    SELECT mc.*, ms.movement_name, maa.action_name
                    FROM Movement_Command mc
                    LEFT JOIN Movement_Sequence ms ON mc.robot_movement_id = ms.movement_sequence_id
                    LEFT JOIN Movement_Additional_Action maa ON mc.movement_additional_action_id = maa.movement_additional_action_id
                    WHERE mc.deleted_at IS NULL
                    ORDER BY ms.movement_name, mc.step_order
                    LIMIT ? OFFSET ?
                """, (limit, offset)).fetchall()
                
                return [dict(command) for command in commands]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting all movement commands: {e}")
            return []
    
    @staticmethod
    def reorder_commands(robot_movement_id: str, command_orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Reorder commands in a sequence
        
        Args:
            robot_movement_id: Robot movement ID
            command_orders: List of dicts with 'command_id' and 'step_order'
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'updated_at': None
        }
        
        try:
            updated_at = datetime.now().isoformat()
            
            conn = MovementCommand.get_db_connection()
            try:
                for order_data in command_orders:
                    command_id = order_data.get('command_id')
                    step_order = order_data.get('step_order')
                    
                    if not command_id or step_order is None:
                        continue
                    
                    conn.execute("""
                        UPDATE Movement_Command 
                        SET step_order = ?, updated_at = ?
                        WHERE movement_command_id = ? AND robot_movement_id = ?
                    """, (step_order, updated_at, command_id, robot_movement_id))
                
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': "Commands reordered successfully",
                    'updated_at': updated_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result 