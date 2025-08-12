"""
Chrome WebDriver management with LinkedIn authentication
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

_driver_instance: Optional[webdriver.Chrome] = None

def get_or_create_driver(authentication=None) -> webdriver.Chrome:
    """
    Get or create a Chrome WebDriver instance with LinkedIn authentication.
    
    Args:
        authentication: Authentication information (optional)
    
    Returns:
        Chrome WebDriver instance with LinkedIn cookies
    """
    global _driver_instance
    
    if _driver_instance is None:
        chrome_options = Options()
        
        # Add user agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Optional: Run in headless mode (comment out for debugging)
        # chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        _driver_instance = webdriver.Chrome(options=chrome_options)
        
        # Execute script to remove webdriver property
        _driver_instance.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Add LinkedIn session cookies if available
        linkedin_session_cookie = os.getenv('LINKEDIN_SESSION_COOKIE')
        if linkedin_session_cookie:
            print("🍪 Adding LinkedIn session cookie to ChromeDriver...")
            
            # First navigate to LinkedIn to set the domain
            _driver_instance.get("https://www.linkedin.com")
            
            # Add the session cookie
            _driver_instance.add_cookie({
                'name': 'li_at',
                'value': linkedin_session_cookie,
                'domain': '.linkedin.com',
                'path': '/',
                'secure': True,
                'httpOnly': True
            })
            
            # Refresh to apply the cookie
            _driver_instance.refresh()
            print("✅ LinkedIn session cookie added successfully")
        else:
            print("⚠️ No LinkedIn session cookie found in environment variables")
    
    return _driver_instance

def close_driver():
    """Close the WebDriver instance"""
    global _driver_instance
    if _driver_instance:
        _driver_instance.quit()
        _driver_instance = None

def test_linkedin_authentication():
    """Test if LinkedIn authentication is working"""
    driver = get_or_create_driver()
    try:
        driver.get("https://www.linkedin.com/feed/")
        
        # Check if we're logged in by looking for the feed
        if "feed" in driver.current_url and "login" not in driver.current_url:
            print("✅ LinkedIn authentication successful - logged in!")
            return True
        else:
            print("❌ LinkedIn authentication failed - not logged in")
            return False
    except Exception as e:
        print(f"❌ Error testing LinkedIn authentication: {e}")
        return False
