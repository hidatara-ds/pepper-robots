from app.model.admin import Admin
from app.utils.jwt_helper import generate_access_token

class AuthService:
    
    @staticmethod
    def admin_login(email, password):
        """
        Authenticate admin user following the flow:
        1. Check IF admin with credential exists
        2a. IF not exists, return status 400 with "Wrong credentials"
        2b. IF credentials true, get the Admin obj
        3. Assign admin.last_login = current timestamp
        4. Create access token from admin
        5. Return response
        """
        
        admin = Admin.find_by_credentials(email, password)
        
        if not admin:
            return None, "Wrong credentials", 400
        
        last_login = Admin.update_last_login(admin['admin_id'])
        admin['last_login'] = last_login
        
        access_token = generate_access_token(admin)
        
        return {
            'access_token': access_token,
            'user': admin['email'],
            'login_at': last_login
        }, None, 200