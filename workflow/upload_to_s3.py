#!/usr/bin/env python3
"""
Script to upload generated data files and images to S3 bucket.
This allows us to keep generated data out of Git and ensure all environments
use the same data from S3.

Usage:
  python upload_to_s3.py [--file <file_path>] [--images] [--data]
"""

import boto3
import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# SECURITY: Never hardcode AWS credentials in your code. Use environment variables,
# IAM roles (in production), or secure secret managers (like AWS Secrets Manager).
# Get AWS credentials from environment
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-3')
BUCKET_NAME = os.environ.get('S3_BUCKET', os.environ.get('BUCKET_NAME', 'pc-builder-data'))

# Create S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def is_allowed_file(file_path):
    """Check if the file is of an allowed type to prevent uploading sensitive or unwanted files."""
    # SECURITY: Only allow specific file types to be uploaded to S3
    allowed_extensions = {'.csv', '.log', '.jpg', '.jpeg', '.png', '.gif', '.webp'}
    _, ext = os.path.splitext(file_path.lower())
    return ext in allowed_extensions

def upload_csv(file_path=None):
    """Upload CSV data to S3."""
    files_to_upload = []
    
    if file_path:
        files_to_upload.append(file_path)
    else:
        # Default files to upload
        files_to_upload = [
            'data-results/graphics-cards.csv',
            'data-results/products.csv',
            'data-results/scraper.log'
        ]
        # Filter to only include files that exist
        files_to_upload = [f for f in files_to_upload if os.path.exists(f)]
    
    for file_path in files_to_upload:
        try:
            # SECURITY: Validate file types before upload to prevent uploading sensitive files
            if not is_allowed_file(file_path):
                logger.warning(f'⚠️ Skipping {file_path}: Not an allowed file type')
                continue
                
            file_name = os.path.basename(file_path)
            s3.upload_file(
                file_path, 
                BUCKET_NAME, 
                f'data/{file_name}',
                ExtraArgs={'ContentType': 'text/csv' if file_name.endswith('.csv') else 'text/plain'}
            )
            logger.info(f'✅ Uploaded {file_name} to S3')
        except Exception as e:
            # SECURITY: Avoid logging full exceptions which may contain sensitive information
            logger.error(f'❌ Failed to upload {file_path}: {type(e).__name__}')

def image_exists_in_s3(key):
    """Check if an image already exists in S3."""
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            # Log but don't crash on other errors
            logger.error(f"Error checking if {key} exists: {str(e)}")
            return False

def generate_presigned_url(s3_key, expiration=3600):
    """
    Generate a presigned URL for a given S3 object key.
    
    Args:
        s3_key (str): The S3 key of the object
        expiration (int): URL expiration time in seconds (default: 1 hour)
        
    Returns:
        str: Presigned URL or None if error
    """
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        # SECURITY: Avoid logging full exceptions which may contain sensitive information
        logger.error(f"❌ Failed to generate presigned URL for {s3_key}: {type(e).__name__}")
        return None

