"""
LinkedIn authentication module
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

def ensure_authentication() -> Dict[str, Any]:
    """
    Ensure LinkedIn authentication is available.
    
    Returns:
        Dict containing authentication information
    """
    linkedin_session_cookie = os.getenv('LINKEDIN_SESSION_COOKIE')
    linkedin_username = os.getenv('LINKEDIN_USERNAME')
    linkedin_password = os.getenv('LINKEDIN_PASSWORD')
    
    if linkedin_session_cookie:
        print("🍪 Using LinkedIn session cookie authentication")
        return {
            "authenticated": True,
            "method": "session_cookies",
            "status": "ready",
            "session_cookie": linkedin_session_cookie
        }
    elif linkedin_username and linkedin_password:
        print("🔐 Using LinkedIn username/password authentication")
        return {
            "authenticated": True,
            "method": "username_password",
            "status": "ready",
            "username": linkedin_username,
            "password": linkedin_password
        }
    else:
        print("⚠️ No LinkedIn authentication credentials found")
        return {
            "authenticated": False,
            "method": "none",
            "status": "missing_credentials",
            "error": "No LinkedIn session cookie or username/password found in environment variables"
        }

def get_linkedin_credentials() -> Dict[str, str]:
    """Get LinkedIn credentials from environment variables"""
    return {
        "session_cookie": os.getenv('LINKEDIN_SESSION_COOKIE', ''),
        "username": os.getenv('LINKEDIN_USERNAME', ''),
        "password": os.getenv('LINKEDIN_PASSWORD', '')
    }
