import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os

OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data-results/graphics-cards.csv'))
URL = "https://azerty.nl/componenten/videokaarten/amd"

async def scrape_azerty():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)
        await page.wait_for_selector('ul.mx-auto.grid')
        
        products = []
        # Select all product forms inside the product grid
        product_forms = await page.query_selector_all('ul.mx-auto.grid > li > form')
        for form in product_forms:
            # Product Name
            name = await form.eval_on_selector('div.product-info h4', 'el => el.textContent.trim()') if await form.query_selector('div.product-info h4') else 'N/A'
            # Product URL
            url = await form.eval_on_selector('div.product-info a.product-item-link', 'el => el.href') if await form.query_selector('div.product-info a.product-item-link') else 'N/A'
            # Brand
            brand = name.split()[0] if name and name != 'N/A' else 'N/A'
            # Price
            price = await form.eval_on_selector('div.price-box span.price-wrapper.price-including-tax span.price', 'el => el.textContent.trim()') if await form.query_selector('div.price-box span.price-wrapper.price-including-tax span.price') else 'N/A'
            # Image URL
            img_url = await form.eval_on_selector('a.product-item-photo img', 'el => el.src') if await form.query_selector('a.product-item-photo img') else 'N/A'
            # Specs
            specs = await form.eval_on_selector('div.product-info h5.product-item-description', 'el => el.textContent.trim()') if await form.query_selector('div.product-info h5.product-item-description') else 'N/A'
            products.append({
                'Product Name': name,
                'Price': price,
                'Brand': brand,
                'Image URL': img_url,
                'Product URL': url,
                'Specs': specs
            })
        await browser.close()
        return products

def main():
    products = asyncio.run(scrape_azerty())
    print(products)  # Debug: print the scraped data
    if products:
        columns = ['Product Name', 'Price', 'Brand', 'Image URL', 'Product URL', 'Specs']
        df = pd.DataFrame(products, columns=columns)
        print(df.head())  # Debug: print DataFrame head
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
        print(f"Scraped {len(df)} products. Data saved to {OUTPUT_PATH}")
    else:
        print("No products scraped. Check selectors or page structure.")

if __name__ == "__main__":
    main()