def upload_images(skip_existing=True, generate_urls=True):
    """
    Upload images from cdn-images to S3.
    
    Args:
        skip_existing (bool): Skip images that already exist in S3
        generate_urls (bool): Generate presigned URLs for uploaded images
        
    Returns:
        tuple: (uploaded_count, list of dicts with image info including presigned URLs)
    """
    image_dir = Path('cdn-images')
    if not image_dir.exists():
        logger.warning(f"Image directory not found: {image_dir}")
        return 0, []
    
    uploaded = 0
    skipped = 0
    failed = 0
    uploaded_images = []  # Track uploaded images and their URLs
    
    for img_path in image_dir.glob('*'):
        if img_path.is_file():
            s3_key = f'images/{img_path.name}'
            try:
                # SECURITY: Validate file types before upload to prevent uploading sensitive files
                if not is_allowed_file(str(img_path)):
                    logger.warning(f'⚠️ Skipping {img_path.name}: Not an allowed file type')
                    skipped += 1
                    continue
                    
                if skip_existing and image_exists_in_s3(s3_key):
                    logger.info(f'⏭️  Skipping {img_path.name} (already exists in S3)')
                    skipped += 1
                else:
                    # SECURITY: Using private ACL with presigned URLs for more secure access control
                    s3.upload_file(
                        str(img_path), 
                        BUCKET_NAME, 
                        s3_key,
                        ExtraArgs={
                            'ContentType': f'image/{img_path.suffix.lstrip(".")}' if img_path.suffix else 'image/jpeg',
                            # No 'ACL': 'public-read' - using private access with presigned URLs instead
                        }
                    )
                    logger.info(f'✅ Uploaded {img_path.name}')
                    uploaded += 1
                    
                    # Add to our tracking list
                    image_info = {
                        'name': img_path.name,
                        's3_key': s3_key,
                        'content_type': f'image/{img_path.suffix.lstrip(".")}' if img_path.suffix else 'image/jpeg',
                    }
                    
                    # Generate presigned URL if requested
                    if generate_urls:
                        url = generate_presigned_url(s3_key)
                        if url:  # Only add if not None
                            image_info['url'] = url
                    
                    uploaded_images.append(image_info)
            except Exception as e:
                # SECURITY: Avoid logging full exceptions which may contain sensitive information
                logger.error(f'❌ Failed to upload {img_path.name}: {type(e).__name__}')
                failed += 1
    
    logger.info(f"Images: {uploaded} uploaded, {skipped} skipped, {failed} failed")
    
    # Return both the count and the list of uploaded images with their URLs
    return uploaded, uploaded_images

def check_credentials():
    """Check if AWS credentials are properly configured."""
    # SECURITY: Avoid logging or displaying credentials or sensitive configuration values
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        logger.error("❌ AWS credentials not found in environment variables or .env file")
        logger.error("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False
    
    if not BUCKET_NAME:
        logger.error("❌ S3 bucket name not specified")
        logger.error("Please set S3_BUCKET or BUCKET_NAME environment variable")
        return False
        
    try:
        # Test connection
        s3.list_buckets()
        logger.info(f"✅ Successfully connected to AWS using provided credentials")
        return True
    except NoCredentialsError:
        logger.error("❌ AWS credentials are invalid")
        return False
    except Exception as e:
        # SECURITY: Avoid logging full exceptions which may contain sensitive information
        logger.error(f"❌ Error connecting to AWS: {type(e).__name__}")
        return False

def main():
    """Main function to parse arguments and upload files."""
    parser = argparse.ArgumentParser(description="Upload data and images to S3")
    parser.add_argument('--file', help='Specific CSV file to upload')
    parser.add_argument('--images', action='store_true', help='Upload images from cdn-images directory')
    parser.add_argument('--data', action='store_true', help='Upload CSV data files')
    parser.add_argument('--force', action='store_true', help='Upload images even if they already exist in S3')
    args = parser.parse_args()
    
    # Check credentials before proceeding
    if not check_credentials():
        return 1
    
    # Default behavior: upload both data and images if no specific flags provided
    if not (args.file or args.images or args.data):
        args.images = True
        args.data = True
    
    try:
        # Upload specific file if provided
        if args.file:
            logger.info(f"Uploading specific file: {args.file}")
            upload_csv(args.file)
        # Upload data files if requested
        elif args.data:
            logger.info("Uploading CSV data files")
            upload_csv()
        
        # Upload images if requested
        if args.images:
            logger.info("Uploading images from cdn-images directory")
            uploaded_count, image_details = upload_images(skip_existing=not args.force)
            
            # Print presigned URLs for uploaded images (useful for testing)
            if uploaded_count > 0:
                logger.info(f"Generated presigned URLs for {len([img for img in image_details if 'url' in img])} images")
                if len(image_details) <= 5:  # Only print URLs if there are 5 or fewer to avoid cluttering logs
                    for img in image_details:
                        if 'url' in img:
                            logger.info(f"Access {img['name']} at: {img['url']}")
        
        return 0
    except Exception as e:
        # SECURITY: Avoid logging full exceptions which may contain sensitive information
        logger.error(f"❌ Unexpected error: {type(e).__name__}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
