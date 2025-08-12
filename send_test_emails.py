#!/usr/bin/env python3
"""
Send AI-customized test emails with LinkedIn scraping via CCAI.
"""

import asyncio
import json
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
    
    async def send_test_email(self, first_name, last_name, to_email, subject, message):
        try:
            pst = pytz.timezone('America/Los_Angeles')
            now = datetime.now(pst)
            # Schedule for 2 minutes from now for testing
            scheduled_time = now + timedelta(minutes=2)
            
            campaign = {
                "subject": subject,
                "title": f"Test AI Email - {first_name}",
                "message": message,
                "senderEmail": os.getenv("SENDER_EMAIL", "andreas@allcode.com"),
                "replyEmail": os.getenv("SENDER_EMAIL", "andreas@allcode.com"),
                "senderName": os.getenv("SENDER_NAME", "Andreas Garcia"),
                "scheduledTimestamp": scheduled_time.isoformat(),
                "scheduledTimezone": "America/Los_Angeles",
                "accounts": [{
                    "firstName": first_name,
                    "lastName": last_name,
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
                        "response": result
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}

async def generate_ai_email_with_linkedin(contact, ai_generator, driver):
    """Generate AI-customized email with LinkedIn scraping and recent posts."""
    
    try:
        # Scrape LinkedIn profile with recent posts
        print(f"🔍 Scraping LinkedIn profile: {contact['linkedin_url']}")
        person_data = ai_generator.scrape_linkedin_with_posts(contact['linkedin_url'], driver)
        
        if not person_data:
            print("⚠️ LinkedIn scraping failed, using fallback data")
            person_data = {
                'name': contact['name'],
                'company': contact['company'],
                'job_title': contact['title'],
                'about': '',
                'recent_posts': [],
                'experiences': []
            }
        
        # Format profile for AI
        profile_info = ai_generator.format_profile_for_ai(person_data)
        
        # Generate AI email
        first_name = contact['name'].split()[0] if contact['name'] else "Friend"
        ai_email = await ai_generator.generate_ai_email(profile_info, first_name)
        
        # Parse subject and content
        lines = ai_email.split('\n')
        subject = lines[0].replace("Subject: ", "")
        
        body_start = 1
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1
        
        content = '\n'.join(lines[body_start:])
        
        return subject, content
        
    except Exception as e:
        print(f"❌ AI generation failed: {e}")
        # Fallback to simple template
        first_name = contact['name'].split()[0] if contact['name'] else "Friend"
        subject = f"Quick question about {contact['company']}"
        content = f"""<p>Hi {first_name},</p>

<p>I came across your profile and wanted to reach out about your work at {contact['company']}.</p>

<p>At AllCode, we help companies optimize their cloud infrastructure. Would you have 15 minutes to discuss potential opportunities?</p>

<p>Thanks,</p>

<p>Andreas Garcia<br>
Account Executive<br>
AllCode: <a href="https://allcode.com/">https://allcode.com/</a><br>
LinkedIn Profile: <a href="https://www.linkedin.com/in/andreas-garcia-0a7963139">www.linkedin.com/in/andreas-garcia-0a7963139</a><br>
(415) 890-6431<br>
101 Montgomery Street<br>
San Francisco, CA 94104</p>"""
        
        return subject, content

async def send_test_emails():
    """Send test AI-customized emails with LinkedIn scraping."""
    
    # Test data based on LinkedIn profiles
    test_contacts = [
        {
            "name": "Andreas Garcia",
            "email": "andreas@allcode.com",
            "company": "AllCode",
            "title": "Software Developer",
            "linkedin_url": "https://www.linkedin.com/in/andreas-garcia-0a7963139"
        },
        {
            "name": "Joel Garcia",
            "email": "joel@allcode.com", 
            "company": "AllCode",
            "title": "CEO & Founder",
            "linkedin_url": "https://www.linkedin.com/in/joelgarcia/"
        }
    ]
    
    print("🤖 Sending AI-customized test emails with LinkedIn scraping...")
    print(f"📅 Emails scheduled for 2 minutes from now")
    print("=" * 60)
    
    # Initialize AI generator and driver
    ai_generator = AIEmailGenerator()
    driver = safe_get_driver()
    ccai_client = CCAPIClient()
    
    try:
        for i, contact in enumerate(test_contacts, 1):
            print(f"\n📤 Processing {contact['name']} ({contact['email']})")
            print(f"🏢 Company: {contact['company']} | Title: {contact['title']}")
            print(f"🔗 LinkedIn: {contact['linkedin_url']}")
            
            try:
                # Generate AI-customized email with LinkedIn data
                print("🤖 Generating AI email with LinkedIn scraping...")
                subject, content = await generate_ai_email_with_linkedin(contact, ai_generator, driver)
                
                # Parse name
                name_parts = contact["name"].split()
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                # Send email
                print("📧 Sending AI-personalized email...")
                result = await ccai_client.send_test_email(
                    first_name=first_name,
                    last_name=last_name,
                    to_email=contact["email"],
                    subject=subject,
                    message=content
                )
                
                if result["success"]:
                    print(f"✅ AI-customized email scheduled successfully")
                    print(f"📧 Subject: {subject}")
                else:
                    print(f"❌ Email failed: {result}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Delay between emails
            await asyncio.sleep(3)
        
        print(f"\n🎉 AI test email campaign completed!")
        print(f"📧 Check your inboxes in about 2 minutes")
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("🤖 AI Email Test System with LinkedIn Scraping - SEND MODE")
    print("=" * 60)
    asyncio.run(send_test_emails())