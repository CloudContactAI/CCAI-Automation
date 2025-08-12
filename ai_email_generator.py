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
            self.bedrock = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
        
        self.goals = [
            "book a 15-minute discovery call to discuss AWS optimization opportunities",
            "introduce AllCode's cloud infrastructure services",
            "offer a collaboration on cloud security solutions",
            "schedule a brief consultation about scaling their infrastructure"
        ]
        
        self.tones = ["professional", "consultative", "friendly"]
    
    def scrape_linkedin_with_posts(self, linkedin_url, driver):
        """Scrape LinkedIn profile including recent posts from last 30 days."""
        try:
            from linkedin_scraper import Person
            import time
            
            # Get basic profile
            person = Person(linkedin_url, driver=driver, close_on_complete=False)
            
            # Get recent activity (posts from last 30 days)
            recent_posts = []
            try:
                driver.get(linkedin_url + "recent-activity/all/")
                time.sleep(3)
                
                # Look for posts in the last 30 days
                activities = driver.find_elements("css selector", "[data-id*='urn:li:activity']")[:5]
                
                for activity in activities:
                    try:
                        # Get post text
                        text_elem = activity.find_element("css selector", ".feed-shared-text")
                        post_text = text_elem.text if text_elem else ""
                        
                        # Get post date (approximate)
                        date_elem = activity.find_element("css selector", "time")
                        post_date = date_elem.get_attribute("datetime") if date_elem else ""
                        
                        if post_text and len(post_text) > 20:  # Filter out very short posts
                            recent_posts.append({
                                "text": post_text[:300],  # Limit length
                                "date": post_date
                            })
                    except:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Could not scrape recent posts: {e}")
            
            return {
                'name': person.name,
                'company': person.company,
                'job_title': person.job_title,
                'about': person.about[:400] if person.about else "",
                'recent_posts': recent_posts[:2],  # Keep top 2 recent posts
                'experiences': [
                    {
                        'position_title': exp.position_title,
                        'institution_name': exp.institution_name,
                        'duration': exp.duration
                    } for exp in person.experiences[:2]
                ] if person.experiences else []
            }
            
        except Exception as e:
            print(f"❌ LinkedIn scraping failed: {e}")
            return None
    
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

Andreas Garcia
Account Executive
AllCode: https://allcode.com/
LinkedIn Profile: www.linkedin.com/in/andreas-garcia-0a7963139
(415) 890-6431
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
        
        email = f"""Subject: {subject}

<p>Hi {first_name},</p>

{post_reference}

<p>Your role as {role} at {company} caught my attention, especially given your insights on LinkedIn.</p>

<p>At AllCode, we help companies optimize their AWS infrastructure and would love to discuss how we might support {company}'s growth.</p>

<p>Would you have 15 minutes for a quick call?</p>

<p>Thanks,</p>

<p>Andreas Garcia<br>
Account Executive<br>
AllCode: <a href="https://allcode.com/">https://allcode.com/</a><br>
LinkedIn Profile: <a href="https://www.linkedin.com/in/andreas-garcia-0a7963139">www.linkedin.com/in/andreas-garcia-0a7963139</a><br>
(415) 890-6431<br>
101 Montgomery Street<br>
San Francisco, CA 94104</p>"""
        
        return email