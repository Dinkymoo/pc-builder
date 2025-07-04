#!/usr/bin/env python3
"""
Quick AWS credentials test script.
Replace the credentials below with your new ones from the AWS Console.
"""
import boto3
import os

def test_aws_credentials():
    # Test with current environment variables
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
        except Exception as e:
            print(f"⚠️  Cannot access bucket {bucket_name}: {e}")
            print(f"   You may need to create it or check permissions")
        
        return True
    except Exception as e:
        print(f"❌ S3 access failed: {e}")
        return False

def main():
    print("🔍 AWS Credentials Test")
    print("=" * 50)
    
    # Show current configuration
    print("Current AWS Configuration:")
    print(f"AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID', 'Not set')[:10]}...")
    print(f"AWS_SECRET_ACCESS_KEY: {os.environ.get('AWS_SECRET_ACCESS_KEY', 'Not set')[:10]}...")
    print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'Not set')}")
    print(f"S3_BUCKET: {os.environ.get('S3_BUCKET', 'Not set')}")
    
    # Test credentials
    if test_aws_credentials():
        test_s3_access()
    else:
        print("\n🔧 To fix:")
        print("1. Get new AWS credentials from the AWS Console (IAM > Users)")
        print("2. Update your .env file with the new keys")
        print("3. Run this test again")

if __name__ == "__main__":
    main()
