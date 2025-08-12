#!/usr/bin/env python3
"""
AI-powered email automation with website scraping
Scrapes contact websites and generates personalized emails using AI
"""
import os
import csv
import json
import asyncio
import aiohttp
import random
import time
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytz

# Load environment variables
load_dotenv()

class WebsiteScraper:
    """Scrapes company websites for relevant information"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver for website scraping"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def scrape_website(self, website_url, contact_name="", company_name=""):
        """
        Scrape a company website for relevant information
        
        Args:
            website_url: URL of the website to scrape
            contact_name: Name of the contact (for context)
            company_name: Name of the company (for context)
        
        Returns:
            Dict with scraped website information
        """
        try:
            print(f"🌐 Scraping website: {website_url}")
            
            # Ensure URL has protocol
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            # Navigate to website
            self.driver.get(website_url)
            time.sleep(3)
            
            # Extract key information
            website_info = {
                'url': website_url,
                'title': self._extract_page_title(),
                'description': self._extract_meta_description(),
                'services': self._extract_services(),
                'about': self._extract_about_section(),
                'recent_news': self._extract_recent_news(),
                'technologies': self._extract_technologies(),
                'industry_keywords': self._extract_industry_keywords(),
                'contact_info': self._extract_contact_info()
            }
            
            print(f"✅ Successfully scraped {website_info['title']}")
            return website_info
            
        except Exception as e:
            print(f"❌ Error scraping website {website_url}: {e}")
            return self._create_fallback_website_info(website_url, company_name)
    
    def _extract_page_title(self):
        """Extract page title"""
        try:
            return self.driver.title.strip()
        except:
            return "Website"
    
    def _extract_meta_description(self):
        """Extract meta description"""
        try:
            meta_desc = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
            return meta_desc.get_attribute('content')[:300]
        except:
            return ""
    
    def _extract_services(self):
        """Extract services/products information"""
        services = []
        
        # Look for common service-related sections
        service_selectors = [
            'section[class*="service"]',
            'div[class*="service"]',
            'section[class*="product"]',
            'div[class*="product"]',
            '.services',
            '.products',
            '#services',
            '#products'
        ]
        
        for selector in service_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements[:3]:  # Limit to first 3
                    text = element.text.strip()
                    if text and len(text) > 20 and len(text) < 500:
                        services.append(text[:200])
            except:
                continue
        
        return services[:3]  # Return max 3 services
    
    def _extract_about_section(self):
        """Extract about/company information"""
        about_selectors = [
            'section[class*="about"]',
            'div[class*="about"]',
            '.about',
            '#about',
            'section[class*="company"]',
            'div[class*="company"]'
        ]
        
        for selector in about_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and len(text) > 50:
                    return text[:400]  # Limit length
            except:
                continue
        
        return ""
    
    def _extract_recent_news(self):
        """Extract recent news or blog posts"""
        news = []
        
        news_selectors = [
            'article',
            '.blog-post',
            '.news-item',
            'section[class*="news"]',
            'div[class*="blog"]',
            '.post'
        ]
        
        for selector in news_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements[:2]:  # Limit to first 2
                    # Look for headlines within the news item
                    headlines = element.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4')
                    if headlines:
                        headline_text = headlines[0].text.strip()
                        if headline_text and len(headline_text) > 10:
                            news.append(headline_text[:150])
            except:
                continue
        
        return news[:2]  # Return max 2 news items
    
    def _extract_technologies(self):
        """Extract technology keywords from the website"""
        tech_keywords = []
        
        # Common technology terms to look for
        tech_terms = [
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'React', 'Angular', 'Vue',
            'Python', 'JavaScript', 'Node.js', 'API', 'REST', 'GraphQL', 'MongoDB', 'PostgreSQL',
            'MySQL', 'Redis', 'Elasticsearch', 'Machine Learning', 'AI', 'Artificial Intelligence',
            'DevOps', 'CI/CD', 'Microservices', 'Serverless', 'Blockchain', 'IoT'
        ]
        
        try:
            page_text = self.driver.page_source.lower()
            for term in tech_terms:
                if term.lower() in page_text:
                    tech_keywords.append(term)
        except:
            pass
        
        return tech_keywords[:5]  # Return max 5 technologies
    
    def _extract_industry_keywords(self):
        """Extract industry-specific keywords"""
        industry_terms = [
            'fintech', 'healthcare', 'e-commerce', 'retail', 'manufacturing', 'logistics',
            'education', 'real estate', 'insurance', 'banking', 'startup', 'enterprise',
            'SaaS', 'B2B', 'B2C', 'marketplace', 'platform', 'analytics', 'automation'
        ]
        
        keywords = []
        try:
            page_text = self.driver.page_source.lower()
            for term in industry_terms:
                if term.lower() in page_text:
                    keywords.append(term)
        except:
            pass
        
        return keywords[:3]  # Return max 3 industry keywords
    
    def _extract_contact_info(self):
        """Extract contact information"""
        contact_info = {}
        
        try:
            # Look for email addresses
            import re
            page_source = self.driver.page_source
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_source)
            if emails:
                contact_info['email'] = emails[0]  # First email found
            
            # Look for phone numbers
            phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', page_source)
            if phones:
                contact_info['phone'] = phones[0]  # First phone found
        except:
            pass
        
        return contact_info
    
    def _create_fallback_website_info(self, website_url, company_name):
        """Create fallback website info when scraping fails"""
        return {
            'url': website_url,
            'title': f"{company_name} Website" if company_name else "Company Website",
            'description': "Website information not available due to access restrictions.",
            'services': [],
            'about': "",
            'recent_news': [],
            'technologies': [],
            'industry_keywords': [],
            'contact_info': {}
        }
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

class AIWebsiteEmailGenerator:
    """Generate AI-powered emails based on website information"""
    
    def __init__(self):
        self.goals = [
            "book a 15-minute discovery call to discuss technology optimization opportunities",
            f"introduce {os.getenv('SENDER_COMPANY', 'AllCode')}'s development and cloud services",
            "offer a collaboration on digital transformation initiatives",
            "schedule a brief consultation about scaling their technology infrastructure"
        ]
        
        self.tones = ["professional", "consultative", "friendly"]
    
    async def generate_ai_email(self, website_info, contact_name, contact_email, goal=None, tone=None):
        """Generate AI email based on website information"""
        
        # Use AWS Bedrock for AI generation
        try:
            import boto3
            
            # Set up AWS credentials
            aws_profile = os.getenv('AWS_PROFILE')
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            
            if aws_profile:
                session = boto3.Session(profile_name=aws_profile)
                bedrock = session.client('bedrock-runtime', region_name=aws_region)
                print(f"🔐 Using AWS profile: {aws_profile}")
            else:
                bedrock = boto3.client('bedrock-runtime', region_name=aws_region)
                print("🔐 Using default AWS credentials")
            
            # Format website information for AI
            website_summary = self.format_website_for_ai(website_info, contact_name)
            
            # Generate email using AI
            goal = goal or random.choice(self.goals)
            tone = tone or random.choice(self.tones)
            
            first_name = contact_name.split()[0] if contact_name else "there"
            
            # Get sender information
            sender_name = os.getenv('SENDER_NAME', 'Your Name')
            sender_title = os.getenv('SENDER_TITLE', 'Your Title')
            sender_company = os.getenv('SENDER_COMPANY', 'Your Company')
            sender_company_url = os.getenv('SENDER_COMPANY_URL', 'https://yourcompany.com')
            sender_linkedin = os.getenv('SENDER_LINKEDIN', 'https://linkedin.com/in/yourprofile')
            sender_phone = os.getenv('SENDER_PHONE', '+1234567890')
            
            prompt = f"""Write a personalized cold outreach email to {first_name} based on their company website:

