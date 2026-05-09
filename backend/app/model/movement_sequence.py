#!/usr/bin/env python3
"""
Movement Sequence Model
Handles movement sequence operations
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
import json

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class MovementSequence:
    # Error message constants
    SEQUENCE_NOT_FOUND = "Movement sequence not found"
    SEQUENCE_CREATED_SUCCESSFULLY = "Movement sequence created successfully"
    SEQUENCE_UPDATED_SUCCESSFULLY = "Movement sequence updated successfully"
    SEQUENCE_DELETED_SUCCESSFULLY = "Movement sequence deleted successfully"
    MOVEMENT_NAME_REQUIRED = "Movement name is required"
    INVALID_SEQUENCE_ID_FORMAT = "Invalid sequence ID format"
    MOVEMENT_NAME_ALREADY_EXISTS = "Movement name already exists"
    
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
    def generate_sequence_id() -> str:
        """Generate unique sequence ID using UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid_uuid(sequence_id: str) -> bool:
        """
        Validate if sequence_id is a valid UUID format
        
        Args:
            sequence_id: Sequence ID to validate
            
        Returns:
            True if valid UUID, False otherwise
        """
        try:
            uuid.UUID(sequence_id)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def movement_name_exists(movement_name: str, exclude_id: str = None) -> bool:
        """
        Check if movement name already exists
        
        Args:
            movement_name: Movement name to check
            exclude_id: Sequence ID to exclude from check (for updates)
            
        Returns:
            True if name exists, False otherwise
        """
        try:
            conn = MovementSequence.get_db_connection()
            try:
                if exclude_id:
                    result = conn.execute("""
                        SELECT COUNT(*) as count FROM Movement_Sequence 
                        WHERE LOWER(movement_name) = LOWER(?) 
                        AND movement_sequence_id != ? 
                        AND deleted_at IS NULL
                    """, (movement_name.strip(), exclude_id)).fetchone()
                else:
                    result = conn.execute("""
                        SELECT COUNT(*) as count FROM Movement_Sequence 
                        WHERE LOWER(movement_name) = LOWER(?) 
                        AND deleted_at IS NULL
                    """, (movement_name.strip(),)).fetchone()
                
                return result['count'] > 0
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error checking movement name existence: {e}")
            return False
    
    @staticmethod
    def create_sequence(movement_name: str, description: str = None) -> Dict[str, Any]:
        """
        Create new movement sequence
        
        Args:
            movement_name: Name of the movement sequence
            description: Description of the movement sequence
            
        Returns:
            Dict with sequence data or error info
        """
        result = {
            'success': False,
            'movement_sequence_id': None,
            'message': '',
            'created_at': None
        }
        
        try:
            # Validate input
            if not movement_name or not movement_name.strip():
                result['message'] = MovementSequence.MOVEMENT_NAME_REQUIRED
                return result
            
            # Check if movement name already exists
            if MovementSequence.movement_name_exists(movement_name):
                result['message'] = MovementSequence.MOVEMENT_NAME_ALREADY_EXISTS
                return result
            
            # Generate sequence ID and timestamp
            sequence_id = MovementSequence.generate_sequence_id()
            created_at = datetime.now().isoformat()
            updated_at = created_at
            
            # Insert sequence into database
            conn = MovementSequence.get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO Movement_Sequence (
                        movement_sequence_id, movement_name, description, 
                        created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (sequence_id, movement_name.strip(), description, created_at, updated_at))
                conn.commit()
                
                result.update({
                    'success': True,
                    'movement_sequence_id': sequence_id,
                    'message': MovementSequence.SEQUENCE_CREATED_SUCCESSFULLY,
                    'created_at': created_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_sequence_by_id(sequence_id: str) -> Optional[Dict[str, Any]]:
        """
        Get movement sequence by ID
        
        Args:
            sequence_id: Sequence ID
            
        Returns:
            Sequence data dict or None if not found
        """
        try:
            conn = MovementSequence.get_db_connection()
            try:
                sequence = conn.execute("""
                    SELECT * FROM Movement_Sequence 
                    WHERE movement_sequence_id = ? AND deleted_at IS NULL
                """, (sequence_id,)).fetchone()
                
                return dict(sequence) if sequence else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting movement sequence: {e}")
            return None
    
    @staticmethod
    def get_sequence_by_name(movement_name: str) -> Optional[Dict[str, Any]]:
        """
        Get movement sequence by name
        
        Args:
            movement_name: Movement name
            
        Returns:
            Sequence data dict or None if not found
        """
        try:
            conn = MovementSequence.get_db_connection()
            try:
                sequence = conn.execute("""
                    SELECT * FROM Movement_Sequence 
                    WHERE LOWER(movement_name) = LOWER(?) AND deleted_at IS NULL
                """, (movement_name.strip(),)).fetchone()
                
                return dict(sequence) if sequence else None
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting movement sequence by name: {e}")
            return None
    
    @staticmethod
    def update_sequence(sequence_id: str, movement_name: str = None, description: str = None) -> Dict[str, Any]:
        """
        Update movement sequence
        
        Args:
            sequence_id: Sequence ID
            movement_name: Movement name
            description: Description
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'updated_at': None
        }
        
        try:
            # Validate sequence_id format
            if not MovementSequence.is_valid_uuid(sequence_id):
                result['message'] = MovementSequence.INVALID_SEQUENCE_ID_FORMAT
                return result
            
            # Check if sequence exists
            existing_sequence = MovementSequence.get_sequence_by_id(sequence_id)
            if not existing_sequence:
                result['message'] = MovementSequence.SEQUENCE_NOT_FOUND
                return result
            
            # Check if movement name already exists (excluding current sequence)
            if movement_name and MovementSequence.movement_name_exists(movement_name, sequence_id):
                result['message'] = MovementSequence.MOVEMENT_NAME_ALREADY_EXISTS
                return result
            
            # Prepare update data
            updated_at = datetime.now().isoformat()
            update_fields = []
            update_values = []
            
            if movement_name is not None:
                update_fields.append("movement_name = ?")
                update_values.append(movement_name.strip())
            
            if description is not None:
                update_fields.append("description = ?")
                update_values.append(description)
            
            if not update_fields:
                result['message'] = "No fields to update"
                return result
            
            update_fields.append("updated_at = ?")
            update_values.append(updated_at)
            update_values.append(sequence_id)
            
            # Update sequence
            conn = MovementSequence.get_db_connection()
            try:
                query = f"UPDATE Movement_Sequence SET {', '.join(update_fields)} WHERE movement_sequence_id = ?"
                conn.execute(query, update_values)
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': MovementSequence.SEQUENCE_UPDATED_SUCCESSFULLY,
                    'updated_at': updated_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def soft_delete_sequence(sequence_id: str) -> Dict[str, Any]:
        """
        Soft delete movement sequence by setting deleted_at timestamp
        
        Args:
            sequence_id: Sequence ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': '',
            'deleted_at': None
        }
        
        try:
            # Validate sequence_id format
            if not MovementSequence.is_valid_uuid(sequence_id):
                result['message'] = MovementSequence.INVALID_SEQUENCE_ID_FORMAT
                return result
            
            # Check if sequence exists
            existing_sequence = MovementSequence.get_sequence_by_id(sequence_id)
            if not existing_sequence:
                result['message'] = MovementSequence.SEQUENCE_NOT_FOUND
                return result
            
            deleted_at = datetime.now().isoformat()
            
            # Soft delete sequence
            conn = MovementSequence.get_db_connection()
            try:
                conn.execute("""
                    UPDATE Movement_Sequence 
                    SET deleted_at = ?, updated_at = ?
                    WHERE movement_sequence_id = ?
                """, (deleted_at, deleted_at, sequence_id))
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': MovementSequence.SEQUENCE_DELETED_SUCCESSFULLY,
                    'deleted_at': deleted_at
                })
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Database error: {str(e)}"
        
        return result
    
    @staticmethod
    def get_all_sequences(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all movement sequences with pagination
        
        Args:
            limit: Maximum number of sequences to return
            offset: Number of sequences to skip
            
        Returns:
            List of sequence dictionaries
        """
        try:
            conn = MovementSequence.get_db_connection()
            try:
                sequences = conn.execute("""
                    SELECT * FROM Movement_Sequence 
                    WHERE deleted_at IS NULL
                    ORDER BY movement_name
                    LIMIT ? OFFSET ?
                """, (limit, offset)).fetchall()
                
                return [dict(sequence) for sequence in sequences]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting all movement sequences: {e}")
            return []
    
    @staticmethod
    def search_sequences(search_term: str) -> List[Dict[str, Any]]:
        """
        Search movement sequences by name or description
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching sequences
        """
        try:
            conn = MovementSequence.get_db_connection()
            try:
                search_pattern = f"%{search_term.strip()}%"
                sequences = conn.execute("""
                    SELECT * FROM Movement_Sequence 
                    WHERE (movement_name LIKE ? OR description LIKE ?) 
                    AND deleted_at IS NULL
                    ORDER BY movement_name
                """, (search_pattern, search_pattern)).fetchall()
                
                return [dict(sequence) for sequence in sequences]
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error searching movement sequences: {e}")
            return []
    
    @staticmethod
    def get_all_sequences_with_details() -> List[Dict[str, Any]]:
        """
        Get all movement sequences with their commands and additional actions details
        for /movement-sequences-list endpoint.
        
        Returns:
            List of sequences with hierarchical command and action details
        """
        result = []
        
        try:
            conn = MovementSequence.get_db_connection()
            try:
                # Step 1: Get all movement sequences
                sequences = conn.execute("""
                    SELECT * FROM Movement_Sequence 
                    WHERE deleted_at IS NULL
                    ORDER BY movement_name
                """).fetchall()
                
                # Step 2: Loop through each sequence
                for sequence in sequences:
                    sequence_obj = dict(sequence)
                    
                    # Step 3: Get all commands for this sequence (ordered by step_order ASC)
                    commands = conn.execute("""
                        SELECT * FROM Movement_Command 
                        WHERE movement_sequence_id = ? AND deleted_at IS NULL
                        ORDER BY step_order ASC
                    """, (sequence_obj['movement_sequence_id'],)).fetchall()
                    
                    # Step 4: Calculate step count
                    step_count = len(commands)
                    
                    # Step 5: Initialize movement_sequences_details list
                    movement_sequences_details = []
                    
                    # Step 6: Loop through each command
                    for command in commands:
                        command_obj = dict(command)
                        
                        # Step 7: Get additional actions for this command
                        additional_actions = conn.execute("""
                            SELECT * FROM Movement_Additional_Action 
                            WHERE movement_command_id = ? AND deleted_at IS NULL
                            ORDER BY movement_additional_action_id
                        """, (command_obj['movement_command_id'],)).fetchall()
                        
                        # Step 8: Format additional actions with additional_step_order
                        additional_movement = []
                        for idx, action in enumerate(additional_actions):
                            action_obj = dict(action)
                            additional_movement.append({
                                "movement_additional_action_id": action_obj['movement_additional_action_id'],
                                "action_name": action_obj['action_name'],
                                "additional_step_order": idx + 1  # Index + 1 for ordering
                            })
                        
                        # Step 9: Build command detail object
                        command_detail = {
                            "movement_command_id": command_obj['movement_command_id'],
                            "type": command_obj['movement_type'],
                            "value": str(command_obj['value']) if command_obj.get('value') is not None else "",
                            "step_order": command_obj['step_order'],
                            "additional_movement": additional_movement
                        }
                        
                        movement_sequences_details.append(command_detail)
                    
                    # Step 10: Build final sequence object
                    sequence_detail = {
                        "id": sequence_obj['movement_sequence_id'],
                        "name": sequence_obj['movement_name'],
                        "description": sequence_obj['description'] or "",
                        "step_count": step_count,
                        "movement_sequences": movement_sequences_details
                    }
                    
                    result.append(sequence_detail)
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting movement sequences with details: {e}")
            return []
        
        return result
    
    @staticmethod
    def get_sequence_with_details_by_id(sequence_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific movement sequence with commands and additional actions details by ID
        for /movement-sequences-list/<movement_sequence_id> endpoint.
        
        Args:
            sequence_id: Movement sequence ID
            
        Returns:
            Single sequence object with hierarchical command and action details, or None if not found
        """
        try:
            conn = MovementSequence.get_db_connection()
            try:
                # Step 1: Get specific movement sequence by ID
                sequence = conn.execute("""
                    SELECT * FROM Movement_Sequence 
                    WHERE movement_sequence_id = ? AND deleted_at IS NULL
                """, (sequence_id,)).fetchone()
                
                if not sequence:
                    return None
                
                sequence_obj = dict(sequence)
                
                # Step 2: Get all commands for this sequence (ordered by step_order ASC)
                commands = conn.execute("""
                    SELECT * FROM Movement_Command 
                    WHERE movement_sequence_id = ? AND deleted_at IS NULL
                    ORDER BY step_order ASC
                """, (sequence_obj['movement_sequence_id'],)).fetchall()
                
                # Step 3: Calculate step count
                step_count = len(commands)
                
                # Step 4: Initialize movement_sequences_details list
                movement_sequences_details = []
                
                # Step 5: Loop through each command
                for command in commands:
                    command_obj = dict(command)
                    
                    # Get additional actions for this command
                    additional_actions = conn.execute("""
                        SELECT * FROM Movement_Additional_Action 
                        WHERE movement_command_id = ? AND deleted_at IS NULL
                        ORDER BY movement_additional_action_id
                    """, (command_obj['movement_command_id'],)).fetchall()
                    
                    # Format additional actions with additional_step_order
                    additional_movement = []
                    for idx, action in enumerate(additional_actions):
                        action_obj = dict(action)
                        additional_movement.append({
                            "movement_additional_action_id": action_obj['movement_additional_action_id'],
                            "action_name": action_obj['action_name'],
                            "additional_step_order": idx + 1  # Index + 1 for ordering
                        })
                    
                    # Build command detail object
                    command_detail = {
                        "movement_command_id": command_obj['movement_command_id'],
                        "type": command_obj['movement_type'],
                        "value": str(command_obj['value']) if command_obj.get('value') is not None else "",
                        "step_order": command_obj['step_order'],
                        "additional_movement": additional_movement
                    }
                    
                    movement_sequences_details.append(command_detail)
                
                # Step 6: Build final sequence object (single object, not array)
                sequence_detail = {
                    "id": sequence_obj['movement_sequence_id'],
                    "name": sequence_obj['movement_name'],
                    "description": sequence_obj['description'] or "",
                    "step_count": step_count,
                    "movement_sequences": movement_sequences_details
                }
                
                return sequence_detail
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error getting movement sequence with details by ID: {e}")
            return None

    @staticmethod
    def create_movement_sequence_with_commands(name: str, description: str, route_map: str, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create new movement sequence with commands and additional actions in a single transaction
        
        Args:
            name: Movement sequence name
            description: Movement sequence description
            route_map: Generated route map JSON string
            commands: List of command objects with additional_actions
            
        Returns:
            Dict with success status and data or error message
        """
        result = {
            'success': False,
            'data': None,
            'message': ''
        }
        
        try:
            # Validate input
            if not name or not name.strip():
                result['message'] = 'Movement name is required'
                return result
            
            if not route_map:
                result['message'] = 'Route map is required'
                return result
                
            if not commands or len(commands) == 0:
                result['message'] = 'Commands array is required and cannot be empty'
                return result
            
            # Check if movement name already exists
            if MovementSequence.movement_name_exists(name):
                result['message'] = 'Movement name already exists'
                return result
            
            conn = MovementSequence.get_db_connection()
            
            try:
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Step 1: Insert into Movement_Sequence
                created_at = datetime.now().isoformat()
                
                sequence_cursor = conn.execute("""
                    INSERT INTO Movement_Sequence (movement_name, description, route_map_image_path, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (name.strip(), description, route_map, created_at, created_at))
                
                new_sequence_id = sequence_cursor.lastrowid
                
                # Step 2: Insert commands and collect response data
                movement_sequences = []
                
                for command in commands:
                    # Generate UUID for movement_command_id
                    movement_command_id = str(uuid.uuid4())
                    
                    # Handle additional actions first to get the action_id if needed
                    additional_movement = []
                    additional_actions = command.get('additional_actions', [])
                    main_action_id = None
                    
                    if additional_actions:
                        # If there are additional actions, use the first one as the main action reference
                        for i, action in enumerate(additional_actions):
                            # Generate UUID for movement_additional_action_id
                            action_id = str(uuid.uuid4())
                            
                            # Insert into Movement_Additional_Action
                            conn.execute("""
                                INSERT INTO Movement_Additional_Action (
                                    movement_additional_action_id, movement_command_id, 
                                    action_name, additional_step_order, created_at, updated_at
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                action_id, movement_command_id, action['action_name'],
                                action['additional_step_order'], created_at, created_at
                            ))
                            
                            # Use first action as main reference
                            if i == 0:
                                main_action_id = action_id
                            
                            # Add to response data
                            additional_movement.append({
                                "movement_additional_action_id": action_id,
                                "action_name": action['action_name'],
                                "additional_step_order": action['additional_step_order']
                            })
                    
                    # Insert into Movement_Command with proper action_id (NULL if no actions)
                    conn.execute("""
                        INSERT INTO Movement_Command (
                            movement_command_id, movement_sequence_id, movement_type, 
                            value, step_order, created_at, updated_at,
                            movement_additional_action_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        movement_command_id, new_sequence_id, command['type'], 
                        command['value'], command['step_order'], created_at, created_at,
                        main_action_id  # NULL if no additional actions
                    ))
                    
                    # Add command to response data
                    movement_sequences.append({
                        "movement_command_id": movement_command_id,
                        "type": command['type'],
                        "value": command['value'],
                        "step_order": command['step_order'],
                        "additional_movement": additional_movement
                    })
                
                # Commit transaction
                conn.commit()
                
                # Prepare successful response data
                result_data = {
                    "id": new_sequence_id,
                    "name": name,
                    "description": description,
                    "created_at": created_at,
                    "movement_sequences": movement_sequences
                }
                
                result.update({
                    'success': True,
                    'data': result_data,
                    'message': 'Movement sequence created successfully'
                })
                
            except Exception as e:
                # Rollback transaction on error
                conn.rollback()
                result['message'] = f"Database transaction error: {str(e)}"
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Error creating movement sequence: {str(e)}"
        
        return result

    @staticmethod
    def delete_movement_command_with_reordering(movement_sequence_id: str, movement_command_id: str) -> Dict[str, Any]:
        """
        Delete movement command and reorder remaining commands' step_order
        
        Flow:
        1. Get target Movement_Command by movement_command_id
        2. Verify command belongs to movement_sequence_id
        3. Get all commands for the sequence
        4. Update step_order: decrease by 1 for commands with step_order > target.step_order
        5. Delete target command (cascade delete Movement_Additional_Action)
        
        Args:
            movement_sequence_id: Movement sequence ID
            movement_command_id: Movement command ID to delete
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Validate input
            if not movement_sequence_id:
                result['message'] = 'Movement sequence ID is required'
                return result
            
            if not movement_command_id:
                result['message'] = 'Movement command ID is required'
                return result
            
            conn = MovementSequence.get_db_connection()
            
            try:
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Step 1: Get target command by movement_command_id
                target_command = conn.execute("""
                    SELECT * FROM Movement_Command 
                    WHERE movement_command_id = ? AND deleted_at IS NULL
                """, (movement_command_id,)).fetchone()
                
                if not target_command:
                    result['message'] = 'Movement command not found'
                    conn.rollback()
                    return result
                
                target_command = dict(target_command)
                
                # Step 2: Verify command belongs to the specified movement_sequence_id
                if str(target_command['movement_sequence_id']) != str(movement_sequence_id):
                    result['message'] = 'Movement command does not belong to the specified movement sequence'
                    conn.rollback()
                    return result
                
                target_step_order = target_command['step_order']
                
                # Step 3: Update step_order for commands with step_order > target.step_order
                # Decrease their step_order by 1
                conn.execute("""
                    UPDATE Movement_Command 
                    SET step_order = step_order - 1, updated_at = ?
                    WHERE movement_sequence_id = ? 
                    AND step_order > ? 
                    AND deleted_at IS NULL
                """, (datetime.now().isoformat(), movement_sequence_id, target_step_order))
                
                # Step 4: Delete target command (cascade delete will handle Movement_Additional_Action)
                # Since we have foreign key with ON DELETE CASCADE, additional actions will be deleted automatically
                conn.execute("""
                    DELETE FROM Movement_Command 
                    WHERE movement_command_id = ?
                """, (movement_command_id,))
                
                # Commit transaction
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': 'Movement command deleted successfully with step order reordering'
                })
                
            except Exception as e:
                # Rollback transaction on error
                conn.rollback()
                result['message'] = f"Database transaction error: {str(e)}"
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Error deleting movement command: {str(e)}"
        
        return result

    @staticmethod
    def swap_movement_command_order(movement_command_id_one: str, movement_command_id_two: str) -> Dict[str, Any]:
        """
        Swap step_order between two movement commands
        
        Flow:
        1. Get both Movement_Command objects by their IDs
        2. Verify both commands exist and belong to the same movement_sequence_id
        3. Swap their step_order values in a transaction
        
        Args:
            movement_command_id_one: First movement command ID
            movement_command_id_two: Second movement command ID
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Validate input
            if not movement_command_id_one:
                result['message'] = 'First movement command ID is required'
                return result
            
            if not movement_command_id_two:
                result['message'] = 'Second movement command ID is required'
                return result
            
            if movement_command_id_one == movement_command_id_two:
                result['message'] = 'Cannot swap command with itself'
                return result
            
            conn = MovementSequence.get_db_connection()
            
            try:
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Step 1: Get first command
                command_one = conn.execute("""
                    SELECT movement_command_id, movement_sequence_id, step_order
                    FROM Movement_Command 
                    WHERE movement_command_id = ? AND deleted_at IS NULL
                """, (movement_command_id_one,)).fetchone()
                
                if not command_one:
                    result['message'] = f'First movement command not found: {movement_command_id_one}'
                    conn.rollback()
                    return result
                
                command_one = dict(command_one)
                
                # Step 2: Get second command
                command_two = conn.execute("""
                    SELECT movement_command_id, movement_sequence_id, step_order
                    FROM Movement_Command 
                    WHERE movement_command_id = ? AND deleted_at IS NULL
                """, (movement_command_id_two,)).fetchone()
                
                if not command_two:
                    result['message'] = f'Second movement command not found: {movement_command_id_two}'
                    conn.rollback()
                    return result
                
                command_two = dict(command_two)
                
                # Step 3: Verify both commands belong to the same movement_sequence_id
                if command_one['movement_sequence_id'] != command_two['movement_sequence_id']:
                    result['message'] = 'Both commands must belong to the same movement sequence'
                    conn.rollback()
                    return result
                
                step_order_one = command_one['step_order']
                step_order_two = command_two['step_order']
                
                # Step 4: Swap step_order values
                # Update first command with second command's step_order
                conn.execute("""
                    UPDATE Movement_Command 
                    SET step_order = ?, updated_at = ?
                    WHERE movement_command_id = ?
                """, (step_order_two, datetime.now().isoformat(), movement_command_id_one))
                
                # Update second command with first command's step_order
                conn.execute("""
                    UPDATE Movement_Command 
                    SET step_order = ?, updated_at = ?
                    WHERE movement_command_id = ?
                """, (step_order_one, datetime.now().isoformat(), movement_command_id_two))
                
                # Commit transaction
                conn.commit()
                
                result.update({
                    'success': True,
                    'message': f'Successfully swapped step_order: {step_order_one} ↔ {step_order_two}'
                })
                
            except Exception as e:
                # Rollback transaction on error
                conn.rollback()
                result['message'] = f"Database transaction error: {str(e)}"
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Error swapping movement command order: {str(e)}"
        
        return result

    @staticmethod
    def update_movement_sequence_complete(movement_sequence_id: int, name: str, description: str, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update movement sequence using Delete + Create approach
        
        Flow:
        1. Validate that movement sequence exists
        2. Manual cascade delete existing sequence, commands, and actions
        3. Create new sequence with same ID using existing create logic
        4. Return formatted response
        
        Args:
            movement_sequence_id: ID of sequence to update
            name: New sequence name
            description: New sequence description
            commands: List of command objects with additional_actions
            
        Returns:
            Dict with success status, message, and sequence data
        """
        result = {
            'success': False,
            'message': '',
            'movement_sequence_id': movement_sequence_id,
            'name': name,
            'description': description,
            'created_at': '',
            'commands': []
        }
        
        try:
            # Validate input
            if not movement_sequence_id or movement_sequence_id <= 0:
                result['message'] = 'Invalid movement sequence ID'
                return result
            
            if not name or not name.strip():
                result['message'] = 'Sequence name is required'
                return result
            
            if not isinstance(commands, list) or len(commands) == 0:
                result['message'] = 'At least one command is required'
                return result
            
            conn = MovementSequence.get_db_connection()
            
            try:
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Step 1: Check if movement sequence exists
                existing_sequence = conn.execute("""
                    SELECT movement_sequence_id, movement_name, description
                    FROM Movement_Sequence 
                    WHERE movement_sequence_id = ? AND deleted_at IS NULL
                """, (movement_sequence_id,)).fetchone()
                
                if not existing_sequence:
                    result['message'] = f'Movement sequence with ID {movement_sequence_id} not found'
                    conn.rollback()
                    return result
                
                # Step 2: Manual cascade delete for data safety
                # Get all command IDs for this sequence first
                command_ids = conn.execute("""
                    SELECT movement_command_id FROM Movement_Command 
                    WHERE movement_sequence_id = ? AND deleted_at IS NULL
                """, (movement_sequence_id,)).fetchall()
                
                # Delete additional actions for each command
                for (command_id,) in command_ids:
                    conn.execute("""
                        DELETE FROM Movement_Additional_Action 
                        WHERE movement_command_id = ?
                    """, (command_id,))
                
                # Delete all commands for this sequence
                conn.execute("""
                    DELETE FROM Movement_Command 
                    WHERE movement_sequence_id = ?
                """, (movement_sequence_id,))
                
                # Delete the sequence itself
                conn.execute("""
                    DELETE FROM Movement_Sequence 
                    WHERE movement_sequence_id = ?
                """, (movement_sequence_id,))
                
                # Step 3: Create new sequence with same ID
                created_at = datetime.now().isoformat()
                route_map = json.dumps({
                    "updated": True,
                    "total_commands": len(commands),
                    "path_summary": [f"{cmd.get('type')}_{cmd.get('value')}" for cmd in commands]
                })
                
                # Insert new Movement_Sequence with explicit ID
                conn.execute("""
                    INSERT INTO Movement_Sequence (
                        movement_sequence_id, movement_name, description, route_map_image_path, 
                        created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (movement_sequence_id, name, description, route_map, created_at, created_at))
                
                # Step 4: Create commands and additional actions (reuse existing logic)
                created_commands = []
                
                for cmd in commands:
                    # Generate UUID for command
                    command_id = str(uuid.uuid4())
                    movement_type = cmd.get('type')
                    value = float(cmd.get('value'))
                    step_order = int(cmd.get('step_order'))
                    additional_actions = cmd.get('additional_actions', [])
                    
                    # Generate UUID for additional action (if exists)
                    action_id = str(uuid.uuid4()) if additional_actions else None
                    
                    # Insert Movement_Command
                    conn.execute("""
                        INSERT INTO Movement_Command (
                            movement_command_id, movement_sequence_id, movement_type, 
                            value, step_order, created_at, updated_at,
                            movement_additional_action_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (command_id, movement_sequence_id, movement_type, value, step_order, 
                          created_at, created_at, action_id))
                    
                    # Prepare command data for response
                    command_data = {
                        'movement_command_id': command_id,
                        'type': movement_type,
                        'value': value,
                        'step_order': step_order,
                        'additional_movement': []
                    }
                    
                    # Insert Movement_Additional_Action objects
                    for action in additional_actions:
                        action_name = action.get('action_name')
                        additional_step_order = int(action.get('additional_step_order'))
                        
                        # Use the same action_id for all actions of this command
                        conn.execute("""
                            INSERT INTO Movement_Additional_Action (
                                movement_additional_action_id, movement_command_id, 
                                action_name, additional_step_order, created_at, updated_at
                            )
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (action_id, command_id, action_name, additional_step_order, 
                              created_at, created_at))
                        
                        # Add to response data
                        command_data['additional_movement'].append({
                            'movement_additional_action_id': action_id,
                            'action_name': action_name,
                            'additional_step_order': additional_step_order
                        })
                    
                    created_commands.append(command_data)
                
                # Commit transaction
                conn.commit()
                
                # Update result with success data
                result.update({
                    'success': True,
                    'message': f'Movement sequence updated successfully with {len(commands)} commands',
                    'created_at': created_at,
                    'commands': sorted(created_commands, key=lambda x: x['step_order'])
                })
                
            except Exception as e:
                # Rollback transaction on error
                conn.rollback()
                result['message'] = f"Database transaction error: {str(e)}"
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Error updating movement sequence: {str(e)}"
        
        return result

    @staticmethod
    def delete_movement_sequence_cascade(movement_sequence_id: int) -> Dict[str, Any]:
        """
        Delete movement sequence and cascade delete all related Movement_Command and Movement_Additional_Action objects
        
        Flow:
        1. Validate that movement sequence exists
        2. Manual cascade delete: Movement_Additional_Action -> Movement_Command -> Movement_Sequence
        3. Return success response
        
        Args:
            movement_sequence_id: ID of sequence to delete
            
        Returns:
            Dict with success status and message
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Validate input
            if not movement_sequence_id or movement_sequence_id <= 0:
                result['message'] = 'Invalid movement sequence ID'
                return result
            
            conn = MovementSequence.get_db_connection()
            
            try:
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Step 1: Check if movement sequence exists
                existing_sequence = conn.execute("""
                    SELECT movement_sequence_id, movement_name
                    FROM Movement_Sequence 
                    WHERE movement_sequence_id = ? AND deleted_at IS NULL
                """, (movement_sequence_id,)).fetchone()
                
                if not existing_sequence:
                    result['message'] = f'Movement sequence with ID {movement_sequence_id} not found'
                    conn.rollback()
                    return result
                
                # Step 2: Manual cascade delete for data safety
                # Get all command IDs for this sequence first
                command_ids = conn.execute("""
                    SELECT movement_command_id FROM Movement_Command 
                    WHERE movement_sequence_id = ? AND deleted_at IS NULL
                """, (movement_sequence_id,)).fetchall()
                
                # Delete additional actions for each command
                deleted_actions_count = 0
                for (command_id,) in command_ids:
                    cursor = conn.execute("""
                        DELETE FROM Movement_Additional_Action 
                        WHERE movement_command_id = ?
                    """, (command_id,))
                    deleted_actions_count += cursor.rowcount
                
                # Delete all commands for this sequence
                cursor = conn.execute("""
                    DELETE FROM Movement_Command 
                    WHERE movement_sequence_id = ?
                """, (movement_sequence_id,))
                deleted_commands_count = cursor.rowcount
                
                # Delete the sequence itself
                cursor = conn.execute("""
                    DELETE FROM Movement_Sequence 
                    WHERE movement_sequence_id = ?
                """, (movement_sequence_id,))
                deleted_sequences_count = cursor.rowcount
                
                # Commit transaction
                conn.commit()
                
                # Update result with success data
                result.update({
                    'success': True,
                    'message': f'Movement sequence deleted successfully. Removed: {deleted_sequences_count} sequence, {deleted_commands_count} commands, {deleted_actions_count} additional actions'
                })
                
            except Exception as e:
                # Rollback transaction on error
                conn.rollback()
                result['message'] = f"Database transaction error: {str(e)}"
                
            finally:
                conn.close()
                
        except Exception as e:
            result['message'] = f"Error deleting movement sequence: {str(e)}"
        
        return result