# CCAI Email Automation Setup Guide

## 1. Install Dependencies

### Basic dependencies:
```bash
pip3 install aiohttp python-dotenv pytz
```

### For LinkedIn scraping functionality:
```bash
pip3 install linkedin_scraper
```

### For AWS Bedrock AI email generation:
```bash
pip3 install boto3
```

### Using a virtual environment (recommended):
```bash
python3 -m venv path/to/venv
source path/to/venv/bin/activate
python3 -m pip install aiohttp python-dotenv pytz linkedin_scraper boto3
```

## 2. Install ChromeDriver (for LinkedIn scraping)

### macOS (using Homebrew):
```bash
brew install chromedriver
```

### Alternative installation methods:
- Download from [ChromeDriver official site](https://chromedriver.chromium.org/)
- Ensure ChromeDriver version matches your Chrome browser version
- Add ChromeDriver to your PATH

### Verify installation:
```bash
chromedriver --version
```

## 3. Configure Environment File

Create a `.env` file in the project root with your CCAI credentials:

```env
CCAI_API_KEY=your_api_key_here
CCAI_CLIENT_ID=your_client_id_here
CCAI_EMAIL_URL=your_email_endpoint_url_here

# Sender Information (used in email signatures)
SENDER_NAME=Your Name
SENDER_TITLE=Your Title
SENDER_EMAIL=your.email@company.com
SENDER_PHONE=+1234567890
SENDER_LINKEDIN=https://www.linkedin.com/in/yourprofile
SENDER_COMPANY=Your Company Name
SENDER_COMPANY_URL=https://yourcompany.com

# AWS Bedrock settings
AWS_REGION=us-east-1
```

## 4. Configure AWS Bedrock (for AI email generation)

### Option 1: AWS SSO/IAM Identity Center (Recommended for Organizations)
```bash
# Install AWS CLI if not already installed
brew install awscli

# Configure SSO
aws configure sso
```
You'll be prompted for:
- SSO session name (e.g., "my-company")
- SSO start URL (e.g., https://my-company.awsapps.com/start)
- SSO region (e.g., us-east-1)
- Account ID and Role name
- Default region (us-east-1) and output format (json)

```bash
# Login to SSO (opens browser)
aws sso login --profile your-profile-name

# Or if set as default profile:
aws sso login
```

### Option 2: AWS CLI Configuration (Individual Users)
```bash
# Install AWS CLI
brew install awscli

# Configure credentials
aws configure
```
Enter your AWS Access Key ID, Secret Access Key, region (us-east-1), and output format (json).

### Option 3: Environment Variables
Add to your `.env` file:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# Optional: Specify AWS profile for SSO
AWS_PROFILE=your-sso-profile-name
```

### AWS Credential Priority Order:
The scripts will attempt to use AWS credentials in this order:
1. **AWS Profile** (if `AWS_PROFILE` is set) - SSO profiles supported
2. **Environment Variables** (if profile fails or not set) - `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
3. **Default AWS Credentials** - IAM roles, default profile, or AWS CLI configuration

### Enable Bedrock Model Access:
1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to "Model access"
3. Enable **Amazon Nova Pro** model (`us.amazon.nova-pro-v1:0`)
4. Submit the request (approval may take a few minutes)

## 5. LinkedIn Authentication Setup

### Option 1: Session Cookies (Recommended)
1. Log into LinkedIn in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage → Cookies → linkedin.com
4. Copy the `li_at` cookie value
5. Add to your `.env` file:
```env
LINKEDIN_SESSION_COOKIE=your_li_at_cookie_value_here
```

### Option 2: Username/Password (Less secure)
Add to your `.env` file:
```env
LINKEDIN_USERNAME=your_linkedin_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password
```

**Note**: Session cookies are more secure and less likely to trigger LinkedIn's security measures.

## 6. Enable WebDriver (if disabled)

If you see "WebDriver disabled" messages, re-enable it by editing:
`linkedin_mcp_server/error_handler.py`

Replace the `safe_get_driver()` function with:
```python
def safe_get_driver():
    """
    Safely get or create a driver with proper error handling.
    """
    from linkedin_mcp_server.authentication import ensure_authentication
    from linkedin_mcp_server.drivers.chrome import get_or_create_driver

    # Get authentication first
    authentication = ensure_authentication()

    # Create driver with authentication
    driver = get_or_create_driver(authentication)

    return driver
```

## 7. Usage Examples

### Send a single email:
```bash
python3 send_single_email.py "recipient@email.com" "Subject" "Message" 30
```

### Run LinkedIn email automation:
```bash
python3 ai_gmail_outbound.py
```

### Run test email campaign with AI generation:
```bash
python3 send_test_emails.py
```

### Preview AI email templates:
```bash
python3 simple_test_emails.py
```

**Note**: All scripts now support AWS profiles for Bedrock AI generation. They will automatically use the `AWS_PROFILE` environment variable if set, or fall back to default AWS credentials.

## 8. Troubleshooting

### Common Issues:

**ChromeDriver not found:**
```bash
brew install chromedriver
# or download manually and add to PATH
```

**AWS Bedrock access denied:**
- Ensure you have proper AWS credentials configured
- For SSO: Run `aws sso login --profile your-profile-name` to refresh session
- Check that Amazon Nova Pro model is enabled in Bedrock console
- Verify your AWS region is set to `us-east-1`
- For SSO profiles, ensure the role has Bedrock permissions

**AWS SSO session expired:**
```bash
# Refresh your SSO session
aws sso login --profile your-profile-name

# Check current session status
aws sts get-caller-identity --profile your-profile-name
```

**LinkedIn login issues:**
- Use session cookies instead of username/password
- Check if your LinkedIn account has 2FA enabled
- Ensure cookies are fresh (re-login if needed)

**Module not found errors:**
- Ensure you're in the virtual environment: `source path/to/venv/bin/activate`
- Install missing dependencies: `pip install <package-name>`

**Rate limiting:**
- LinkedIn may rate limit requests
- Add delays between profile scraping
- Use session cookies for better authentication

## Dependencies Overview
- `aiohttp`: For async HTTP requests to CCAI API
- `python-dotenv`: For loading environment variables from .env file
- `pytz`: For timezone handling in email scheduling
- `linkedin_scraper`: For LinkedIn profile and post scraping
- `selenium`: WebDriver automation (installed with linkedin_scraper)
- `boto3`: AWS SDK for Bedrock AI email generation

## Security Notes
- Never commit your `.env` file to version control
- Use session cookies instead of passwords when possible
- Regularly refresh LinkedIn session cookies
- Store AWS credentials securely (use IAM roles when possible)
- Be mindful of LinkedIn's rate limits and terms of service