{website_summary}

IMPORTANT REQUIREMENTS:
1. Reference specific details from their website (services, technologies, recent news, etc.)
2. Connect their business to relevant technology solutions
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

            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 1000,
                    "temperature": 0.7
                }
            })
            
            response = bedrock.invoke_model(
                modelId="us.amazon.nova-pro-v1:0",
                body=body,
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            email_content = response_body['output']['message']['content'][0]['text']
            
            return email_content
            
        except Exception as e:
            print(f"❌ AI generation failed: {e}")
            return self.generate_fallback_email(website_info, contact_name)
    
    def format_website_for_ai(self, website_info, contact_name):
        """Format website information for AI prompt"""
        summary = []
        
        summary.append(f"Contact: {contact_name}")
        summary.append(f"Website: {website_info['url']}")
        summary.append(f"Company: {website_info['title']}")
        
        if website_info['description']:
            summary.append(f"Description: {website_info['description']}")
        
        if website_info['services']:
            summary.append(f"Services: {', '.join(website_info['services'])}")
        
        if website_info['about']:
            summary.append(f"About: {website_info['about'][:200]}...")
        
        if website_info['technologies']:
            summary.append(f"Technologies: {', '.join(website_info['technologies'])}")
        
        if website_info['industry_keywords']:
            summary.append(f"Industry: {', '.join(website_info['industry_keywords'])}")
        
        if website_info['recent_news']:
            summary.append(f"Recent News: {'; '.join(website_info['recent_news'])}")
        
        return "\n".join(summary)
    
    def generate_fallback_email(self, website_info, contact_name):
        """Generate fallback email when AI generation fails"""
        
        first_name = contact_name.split()[0] if contact_name else "there"
        company_name = website_info['title']
        
        # Get sender information
        sender_name = os.getenv('SENDER_NAME', 'Your Name')
        sender_title = os.getenv('SENDER_TITLE', 'Your Title')
        sender_company = os.getenv('SENDER_COMPANY', 'Your Company')
        sender_company_url = os.getenv('SENDER_COMPANY_URL', 'https://yourcompany.com')
        sender_linkedin = os.getenv('SENDER_LINKEDIN', 'https://linkedin.com/in/yourprofile')
        sender_phone = os.getenv('SENDER_PHONE', '+1234567890')
        
        # Create personalized content based on website info
        tech_mention = ""
        if website_info['technologies']:
            tech_mention = f" I noticed you're using {website_info['technologies'][0]} - we have extensive experience optimizing similar technology stacks."
        
        subject = f"Technology optimization opportunity for {company_name}"
        
        content = f"""<p>Hi {first_name},</p>

<p>I came across {company_name}'s website and was impressed by your {website_info['description'][:100] if website_info['description'] else 'business approach'}.{tech_mention}</p>

<p>At {sender_company}, we help companies optimize their technology infrastructure and accelerate digital transformation. Would you have 15 minutes to discuss potential opportunities?</p>

<p>Thanks,</p>

<p>{sender_name}<br>
{sender_title}<br>
{sender_company}: <a href="{sender_company_url}">{sender_company_url}</a><br>
LinkedIn Profile: <a href="{sender_linkedin}">{sender_linkedin}</a><br>
{sender_phone}<br>
101 Montgomery Street<br>
San Francisco, CA 94104</p>"""
        
        return f"Subject: {subject}\n\n{content}"

async def send_email_via_ccai(subject, content, recipient_email, sender_name):
    """Send email through CloudContactAI API"""
    
    # Get CCAI credentials
    api_key = os.getenv('CCAI_API_KEY')
    client_id = os.getenv('CCAI_CLIENT_ID')
    email_url = os.getenv('CCAI_EMAIL_URL')
    
    if not all([api_key, client_id, email_url]):
        print("❌ Missing CCAI credentials in environment variables")
        return False
    
    # Schedule email for immediate delivery
    scheduled_time = datetime.now(pytz.timezone('America/Los_Angeles')) + timedelta(minutes=1)
    
    email_data = {
        "title": f"Website Email - {recipient_email}",
        "message": content,
        "senderEmail": os.getenv("SENDER_EMAIL", "your@email.com"),
        "replyEmail": os.getenv("SENDER_EMAIL", "your@email.com"),
        "senderName": sender_name,
        "scheduledTimestamp": scheduled_time.isoformat(),
        "scheduledTimezone": "America/Los_Angeles",
        "subject": subject,
        "recipients": [{"email": recipient_email}]
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'X-Client-ID': client_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{email_url}/api/email-campaigns", json=email_data, headers=headers) as response:
                if response.status == 200:
                    print(f"✅ Email sent successfully to {recipient_email}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to send email: {response.status} - {error_text}")
                    return False
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

async def process_website_contacts():
    """Main function to process contacts with website scraping"""
    
    print("🌐 AI Website Email Automation")
    print("=" * 40)
    
    # Look for CSV files with company name
    sender_company = os.getenv('SENDER_COMPANY', 'AllCode')
    csv_files = list(Path(".").glob(f"{sender_company}*.csv"))
    
    if not csv_files:
        print(f"❌ No {sender_company} CSV file found")
        return
    
    csv_file = csv_files[0]
    print(f"📁 Processing: {csv_file}")
    
    # Initialize scraper and AI generator
    scraper = WebsiteScraper()
    ai_generator = AIWebsiteEmailGenerator()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            contacts = list(reader)
        
        print(f"📋 Found {len(contacts)} contacts")
        
        successful_emails = 0
        
        for i, contact in enumerate(contacts[:5], 1):  # Process first 5 contacts
            print(f"\n📤 Processing contact {i}/{min(5, len(contacts))}")
            print(f"👤 Name: {contact.get('name', 'Unknown')}")
            print(f"📧 Email: {contact.get('email', 'Unknown')}")
            print(f"🌐 Website: {contact.get('website', 'Unknown')}")
            
            # Skip if no website
            if not contact.get('website'):
                print("⚠️ No website found, skipping...")
                continue
            
            # Scrape website
            website_info = scraper.scrape_website(
                contact['website'], 
                contact.get('name', ''),
                contact.get('company', '')
            )
            
            # Generate AI email
            email_content = await ai_generator.generate_ai_email(
                website_info,
                contact.get('name', ''),
                contact.get('email', '')
            )
            
            if email_content:
                # Parse subject and content
                lines = email_content.split('\n', 1)
                subject = lines[0].replace('Subject: ', '').strip()
                content = lines[1].strip() if len(lines) > 1 else email_content
                
                print(f"📝 Generated email with subject: {subject}")
                
                # Send email
                success = await send_email_via_ccai(
                    subject,
                    content,
                    contact['email'],
                    os.getenv('SENDER_NAME', 'Your Name')
                )
                
                if success:
                    successful_emails += 1
                
                # Add delay between emails
                await asyncio.sleep(2)
            
            else:
                print("❌ Failed to generate email")
        
        print(f"\n🎉 Completed! Successfully sent {successful_emails} emails")
        
    except Exception as e:
        print(f"❌ Error processing contacts: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    asyncio.run(process_website_contacts())
