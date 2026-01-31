import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class EmailService:
    """Email service for sending password reset emails"""
    
    # Email configuration - should be moved to environment variables in production
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    
    # These should be loaded from environment variables
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    
    # Base URL for password reset links
    BASE_URL = os.getenv("BASE_URL", "https://tselsmp.id")
    
    # Validate required environment variables
    @classmethod
    def _validate_smtp_config(cls):
        """Validate that required SMTP environment variables are set"""
        if not cls.SMTP_USERNAME:
            raise ValueError("SMTP_USERNAME environment variable is required")
        if not cls.SMTP_PASSWORD:
            raise ValueError("SMTP_PASSWORD environment variable is required")
    
    # Email settings
    FROM_NAME = "Pepper Robot Management"
    SUBJECT_RESET_PASSWORD = "Pepper Robot - Reset Password"
    
    # Deeplink configuration
    DEEPLINK_SCHEME = "pepper"
    
    @staticmethod
    def create_reset_password_email(recipient_email, reset_token, admin_name=None):
        """
        Create password reset email with HTML template and deeplink
        
        Args:
            recipient_email (str): Recipient email address
            reset_token (str): Password reset token
            admin_name (str): Admin name for personalization (optional)
            
        Returns:
            MIMEMultipart: Email message object
        """
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = EmailService.SUBJECT_RESET_PASSWORD
        msg['From'] = f"{EmailService.FROM_NAME} <{EmailService.SMTP_USERNAME}>"
        msg['To'] = recipient_email
        
        # Generate deeplink
        deeplink = f"{EmailService.DEEPLINK_SCHEME}://robotmanagement/fr/reset-password?token={reset_token}"
        
        # Personalization
        greeting = f"Hello {admin_name}," if admin_name else "Hello,"
        
        # Get base URL for reset links
        base_url = EmailService.BASE_URL
        
        # Get current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create plain text version
        text_content = f"""
{EmailService.FROM_NAME} - Password Reset Request

{greeting}

You have requested to reset your password for the Pepper Robot Management system.

To reset your password, please use the following link:

Open in Mobile App:
   {deeplink}

Manual Token Entry:
   Token: {reset_token}

IMPORTANT SECURITY INFORMATION:
- This reset link will expire in 15 minutes
- If you didn't request this password reset, please ignore this email
- Never share this link or token with anyone
- For security purposes, this token can only be used once

If you have any questions or concerns, please contact our support team.

Best regards,
{EmailService.FROM_NAME} Team

---
This is an automated message, please do not reply to this email.
        """.strip()
        
        # Create HTML version
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset - {EmailService.FROM_NAME}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{ 
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{ 
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
        }}
        .logo {{ 
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
        }}
        .title {{ 
            font-size: 20px;
            color: #333;
            margin: 0;
        }}
        .content {{ 
            margin-bottom: 30px;
        }}
        .button-container {{ 
            text-align: center;
            margin: 30px 0;
        }}
        .reset-button {{ 
            display: inline-block;
            background-color: #007bff;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 16px;
            margin: 10px;
        }}
        .reset-button:hover {{ 
            background-color: #0056b3;
        }}
        .copy-button {{ 
            display: inline-block;
            background-color: #6c757d;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
            margin: 10px;
            cursor: pointer;
        }}
        .copy-button:hover {{ 
            background-color: #5a6268;
        }}
        .token-box {{ 
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }}
        .security-notice {{ 
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }}
        .security-title {{ 
            font-weight: bold;
            color: #856404;
            margin-bottom: 10px;
        }}
        .security-list {{ 
            margin: 0;
            padding-left: 20px;
            color: #856404;
        }}
        .footer {{ 
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            font-size: 12px;
            color: #6c757d;
        }}
        .expiry {{ 
            color: #dc3545;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">{EmailService.FROM_NAME}</div>
            <h1 class="title">Password Reset Request</h1>
        </div>
        
        <div class="content">
            <p>{greeting}</p>
            <p>You have requested to reset your password for the <strong>Pepper Robot Management</strong> system.</p>
            <p>Click the button below to reset your password:</p>
        </div>
        
        <div class="button-container">
            <a href="{base_url}/reset-password?token={reset_token}" class="reset-button" target="_blank" rel="noopener">📱 Reset Password</a>
            <br>
            <button class="copy-button" onclick="copyToClipboard('pepper://robotmanagement/fr/reset-password?token={reset_token}')">📋 Copy Deeplink</button>
        </div>
        
        <script>
        function copyToClipboard(text) {{
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(text).then(function() {{
                    alert('Deeplink copied to clipboard!');
                }}).catch(function() {{
                    fallbackCopy(text);
                }});
            }} else {{
                fallbackCopy(text);
            }}
        }}
        
        function fallbackCopy(text) {{
            var textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {{
                document.execCommand('copy');
                alert('Deeplink copied to clipboard!');
            }} catch (err) {{
                alert('Copy failed. Please copy manually: ' + text);
            }}
            document.body.removeChild(textArea);
        }}
        </script>
        
        <div class="content">
            <h3>Manual Token Entry:</h3>
            <p>If the buttons above don't work, you can manually enter this token in the app:</p>
            <div class="token-box">
                <strong>Token:</strong> {reset_token}
            </div>
        </div>
        
        <div class="security-notice">
            <div class="security-title">🛡️ Security Information</div>
            <ul class="security-list">
                <li>This reset link will <span class="expiry">expire in 15 minutes</span></li>
                <li>If you didn't request this password reset, please ignore this email</li>
                <li>Never share this link or token with anyone</li>
                <li>This token can only be used once for security purposes</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Best regards,<br><strong>{EmailService.FROM_NAME} Team</strong></p>
            <p><em>This is an automated message, please do not reply to this email.</em></p>
            <p>Generated on: {current_time}</p>
        </div>
    </div>
