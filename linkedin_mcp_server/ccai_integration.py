# src/linkedin_mcp_server/ccai_integration.py
"""
CCAI (Contact Center AI) integration for sending emails and SMS.
"""

import logging
from typing import Any, Dict, Optional
import aiohttp
import json

logger = logging.getLogger(__name__)


class CCAPIClient:
    """Client for CCAI API integration."""
    
    def __init__(self, api_key: str, client_id: str = "1231", base_url: str = "https://email-campaigns-test-cloudcontactai.allcode.com"):
        self.api_key = api_key
        self.client_id = client_id
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "clientId": client_id,
            "accountId": "1223"
        }
    
    async def send_email(
        self,
        first_name: str,
        last_name: str,
        to_email: str,
        subject: str,
        message: str,
        sender_email: str,
        reply_email: str,
        sender_name: str,
        title: str
    ) -> Dict[str, Any]:
        """Send email via CCAI campaigns API."""
        try:
            from datetime import datetime, timedelta
            import pytz
            
            # Schedule for 4:30 PM PST tomorrow
            pst = pytz.timezone('America/Los_Angeles')
            tomorrow = datetime.now(pst) + timedelta(days=1)
            scheduled_time = tomorrow.replace(hour=16, minute=30, second=0, microsecond=0)
            
            campaign = {
                "subject": subject,
                "title": title,
                "message": message,
                "senderEmail": sender_email,
                "replyEmail": reply_email,
                "senderName": sender_name,
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
                    f"{self.base_url}/api/v1/campaigns",
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
            logger.error(f"Email send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_sms(
        self,
        first_name: str,
        last_name: str,
        to_phone: str,
        message: str,
        sender_name: str,
        title: str
    ) -> Dict[str, Any]:
        """Send SMS via CCAI campaigns API."""
        try:
            campaign = {
                "title": title,
                "message": message,
                "senderName": sender_name,
                "accounts": [{
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": "",
                    "phone": to_phone
                }],
                "campaignType": "SMS",
                "addToList": "noList",
                "contactInput": "accounts",
                "fromType": "single",
                "senders": []
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/campaigns",
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
            logger.error(f"SMS send failed: {e}")
            return {"success": False, "error": str(e)}