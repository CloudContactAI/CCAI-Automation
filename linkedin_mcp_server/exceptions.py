"""
Custom exceptions for LinkedIn MCP Server
"""

class LinkedInMCPError(Exception):
    """Base exception for LinkedIn MCP Server"""
    pass

class CredentialsNotFoundError(LinkedInMCPError):
    """Raised when LinkedIn credentials are not found"""
    pass
