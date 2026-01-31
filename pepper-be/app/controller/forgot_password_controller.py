from flask import request, jsonify
from app.model.admin import Admin
from app.model.password_reset import PasswordReset
from app.services.email_service import EmailService
import re

class ForgotPasswordController:
    """Controller for handling forgot password functionality"""
    
    @staticmethod
    def forgot_password():
        """
        Handle forgot password request
        Expected request body: {"email": "admin@example.com"}
        
        Flow:
        1. Check IF admin with credential <email> exists in Admin table
        2a. IF not exists, return status: 400, message: "Email doesn't exists"
        2b. IF email exists, send link Change Password to Email
        3. Return response message: "Email sended"
        
        Returns:
            tuple: Flask response tuple (response_data, status_code)
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            email = data.get('email')
            
            # Validate email parameter
            if not email:
                return jsonify({'message': 'Email is required'}), 400
            
            # Validate email format
            if not ForgotPasswordController._is_valid_email(email):
                return jsonify({'message': 'Invalid email format'}), 400
            
            # Step 1: Check IF admin with credential <email> exists in Admin table
            admin = Admin.find_by_email(email)
            
            # Step 2a: IF not exists, return error
            if not admin:
                return jsonify({'message': 'Email doesn\'t exists'}), 400
            
            # Step 2b: IF email exists, create reset token and send email
            try:
                # Create password reset token (expires in 15 minutes)
                admin_id = admin['admin_id']
                reset_token = PasswordReset.create_reset_token(admin_id, expires_minutes=15)
                
                if not reset_token:
                    return jsonify({'message': 'Failed to generate reset token'}), 500
                
                # Extract admin name for personalization (if available)
                admin_name = admin.get('name') or admin.get('email', '').split('@')[0]
                
                # Send reset password email with deeplink
                success, error_msg = EmailService.send_reset_password_email(
                    recipient_email=email,
                    reset_token=reset_token,
                    admin_name=admin_name
                )
                
                if not success:
                    # Clean up token if email failed to send
                    PasswordReset.mark_token_used(reset_token)
                    
                    # Return user-friendly error message
                    return jsonify({'message': 'Error when sending email'}), 500
                
                # Step 3: Return success response
                return jsonify({'message': 'Email sended'}), 200
                
            except Exception as e:
                print(f"Error in forgot password process: {e}")
                return jsonify({'message': 'Internal server error'}), 500
                
        except Exception as e:
            print(f"Error handling forgot password request: {e}")
            return jsonify({'message': 'Internal server error'}), 500
    
    @staticmethod
    def reset_password():
        """
        Handle reset password request using token
        Expected request body: {"token": "abc123", "new_password": "newpass123"}
        
        Returns:
            tuple: Flask response tuple (response_data, status_code)
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            token = data.get('token')
            new_password = data.get('new_password')
            
            # Validate required parameters
            if not token:
                return jsonify({'message': 'Token is required'}), 400
            
            if not new_password:
                return jsonify({'message': 'New password is required'}), 400
            
            # Validate password strength
            if not ForgotPasswordController._is_valid_password(new_password):
                return jsonify({'message': 'Password must be at least 6 characters long'}), 400
            
            # Check if token exists and is valid
            if not PasswordReset.is_token_valid(token):
                return jsonify({'message': 'Invalid or expired token'}), 400
            
            # Get token details
            token_data = PasswordReset.get_reset_token(token)
            if not token_data:
                return jsonify({'message': 'Token not found'}), 400
            
            admin_id = token_data['admin_id']
            
            # Update admin password
            success = Admin.update_password(admin_id, new_password)
            if not success:
                return jsonify({'message': 'Failed to update password'}), 500
            
            # Mark token as used (invalidate it)
            PasswordReset.mark_token_used(token)
            
            # Invalidate all other tokens for this admin for security
            PasswordReset.invalidate_all_tokens_for_admin(admin_id)
            
            # Return success response
            return jsonify({'message': 'Password changed successfully'}), 200
            
        except Exception as e:
            print(f"Error handling reset password request: {e}")
            return jsonify({'message': 'Internal server error'}), 500
    
    @staticmethod
    def validate_token():
        """
        Validate reset token without changing password
        Expected request body: {"token": "abc123"}
        
        Returns:
            tuple: Flask response tuple (response_data, status_code)
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            token = data.get('token')
            
            if not token:
                return jsonify({'message': 'Token is required'}), 400
            
            # Check if token is valid
            if PasswordReset.is_token_valid(token):
                token_data = PasswordReset.get_reset_token(token)
                return jsonify({
                    'message': 'Token is valid',
                    'admin_id': token_data['admin_id'],
                    'expires_at': token_data['expires_at'],
                    'valid': True
                }), 200
            else:
                return jsonify({
                    'message': 'Invalid or expired token',
                    'valid': False
                }), 400
                
        except Exception as e:
            print(f"Error validating token: {e}")
            return jsonify({'message': 'Internal server error'}), 500
    
    @staticmethod
    def cleanup_expired_tokens():
        """
        Maintenance endpoint to cleanup expired tokens
        
        Returns:
            tuple: Flask response tuple (response_data, status_code)
        """
        try:
            cleaned_count = PasswordReset.cleanup_expired_tokens()
            
            return jsonify({
                'message': 'Expired tokens cleaned up successfully',
                'cleaned_count': cleaned_count
            }), 200
            
        except Exception as e:
            print(f"Error cleaning up expired tokens: {e}")
            return jsonify({'message': 'Internal server error'}), 500
    
    @staticmethod
    def get_token_stats():
        """
        Get password reset token statistics (for monitoring)
        
        Returns:
            tuple: Flask response tuple (response_data, status_code)
        """
        try:
            stats = PasswordReset.get_token_stats()
            
            return jsonify({
                'message': 'Token statistics retrieved successfully',
                'stats': stats
            }), 200
            
        except Exception as e:
            print(f"Error getting token statistics: {e}")
            return jsonify({'message': 'Internal server error'}), 500
    
    @staticmethod
    def _is_valid_email(email):
        """
        Validate email format using regex
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if valid email format, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def _is_valid_password(password):
        """
        Validate password strength
        
        Args:
            password (str): Password to validate
            
        Returns:
            bool: True if valid password, False otherwise
        """
        if not password or not isinstance(password, str):
            return False
        
        # Minimum 6 characters for now (can be enhanced with more rules)
        return len(password) >= 6 