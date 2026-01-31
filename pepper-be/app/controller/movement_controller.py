#!/usr/bin/env python3
"""
Movement Controller
Handles movement-related API endpoints
"""

from flask import jsonify, request
import uuid
import json
from app.model.movement_sequence import MovementSequence

class MovementController:
    
    @staticmethod
    def get_movement_sequences_list():
        """
        Handle GET /<feature>/movement-sequences-list request
        Returns all movement sequences with their commands and additional actions
        """
        try:
            # Get all sequences with hierarchical details
            sequences = MovementSequence.get_all_sequences_with_details()
            
            return jsonify(sequences), 200
            
        except Exception as e:
            return jsonify({'message': f'Error retrieving movement sequences: {str(e)}'}), 500
    
    @staticmethod
    def get_movement_sequence_by_id(sequence_id: str):
        """
        Handle GET /<feature>/movement-sequences-list/<movement_sequence_id> request
        Returns specific movement sequence with commands and additional actions
        
        Args:
            sequence_id: Movement sequence ID from URL parameter
        """
        try:
            # Get sequence with hierarchical details by ID
            sequence = MovementSequence.get_sequence_with_details_by_id(sequence_id)
            
            if not sequence:
                return jsonify({'message': 'Movement sequence not found'}), 404
                
            return jsonify(sequence), 200
            
        except Exception as e:
            return jsonify({'message': f'Error retrieving movement sequence: {str(e)}'}), 500

    @staticmethod
    def add_movement_sequence():
        """
        Handle POST /movement/movement-sequences-list/add request
        Creates new movement sequence with commands and additional actions
        
        Flow:
        1. Insert data into Movement_Sequence table using name and description from request body
        2. Loop through commands array and insert into Movement_Command table
        3. For each command, check if additional_actions exists and insert into Movement_Additional_Action table
        4. Return formatted response with all created data
        """
        try:
            # Get request data
            data = request.get_json(force=True, silent=True)
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            # Validate required fields
            name = data.get('name')
            if not name:
                return jsonify({'message': 'name is required'}), 400
            
            description = data.get('description', '')
            commands = data.get('commands', [])
            
            if not isinstance(commands, list) or len(commands) == 0:
                return jsonify({'message': 'commands array is required and cannot be empty'}), 400
            
            # Validate movement types and action names
            valid_movement_types = ['FORWARD', 'BACKWARD', 'ROTATE_LEFT', 'ROTATE_RIGHT']
            valid_action_names = [
                'Hey_1', 'Wave_1', 'Salute_1', 'BowShort_1', 'Explain_1',
                'ShowTablet_1', 'Enthusiastic_4', 'You_1', 'Me_1', 'ComeHere_1',
                'Think_1', 'No_1', 'Yes_1', 'Surprised_1', 'Embarrassed_1',
                'AirGuitar_1', 'RobotDance_1', 'SelfCheck_1'
            ]
            
            # Validate commands structure
            for i, command in enumerate(commands):
                if not isinstance(command, dict):
                    return jsonify({'message': f'Command at index {i} must be an object'}), 400
                
                cmd_type = command.get('type')
                if not cmd_type or cmd_type not in valid_movement_types:
                    return jsonify({'message': f'Command at index {i}: type must be one of {valid_movement_types}'}), 400
                
                value = command.get('value')
                if value is None or not isinstance(value, (int, float)):
                    return jsonify({'message': f'Command at index {i}: value must be a number'}), 400
                
                step_order = command.get('step_order')
                if step_order is None or not isinstance(step_order, int):
                    return jsonify({'message': f'Command at index {i}: step_order must be an integer'}), 400
                
                additional_actions = command.get('additional_actions', [])
                if not isinstance(additional_actions, list):
                    return jsonify({'message': f'Command at index {i}: additional_actions must be an array'}), 400
                
                # Validate additional actions
                for j, action in enumerate(additional_actions):
                    if not isinstance(action, dict):
                        return jsonify({'message': f'Command {i}, action {j}: must be an object'}), 400
                    
                    action_name = action.get('action_name')
                    if not action_name or action_name not in valid_action_names:
                        return jsonify({'message': f'Command {i}, action {j}: action_name must be one of {valid_action_names}'}), 400
                    
                    additional_step_order = action.get('additional_step_order')
                    if additional_step_order is None or not isinstance(additional_step_order, int):
                        return jsonify({'message': f'Command {i}, action {j}: additional_step_order must be an integer'}), 400
            
            # Generate default route_map from commands
            route_map = json.dumps({
                "generated": True,
                "total_commands": len(commands),
                "path_summary": [f"{cmd.get('type')}_{cmd.get('value')}" for cmd in commands]
            })
            
            # Start database transaction using MovementSequence model
            result = MovementSequence.create_movement_sequence_with_commands(
                name=name,
                description=description,
                route_map=route_map,
                commands=commands
            )
            
            if result.get('success'):
                return jsonify(result['data']), 201
            else:
                return jsonify({'message': result.get('message', 'Failed to create movement sequence')}), 500
                
        except Exception as e:
            return jsonify({'message': f'Error creating movement sequence: {str(e)}'}), 500

    @staticmethod
    def delete_movement_command(movement_sequence_id: str, movement_command_id: str):
        """
        Handle POST /movement/movement-sequences-list/<movement_sequence_id>/delete/<movement_command_id> request
        Deletes movement command and reorders remaining commands
        
        Flow:
        1. Validate input parameters
        2. Get target Movement_Command by movement_command_id
        3. Verify command belongs to the specified movement_sequence_id
        4. Delete command with step_order reordering
        5. Return success response
        
        Args:
            movement_sequence_id: Movement sequence ID from URL parameter
            movement_command_id: Movement command ID from URL parameter
        """
        try:
            # Validate input parameters
            if not movement_sequence_id:
                return jsonify({'message': 'movement_sequence_id is required'}), 400
            
            if not movement_command_id:
                return jsonify({'message': 'movement_command_id is required'}), 400
            
            # Call model method to handle deletion with reordering
            result = MovementSequence.delete_movement_command_with_reordering(
                movement_sequence_id=movement_sequence_id,
                movement_command_id=movement_command_id
            )
            
            if result.get('success'):
                return jsonify({
                    'status': 200,
                    'message': 'Deletion success'
                }), 200
            else:
                # Return appropriate error status based on the error type
                error_message = result.get('message', 'Failed to delete movement command')
                
                if 'not found' in error_message.lower():
                    return jsonify({'message': error_message}), 404
                elif 'not belong' in error_message.lower():
                    return jsonify({'message': error_message}), 400
                else:
                    return jsonify({'message': error_message}), 500
                    
        except Exception as e:
            return jsonify({'message': f'Error deleting movement command: {str(e)}'}), 500

    @staticmethod
    def swap_movement_command_order():
        """
        Handle POST /movement/movement-sequences-list/swap_order request
        Swaps step_order between two movement commands
        
        Flow:
        1. Validate request data
        2. Get both Movement_Command objects by their IDs
        3. Verify both commands belong to the same movement_sequence_id
        4. Swap their step_order values
        5. Return success response
        """
        try:
            # Get request data
            data = request.get_json(force=True, silent=True)
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            # Validate required fields
            movement_command_id_one = data.get('movement_command_id_one')
            movement_command_id_two = data.get('movement_command_id_two')
            
            if not movement_command_id_one:
                return jsonify({'message': 'movement_command_id_one is required'}), 400
            
            if not movement_command_id_two:
                return jsonify({'message': 'movement_command_id_two is required'}), 400
            
            # Validate that IDs are different
            if movement_command_id_one == movement_command_id_two:
                return jsonify({'message': 'Cannot swap command with itself'}), 400
            
            # Call model method to handle swap operation
            result = MovementSequence.swap_movement_command_order(
                movement_command_id_one=movement_command_id_one,
                movement_command_id_two=movement_command_id_two
            )
            
            if result.get('success'):
                return jsonify({
                    'status': 200,
                    'message': 'Swap success'
                }), 200
            else:
                # Return appropriate error status based on the error type
                error_message = result.get('message', 'Failed to swap movement commands')
                
                if 'not found' in error_message.lower():
                    return jsonify({'message': error_message}), 404
                elif 'not belong' in error_message.lower() or 'different sequence' in error_message.lower():
                    return jsonify({'message': error_message}), 400
                else:
                    return jsonify({'message': error_message}), 500
                    
        except Exception as e:
            return jsonify({'message': f'Error swapping movement command order: {str(e)}'}), 500

    @staticmethod
    def update_movement_sequence(movement_sequence_id: str):
        """
        Handle PUT /movement/movement-sequences-list/update/<movement_sequence_id> request
        Updates movement sequence using delete + create approach
        
        Flow:
        1. Validate request data and movement_sequence_id
        2. Check if movement sequence exists
        3. Delete existing sequence and create new one with same ID
        4. Return formatted response with updated sequence details
        """
        try:
            # Validate movement_sequence_id parameter
            if not movement_sequence_id:
                return jsonify({'message': 'Movement sequence ID is required'}), 400
            
            # Convert to integer for validation
            try:
                sequence_id_int = int(movement_sequence_id)
            except ValueError:
                return jsonify({'message': 'Invalid movement sequence ID format'}), 400
            
            # Get request data
            data = request.get_json(force=True, silent=True)
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            # Validate required fields
            name = data.get('name')
            if not name or not isinstance(name, str) or not name.strip():
                return jsonify({'message': 'Name is required and must be a non-empty string'}), 400
            
            # Optional description
            description = data.get('description', '')
            if description and not isinstance(description, str):
                return jsonify({'message': 'Description must be a string'}), 400
            
            # Validate commands array
            commands = data.get('commands', [])
            if not isinstance(commands, list):
                return jsonify({'message': 'Commands must be an array'}), 400
            
            if len(commands) == 0:
                return jsonify({'message': 'At least one command is required'}), 400
            
            # Validate each command structure
            valid_movement_types = ['FORWARD', 'BACKWARD', 'ROTATE_LEFT', 'ROTATE_RIGHT']
            valid_action_names = [
                'Hey_1', 'Wave_1', 'Salute_1', 'BowShort_1', 'Explain_1',
                'ShowTablet_1', 'Enthusiastic_4', 'You_1', 'Me_1', 'ComeHere_1',
                'Think_1', 'No_1', 'Yes_1', 'Surprised_1', 'Embarrassed_1',
                'AirGuitar_1', 'RobotDance_1', 'SelfCheck_1'
            ]
            
            step_orders = []
            for i, cmd in enumerate(commands):
                if not isinstance(cmd, dict):
                    return jsonify({'message': f'Command {i+1} must be an object'}), 400
                
                # Validate movement type
                movement_type = cmd.get('type')
                if movement_type not in valid_movement_types:
                    return jsonify({'message': f'Command {i+1}: Invalid movement type. Must be one of: {valid_movement_types}'}), 400
                
                # Validate value
                value = cmd.get('value')
                if not isinstance(value, (int, float)):
                    return jsonify({'message': f'Command {i+1}: Value must be a number'}), 400
                
                # Validate step_order
                step_order = cmd.get('step_order')
                if not isinstance(step_order, int) or step_order < 1:
                    return jsonify({'message': f'Command {i+1}: Step order must be a positive integer'}), 400
                
                if step_order in step_orders:
                    return jsonify({'message': f'Command {i+1}: Duplicate step order {step_order}'}), 400
                step_orders.append(step_order)
                
                # Validate additional_actions
                additional_actions = cmd.get('additional_actions', [])
                if not isinstance(additional_actions, list):
                    return jsonify({'message': f'Command {i+1}: Additional actions must be an array'}), 400
                
                # Validate each additional action
                action_step_orders = []
                for j, action in enumerate(additional_actions):
                    if not isinstance(action, dict):
                        return jsonify({'message': f'Command {i+1}, Action {j+1}: Must be an object'}), 400
                    
                    action_name = action.get('action_name')
                    if action_name not in valid_action_names:
                        return jsonify({'message': f'Command {i+1}, Action {j+1}: Invalid action name. Must be one of: {valid_action_names}'}), 400
                    
                    additional_step_order = action.get('additional_step_order')
                    if not isinstance(additional_step_order, int) or additional_step_order < 1:
                        return jsonify({'message': f'Command {i+1}, Action {j+1}: Additional step order must be a positive integer'}), 400
                    
                    if additional_step_order in action_step_orders:
                        return jsonify({'message': f'Command {i+1}: Duplicate additional step order {additional_step_order}'}), 400
                    action_step_orders.append(additional_step_order)
            
            # Validate step orders are sequential (1, 2, 3, ...)
            step_orders.sort()
            expected_orders = list(range(1, len(commands) + 1))
            if step_orders != expected_orders:
                return jsonify({'message': f'Step orders must be sequential starting from 1. Expected: {expected_orders}, Got: {step_orders}'}), 400
            
            # Call model method to handle update operation
            result = MovementSequence.update_movement_sequence_complete(
                movement_sequence_id=sequence_id_int,
                name=name.strip(),
                description=description.strip() if description else '',
                commands=commands
            )
            
            if result.get('success'):
                # Format successful response
                response_data = {
                    'message': 'Update success',
                    'id': result.get('movement_sequence_id'),
                    'name': result.get('name'),
                    'description': result.get('description'),
                    'created_at': result.get('created_at'),
                    'movement_sequences': result.get('commands', [])
                }
                return jsonify(response_data), 200
            else:
                # Return appropriate error status based on the error type
                error_message = result.get('message', 'Failed to update movement sequence')
                
                if 'not found' in error_message.lower():
                    return jsonify({'message': error_message}), 404
                elif 'validation' in error_message.lower() or 'invalid' in error_message.lower():
                    return jsonify({'message': error_message}), 400
                else:
                    return jsonify({'message': error_message}), 500
                    
        except Exception as e:
            return jsonify({'message': f'Error updating movement sequence: {str(e)}'}), 500

    @staticmethod
    def delete_movement_sequence(movement_sequence_id: str):
        """
        Handle POST /<feature>/movement-sequences-list/<movement_sequence_id>/delete request
        Deletes movement sequence and cascade delete all related Movement_Command and Movement_Additional_Action objects
        
        Flow:
        1. Get object Movement_Sequence where Movement_Sequence.movement_sequence_id == <movement_sequence_id>
        2. Delete object cascade all related Movement_Command objects and Movement_Additional_Action objects
        
        Args:
            movement_sequence_id: Movement sequence ID from URL parameter
        """
        try:
            # Validate movement_sequence_id parameter
            if not movement_sequence_id:
                return jsonify({'message': 'Movement sequence ID is required'}), 400
            
            # Convert to integer for validation
            try:
                sequence_id_int = int(movement_sequence_id)
            except ValueError:
                return jsonify({'message': 'Invalid movement sequence ID format'}), 400
            
            # Check if movement sequence exists
            sequence = MovementSequence.get_sequence_with_details_by_id(movement_sequence_id)
            if not sequence:
                return jsonify({'message': 'Movement sequence not found'}), 404
            
            # Call model method to handle cascade deletion
            result = MovementSequence.delete_movement_sequence_cascade(sequence_id_int)
            
            if result.get('success'):
                return jsonify({
                    'status': 200,
                    'message': 'Deletion success'
                }), 200
            else:
                error_message = result.get('message', 'Failed to delete movement sequence')
                return jsonify({'message': error_message}), 500
                
        except Exception as e:
            return jsonify({'message': f'Error deleting movement sequence: {str(e)}'}), 500
    
    @staticmethod
    def get_movement_sequence_for_tablet(movement_sequence_id: str):
        """
        Handle GET /<feature>/movement-sequences-list/tablet/<movement_sequence_id> request
        Returns movement sequence data for tablet interface
        
        Args:
            movement_sequence_id: Movement sequence ID from URL parameter
        """
        try:
            # Get sequence by ID
            sequence = MovementSequence.get_sequence_by_id(movement_sequence_id)
            
            if not sequence:
                return jsonify({'message': 'Movement sequence not found'}), 404
            
            # Format response according to specification
            response = {
                'id': sequence.get('movement_sequence_id'),
                'name': sequence.get('movement_name'),
                'description': sequence.get('description'),
                'route_map_image_path': sequence.get('route_map_image_path')
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            return jsonify({'message': f'Error retrieving movement sequence for tablet: {str(e)}'}), 500
