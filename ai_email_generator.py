#!/usr/bin/env python3
"""
Shared AI email generator with LinkedIn scraping and recent post analysis.
"""

import json
import random
import os
from datetime import datetime, timedelta
from pathlib import Path

# You'll need to install: uv add boto3
try:
    import boto3
    HAS_BEDROCK = True
except ImportError:
    HAS_BEDROCK = False

class AIEmailGenerator:
    """AI-powered email generator with LinkedIn integration."""
    
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
                    # Fall back to environment variables by temporarily unsetting AWS_PROFILE
                    try:
                        # Create session with explicit credentials from environment
                        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
                        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
                        
                        if aws_access_key and aws_secret_key:
                            # Temporarily unset AWS_PROFILE to avoid boto3 confusion
                            original_profile = os.environ.pop('AWS_PROFILE', None)
                            try:
                                session = boto3.Session(
                                    aws_access_key_id=aws_access_key,
                                    aws_secret_access_key=aws_secret_key,
                                    region_name=aws_region
                                )
                                self.bedrock = session.client('bedrock-runtime')
                                print(f"🔐 Using AWS credentials from environment variables in region: {aws_region}")
                            finally:
                                # Restore AWS_PROFILE if it was set
                                if original_profile:
                                    os.environ['AWS_PROFILE'] = original_profile
                        else:
                            # Temporarily unset AWS_PROFILE and use default credentials
                            original_profile = os.environ.pop('AWS_PROFILE', None)
                            try:
                                self.bedrock = boto3.client('bedrock-runtime', region_name=aws_region)
                                print(f"🔐 Using default AWS credentials in region: {aws_region}")
                            finally:
                                # Restore AWS_PROFILE if it was set
                                if original_profile:
                                    os.environ['AWS_PROFILE'] = original_profile
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
    
    def scrape_linkedin_with_posts(self, linkedin_url, driver):
        """Scrape LinkedIn profile with fallback when scraping fails."""
        try:
            import time
            from selenium.webdriver.common.by import By
            
            print(f"🔍 Scraping LinkedIn profile: {linkedin_url}")
            
            # Navigate to profile
            driver.get(linkedin_url)
            time.sleep(5)
            
            # Check if page loaded properly
            page_title = driver.title.lower()
            current_url = driver.current_url.lower()
            
            if ("this page isn't working" in page_title or 
                "login" in current_url or 
                "authwall" in current_url or
                "challenge" in current_url):
                
                print("⚠️ LinkedIn access blocked or session expired")
                return self._create_fallback_profile(linkedin_url)
            
            # Try to extract basic information
            name = self._extract_element_text(driver, [
                "h1.text-heading-xlarge", "h1.break-words", "h1", 
                "[data-generated-suggestion-target]", ".pv-text-details__left-panel h1"
            ], "Name not found")
            
            headline = self._extract_element_text(driver, [
                ".text-body-medium.break-words", ".text-body-medium",
                ".pv-text-details__left-panel .text-body-medium"
            ], "Headline not found", filter_func=lambda x: len(x) > 5 and "connections" not in x.lower())
            
            location = self._extract_element_text(driver, [
                ".text-body-small.inline.t-black--light.break-words",
                ".text-body-small", ".pv-text-details__left-panel .text-body-small"
            ], "Location not found", filter_func=lambda x: ',' in x)
            
            # If we couldn't extract basic info, use fallback
            if name == "Name not found" and headline == "Headline not found":
                print("⚠️ Could not extract profile information, using fallback")
                return self._create_fallback_profile(linkedin_url)
            
            result = {
                'name': name,
                'company': self._extract_company_from_headline(headline),
                'job_title': headline,
                'about': "",
                'recent_posts': [],  # Skip posts for now due to reliability issues
                'location': location,
                'experiences': []
            }
            
            print(f"✅ Successfully scraped profile for {name}")
            return result
            
        except Exception as e:
            print(f"❌ LinkedIn scraping failed: {e}")
            return self._create_fallback_profile(linkedin_url)
    
    def _create_fallback_profile(self, linkedin_url):
        """Create a fallback profile when scraping fails"""
        # Extract name from URL if possible
        url_parts = linkedin_url.rstrip('/').split('/')
        profile_slug = url_parts[-1] if url_parts else "unknown"
        
        # Try to make a reasonable name from the profile slug
        if profile_slug and profile_slug != "unknown":
            # Convert joelgarcia -> Joel Garcia
            name_parts = []
            current_part = ""
            for char in profile_slug:
                if char.isupper() and current_part:
                    name_parts.append(current_part.capitalize())
                    current_part = char
                elif char.isalpha():
                    current_part += char
                elif char in ['-', '_'] and current_part:
                    name_parts.append(current_part.capitalize())
                    current_part = ""
            
            if current_part:
                name_parts.append(current_part.capitalize())
            
            fallback_name = " ".join(name_parts) if name_parts else "LinkedIn User"
        else:
            fallback_name = "LinkedIn User"
        
        print(f"🔄 Using fallback profile for {fallback_name}")
        
        return {
            'name': fallback_name,
            'company': "Company not available",
            'job_title': "Professional",
            'about': "LinkedIn profile information not available due to access restrictions.",
            'recent_posts': [],
            'location': "Location not available",
            'experiences': []
        }
    
    def _extract_element_text(self, driver, selectors, default="Not found", filter_func=None):
        """Extract text from element using multiple selectors with optional filtering"""
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        text = element.text.strip()
                        if text and (not filter_func or filter_func(text)):
                            return text
                    except:
                        continue
            except:
                continue
        return default
    
    def _extract_company_from_headline(self, headline):
        """Extract company name from headline"""
        if " at " in headline:
            return headline.split(" at ")[-1].strip()
        elif " @ " in headline:
            return headline.split(" @ ")[-1].strip()
        return "Company not found"
    
    def format_profile_for_ai(self, person_data, csv_data=None):
        """Format LinkedIn profile info for AI prompt including recent posts."""
        profile_info = []
        
        # Basic info
        name = person_data.get('name', csv_data.get('First Name', '') if csv_data else '')
        title = person_data.get('job_title', csv_data.get('Title', '') if csv_data else '')
        company = person_data.get('company', csv_data.get('Company', '') if csv_data else '')
        
        profile_info.append(f"Name: {name}")
        profile_info.append(f"Role: {title} at {company}")
        
        # About section
        if person_data.get('about'):
            profile_info.append(f"About: {person_data['about']}")
        
        # Recent posts (key feature!)
        recent_posts = person_data.get('recent_posts', [])
        if recent_posts:
            profile_info.append("Recent LinkedIn Posts:")
            for i, post in enumerate(recent_posts, 1):
                profile_info.append(f"Post {i}: {post['text']}")
        
        # Recent experiences
        experiences = person_data.get('experiences', [])
        if experiences:
            profile_info.append("Recent Experience:")
            for exp in experiences:
                if exp.get('position_title') and exp.get('institution_name'):
                    profile_info.append(f"- {exp['position_title']} at {exp['institution_name']}")
        
        # Company context from CSV if available
        if csv_data:
            industry = csv_data.get('Industry', '')
            if industry:
                profile_info.append(f"Industry: {industry}")
            
            aws_usage = csv_data.get('AWS User - Gemini', '')
            if aws_usage and 'confirmed' in aws_usage.lower():
                profile_info.append(f"AWS Usage: {aws_usage}")
        
        return "\n".join(profile_info)
    
    async def generate_ai_email(self, profile_info, first_name, goal=None, tone=None):
        """Generate AI email using Bedrock Nova Pro with recent post context."""
        
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
        
        prompt = f"""Write a personalized cold outreach email to {first_name} based on their LinkedIn profile:

{profile_info}

IMPORTANT REQUIREMENTS:
1. If they have recent LinkedIn posts, reference their most recent post naturally in the email
2. Connect their post content to their business/role
3. The goal is to {goal}
4. Keep it under 150 words, {tone} tone
5. Use HTML format with <p> tags for paragraphs
6. Include professional signature

Format as:
Subject: [compelling subject line - no HTML tags]

[email body in HTML format with proper <p> tags]

Thanks,

{sender_name}
{sender_title}
{sender_company}: {sender_company_url}
LinkedIn Profile: {sender_linkedin}
{sender_phone}
101 Montgomery Street
San Francisco, CA 94104"""

        try:
            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 400,
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
        """Fallback email when AI is not available."""
        
        # Extract key details
        lines = profile_info.split('\n')
        company = ""
        role = ""
        recent_post = ""
        
        for line in lines:
            if line.startswith("Role:"):
                role_info = line.replace("Role:", "").strip()
                if " at " in role_info:
                    role, company = role_info.split(" at ", 1)
                else:
                    role = role_info
            elif line.startswith("Post 1:"):
                recent_post = line.replace("Post 1:", "").strip()[:100]
        
        subject = f"Your recent LinkedIn post caught my attention"
        
        post_reference = ""
        if recent_post:
            post_reference = f"<p>I saw your recent LinkedIn post about {recent_post[:50]}... and it really resonated with me.</p>"
        
        sender_name = os.getenv('SENDER_NAME', 'Andreas Garcia')
        sender_title = os.getenv('SENDER_TITLE', 'Account Executive')
        sender_linkedin = os.getenv('SENDER_LINKEDIN', 'https://www.linkedin.com/in/andreas-garcia-0a7963139')
        sender_phone = os.getenv('SENDER_PHONE', '(415) 890-6431')
        sender_company = os.getenv('SENDER_COMPANY', 'AllCode')
        sender_company_url = os.getenv('SENDER_COMPANY_URL', 'https://allcode.com')
        
        email = f"""Subject: {subject}

<p>Hi {first_name},</p>

{post_reference}

<p>Your role as {role} at {company} caught my attention, especially given your insights on LinkedIn.</p>

<p>At {sender_company}, we help companies optimize their AWS infrastructure and would love to discuss how we might support {company}'s growth.</p>

<p>Would you have 15 minutes for a quick call?</p>

<p>Thanks,</p>

<p>{sender_name}<br>
{sender_title}<br>
{sender_company}: <a href="{sender_company_url}">{sender_company_url}</a><br>
LinkedIn Profile: <a href="{sender_linkedin}">{sender_linkedin}</a><br>
{sender_phone}<br>
101 Montgomery Street<br>
San Francisco, CA 94104</p>"""
        
        return email