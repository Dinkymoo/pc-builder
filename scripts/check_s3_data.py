#!/usr/bin/env python3
"""
PC Builder S3 Connectivity Test Script
This script verifies S3 connectivity, CSV file existence, and content validation.
"""

import boto3
import csv
import io
import os
import sys
import json
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('s3-test')

# S3 configuration - can be overridden by environment variables
AWS_REGION = os.environ.get('MY_AWS_REGION', 'eu-west-3')
S3_BUCKET = os.environ.get('S3_BUCKET', 'pc-builder-bucket-dvg-2025')
S3_CSV_KEY = os.environ.get('S3_CSV_KEY', 'graphics-cards.csv')

def test_s3_connection():
    """Test basic S3 connectivity"""
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        
        logger.info(f"✅ S3 connection successful. Found {len(buckets)} buckets.")
        
        if S3_BUCKET in buckets:
            logger.info(f"✅ Target bucket '{S3_BUCKET}' found in account.")
        else:
            logger.warning(f"⚠️ Target bucket '{S3_BUCKET}' NOT FOUND in your account. Available buckets:")
            for b in buckets:
                logger.info(f"  - {b}")
        
        return True, buckets
    except Exception as e:
        logger.error(f"❌ S3 connection failed: {type(e).__name__}: {str(e)}")
        return False, []

def check_csv_in_bucket():
    """Check if the CSV file exists in the bucket"""
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        
        # List objects in bucket with prefix
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_CSV_KEY)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'] == S3_CSV_KEY:
                    size_kb = obj['Size'] / 1024
                    logger.info(f"✅ CSV file found: {S3_CSV_KEY} (Size: {size_kb:.2f} KB)")
                    return True, size_kb
        
        logger.error(f"❌ CSV file '{S3_CSV_KEY}' not found in bucket '{S3_BUCKET}'")
        return False, 0
    except Exception as e:
        logger.error(f"❌ Error checking CSV file: {type(e).__name__}: {str(e)}")
        return False, 0

def validate_csv_content():
    """Download and validate the CSV content"""
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        
        # Download CSV file from S3
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_CSV_KEY)
        csv_bytes = obj['Body'].read()
        csv_str = csv_bytes.decode('utf-8')
        
        # Parse CSV and check structure
        reader = csv.DictReader(csv_str.splitlines())
        rows = list(reader)
        
        if not rows:
            logger.error("❌ CSV file is empty or has no data rows")
            return False, 0, []
        
        # Check for required columns
        first_row = rows[0]
        required_columns = ['Product Name', 'Brand', 'Price', 'Specs']
        missing_columns = [col for col in required_columns if col not in first_row]
        
        if missing_columns:
            logger.error(f"❌ CSV missing required columns: {', '.join(missing_columns)}")
            logger.info(f"Available columns: {', '.join(first_row.keys())}")
            return False, len(rows), list(first_row.keys())
        
        # Log sample data
        logger.info(f"✅ CSV validation successful: {len(rows)} products found")
        logger.info(f"Sample data (first product):")
        for key, value in first_row.items():
            logger.info(f"  - {key}: {value[:50]}..." if len(str(value)) > 50 else f"  - {key}: {value}")
        
        return True, len(rows), list(first_row.keys())
    except Exception as e:
        logger.error(f"❌ Error validating CSV content: {type(e).__name__}: {str(e)}")
        return False, 0, []

def check_lambda_iam_permissions():
    """Check if Lambda execution role has S3 permissions"""
    try:
        # Get Lambda function
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        functions = lambda_client.list_functions()['Functions']
        
        pc_builder_functions = [f for f in functions if 'pc-builder' in f['FunctionName'].lower()]
        
        if not pc_builder_functions:
            logger.error("❌ No PC Builder Lambda functions found.")
            return False
        
        for func in pc_builder_functions:
            func_name = func['FunctionName']
            role_arn = func['Role']
            role_name = role_arn.split('/')[-1]
            
            logger.info(f"Checking IAM permissions for function: {func_name}")
            logger.info(f"Role ARN: {role_arn}")
            
            # Get role policies
            iam = boto3.client('iam')
            try:
                attached_policies = iam.list_attached_role_policies(RoleName=role_name)
                for policy in attached_policies['AttachedPolicies']:
                    policy_name = policy['PolicyName']
                    logger.info(f"  - Policy: {policy_name}")
                
                inline_policies = iam.list_role_policies(RoleName=role_name)
                for policy_name in inline_policies['PolicyNames']:
                    logger.info(f"  - Inline Policy: {policy_name}")
                    
                    # Get inline policy details
                    policy_detail = iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                    has_s3_read = False
                    
                    if 'PolicyDocument' in policy_detail:
                        doc = policy_detail['PolicyDocument']
                        for statement in doc.get('Statement', []):
                            action = statement.get('Action', [])
                            if 's3:GetObject' in action or 's3:Get*' in action or 's3:*' in action:
                                has_s3_read = True
                                logger.info(f"    ✅ S3 read permission found")
                
                if has_s3_read:
                    logger.info(f"✅ Lambda function {func_name} has S3 read permissions")
                else:
                    logger.warning(f"⚠️ Lambda function {func_name} MAY NOT have S3 read permissions")
            except Exception as role_err:
                logger.error(f"❌ Error checking role policies: {str(role_err)}")
                
        return True
    except Exception as e:
        logger.error(f"❌ Error checking Lambda permissions: {str(e)}")
        return False

