import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    """Service for sending emails (OTP, password reset, etc.)"""
    
    # SMTP Configuration - loaded from .env file
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    
    @staticmethod
    def generate_otp(length=6):
        """Generate a random OTP code"""
        return str(random.randint(10**(length-1), 10**length - 1))
    
    @staticmethod
    def send_otp_email(recipient_email, otp_code, purpose="verification"):
        """
        Send OTP email to recipient
        
        Args:
            recipient_email: Email address to send OTP to
            otp_code: The OTP code to send
            purpose: Purpose of OTP ("verification" or "password_reset")
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Check if email credentials are configured
        if not EmailService.SENDER_EMAIL or not EmailService.SENDER_PASSWORD:
            print("✗ Email credentials not configured in .env file")
            print(f"[TESTING MODE] OTP for {recipient_email}: {otp_code}")
            return False
        
        if EmailService.SENDER_PASSWORD == "your-app-password":
            print("✗ Please update SENDER_PASSWORD in .env with your Gmail App Password")
            print(f"[TESTING MODE] OTP for {recipient_email}: {otp_code}")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = EmailService._get_subject(purpose)
            message["From"] = EmailService.SENDER_EMAIL
            message["To"] = recipient_email
            
            # Create HTML content
            html_content = EmailService._get_email_template(otp_code, purpose)
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            print(f"Attempting to send email to {recipient_email}...")
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.set_debuglevel(0)  # Set to 1 for detailed SMTP logs
                server.starttls()
                print("Logging in to Gmail SMTP...")
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                print("Sending email...")
                server.sendmail(EmailService.SENDER_EMAIL, recipient_email, message.as_string())
            
            print(f"✓ OTP email sent successfully to {recipient_email}: {otp_code}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"✗ Gmail authentication failed: {e}")
            print("\n--- GMAIL APP PASSWORD REQUIRED ---")
            print("Gmail blocks regular passwords. You need to:")
            print("1. Go to https://myaccount.google.com/security")
            print("2. Enable 2-Step Verification")
            print("3. Go to https://myaccount.google.com/apppasswords")
            print("4. Create an App Password for 'Mail'")
            print("5. Update SENDER_PASSWORD in .env with the 16-character app password")
            print("------------------------------------\n")
            print(f"[TESTING MODE] OTP for {recipient_email}: {otp_code}")
            return False
            
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            print(f"[TESTING MODE] OTP for {recipient_email}: {otp_code}")
            return False
    
    @staticmethod
    def _get_subject(purpose):
        """Get email subject based on purpose"""
        if purpose == "verification":
            return "SARI NA - Email Verification Code"
        elif purpose == "password_reset":
            return "SARI NA - Password Reset Code"
        else:
            return "SARI NA - Verification Code"
    
    @staticmethod
    def _get_email_template(otp_code, purpose):
        """Get HTML email template"""
        if purpose == "verification":
            title = "Email Verification"
            message = "Thank you for signing up for SARI NA! Please use the following code to verify your email address:"
            footer = "If you didn't create an account, please ignore this email."
        elif purpose == "password_reset":
            title = "Password Reset"
            message = "You requested to reset your password. Please use the following code to complete the process:"
            footer = "If you didn't request a password reset, please ignore this email and your password will remain unchanged."
        else:
            title = "Verification Code"
            message = "Your verification code is:"
            footer = "Thank you for using SARI NA."
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #002A7A;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .otp-code {{
                    background-color: #002A7A;
                    color: white;
                    font-size: 32px;
                    font-weight: bold;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px;
                    margin: 20px 0;
                    letter-spacing: 5px;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SARI NA</h1>
                    <h2>{title}</h2>
                </div>
                <div class="content">
                    <p>{message}</p>
                    <div class="otp-code">{otp_code}</div>
                    <p>This code will expire in 10 minutes.</p>
                    <div class="footer">
                        <p>{footer}</p>
                        <p>&copy; 2025 SARI NA. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
