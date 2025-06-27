"""
Download all product images from products.csv and save them to src/assets/images/.
Renames images to a slugified format: <brand>_<product_name>.<ext>
"""
import os
import csv
import requests
import re
from urllib.parse import urlparse, unquote

CSV_PATH = '/Users/daniellevangraan/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/data-results/graphics-cards.csv'  # Adjust if needed
DEST_DIR = '/Users/daniellevangraan/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/pc-builder-app/pc-builder-app/src/assets/images'

os.makedirs(DEST_DIR, exist_ok=True)

def slugify(value):
    value = str(value)
    value = value.lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    value = value.strip('-')
    return value

def get_extension_from_url(url):
    path = urlparse(url).path
    ext = os.path.splitext(path)[1]
    if ext:
        return ext
    return '.jpg'  # fallback

def download_image(url, dest_folder, brand, name):
    if not url or url == 'N/A':
        return None
    ext = get_extension_from_url(url)
    slug = f"{slugify(brand)}_{slugify(name)}{ext}"
    dest_path = os.path.join(dest_folder, slug)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(resp.content)
        print(f"Downloaded: {slug}")
        return slug
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def main():
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            img_url = row.get('Image URL', '')
            brand = row.get('Brand', 'unknown')
            name = row.get('Name', 'product')
            download_image(img_url, DEST_DIR, brand, name)

if __name__ == "__main__":
    main()
