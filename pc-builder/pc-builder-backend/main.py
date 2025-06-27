from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from typing import List, Optional
from pydantic import BaseModel
import csv
import os
import boto3
from botocore.exceptions import ClientError

app = FastAPI()

# Allow CORS for local Angular dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GraphicCard(BaseModel):
    id: int
    name: str
    category: str
    manufacturer: str
    price: float
    inStock: bool
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    compatibility: Optional[List[str]] = None

# Use Docker-friendly absolute paths for images only
IMAGES_DIR = "cdn-images"

# S3 config
AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-3')
S3_BUCKET = os.environ.get('S3_BUCKET', 'pc-builder-bucket-dvg-2025')
S3_CSV_KEY = os.environ.get('S3_CSV_KEY', 'graphics-cards.csv')

s3 = boto3.client('s3', region_name=AWS_REGION)

def load_graphic_cards_from_s3():
    try:
        # Download CSV file from S3
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_CSV_KEY)
        csv_bytes = obj['Body'].read()
        csv_str = csv_bytes.decode('utf-8')
        reader = csv.DictReader(csv_str.splitlines())
        cards = []
        for idx, row in enumerate(reader, start=1):
            price_str = row['Price'].replace('€', '').replace(',', '').replace('-', '').replace('\xa0', '').strip()
            try:
                price = float(price_str)
            except Exception:
                price = 0.0
            cards.append(GraphicCard(
                id=idx,
                name=row['Product Name'],
                category='gpu',
                manufacturer=row['Brand'],
                price=price,
                inStock=True,
                description=row['Specs'],
                imageUrl=row.get('Image Path', ''),
                compatibility=[]
            ))
        return cards
    except Exception as e:
        print(f"Error loading CSV from S3: {e}")
        return []

# Load graphics cards from S3 at startup
graphic_cards_db = load_graphic_cards_from_s3()

router = APIRouter(prefix="/api")

@app.get("/graphic-cards", response_model=List[GraphicCard])
def get_graphic_cards():
    return graphic_cards_db

@app.get("/graphic-cards/{card_id}", response_model=GraphicCard)
def get_graphic_card(card_id: int):
    for card in graphic_cards_db:
        if card.id == card_id:
            return card
    return {"error": "Graphic card not found"}

@app.get("/images/{image_filename}")
def serve_image(image_filename: str):
    try:
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': f'images/{image_filename}'},
            ExpiresIn=3600
        )
        return RedirectResponse(presigned_url)
    except ClientError:
        return {"error": "Image not found"}

app.include_router(router)