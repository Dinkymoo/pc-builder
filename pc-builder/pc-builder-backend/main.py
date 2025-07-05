from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import csv
import os
import json
import sys
import logging
import boto3
from botocore.exceptions import ClientError
from mangum import Mangum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PC Builder API",
    description="API for PC Builder application",
    version="1.0.0"
)

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
        logger.info(f"Loading graphics cards from S3: {S3_BUCKET}/{S3_CSV_KEY}")
        # Download CSV file from S3
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_CSV_KEY)
        csv_bytes = obj['Body'].read()
        csv_str = csv_bytes.decode('utf-8')
        reader = csv.DictReader(csv_str.splitlines())
        cards = []
        
        for idx, row in enumerate(reader, start=1):
            logger.debug(f"Processing row {idx}: {row}")
            price_str = row.get('Price', '0')
            # Clean price string
            price_str = price_str.replace('€', '').replace(',', '').replace('-', '').replace('\xa0', '').strip()
            try:
                price = float(price_str)
            except Exception as e:
                logger.warning(f"Failed to parse price '{price_str}': {e}")
                price = 0.0
            
            # Create graphic card object
            cards.append(GraphicCard(
                id=idx,
                name=row.get('Product Name', 'Unknown Product'),
                category='gpu',
                manufacturer=row.get('Brand', 'Unknown Brand'),
                price=price,
                inStock=True,
                description=row.get('Specs', ''),
                imageUrl=row.get('Image Path', ''),
                compatibility=[]
            ))
        
        logger.info(f"Successfully loaded {len(cards)} graphic cards from S3")
        return cards
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"S3 Client Error: {error_code} - {error_message}")
        if error_code == 'NoSuchKey':
            logger.error(f"CSV file not found: {S3_CSV_KEY}")
        elif error_code == 'NoSuchBucket':
            logger.error(f"S3 bucket not found: {S3_BUCKET}")
        return []
    except Exception as e:
        logger.error(f"Error loading CSV from S3: {e}", exc_info=True)
        return []

# Load graphics cards from S3 at startup
graphic_cards_db = load_graphic_cards_from_s3()

router = APIRouter(prefix="/api")

@app.get("/graphic-cards", response_model=List[GraphicCard])
def get_graphic_cards():
    logger.info(f"Graphic cards requested. Data count: {len(graphic_cards_db)}")
    
    # If no data is loaded, try to reload from S3
    if len(graphic_cards_db) == 0:
        logger.warning("No data found, attempting to reload from S3...")
        global graphic_cards_db
        graphic_cards_db = load_graphic_cards_from_s3()
        logger.info(f"Reload attempt completed. New data count: {len(graphic_cards_db)}")
    
    return graphic_cards_db

@app.get("/graphic-cards/{card_id}", response_model=GraphicCard)
def get_graphic_card(card_id: int):
    logger.info(f"Looking for graphic card with id: {card_id}")
    for card in graphic_cards_db:
        if card.id == card_id:
            return card
    logger.warning(f"Graphic card with id {card_id} not found")
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

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok", 
        "version": "1.0.0",
        "data_count": len(graphic_cards_db),
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

@app.get("/debug/check-s3")
def check_s3_connection():
    """Debug endpoint to check S3 connectivity"""
    try:
        # List buckets to check connection
        buckets = s3.list_buckets()
        bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]
        
        # Check if our bucket exists
        bucket_exists = S3_BUCKET in bucket_names
        
        # Check if CSV file exists
        csv_exists = False
        if bucket_exists:
            try:
                s3.head_object(Bucket=S3_BUCKET, Key=S3_CSV_KEY)
                csv_exists = True
            except ClientError:
                pass
        
        return {
            "status": "ok",
            "s3_connected": True,
            "bucket_exists": bucket_exists,
            "csv_exists": csv_exists,
            "bucket_name": S3_BUCKET,
            "csv_key": S3_CSV_KEY,
            "aws_region": AWS_REGION
        }
    except Exception as e:
        logger.error(f"S3 connection error: {e}", exc_info=True)
        error_type = type(e).__name__
        error_message = str(e)
        
        return {
            "status": "error",
            "error_type": error_type,
            "message": error_message,
            "bucket_name": S3_BUCKET,
            "csv_key": S3_CSV_KEY,
            "aws_region": AWS_REGION
        }

@app.get("/debug/diagnostics")
def diagnostics():
    """System diagnostics endpoint"""
    try:
        return {
            "python_version": sys.version,
            "environment_variables": {k: v for k, v in os.environ.items() if not k.startswith("AWS_") and k not in ["SECRET", "TOKEN"]},
            "loaded_modules": list(sys.modules.keys()),
            "working_directory": os.getcwd(),
            "data_count": len(graphic_cards_db),
            "pydantic_version": getattr(sys.modules.get('pydantic', None), '__version__', 'Not available'),
            "fastapi_version": getattr(sys.modules.get('fastapi', None), '__version__', 'Not available'),
            "mangum_version": getattr(sys.modules.get('mangum', None), '__version__', 'Not available')
        }
    except Exception as e:
        logger.error(f"Error in diagnostics: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

app.include_router(router)

# Lambda handler
handler = Mangum(app, api_gateway_base_path="/Prod")