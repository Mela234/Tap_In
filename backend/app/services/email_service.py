import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from jinja2 import Template
from datetime import datetime


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.sender_name = os.getenv("SENDER_NAME", "TAPIN")
        
        if not self.sender_email or not self.sender_password:
            raise ValueError("SMTP credentials not configured in environment variables")
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send an email to a single recipient"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.sender_name} <{self.sender_email}>"
            msg["To"] = to_email
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_bulk_email(self, recipients: List[str], subject: str, html_content: str) -> dict:
        """Send email to multiple recipients"""
        results = {
            "sent": [],
            "failed": []
        }
        
        for email in recipients:
            if self.send_email(email, subject, html_content):
                results["sent"].append(email)
            else:
                results["failed"].append(email)
        
        return results
    
    def generate_weekly_digest_email(self, trends: List[dict], recipient_email: str) -> str:
        """Generate HTML email content for weekly trends digest"""
        
        trends_html = ""
        for trend in trends[:10]:  # Limit to top 10 trends
            trends_html += f"""
            <div style="margin-bottom: 20px; border-left: 4px solid #6366f1; padding-left: 15px;">
                <h3 style="margin: 5px 0; color: #1f2937; font-size: 18px;">
                    {trend.get('title', 'Untitled')}
                </h3>
                <p style="margin: 8px 0; color: #6b7280; font-size: 12px;">
                    📌 <strong>{trend.get('category', 'General')}</strong> | 
                    🔥 {int((trend.get('relevance_score', 0) or 0) * 100)}% trending
                </p>
                <p style="margin: 10px 0; color: #374151; line-height: 1.6;">
                    {trend.get('description', 'No description available')[:300]}...
                </p>
                {f'<p style="margin: 10px 0; color: #059669; font-style: italic;">💡 {trend.get("why_it_matters", "")}</p>' if trend.get('why_it_matters') else ''}
                <p style="margin: 10px 0; color: #6b7280; font-size: 12px;">
                    📚 Source: {trend.get('source', 'Unknown').upper()}
                </p>
            </div>
            """
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f9fafb;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #6366f1;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #6366f1;
                    margin: 0 0 10px 0;
                    font-size: 32px;
                }}
                .header p {{
                    color: #6b7280;
                    margin: 0;
                    font-size: 14px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .trends-section {{
                    margin-bottom: 30px;
                }}
                .footer {{
                    border-top: 1px solid #e5e7eb;
                    padding-top: 20px;
                    text-align: center;
                    color: #6b7280;
                    font-size: 12px;
                }}
                .cta-button {{
                    display: inline-block;
                    background-color: #6366f1;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin-top: 20px;
                    font-weight: 600;
                }}
                .cta-button:hover {{
                    background-color: #4f46e5;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔥 This Week's Trends</h1>
                    <p>Your bi-weekly digest from TAPIN - Gen Z Trend Mining</p>
                </div>
                
                <div class="content">
                    <p>Hi there! 👋</p>
                    <p>Here are the top trending topics this week that Gen Z is talking about. Stay ahead of the curve!</p>
                    
                    <div class="trends-section">
                        {trends_html}
                    </div>
                    
                    <center>
                        <a href="http://localhost:3000/trends/weekly" class="cta-button">
                            View All Trends →
                        </a>
                    </center>
                </div>
                
                <div class="footer">
                    <p>© {datetime.now().year} TAPIN. All rights reserved.</p>
                    <p>
                        You're receiving this email because you subscribed to our weekly trends digest.
                        <a href="http://localhost:3000" style="color: #6366f1; text-decoration: none;">Manage preferences</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template


# Create a singleton instance
email_service = None


def get_email_service() -> EmailService:
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service
