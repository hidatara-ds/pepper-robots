#!/usr/bin/env python3
"""
Config Controller
Handles configuration-related API endpoints
"""

from flask import jsonify, request, g
from app.model.pepper_mode import PepperMode
from app.model.configuration import Configuration


class ConfigController:
    
    @staticmethod
    def get_config():
        """
        Handle GET /<feature>/config request
        Returns all pepper modes with is_used flag based on current admin's configuration
        
        Flow:
        1. Get all pepper modes from Pepper_Mode table
        2. Get configuration for current logged admin from Configuration table
        3. Set is_used = true for pepper mode that matches admin's current configuration
        4. Return formatted response
        """
        try:
            # Get current admin ID from JWT token       
            admin_id = g.current_user['admin_id']
            
            config_obj = Configuration.get_configuration_by_admin_id(admin_id)
                
            return jsonify(config_obj), 200
            
        except Exception as e:
            return jsonify({'message': f'Error retrieving config: {str(e)}'}), 500
    
    @staticmethod
    def update_config():
        """
        Handle POST /<feature>/config request
        Updates pepper mode configuration for current admin
        
        Flow:
        1. Get admin_id from JWT token
        2. Get new_pepper_mode_id from request body
        3. Validate new_pepper_mode_id exists in Pepper_Mode table
        4. Update/Create configuration record for admin
        5. Return success response
        """
        try:
            # Get current admin ID from JWT token
            current_user = getattr(request, 'current_user', None)
            if not current_user or 'admin_id' not in current_user:
                return jsonify({'message': 'Admin ID not found in token'}), 401
            
            admin_id = current_user['admin_id']
            
            # Get request data
            data = request.get_json(force=True, silent=True)
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            new_pepper_mode_id = data.get('new_pepper_mode_id')
            if not new_pepper_mode_id:
                return jsonify({'message': 'new_pepper_mode_id is required'}), 400
            
            # Validate new_pepper_mode_id exists in Pepper_Mode table
            pepper_mode = PepperMode.get_pepper_mode_by_id(str(new_pepper_mode_id))
            if not pepper_mode:
                return jsonify({'message': 'Invalid pepper_mode_id'}), 400
            
            # Get existing configuration for admin
            existing_config = Configuration.get_configuration_by_admin_id(admin_id)
            
            if existing_config:
                # Update existing configuration
                config_id = existing_config.get('config_id')
                result = Configuration.update_configuration(
                    config_id=str(config_id), 
                    pepper_mode_id=str(new_pepper_mode_id)
                )
            else:
                # Create new configuration
                result = Configuration.create_configuration(
                    admin_id=admin_id,
                    pepper_mode_id=str(new_pepper_mode_id)
                )
            
            if result:
                return jsonify({
                    'status': 200,
                    'message': 'Configuration changed successfully'
                }), 200
            else:
                return jsonify({'message': 'Failed to update configuration'}), 500
                
        except Exception as e:
            return jsonify({'message': f'Error updating config: {str(e)}'}), 500
