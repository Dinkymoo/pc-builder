import os
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from typing import List, Optional
from pydantic import BaseModel
import csv
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
# Configure Mangum with API Gateway settings
# The api_gateway_base_path parameter is set to the stage name to handle paths correctly
handler = Mangum(app, lifespan="off", api_gateway_base_path="/Prod")
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

def generate_presigned_image_url(image_path: str) -> str:
    if not image_path:
        return ""  # Or a default image URL from S3
    try:
        return s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': f'images/{image_path}'},
            ExpiresIn=3600
        )
    except Exception as e:
        logger.warning(f"Failed to generate presigned URL for {image_path}: {type(e).__name__}")
        return ""

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
            image_path = row.get('Image Path', '')
            presigned_url = generate_presigned_image_url(image_path) if image_path else ""
            cards.append(GraphicCard(
                id=idx,
                name=row['Product Name'],
                category='gpu',
                manufacturer=row['Brand'],
                price=price,
                inStock=True,
                description=row['Specs'],
                imageUrl=presigned_url,
                compatibility=[]
            ))
        logger.info(f"Successfully loaded {len(cards)} products from S3")
        return cards
    except Exception as e:
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
                        image_path = row.get('Image Path', '')
                        presigned_url = generate_presigned_image_url(image_path) if image_path else ""
                        cards.append(GraphicCard(
                            id=idx,
                            name=row['Product Name'],
                            category='gpu',
                            manufacturer=row['Brand'],
                            price=price,
                            inStock=True,
                            description=row['Specs'],
                            imageUrl=presigned_url,
                            compatibility=[]
                        ))
                    logger.info(f"Successfully loaded {len(cards)} products from local file")
                    return cards
    except Exception as e:
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
    global graphic_cards_db  # Moved to the top to fix SyntaxError
    logger.info("API endpoint called: /graphic-cards with data length: {}".format(len(graphic_cards_db)))
    if len(graphic_cards_db) == 0:
        logger.warning("Data is empty, attempting to reload from S3...")
        graphic_cards_db = load_graphic_cards_from_s3()
        logger.info(f"Reload complete, loaded {len(graphic_cards_db)} products")
    # Log the data structure to help debug
    if len(graphic_cards_db) > 0:
        logger.info(f"Sample data (first item): {graphic_cards_db[0].dict()}")
    else:
        logger.error("NO DATA AVAILABLE - Check S3 bucket and CSV file!")
        # Return a single item with error details to help troubleshoot
        return [GraphicCard(
            id=0,
            name="ERROR: No data loaded",
            category="error",
            manufacturer="System",
            price=0.0,
            inStock=False,
            description="Check logs and S3 configuration. Use /debug/check-s3 endpoint.",
            imageUrl="",
            compatibility=[]
        )]
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
        "service": "pc-builder-backend",
        "data_count": len(graphic_cards_db),
        "s3_config": {
            "region": AWS_REGION,
            "bucket": S3_BUCKET,
            "key": S3_CSV_KEY
        }
    }

@app.get("/debug/diagnostics", tags=["Debug"])
async def system_diagnostics(request: Request):
    """
    Comprehensive system diagnostics for troubleshooting
    """
    # Check current working directory and files
    import os
    cwd = os.getcwd()
    
    # Collect local file paths for debugging
    local_files = {}
    possible_paths = [
        'data-results/graphics-cards.csv',
        '../data-results/graphics-cards.csv',
        '../../data-results/graphics-cards.csv',
        '../../../data-results/graphics-cards.csv',
    ]
    
    for path in possible_paths:
        local_files[path] = os.path.exists(path)
        if os.path.exists(path):
            try:
                size = os.path.getsize(path)
                local_files[f"{path}_size"] = f"{size} bytes"
                # Read first line to verify it's valid CSV
                with open(path, 'r', encoding='utf-8') as f:
                    header = f.readline().strip()
                    local_files[f"{path}_header"] = header
            except Exception as e:
                local_files[f"{path}_error"] = str(type(e).__name__)
    
    # Get environment variables (excluding secrets)
    safe_env_vars = {k: v for k, v in os.environ.items() 
                     if not any(secret in k.lower() for secret in 
                               ['key', 'secret', 'token', 'password', 'credential'])}
    
    # Get request path info
    path_info = {
        "raw_path": str(request.url.path),
        "base_url": str(request.base_url),
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers)
    }
    
    # Lambda context path info
    lambda_context = {
        "api_gateway_base_path": "/Prod",
        "current_path": request.url.path,
        "data_source": "S3" if len(graphic_cards_db) > 0 else "Empty/Failed"
    }
    
    return {
        "diagnostics": {
            "environment": safe_env_vars,
            "current_directory": cwd,
            "local_files": local_files,
            "request": path_info,
            "lambda_context": lambda_context,
            "data_loaded": len(graphic_cards_db),
            "data_sample": str(graphic_cards_db[0].dict()) if len(graphic_cards_db) > 0 else "No data"
        }
    }

@app.get("/debug/check-s3", tags=["Debug"])
async def check_s3_connectivity():
    """
    Debug endpoint to check S3 connectivity
    """
    try:
        # List objects in the S3 bucket
        response = s3.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=10)
        objects = []
        if 'Contents' in response:
            objects = [obj['Key'] for obj in response['Contents']]
        
        # Check if the CSV file exists
        csv_exists = False
        csv_content = None
        try:
            s3.head_object(Bucket=S3_BUCKET, Key=S3_CSV_KEY)
            csv_exists = True
            
            # Try to get the first few lines of the CSV
            try:
                obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_CSV_KEY)
                csv_bytes = obj['Body'].read(1024)  # Just read first 1KB
                csv_content = csv_bytes.decode('utf-8')[:500] + "..." # Truncate for display
            except Exception as csv_e:
                logger.error(f"Error reading CSV content: {type(csv_e).__name__}")
        except Exception as e:
            logger.error(f"CSV file not found: {S3_CSV_KEY}, error: {type(e).__name__}")
        
        return {
            "status": "success",
            "bucket": S3_BUCKET,
            "region": AWS_REGION,
            "csv_key": S3_CSV_KEY,
            "csv_exists": csv_exists,
            "csv_preview": csv_content,
            "data_loaded": len(graphic_cards_db),
            "objects": objects[:10],  # Return first 10 objects
            "environment": {
                "environment": os.environ.get('ENVIRONMENT'),
                "region_env": os.environ.get('MY_AWS_REGION')
            }
        }
    except Exception as e:
        logger.error(f"S3 check failed: {type(e).__name__}")
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "bucket": S3_BUCKET,
            "region": AWS_REGION,
            "csv_key": S3_CSV_KEY,
            "data_loaded": len(graphic_cards_db),
            "environment": {
                "environment": os.environ.get('ENVIRONMENT'),
                "region_env": os.environ.get('MY_AWS_REGION')
            }
        }
