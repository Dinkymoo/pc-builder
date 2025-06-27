# PC Builder Scraper

## Architecture Overview

```
+-------------------+        +-------------------+        +-------------------+
|                   |        |                   |        |                   |
|  Scraper Script   +------->+   Data Results    +<-------+   FastAPI Backend  |
| (Playwright/Python|  CSV   |  (graphics-cards. |  Reads |  (Python backend)  |
|  in pc-builder-   |        |      .csv on S3)  |  from  |  loads CSV from S3 |
|  scraper)         |        +-------------------+        |  and serves images |
+-------------------+                                     |  via S3 presigned  |
                                                         |  URLs              |
                                                         +-------------------+
                                                                |
                                                                | REST API
                                                                v
                                                     +-----------------------+
                                                     |   Angular Frontend    |
                                                     |  (pc-builder-app)     |
                                                     +-----------------------+
```

- **Scraper**: Python script using Playwright scrapes product data from Azerty and writes to `data-results/graphics-cards.csv`.
- **S3 Upload**: After scraping, the CSV and all product images are uploaded to S3 using `upload_to_s3.py` or the AWS CLI.
- **FastAPI Backend**: Loads the CSV directly from S3 at startup and serves `/graphic-cards` API endpoints. Images are served via S3 presigned URLs.
- **Angular Frontend**: Fetches data from the backend and displays it to users.

### Data Flow
1. Scraper fetches and saves product data to CSV and downloads images.
2. CSV and images are uploaded to S3.
3. FastAPI backend loads CSV from S3 and serves data/images via REST API.
4. Angular frontend fetches and displays the data.

---

- See `upload_to_s3.py` for automated S3 upload.
- Ensure your S3 bucket is up to date before running the backend.

