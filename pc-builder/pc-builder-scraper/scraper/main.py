import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from product_scraper_graphics_cards import main as scrape_main

if __name__ == "__main__":
    scrape_main()
