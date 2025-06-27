# FastAPI Backend for PC Builder

## Overview
This backend serves PC part data and images to the Angular frontend. It loads the graphics card CSV directly from AWS S3 at startup and serves images via S3 presigned URLs.

## Setup

1. Create a virtual environment (optional but recommended):
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the backend root with your AWS credentials and S3 config:
   ```env
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=eu-west-3
   S3_BUCKET=pc-builder-bucket-dvg-2025
   S3_CSV_KEY=graphics-cards.csv
   ```
4. Run the server:
   ```sh
   uvicorn main:app --reload
   ```

## Endpoints
- `GET /graphic-cards` — List all graphics cards
- `GET /graphic-cards/{card_id}` — Get a single card by ID
- `GET /images/{image_filename}` — Redirect to S3 presigned URL for image

CORS is enabled for local development.

## Docker Usage
To build and run with Docker:
```sh
docker build -t pc-builder-backend .
docker run --rm -p 8000:8000 --env-file .env pc-builder-backend
```

## Notes
- The backend does NOT require a local CSV file; it always loads from S3.
- Make sure your S3 bucket contains the latest `graphics-cards.csv` and images in the correct paths.