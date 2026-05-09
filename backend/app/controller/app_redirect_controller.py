from flask import request, redirect, render_template_string, jsonify
import re

class AppRedirectController:
    """Controller for handling app redirects from email links"""
    
    @staticmethod
    def redirect_to_app():
        """
        Handle app redirect from email links
        This endpoint receives web links and redirects to mobile app or shows instructions
        
        Expected URL: /app-redirect/reset-password?token=abc123
        
        Returns:
            Flask response: Redirect to app or HTML page with instructions
        """
        try:
            # Get token from query parameters
            token = request.args.get('token')
            
            if not token:
                return jsonify({'message': 'Token is required'}), 400
            
            # Get user agent to detect mobile device
            user_agent = request.headers.get('User-Agent', '').lower()
            
            # Check if it's a mobile device
            is_mobile = any(mobile in user_agent for mobile in [
                'android', 'iphone', 'ipad', 'mobile', 'tablet'
            ])
            
            # Create deeplink
            deeplink = f"pepper://robotmanagement/fr/reset-password?token={token}"
            
            if is_mobile:
                # For mobile devices, try to redirect to app
                return AppRedirectController._create_mobile_redirect_page(deeplink, token)
            else:
                # For desktop, show instructions
                return AppRedirectController._create_desktop_instructions_page(deeplink, token)
                
        except Exception as e:
            print(f"Error in app redirect: {e}")
            return jsonify({'message': 'Internal server error'}), 500
    
    @staticmethod
    def _create_mobile_redirect_page(deeplink, token):
        """Create mobile redirect page that attempts to open the app"""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Opening Pepper Robot Management App...</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            min-height: 100vh;
            margin: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .container {{
            max-width: 400px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        .spinner {{
            border: 3px solid rgba(255,255,255,0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .manual-link {{
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            word-break: break-all;
            font-family: monospace;
            font-size: 12px;
        }}
        .button {{
            background: white;
            color: #007bff;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            margin: 10px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Opening Pepper Robot Management</h2>
        <div class="spinner"></div>
        <p>Redirecting to your app...</p>
        
        <div id="fallback" style="display: none;">
            <h3>App didn't open?</h3>
            <p>Please copy this link and paste it in your Pepper Robot Management app:</p>
            <div class="manual-link">{deeplink}</div>
            <button class="button" onclick="copyToClipboard()">📋 Copy Link</button>
            <p><small>Token: {token}</small></p>
        </div>
    </div>
    
    <script>
        // Try to open the app immediately
        window.location.href = '{deeplink}';
        
        // Show fallback after 3 seconds
        setTimeout(function() {{
            document.getElementById('fallback').style.display = 'block';
        }}, 3000);
        
        function copyToClipboard() {{
            const text = '{deeplink}';
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(text).then(function() {{
                    alert('Link copied to clipboard!');
                }});
            }} else {{
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('Link copied to clipboard!');
            }}
        }}
    </script>
</body>
</html>
        """
        
        return html_template
    
    @staticmethod
    def _create_desktop_instructions_page(deeplink, token):
        """Create desktop instructions page"""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pepper Robot Management - Reset Password</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: #007bff;
        }}
        .instructions {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .token-box {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            font-family: monospace;
            word-break: break-all;
        }}
        .button {{
            background: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px 5px;
        }}
        .button:hover {{
            background: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Pepper Robot Management</h1>
            <h2>Password Reset</h2>
        </div>
        
        <div class="instructions">
            <h3>📱 To reset your password on mobile:</h3>
            <ol>
                <li>Open your <strong>Pepper Robot Management</strong> mobile app</li>
                <li>Go to the password reset section</li>
                <li>Copy and paste the link below, or enter the token manually</li>
            </ol>
        </div>
        
        <h3>🔗 Reset Link:</h3>
        <div class="token-box">{deeplink}</div>
        <button class="button" onclick="copyLink()">📋 Copy Link</button>
        
        <h3>🔑 Manual Token Entry:</h3>
        <div class="token-box">{token}</div>
        <button class="button" onclick="copyToken()">📋 Copy Token</button>
        
        <div style="margin-top: 30px; padding: 20px; background: #fff3cd; border-radius: 5px;">
            <h4>🛡️ Security Notice:</h4>
            <ul>
                <li>This reset link expires in <strong>15 minutes</strong></li>
                <li>The token can only be used once</li>
                <li>Never share this link or token with anyone</li>
            </ul>
        </div>
    </div>
    
    <script>
        function copyLink() {{
            copyToClipboard('{deeplink}', 'Link copied to clipboard!');
        }}
        
        function copyToken() {{
            copyToClipboard('{token}', 'Token copied to clipboard!');
        }}
        
        function copyToClipboard(text, message) {{
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(text).then(function() {{
                    alert(message);
                }});
            }} else {{
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert(message);
            }}
        }}
    </script>
</body>
</html>
        """
        
        return html_template