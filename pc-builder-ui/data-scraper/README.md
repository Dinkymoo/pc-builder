# web-scraper-beautiful-soup

## Architecture Overview

```
+-------------------+        +-------------------+        +-------------------+
|                   |        |                   |        |                   |
|  Scraper Script   +------->+   Data Results    +<-------+   FastAPI BFF      |
| (Playwright/Python|  CSV   |  (graphics-cards. |  Reads |  (Python backend)  |
|  in data-scraper) |        |      .csv)        |        |                   |
+-------------------+        +-------------------+        +-------------------+
                                                           |
                                                           | REST API
                                                           v
                                                +-----------------------+
                                                |   Angular Frontend    |
                                                |  (pc-builder-ui)      |
                                                +-----------------------+
```

- **Scraper**: Python script using Playwright scrapes product data from Azerty and writes to `data-results/graphics-cards.csv`.
- **Data Results**: CSV file acts as the single source of truth for graphics card data.
- **FastAPI BFF**: Reads the CSV and exposes `/graphic-cards` API endpoints for the frontend.
- **Angular Frontend**: Fetches data from the BFF and displays it to users.

### Data Flow
1. Scraper fetches and saves product data to CSV.
2. FastAPI backend loads CSV and serves it via REST API.
3. Angular frontend fetches and displays the data.

---

