from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
import csv
import os

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

# Use Docker-friendly absolute paths for CSV and images
CSV_PATH = "data-results/graphics-cards.csv"
IMAGES_DIR = "cdn-images"

# Load graphics cards from CSV
graphic_cards_db = []
with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader, start=1):
        # Convert price to float, remove currency symbols and commas
        price_str = row['Price'].replace('€', '').replace(',', '').replace('-', '').replace('\xa0', '').strip()
        try:
            price = float(price_str)
        except Exception:
            price = 0.0
        graphic_cards_db.append(GraphicCard(
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
    image_path = os.path.join(IMAGES_DIR, image_filename)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return {"error": "Image not found"}

app.include_router(router)