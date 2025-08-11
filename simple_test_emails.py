#!/usr/bin/env python3
"""
Simple test file for AI-customized Gmail-style emails.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

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
    
    return f"Subject: {subject}\n\n{content}"

def preview_test_emails():
    """Preview the test emails."""
    
    # Test data based on LinkedIn profiles (you can update with real scraped data)
    test_contacts = [
        {
            "name": "Andreas Garcia",
            "email": "andreas@allcode.com",
            "company": "AllCode",
            "title": "CEO & Founder",
            "linkedin_url": "https://www.linkedin.com/in/andreas-garcia-0a7963139"
        },
        {
            "name": "Joel Garcia",
            "email": "joel@allcode.com", 
            "company": "AllCode",
            "title": "Software Developer",
            "linkedin_url": "https://www.linkedin.com/in/joelgarcia/"
        }
    ]
    
    print("📧 AI-customized email previews:")
    print("=" * 50)
    
    for i, contact in enumerate(test_contacts, 1):
        print(f"\n📤 Test Email {i} - To: {contact['name']} ({contact['email']})")
        print(f"🏢 Company: {contact['company']} | Title: {contact['title']}")
        print(f"🔗 LinkedIn: {contact['linkedin_url']}")
        
        # Generate AI-customized email
        ai_email = generate_ai_email(
            contact['name'], 
            contact['company'], 
            contact['title'], 
            contact['email']
        )
        
        print("-" * 50)
        print(ai_email)
        print("-" * 50)

if __name__ == "__main__":
    print("🧪 Simple AI Email Test System")
    print("=" * 35)
    preview_test_emails()