</body>
</html>
        """.strip().format(
            greeting=greeting,
            base_url=base_url,
            reset_token=reset_token,
            EmailService=EmailService,
            current_time=current_time
        )
        
        # Attach parts to message
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        return msg
    
    @staticmethod
    def send_reset_password_email(recipient_email, reset_token, admin_name=None):
        """
        Send password reset email to recipient
        
        Args:
            recipient_email (str): Recipient email address
            reset_token (str): Password reset token
            admin_name (str): Admin name for personalization (optional)
            
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            # Validate SMTP configuration before sending
            EmailService._validate_smtp_config()
            
            # Create email message
            msg = EmailService.create_reset_password_email(recipient_email, reset_token, admin_name)
            
            # Connect to SMTP server
            print(f"Connecting to SMTP server: {EmailService.SMTP_SERVER}:{EmailService.SMTP_PORT}")
            server = smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT)
            
            # Enable TLS encryption
            server.starttls()
            
            # Login to email account
            print(f"Logging in as: {EmailService.SMTP_USERNAME}")
            server.login(EmailService.SMTP_USERNAME, EmailService.SMTP_PASSWORD)
            
            # Send email
            print(f"Sending email to: {recipient_email}")
            text = msg.as_string()
            server.sendmail(EmailService.SMTP_USERNAME, recipient_email, text)
            
            # Close connection
            server.quit()
            
            print(f"✅ Password reset email sent successfully to: {recipient_email}")
            return True, None
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication failed: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipient email refused: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"SMTP server disconnected: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    @staticmethod
    def test_smtp_connection():
        """
        Test SMTP connection without sending email
        
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            print(f"Testing SMTP connection to: {EmailService.SMTP_SERVER}:{EmailService.SMTP_PORT}")
            
            # Connect to SMTP server
            server = smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT)
            server.starttls()
            
            # Test login
            server.login(EmailService.SMTP_USERNAME, EmailService.SMTP_PASSWORD)
            server.quit()
            
            print("✅ SMTP connection test successful")
            return True, None
            
        except Exception as e:
            error_msg = f"SMTP connection test failed: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg