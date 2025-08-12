#!/usr/bin/env python3
"""
Send AI-personalized single email via CCAI API with LinkedIn scraping.
Usage: python3 send_single_email.py "recipient@email.com" "linkedin_url"
"""

import asyncio
import sys
import os
import aiohttp
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from ai_email_generator import AIEmailGenerator
from linkedin_mcp_server.error_handler import safe_get_driver

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

async def send_ai_email(to_email: str, linkedin_url: str, schedule_minutes: int = 2):
    """Send AI-personalized email based on LinkedIn profile."""
    
    print(f"📧 Sending AI-personalized email to: {to_email}")
    print(f"🔗 LinkedIn: {linkedin_url}")
    print(f"⏰ Scheduled for: {schedule_minutes} minutes from now")
    print("-" * 60)
    
    # Initialize AI generator and driver
    ai_generator = AIEmailGenerator()
    driver = safe_get_driver()
    
    try:
        # Scrape LinkedIn profile with recent posts
        print("🔍 Scraping LinkedIn profile and recent posts...")
        person_data = ai_generator.scrape_linkedin_with_posts(linkedin_url, driver)
        
        if not person_data:
            print("❌ Failed to scrape LinkedIn profile")
            return
        
        # Format profile for AI
        print("🧠 Formatting profile data for AI...")
        profile_info = ai_generator.format_profile_for_ai(person_data)
        
        # Generate AI email
        print("🤖 Generating AI-personalized email...")
        first_name = person_data.get('name', '').split()[0] if person_data.get('name') else to_email.split('@')[0]
        ai_email = await ai_generator.generate_ai_email(profile_info, first_name)
        
        # Parse subject and message
        lines = ai_email.split('\n')
        subject = lines[0].replace("Subject: ", "")
        
        body_start = 1
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1
        
        message = '\n'.join(lines[body_start:])
        
        print(f"📝 Subject: {subject}")
        print("📧 Sending AI-personalized email...")
        
        # Send email
        ccai_client = CCAPIClient()
        result = await ccai_client.send_single_email(to_email, subject, message, schedule_minutes)
        
        if result["success"]:
            print(f"✅ AI-personalized email sent successfully!")
            print(f"📅 Scheduled for: {result.get('scheduled_time', 'Unknown time')}")
        else:
            print(f"❌ Email failed: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if driver:
            driver.quit()

def show_usage():
    print("🤖 AI-Powered Single Email Sender")
    print("=" * 40)
    print("Usage:")
    print('  python3 send_single_email.py "email@domain.com" "linkedin_url"')
    print('  python3 send_single_email.py "email@domain.com" "linkedin_url" 5  # Schedule 5 minutes from now')
    print()
    print("Examples:")
    print('  python3 send_single_email.py "john@company.com" "https://linkedin.com/in/john-doe"')
    print('  python3 send_single_email.py "jane@startup.com" "https://linkedin.com/in/jane-smith" 10')
    print()
    print("Features:")
    print('  • Scrapes LinkedIn profile and recent posts')
    sender_company = os.getenv('SENDER_COMPANY', 'AllCode')
    print('  • Uses AWS Bedrock AI for personalization')
    print('  • References recent LinkedIn activity in email')
    print(f'  • Professional {sender_company} signature included')

if __name__ == "__main__":
    if len(sys.argv) < 3:
        show_usage()
        sys.exit(1)
    
    to_email = sys.argv[1]
    linkedin_url = sys.argv[2]
    schedule_minutes = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    asyncio.run(send_ai_email(to_email, linkedin_url, schedule_minutes))