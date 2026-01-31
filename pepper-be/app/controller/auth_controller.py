from flask import request, jsonify
from app.services.auth_service import AuthService

class AuthController:
    
    @staticmethod
    def login():
        """
        Handle login request
        Expected request body: {"email": "...", "password": "..."}
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'message': 'Email and password are required'}), 400
            
            # Call auth service
            result, error, status_code = AuthService.admin_login(email, password)
            
            if error:
                return jsonify({'message': error}), status_code
            
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
        
    