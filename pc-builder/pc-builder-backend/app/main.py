from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from typing import List, Optional
from pydantic import BaseModel
import csv
import os
import logging
import boto3
from botocore.exceptions import ClientError
from mangum import Mangum
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.environ.get('ENVIRONMENT') == 'production' else logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# WARNING: CORS is set to allow all origins. This is insecure for production environments.
# Restrict 'allow_origins' to trusted domains in production.
if os.environ.get('ENVIRONMENT') == 'production':
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', '').split(',')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins if allowed_origins != [''] else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
handler = Mangum(app)
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

# S3 config
AWS_REGION = os.environ.get('MY_AWS_REGION', 'eu-west-3')
S3_BUCKET = os.environ.get('S3_BUCKET', 'pc-builder-bucket-dvg-2025')
S3_CSV_KEY = os.environ.get('S3_CSV_KEY', 'graphics-cards.csv')

s3 = boto3.client('s3', region_name=AWS_REGION)

def load_graphic_cards_from_s3():
    try:
        logger.info(f"Loading data from S3 bucket: {S3_BUCKET}")
        # Download CSV file from S3
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_CSV_KEY)
        csv_bytes = obj['Body'].read()
        csv_str = csv_bytes.decode('utf-8')
        reader = csv.DictReader(csv_str.splitlines())
        cards = []
        for idx, row in enumerate(reader, start=1):
            try:
                price_str = row['Price'].replace('€', '').replace(',', '').replace('-', '').replace('\xa0', '').strip()
                price = float(price_str) if price_str else 0.0
            except Exception:
                price = 0.0
                logger.debug(f"Price parsing error for product {idx}")
            
            # SECURITY: Validate and sanitize all fields from S3 if exposed to users
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
        logger.info(f"Successfully loaded {len(cards)} products from S3")
        return cards
    except Exception as e:
        # SECURITY: Avoid returning raw exception messages to users. Log only necessary info.
        logger.warning(f"Error loading data from S3: {type(e).__name__}")
        return load_graphic_cards_from_local()

def load_graphic_cards_from_local():
    try:
        # Fallback to local CSV file - try multiple paths
        possible_paths = [
            '/workspace/data-results/graphics-cards.csv',  # Docker path
            '../../../data-results/graphics-cards.csv',    # Local relative path
            '../../data-results/graphics-cards.csv',       # Alternative relative path
            os.path.join(os.path.dirname(__file__), '../../../data-results/graphics-cards.csv')  # Absolute relative path
        ]
        
        for local_csv_path in possible_paths:
            logger.debug(f"Trying local path: {os.path.basename(local_csv_path)}")
            if os.path.exists(local_csv_path):
                logger.info(f"Found local data file")
                with open(local_csv_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    cards = []
                    for idx, row in enumerate(reader, start=1):
                        try:
                            price_str = row['Price'].replace('€', '').replace(',', '').replace('-', '').replace('\xa0', '').strip()
                            price = float(price_str) if price_str else 0.0
                        except Exception:
                            price = 0.0
                            logger.debug(f"Price parsing error for product {idx}")
                        # SECURITY: Validate and sanitize all fields from CSV if exposed to users
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
                    logger.info(f"Successfully loaded {len(cards)} products from local file")
                    return cards
    except Exception as e:
        # SECURITY: Avoid exposing internal error details in production
        logger.error(f"Error loading local data: {type(e).__name__}")
    return []

# Load graphics cards from S3 at startup
logger.info("Starting application and loading product data")
graphic_cards_db = load_graphic_cards_from_s3()
logger.info(f"Application initialized with {len(graphic_cards_db)} products")

router = APIRouter(prefix="/api")

@router.get("/graphic-cards", response_model=List[GraphicCard])
def get_graphic_cards():
    logger.debug("API endpoint called: /api/graphic-cards")
    return graphic_cards_db

@app.get("/graphic-cards", response_model=List[GraphicCard])
def get_graphic_cards_root():
    logger.debug("API endpoint called: /graphic-cards")
    return graphic_cards_db

@app.get("/images/{image_filename}")
def serve_image(image_filename: str):
    # SECURITY: Validate all user input, not just filenames, to prevent injection and traversal attacks.
    import re
    from fastapi.responses import FileResponse
    # Only allow filenames with safe characters (alphanumeric, dash, underscore, dot)
    if not re.fullmatch(r"[\w\-. ]+", image_filename):
        logger.warning(f"Rejected suspicious image filename: {image_filename}")
        return {"error": "Invalid image filename"}
    # Use os.path.basename to strip directory components
    image_filename = os.path.basename(image_filename)
    # Try to check if S3 object exists first (quick test)
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=f'images/{image_filename}')
        # If head_object succeeds, generate presigned URL
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': f'images/{image_filename}'},
            ExpiresIn=3600
        )
        logger.debug(f"Serving image from S3: {image_filename}")
        return RedirectResponse(presigned_url)
    except Exception as e:
        # SECURITY: Log exception type only, avoid sensitive info
        logger.debug(f"Image not found in S3, trying local paths. Exception: {type(e).__name__}")
        # Fallback to local images
        import os
        from fastapi.responses import FileResponse
        
        # Try multiple local paths
        local_paths = [
            f"../../../cdn-images/{image_filename}",
            f"../../cdn-images/{image_filename}",
            f"cdn-images/{image_filename}",
            os.path.join(os.path.dirname(__file__), f"../../../cdn-images/{image_filename}")
        ]
        for local_path in local_paths:
            if os.path.exists(local_path):
                logger.debug(f"Serving local image")
                return FileResponse(local_path)
        logger.warning(f"Image not found: {image_filename}")
        return {"error": "Image not found"}

@app.get("/debug/reload")
def reload_data():
    global graphic_cards_db
    logger.info("Reloading product data")
    graphic_cards_db = load_graphic_cards_from_s3()
    count = len(graphic_cards_db)
    logger.info(f"Reload complete, loaded {count} products")
    return {"message": f"Reloaded {count} graphics cards", "count": count}

# SECURITY: Use environment variables for all secrets and credentials. In production, use a secure secret manager (e.g., AWS Secrets Manager).
app.include_router(router)

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for AWS ECS.
    Returns status and version information to verify the service is running properly.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "pc-builder-backend"
    }
