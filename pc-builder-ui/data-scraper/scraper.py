"""
Basic web scraper using Beautiful Soup
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
from typing import Dict, List, Union

# Set up logging
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
        """
        Initialize the scraper with a base URL and optional headers
        
        Args:
            base_url: The base URL of the website to scrape
            headers: Optional dictionary of HTTP headers to send with each request
        """
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logger.info(f"Initialized scraper for {base_url}")
        
    def get_page(self, url: str) -> BeautifulSoup:
        """
        Fetch a web page and return a Beautiful Soup object
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object
        """
        try:
            logger.info(f"Fetching {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the HTML content of the page with Beautiful Soup
            soup = BeautifulSoup(response.text, 'lxml')
            return soup
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_data(self, soup: BeautifulSoup, selectors: Dict) -> Dict:
        """
        Extract data from a Beautiful Soup object using the provided CSS selectors
        
        Args:
            soup: BeautifulSoup object
            selectors: Dictionary mapping data fields to CSS selectors
            
        Returns:
            Dictionary of extracted data
        """
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
        """
        Scrape multiple pages with pagination
        
        Args:
            url_pattern: URL pattern with {} placeholder for page number
            pages: Number of pages to scrape
            selectors: Dictionary mapping data fields to CSS selectors
            delay: Time to wait between requests (seconds)
            
        Returns:
            List of dictionaries with extracted data
        """
        all_results = []
        
        for page in range(1, pages + 1):
            url = url_pattern.format(page)
            logger.info(f"Scraping page {page} of {pages}")
            
            soup = self.get_page(url)
            if soup:
                data = self.extract_data(soup, selectors)
                all_results.append(data)
            
            # Add random delay to be respectful to the website
            wait_time = delay + random.random()
            logger.debug(f"Waiting {wait_time:.2f} seconds before next request")
            time.sleep(wait_time)
        
        return all_results
    
    def save_to_csv(self, data: Union[List[Dict], Dict], filename: str) -> None:
        """
        Save scraped data to a CSV file
        
        Args:
            data: Data to save (list of dictionaries or a single dictionary)
            filename: Name of the output file
        """
        try:
            if isinstance(data, list):
                # Combine multiple dictionaries into one
                combined_data = {}
                for d in data:
                    for key, value in d.items():
                        if key in combined_data:
                            combined_data[key].extend(value)
                        else:
                            combined_data[key] = value
                # Pad lists to the same length
                max_len = max(len(v) for v in combined_data.values()) if combined_data else 0
                for key in combined_data:
                    if len(combined_data[key]) < max_len:
                        combined_data[key].extend([''] * (max_len - len(combined_data[key])))
                df = pd.DataFrame(combined_data)
            else:
                # Pad lists to the same length for single dictionary
                max_len = max(len(v) for v in data.values()) if data else 0
                for key in data:
                    if len(data[key]) < max_len:
                        data[key].extend([''] * (max_len - len(data[key])))
                df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {e}")


def main():
    """Example usage of the WebScraper class"""
    
    # Example: Scraping quotes from quotes.toscrape.com
    scraper = WebScraper("https://quotes.toscrape.com")
    
    # Define selectors for the data we want to extract
    selectors = {
        'quotes': '.quote .text',
        'authors': '.quote .author',
        'tags': '.quote .tags .tag',
    }
    
    # Fetch the main page
    soup = scraper.get_page("https://quotes.toscrape.com")
    
    if soup:
        # Extract data
        data = scraper.extract_data(soup, selectors)
        
        # Save to CSV
        scraper.save_to_csv(data, "quotes.csv")
        
        print("Scraping completed successfully. Check quotes.csv for results.")
    else:
        print("Failed to fetch the page.")


if __name__ == "__main__":
    main()
