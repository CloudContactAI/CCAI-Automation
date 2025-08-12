#!/usr/bin/env python3
"""
AI-powered Gmail-style outbound using structured prompts.
Uses OpenAI/Claude to generate unique, personalized emails.
"""

import asyncio
import csv
import json
import random
import os
from pathlib import Path
from linkedin_scraper import Person
from linkedin_mcp_server.error_handler import safe_get_driver

# You'll need to install: uv add boto3
try:
    import boto3
    HAS_BEDROCK = True
except ImportError:
    HAS_BEDROCK = False

class AIEmailGenerator:
    """AI-powered email generator using structured prompts."""
    
    def __init__(self):
        if HAS_BEDROCK:
            # Support AWS profiles (including SSO profiles)
            aws_profile = os.getenv('AWS_PROFILE')
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            
            if aws_profile:
                try:
                    # Use specific profile (works with SSO profiles)
                    session = boto3.Session(profile_name=aws_profile)
                    self.bedrock = session.client('bedrock-runtime', region_name=aws_region)
                    print(f"🔐 Using AWS profile: {aws_profile}")
                except Exception as e:
                    print(f"⚠️ AWS profile '{aws_profile}' not found or invalid: {e}")
                    print("🔄 Falling back to environment variables or default credentials...")
                    # Fall back to environment variables by creating session without profile
                    try:
                        # Create session with explicit credentials from environment
                        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
                        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
                        
                        if aws_access_key and aws_secret_key:
                            session = boto3.Session(
                                aws_access_key_id=aws_access_key,
                                aws_secret_access_key=aws_secret_key,
                                region_name=aws_region
                            )
                            self.bedrock = session.client('bedrock-runtime')
                            print(f"🔐 Using AWS credentials from environment variables in region: {aws_region}")
                        else:
                            # Use default credentials (IAM role, default profile, etc.)
                            self.bedrock = boto3.client('bedrock-runtime', region_name=aws_region)
                            print(f"🔐 Using default AWS credentials in region: {aws_region}")
                    except Exception as fallback_error:
                        print(f"❌ Fallback also failed: {fallback_error}")
                        raise
            else:
                # No profile specified, use environment variables or default credentials
                aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
                aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
                
                if aws_access_key and aws_secret_key:
                    session = boto3.Session(
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=aws_region
                    )
                    self.bedrock = session.client('bedrock-runtime')
                    print(f"🔐 Using AWS credentials from environment variables in region: {aws_region}")
                else:
                    # Use default credentials (IAM role, default profile, etc.)
                    self.bedrock = boto3.client('bedrock-runtime', region_name=aws_region)
                    print(f"🔐 Using default AWS credentials in region: {aws_region}")
        
        self.goals = [
            "book a 15-minute discovery call to discuss AWS optimization opportunities",
            f"introduce {os.getenv('SENDER_COMPANY', 'AllCode')}'s cloud infrastructure services",
            "offer a collaboration on cloud security solutions",
            "schedule a brief consultation about scaling their infrastructure"
        ]
        
        self.tones = ["professional", "consultative", "friendly"]
    
    def format_profile_info(self, person_data, csv_data):
        """Format LinkedIn profile info for the AI prompt."""
        profile_info = []
        
        # Basic info
        name = person_data.get('name', csv_data.get('First Name', ''))
        title = person_data.get('job_title', csv_data.get('Title', ''))
        company = person_data.get('company', csv_data.get('Company', ''))
        
        profile_info.append(f"Name: {name}")
        profile_info.append(f"Role: {title} at {company}")
        
        # About section
        if person_data.get('about'):
            profile_info.append(f"About: {person_data['about'][:300]}")
        
        # Recent experiences
        experiences = person_data.get('experiences', [])
        if experiences:
            profile_info.append("Recent Experience:")
            for exp in experiences[:2]:
                if exp.get('position_title') and exp.get('institution_name'):
                    profile_info.append(f"- {exp['position_title']} at {exp['institution_name']}")
        
        # Recent activity
        if person_data.get('recent_activity'):
            profile_info.append(f"Recent Post: {person_data['recent_activity'][:200]}")
        
        # Company context from CSV
        industry = csv_data.get('Industry', '')
        if industry:
            profile_info.append(f"Industry: {industry}")
        
        aws_usage = csv_data.get('AWS User - Gemini', '')
        if aws_usage and 'confirmed' in aws_usage.lower():
            profile_info.append(f"AWS Usage: {aws_usage}")
        
        return "\n".join(profile_info)
    
    async def generate_email_with_ai(self, profile_info, first_name, goal=None, tone=None):
        """Generate email using Bedrock Nova Pro with the structured prompt."""
        
        if not HAS_BEDROCK:
            return self.generate_fallback_email(profile_info, first_name)
        
        goal = goal or random.choice(self.goals)
        tone = tone or random.choice(self.tones)
        
        sender_name = os.getenv('SENDER_NAME', 'Andreas Garcia')
        sender_title = os.getenv('SENDER_TITLE', 'Account Executive')
        sender_linkedin = os.getenv('SENDER_LINKEDIN', 'https://www.linkedin.com/in/andreas-garcia-0a7963139')
        sender_phone = os.getenv('SENDER_PHONE', '(415) 890-6431')
        sender_company = os.getenv('SENDER_COMPANY', 'AllCode')
        sender_company_url = os.getenv('SENDER_COMPANY_URL', 'https://allcode.com')
        
        prompt = f"""Write a cold outreach email to {first_name}, based on the following LinkedIn profile info:

{profile_info}

The goal is to {goal}. Make the email personalized, concise (under 150 words), and reference specific details from the profile (e.g., role, experience, recent posts, skills, education, or interests). The tone should be {tone}. 

Format as professional business email with:
- Proper greeting
- 2-3 short paragraphs (each paragraph should be separate with <p> tags)
- Clear call-to-action
- Professional signature

Format as:
Subject: [real subject line - no HTML tags]

[email body in HTML format with proper paragraph breaks using <p> tags]

Thanks,

{sender_name}
{sender_title}
{sender_company}: {sender_company_url}
LinkedIn Profile: {sender_linkedin}
{sender_phone}
101 Montgomery Street
San Francisco, CA 94104"""

        try:
            import json
            
            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 300,
                    "temperature": 0.7
                }
            })
            
            response = self.bedrock.invoke_model(
                modelId="us.amazon.nova-pro-v1:0",
                body=body,
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['output']['message']['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"⚠️ Bedrock generation failed: {e}")
            return self.generate_fallback_email(profile_info, first_name)
    
    def generate_fallback_email(self, profile_info, first_name):
        """Fallback email generation when AI is not available."""
        
        sender_name = os.getenv('SENDER_NAME', 'Andreas Garcia')
        sender_title = os.getenv('SENDER_TITLE', 'Account Executive')
        sender_linkedin = os.getenv('SENDER_LINKEDIN', 'https://www.linkedin.com/in/andreas-garcia-0a7963139')
        sender_phone = os.getenv('SENDER_PHONE', '(415) 890-6431')
        sender_company = os.getenv('SENDER_COMPANY', 'AllCode')
        sender_company_url = os.getenv('SENDER_COMPANY_URL', 'https://allcode.com')
        
        # Extract key details from profile info
        lines = profile_info.split('\n')
        company = ""
        role = ""
        
        for line in lines:
            if line.startswith("Role:"):
                role_info = line.replace("Role:", "").strip()
                if " at " in role_info:
                    role, company = role_info.split(" at ", 1)
                else:
                    role = role_info
        
        subject_options = [
            f"AWS optimization opportunity for {first_name}",
            f"Exploring AWS optimization with {company}",
            f"Quick AWS discussion for {first_name}"
        ]
        
        subject = random.choice(subject_options)
        
        email = f"""Subject: {subject}

<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333; max-width: 600px; }}
        p {{ margin-bottom: 16px; }}
        .signature {{ margin-top: 20px; border-top: 1px solid #ddd; padding-top: 15px; }}
        a {{ color: #1a73e8; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <p>Hi {first_name},</p>
    
    <p>I noticed your role as {role} at {company} and thought you might be interested in how we're helping similar companies optimize their AWS infrastructure.</p>
    
    <p>At {sender_company}, we've helped companies reduce cloud costs by 30-40% while improving performance and reliability. Our clients typically see immediate improvements in both cost efficiency and system performance.</p>
    
    <p>Would you have 15 minutes for a quick call to discuss your current setup and explore potential optimizations?</p>
    
    <div class="signature">
        <p>Thanks,</p>
        <p><strong>{sender_name}</strong><br>
        {sender_title}<br>
        <strong>{sender_company}:</strong> <a href="{sender_company_url}">{sender_company_url}</a><br>
        <strong>LinkedIn:</strong> <a href="{sender_linkedin}">{sender_linkedin}</a><br>
        <a href="tel:{sender_phone.replace('(', '').replace(')', '').replace(' ', '').replace('-', '')}">{sender_phone}</a><br>
        101 Montgomery Street<br>
        San Francisco, CA 94104</p>
    </div>
</body>
</html>"""
        
        return email

async def generate_ai_gmail_outbound(limit=10):
    """Generate AI-powered Gmail-style emails."""
    
    sender_company = os.getenv('SENDER_COMPANY', 'AllCode')
    csv_files = list(Path(".").glob(f"{sender_company}*.csv"))
    if not csv_files:
        print(f"❌ No {sender_company} CSV file found")
        return
    
    csv_file = csv_files[0]
    print(f"📁 Processing: {csv_file}")
    
    if not HAS_BEDROCK:
        print("⚠️ Boto3 not installed. Using fallback generation.")
        print("Install with: uv add boto3")
    else:
        print("🤖 Using AWS Bedrock Nova Pro for email generation")
    
    driver = safe_get_driver()
    ai_generator = AIEmailGenerator()
    results = []
    
    with open(csv_file, 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.DictReader(file)
        all_rows = list(reader)
        
        valid_rows = [row for row in all_rows 
                     if row.get("Person Linkedin Url", "").strip() 
                     and row.get("Email", "").strip()]
        
        selected_rows = random.sample(valid_rows, min(limit, len(valid_rows)))
        print(f"📊 Found {len(valid_rows)} valid contacts, selecting {len(selected_rows)}")
        
        for row_num, row in enumerate(selected_rows, 1):
            linkedin_url = row.get("Person Linkedin Url", "").strip()
            first_name = row.get("First Name", "")
            last_name = row.get("Last Name", "")
            email = row.get("Email", "")
            company = row.get("Company", "")
            
            full_name = f"{first_name} {last_name}".strip()
            
            print(f"\n👤 Contact {row_num}: {full_name} at {company}")
            
            try:
                # Get LinkedIn profile data
                cache_file = f"cache_{linkedin_url.split('/')[-2]}.json"
                if Path(cache_file).exists():
                    print("📋 Using cached profile...")
                    with open(cache_file, 'r') as f:
                        person_data = json.load(f)
                else:
                    print("🔍 Scraping LinkedIn profile...")
                    person = Person(linkedin_url, driver=driver, close_on_complete=False)
                    
                    # Get recent activity
                    recent_activity = ""
                    try:
                        driver.get(linkedin_url + "recent-activity/all/")
                        import time
                        time.sleep(3)
                        
                        activities = driver.find_elements("css selector", "[data-id*='urn:li:activity']")[:1]
                        if activities:
                            try:
                                text_elem = activities[0].find_element("css selector", ".feed-shared-text")
                                if text_elem and text_elem.text:
                                    recent_activity = text_elem.text[:250]
                            except:
                                pass
                    except:
                        pass
                    
                    person_data = {
                        'name': person.name,
                        'company': person.company,
                        'job_title': person.job_title,
                        'about': person.about[:400] if person.about else "",
                        'recent_activity': recent_activity,
                        'experiences': [
                            {
                                'position_title': exp.position_title,
                                'institution_name': exp.institution_name,
                                'duration': exp.duration
                            } for exp in person.experiences[:2]
                        ] if person.experiences else []
                    }
                    
                    with open(cache_file, 'w') as f:
                        json.dump(person_data, f, indent=2)
                
                # Format profile info for AI prompt
                print("🧠 Formatting profile for AI generation...")
                profile_info = ai_generator.format_profile_info(person_data, row)
                
                # Generate AI-powered email
                print("🤖 Generating AI-powered email...")
                ai_email = await ai_generator.generate_email_with_ai(
                    profile_info, first_name
                )
                
                contact_result = {
                    "row_number": row_num,
                    "contact_info": {
                        "name": full_name,
                        "email": email,
                        "company": company,
                        "title": row.get("Title", "")
                    },
                    "linkedin_data": person_data,
                    "profile_info_used": profile_info,
                    "ai_generated_email": ai_email
                }
                
                results.append(contact_result)
                print(f"✅ AI email generated successfully!")
                
            except Exception as e:
                print(f"❌ Error processing {linkedin_url}: {e}")
                continue
    
    # Save results
    output_file = "ai_gmail_outbound_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 AI Gmail outbound generation complete!")
    print(f"📊 Generated {len(results)} AI-powered emails")
    print(f"💾 Results saved to: {output_file}")
    
    # Display sample emails
    if results:
        for i, result in enumerate(results[:2], 1):
            print(f"\n📧 AI Email {i} for {result['contact_info']['name']}:")
            print("=" * 80)
            print(result['ai_generated_email'])
            print("=" * 80)
    
    return results

if __name__ == "__main__":
    print("🤖 Bedrock Nova Pro Gmail Outbound Generator")
    print("=" * 50)
    
    asyncio.run(generate_ai_gmail_outbound(limit=5))