def check_image_files():
    """Check if image files exist in S3"""
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        
        # List objects in images directory
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix='images/')
        
        if 'Contents' not in response:
            logger.warning("⚠️ No images found in S3 bucket under 'images/' prefix")
            return False, 0
        
        image_count = len(response['Contents'])
        logger.info(f"✅ Found {image_count} images in S3 bucket")
        
        # Sample a few images
        sample_size = min(5, image_count)
        sample_images = [obj['Key'] for obj in response['Contents'][:sample_size]]
        
        logger.info(f"Sample images:")
        for img in sample_images:
            logger.info(f"  - {img}")
        
        return True, image_count
    except Exception as e:
        logger.error(f"❌ Error checking image files: {type(e).__name__}: {str(e)}")
        return False, 0

def fix_common_issues():
    """Attempt to fix common issues with S3 access"""
    try:
        # Upload a local CSV file if it exists
        local_csv_paths = [
            'graphics-cards.csv', 
            '../data-results/graphics-cards.csv',
            '../../data-results/graphics-cards.csv'
        ]
        
        csv_found = False
        for csv_path in local_csv_paths:
            if os.path.exists(csv_path):
                logger.info(f"Found local CSV at {csv_path}")
                csv_found = True
                
                try:
                    # Upload to S3
                    s3 = boto3.client('s3', region_name=AWS_REGION)
                    s3.upload_file(
                        csv_path, 
                        S3_BUCKET, 
                        S3_CSV_KEY,
                        ExtraArgs={'ACL': 'public-read'}
                    )
                    logger.info(f"✅ Successfully uploaded {csv_path} to s3://{S3_BUCKET}/{S3_CSV_KEY}")
                except Exception as upload_err:
                    logger.error(f"❌ Failed to upload CSV: {str(upload_err)}")
                break
        
        if not csv_found:
            logger.error("❌ No local CSV file found to upload")
            
        # Check bucket policy
        try:
            s3 = boto3.client('s3', region_name=AWS_REGION)
            try:
                policy = s3.get_bucket_policy(Bucket=S3_BUCKET)
                logger.info("Bucket has a policy. Make sure it allows GetObject actions.")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                    logger.warning("⚠️ Bucket has no policy - consider adding one for better access control")
                else:
                    raise
                    
            # Make object public if requested
            if input("Make the CSV file public-readable for testing? (y/n): ").lower() == 'y':
                try:
                    s3.put_object_acl(
                        Bucket=S3_BUCKET,
                        Key=S3_CSV_KEY,
                        ACL='public-read'
                    )
                    logger.info(f"✅ Made {S3_CSV_KEY} public-readable")
                except Exception as acl_err:
                    logger.error(f"❌ Failed to modify object ACL: {str(acl_err)}")
            
        except Exception as policy_err:
            logger.error(f"❌ Error checking bucket policy: {str(policy_err)}")
            
        return True
    except Exception as e:
        logger.error(f"❌ Error fixing issues: {str(e)}")
        return False

def main():
    """Main function to run all checks"""
    logger.info("=" * 60)
    logger.info("PC BUILDER S3 CONNECTIVITY TEST")
    logger.info("=" * 60)
    logger.info(f"AWS Region: {AWS_REGION}")
    logger.info(f"S3 Bucket: {S3_BUCKET}")
    logger.info(f"CSV Key: {S3_CSV_KEY}")
    logger.info("-" * 60)
    
    # Run tests
    s3_conn_success, buckets = test_s3_connection()
    if not s3_conn_success:
        logger.error("❌ S3 connection test failed. Exiting.")
        return
    
    csv_exists, csv_size = check_csv_in_bucket()
    if not csv_exists:
        logger.warning("⚠️ CSV file not found in bucket. This could be the source of empty data.")
    
    if csv_exists:
        csv_valid, row_count, columns = validate_csv_content()
        if not csv_valid:
            logger.warning("⚠️ CSV validation failed. This could cause empty data in the API.")
    
    img_exists, img_count = check_image_files()
    lambda_perms = check_lambda_iam_permissions()
    
    # Summary
    logger.info("=" * 60)
    logger.info("RESULTS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"S3 Connection: {'✅ PASS' if s3_conn_success else '❌ FAIL'}")
    logger.info(f"CSV File Exists: {'✅ PASS' if csv_exists else '❌ FAIL'}")
    logger.info(f"CSV Content Valid: {'✅ PASS' if csv_exists and csv_valid else '❌ FAIL'}")
    logger.info(f"Image Files: {'✅ PASS' if img_exists else '⚠️ WARNING'}")
    logger.info(f"Lambda Permissions: {'✅ PASS' if lambda_perms else '⚠️ WARNING'}")
    logger.info("-" * 60)
    
    # Fix issues?
    if not csv_exists or (csv_exists and not csv_valid):
        if input("Would you like to attempt automatic fixes? (y/n): ").lower() == 'y':
            fix_common_issues()
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
