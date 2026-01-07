# backend/utils/email_templates.py
def get_email_header(logo_url: str = "http://localhost:8000/images/logo.png") -> str:
    """Generate email header with SPMS logo"""
    return f"""
    <div style="background: linear-gradient(135deg, #0b6e6b, #095a58); 
                padding: 20px; text-align: center;">
        <img src="{logo_url}" alt="SPMS Logo" 
             style="width: 150px; background: white; 
                    padding: 12px; border-radius: 8px;">
        <h2 style="color: white; margin-top: 12px;">
            Smart Participants Management System
        </h2>
    </div>
    """

def generate_welcome_email(user_name: str, logo_url: str = None) -> str:
    """Generate welcome email HTML"""
    if not logo_url:
        logo_url = "http://localhost:8000/images/logo.png"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
        {get_email_header(logo_url)}
        <div style="padding: 30px; background: #f5f7fa;">
            <div style="background: white; padding: 30px; border-radius: 8px; 
                        max-width: 600px; margin: 0 auto;">
                <h2 style="color: #0b6e6b;">Welcome to SPMS, {user_name}!</h2>
                <p>Your account has been created successfully.</p>
                <p>You can now login to the system and start managing participants.</p>
                <a href="http://localhost:5173" 
                   style="display: inline-block; background: #0b6e6b; color: white; 
                          padding: 12px 24px; text-decoration: none; border-radius: 4px; 
                          margin-top: 20px;">
                    Login to SPMS
                </a>
            </div>
        </div>
        <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
            <p>&copy; 2024 SPMS. All rights reserved.</p>
        </div>
    </body>
    </html>
    """