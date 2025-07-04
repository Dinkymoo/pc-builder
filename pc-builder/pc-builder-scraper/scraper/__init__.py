import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
from typing import Dict, List, Union, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebScraper:
    """A class to handle web scraping tasks using Beautiful Soup"""
    def __init__(self, base_url: str, headers: Dict = None):
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logger.info(f"Initialized scraper for {base_url}")
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            logger.info(f"Fetching {url}")
            # BANDIT B113: Always specify a timeout to avoid hanging requests.
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            return soup
        except requests.exceptions.RequestException as e:
            # SECURITY: Avoid logging sensitive data in production logs.
            logger.error(f"Error fetching {url}: {e}")
            return None
    def extract_data(self, soup: BeautifulSoup, selectors: Dict) -> Dict:
        data = {}
        try:
            for field, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    data[field] = [elem.text.strip() for elem in elements]
                else:
                    data[field] = []
                    logger.warning(f"No elements found for selector: {selector}")
            return data
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            return {}
    def scrape_with_pagination(self, url_pattern: str, pages: int, selectors: Dict, delay: float = 1.0) -> List[Dict]:
        all_results = []
        for page in range(1, pages + 1):
            url = url_pattern.format(page)
            logger.info(f"Scraping page {page} of {pages}")
            soup = self.get_page(url)
            if soup:
                data = self.extract_data(soup, selectors)
                all_results.append(data)
            # BANDIT B311: Use of 'random' is safe here for delays, not for security/crypto.
            wait_time = delay + random.random()
            logger.debug(f"Waiting {wait_time:.2f} seconds before next request")
            time.sleep(wait_time)
        return all_results
    def save_to_csv(self, data: Union[List[Dict], Dict], filename: str) -> None:
        try:
            # SECURITY: Avoid logging sensitive data or file paths in production logs.
            if isinstance(data, list):
                combined_data = {}
                for d in data:
                    for key, value in d.items():
                        if key in combined_data:
                            combined_data[key].extend(value)
                        else:
                            combined_data[key] = value
                max_len = max(len(v) for v in combined_data.values()) if combined_data else 0
                for key in combined_data:
                    if len(combined_data[key]) < max_len:
                        combined_data[key].extend([''] * (max_len - len(combined_data[key])))
                df = pd.DataFrame(combined_data)
            else:
                max_len = max(len(v) for v in data.values()) if data else 0
                for key in data:
                    if len(data[key]) < max_len:
                        data[key].extend([''] * (max_len - len(data[key])))
                df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            # SECURITY: Avoid exposing sensitive info in logs
            logger.error(f"Error saving data to {filename}: {type(e).__name__}")
