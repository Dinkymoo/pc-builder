#!/usr/bin/env python3
"""
AWS Credentials Test Script

This script tests AWS credential configuration and access to required services.
It verifies:
- Valid AWS credentials are configured
- Access to S3 buckets
- Proper environment variable configuration

Usage:
    python test-aws-credentials.py
"""
import boto3
import os
import sys
from datetime import datetime

# Add the project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_aws_credentials():
    """Test if current AWS credentials are valid."""
    print("=== Testing Current Credentials ===")
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ Current credentials work!")
        print(f"Account: {identity.get('Account')}")
        print(f"User: {identity.get('Arn')}")
        return True
    except Exception as e:
        print(f"❌ Current credentials failed: {e}")
        return False

def test_s3_access():
    """Test access to S3 buckets and verify project bucket exists."""
    print("\n=== Testing S3 Access ===")
    try:
        s3 = boto3.client('s3')
        
        # Try to list buckets
        response = s3.list_buckets()
        print(f"✅ S3 access works! Found {len(response['Buckets'])} buckets:")
        for bucket in response['Buckets']:
            print(f"  - {bucket['Name']}")
        
        # Try to access our specific bucket
        bucket_name = os.environ.get('S3_BUCKET', 'pc-builder-bucket-dvg-2025')
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✅ Can access bucket: {bucket_name}")
            
            # Test listing objects in bucket
            objects = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
            if 'Contents' in objects:
                print(f"  Found {len(objects['Contents'])} objects (showing max 5):")
                for obj in objects['Contents']:
                    print(f"  - {obj['Key']} ({obj['Size']} bytes)")
            else:
                print(f"  Bucket is empty")
            
        except Exception as e:
            print(f"⚠️  Cannot access bucket {bucket_name}: {e}")
            print(f"   You may need to create it or check permissions")
        
        return True
    except Exception as e:
        print(f"❌ S3 access failed: {e}")
        return False

def check_environment_variables():
    """Check if all required AWS environment variables are set."""
    print("\n=== Checking Environment Variables ===")
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION']
    recommended_vars = ['S3_BUCKET']
    
    all_required_set = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
            print(f"✅ {var} is set: {masked}")
        else:
            print(f"❌ {var} is NOT set")
            all_required_set = False
    
    for var in recommended_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} is set: {value}")
        else:
            print(f"⚠️  {var} is NOT set (recommended)")
    
    return all_required_set

def main():
    """Main function to run all AWS credential tests."""
    print("🔍 AWS Credentials Test")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check environment variables
    env_vars_ok = check_environment_variables()
    
    # Test credentials
    if not env_vars_ok:
        print("\n⚠️  Environment variables incomplete. Tests may fail.")
    
    creds_ok = test_aws_credentials()
    s3_ok = False
    
    if creds_ok:
        s3_ok = test_s3_access()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Environment Variables: {'✅ OK' if env_vars_ok else '⚠️  Missing'}")
    print(f"AWS Credentials: {'✅ OK' if creds_ok else '❌ Failed'}")
    print(f"S3 Access: {'✅ OK' if s3_ok else '❌ Failed'}")
    
    if not (env_vars_ok and creds_ok and s3_ok):
        print("\n🔧 To fix:")
        print("1. Check your .env file has the correct AWS credentials")
        print("2. Ensure AWS CLI is configured properly")
        print("3. Verify your IAM user has the required permissions")
        print("4. Run this test again")
        return 1
    else:
        print("\n✅ All AWS credential tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
