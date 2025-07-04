"""
Utility functions for web scraping

SECURITY: The 'random' module is imported for use in non-security-sensitive delays only.
Do NOT use 'random' for cryptographic or security purposes anywhere in this module.
"""
import time
import random
import re
import logging
from urllib.parse import urlparse, urljoin

# Configure logging
logger = logging.getLogger(__name__)

def random_delay(min_seconds=1, max_seconds=3):
    """
    Sleep for a random amount of time between requests
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    # BANDIT B311: Use of 'random' is safe here because delays are not security-sensitive.
    # Do NOT use 'random' for cryptographic or security purposes.
    delay = min_seconds + random.random() * (max_seconds - min_seconds)
    logger.debug(f"Waiting for {delay:.2f} seconds")
    time.sleep(delay)

def is_absolute_url(url):
    """
    Check if a URL is absolute
    
    Args:
        url: URL to check
        
    Returns:
        Boolean indicating if the URL is absolute
    """
    return bool(urlparse(url).netloc)

def make_absolute_url(base_url, relative_url):
    """
    Convert a relative URL to an absolute URL
    
    Args:
        base_url: Base URL of the website
        relative_url: Relative URL to convert
        
    Returns:
        Absolute URL
    """
    if is_absolute_url(relative_url):
        return relative_url
    return urljoin(base_url, relative_url)

def clean_text(text):
    """
    Clean up text by removing extra whitespace, newlines, etc.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace newlines and tabs with spaces
    text = re.sub(r'[\n\t\r]+', ' ', text)
    
    # Remove extra spaces
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def extract_number(text):
    """
    Extract a number from text
    
    Args:
        text: Text containing a number
        
    Returns:
        Extracted number as float or None if no number found
    """
    if not text:
        return None
    
    # Try to find a number in the text
    matches = re.search(r'[-+]?\d*\.\d+|\d+', text)
    if matches:
        return float(matches.group(0))
    
    return None

def extract_price(text):
    """
    Extract a price from text
    
    Args:
        text: Text containing a price
        
    Returns:
        Extracted price as float or None if no price found
    """
    if not text:
        return None
    
    # Remove currency symbols and commas
    cleaned_text = re.sub(r'[$£€¥,]', '', text)
    
    # Try to find a decimal number
    matches = re.search(r'[-+]?\d*\.\d+|\d+', cleaned_text)
    if matches:
        return float(matches.group(0))
    
    return None

def get_domain(url):
    """
    Extract domain from URL
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # Remove www. if present
    domain = re.sub(r'^www\.', '', domain)
    
    return domain

def is_valid_image_url(url):
    """
    Check if URL points to an image
    
    Args:
        url: URL to check
        
    Returns:
        Boolean indicating if the URL is likely an image
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()
    
    for ext in image_extensions:
        if path.endswith(ext):
            return True
    
    return False

def sanitize_filename(filename):
    """
    Sanitize a string to be used as a filename
    
    Args:
        filename: String to sanitize
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscore
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized

def parse_date(date_string, formats=None):
    """
    Try to parse a date string using multiple formats
    
    Args:
        date_string: String containing a date
        formats: List of date formats to try
        
    Returns:
        datetime object or None if parsing failed
    """
    import datetime
    
    if not date_string:
        return None
    
    if formats is None:
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%B %d, %Y',
            '%d %B %Y',
            '%Y/%m/%d',
        ]
    
    for date_format in formats:
        try:
            return datetime.datetime.strptime(date_string.strip(), date_format)
        except ValueError:
            continue
    
    return None
