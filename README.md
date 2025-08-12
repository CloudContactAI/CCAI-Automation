# Steps to get this to work

## 1. Install the Dependencies

### Basic dependencies:
```bash
pip3 install aiohttp python-dotenv pytz
```

### For LinkedIn scraping functionality (ai_gmail_outbound.py):
```bash
pip3 install linkedin_scraper
```

### Using a virtual environment (recommended):
```bash
python3 -m venv path/to/venv
source path/to/venv/bin/activate
python3 -m pip install aiohttp python-dotenv pytz linkedin_scraper
```

## 2. Configure Environment File
Configure a new .env file with CCAI information and email information

## 3. Usage Examples

### Send a single email:
```bash
python3 send_single_email.py "recipient@email.com" "Subject" "Message" 30
```

### Run LinkedIn email automation:
```bash
python3 ai_gmail_outbound.py
```

## Dependencies Overview
- `aiohttp`: For async HTTP requests
- `python-dotenv`: For loading environment variables
- `pytz`: For timezone handling
- `linkedin_scraper`: For LinkedIn profile scraping (required for ai_gmail_outbound.py)