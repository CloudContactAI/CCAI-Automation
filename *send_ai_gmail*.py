#!/usr/bin/env python3
"""
Send AI-generated Gmail-style emails via CCAI.
"""

import asyncio
import json
import os
import aiohttp
from pathlib import Path
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
    
    async def send_ai_email(self, first_name: str, last_name: str, to_email: str, subject: str, message: str):
        try:
            from datetime import datetime, timedelta
            import pytz
            
            pst = pytz.timezone('America/Los_Angeles')
            tomorrow = datetime.now(pst) + timedelta(days=1)
            scheduled_time = tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
            
            campaign = {
                "subject": subject,
                "title": f"AI Outbound - {first_name}",
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

async def send_ai_batch():
    """Send AI-generated emails via CCAI."""
    
    results_file = "ai_gmail_outbound_results.json"
    if not Path(results_file).exists():
        print(f"❌ Results file not found: {results_file}")
        print("Run ai_gmail_outbound.py first to generate emails")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        contacts = json.load(f)
    
    if not contacts:
        print("❌ No contacts found in results file")
        return
    
    print(f"📧 Sending {len(contacts)} AI-generated emails via CCAI...")
    
    ccai_client = CCAPIClient()
    sent_emails = 0
    errors = []
    
    for i, contact in enumerate(contacts, 1):
        contact_info = contact["contact_info"]
        email_content = contact["ai_generated_email"]
        
        print(f"\n📤 Sending to {contact_info['name']} ({i}/{len(contacts)})")
        
        try:
            lines = email_content.split('\n')
            subject = lines[0].replace("Subject: ", "")
            
            body_start = 1
            while body_start < len(lines) and not lines[body_start].strip():
                body_start += 1
            
            body = '\n'.join(lines[body_start:])
            
            name_parts = contact_info["name"].split()
            first_name = name_parts[0] if name_parts else "Friend"
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            email_result = await ccai_client.send_ai_email(
                first_name=first_name,
                last_name=last_name,
                to_email=contact_info["email"],
                subject=subject,
                message=body
            )
            
            if email_result["success"]:
                print(f"✅ AI email sent successfully")
                sent_emails += 1
            else:
                print(f"❌ Email failed: {email_result}")
                errors.append(f"Email to {contact_info['name']}: {email_result}")
                
        except Exception as e:
            print(f"❌ Email error: {e}")
            errors.append(f"Email to {contact_info['name']}: {e}")
        
        await asyncio.sleep(3)
    
    print(f"\n🎉 AI Gmail campaign completed!")
    print(f"📧 Emails sent: {sent_emails}")
    
    if errors:
        print(f"⚠️  Errors: {len(errors)}")
        for error in errors[:3]:
            print(f"   {error}")

async def preview_ai_emails():
    """Preview AI-generated emails."""
    
    results_file = "ai_gmail_outbound_results.json"
    if not Path(results_file).exists():
        print(f"❌ Results file not found: {results_file}")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        contacts = json.load(f)
    
    print(f"📧 Preview of {len(contacts)} AI-generated emails:")
    print("=" * 80)
    
    for i, contact in enumerate(contacts, 1):
        contact_info = contact["contact_info"]
        email_content = contact["ai_generated_email"]
        
        print(f"\n📤 AI Email {i} - To: {contact_info['name']} ({contact_info['email']})")
        print(f"🏢 Company: {contact_info['company']} | Title: {contact_info['title']}")
        print("-" * 60)
        print(email_content)
        print("-" * 60)

if __name__ == "__main__":
    import sys
    
    print("🤖 AI Gmail Email Sender")
    print("=" * 30)
    
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        asyncio.run(preview_ai_emails())
    else:
        asyncio.run(send_ai_batch())