#!/usr/bin/env python3
"""
Send AI-customized test emails via CCAI.
"""

import asyncio
import json
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

def generate_ai_email(name, company, title, recipient_email):
    """Generate AI-customized email based on profile data."""
    
    first_name = name.split()[0] if name else "Friend"
    
    if 'CEO' in title or 'Founder' in title:
        subject = f"Quick question about {company}'s growth strategy"
        content = f"""<p>Hi {first_name},</p>

<p>I came across your profile and was impressed by your leadership at {company}.</p>

<p>As {title}, you probably understand the challenges of scaling technology infrastructure while maintaining operational efficiency.</p>

<p>We've helped companies like {company} streamline their cloud architecture and reduce operational costs by up to 40%.</p>

<p>Would you be open to a brief 15-minute call to discuss how we might help {company} with your technology initiatives?</p>

<p>Thanks,</p>

<p>Andreas Garcia<br>
Account Executive<br>
AllCode: <a href="https://allcode.com/">https://allcode.com/</a><br>
LinkedIn Profile: <a href="https://www.linkedin.com/in/andreas-garcia-0a7963139">www.linkedin.com/in/andreas-garcia-0a7963139</a><br>
(415) 890-6431<br>
101 Montgomery Street<br>
San Francisco, CA 94104</p>"""
    else:
        subject = f"Your work at {company}"
        content = f"""<p>Hi {first_name},</p>

<p>I noticed your experience as {title} at {company} and wanted to reach out.</p>

<p>Given your background in technology, you'd probably appreciate our approach to cloud-native architecture and DevOps automation.</p>

<p>We specialize in helping companies like {company} build more scalable, reliable infrastructure.</p>

<p>Would you have 15 minutes to discuss some of the technical challenges you're facing?</p>

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
    """Send test AI-customized emails."""
    
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
    
    print("🧪 Sending AI-customized test emails...")
    print(f"📅 Emails scheduled for 2 minutes from now")
    print("=" * 50)
    
    ccai_client = CCAPIClient()
    
    for i, contact in enumerate(test_contacts, 1):
        print(f"\n📤 Processing {contact['name']} ({contact['email']})")
        print(f"🏢 Company: {contact['company']} | Title: {contact['title']}")
        
        try:
            # Generate AI-customized email
            print("🤖 Generating AI-customized email...")
            subject, content = generate_ai_email(
                contact['name'], 
                contact['company'], 
                contact['title'], 
                contact['email']
            )
            
            # Parse name
            name_parts = contact["name"].split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            # Send email
            print("📧 Sending personalized email...")
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
    
    print(f"\n🎉 Test email campaign completed!")
    print(f"📧 Check your inboxes in about 2 minutes")

if __name__ == "__main__":
    print("🧪 AI Email Test System - SEND MODE")
    print("=" * 40)
    asyncio.run(send_test_emails())