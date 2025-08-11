#!/usr/bin/env python3
"""
Send a single email via CCAI API.
Usage: python3 send_single_email.py "recipient@email.com" "Subject" "Message"
"""

import asyncio
import sys
import os
import aiohttp
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

class CCAPIClient:
    def __init__(self):
        self.api_key = os.getenv("CCAI_API_KEY")
        self.client_id = os.getenv("CCAI_CLIENT_ID")
        self.email_url = os.getenv("CCAI_EMAIL_URL")
        
        if not self.api_key or not self.client_id:
            raise ValueError("CCAI_API_KEY and CCAI_CLIENT_ID must be set in .env file")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "clientId": self.client_id,
            "accountId": "1223"
        }
    
    async def send_single_email(self, to_email: str, subject: str, message: str, schedule_minutes: int = 2):
        try:
            pst = pytz.timezone('America/Los_Angeles')
            scheduled_time = datetime.now(pst) + timedelta(minutes=schedule_minutes)
            
            # Extract name from email if possible
            name_part = to_email.split('@')[0]
            first_name = name_part.replace('.', ' ').replace('_', ' ').title()
            
            campaign = {
                "subject": subject,
                "title": f"Single Email - {first_name}",
                "message": message,
                "senderEmail": os.getenv("SENDER_EMAIL", "andreas@allcode.com"),
                "replyEmail": os.getenv("SENDER_EMAIL", "andreas@allcode.com"),
                "senderName": os.getenv("SENDER_NAME", "Andreas Garcia"),
                "scheduledTimestamp": scheduled_time.isoformat(),
                "scheduledTimezone": "America/Los_Angeles",
                "accounts": [{
                    "firstName": first_name,
                    "lastName": "",
                    "email": to_email,
                    "phone": ""
                }],
                "campaignType": "EMAIL",
                "addToList": "noList",
                "contactInput": "accounts",
                "fromType": "single",
                "senders": []
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.email_url}/api/v1/campaigns",
                    headers=self.headers,
                    json=campaign
                ) as response:
                    result = await response.json()
                    return {
                        "success": response.status in [200, 201],
                        "status_code": response.status,
                        "response": result,
                        "scheduled_time": scheduled_time.strftime("%I:%M %p PST")
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}

async def send_email(to_email: str, subject: str, message: str, schedule_minutes: int = 2):
    """Send a single email."""
    
    print(f"📧 Sending email to: {to_email}")
    print(f"📝 Subject: {subject}")
    print(f"⏰ Scheduled for: {schedule_minutes} minutes from now")
    print("-" * 50)
    
    ccai_client = CCAPIClient()
    
    result = await ccai_client.send_single_email(to_email, subject, message, schedule_minutes)
    
    if result["success"]:
        print(f"✅ Email sent successfully!")
        print(f"📅 Scheduled for: {result.get('scheduled_time', 'Unknown time')}")
    else:
        print(f"❌ Email failed: {result}")

def show_usage():
    print("📧 Single Email Sender")
    print("=" * 30)
    print("Usage:")
    print('  python3 send_single_email.py "email@domain.com" "Subject" "Message"')
    print('  python3 send_single_email.py "email@domain.com" "Subject" "Message" 5  # Schedule 5 minutes from now')
    print()
    print("Examples:")
    print('  python3 send_single_email.py "john@company.com" "Quick question" "Hi John, hope you\'re well..."')
    print('  python3 send_single_email.py "jane@startup.com" "AWS Discussion" "<p>Hi Jane,</p><p>Interested in AWS optimization?</p>"')

if __name__ == "__main__":
    if len(sys.argv) < 4:
        show_usage()
        sys.exit(1)
    
    to_email = sys.argv[1]
    subject = sys.argv[2]
    message = sys.argv[3]
    schedule_minutes = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    
    asyncio.run(send_email(to_email, subject, message, schedule_minutes))