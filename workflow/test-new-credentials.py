#!/usr/bin/env python3
"""
Test new AWS credentials before updating .env file
Usage: python test-new-credentials.py ACCESS_KEY SECRET_KEY
"""
import sys
import boto3

def test_credentials(access_key, secret_key):
    print("🔍 Testing New AWS Credentials")
    print("=" * 50)
    print(f"Access Key: {access_key[:10]}...")
    print(f"Secret Key: {secret_key[:10]}...")
    
    try:
        # Create boto3 client with explicit credentials
        sts = boto3.client(
            'sts',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='eu-west-3'
        )
        
        # Test identity
        identity = sts.get_caller_identity()
        print(f"✅ Credentials work!")
        print(f"Account: {identity.get('Account')}")
        print(f"User ARN: {identity.get('Arn')}")
        
        # Test S3
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='eu-west-3'
        )
        
        buckets = s3.list_buckets()
        print(f"✅ S3 access works! Found {len(buckets['Buckets'])} buckets")
        
        return True
        
    except Exception as e:
        print(f"❌ Credentials failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test-new-credentials.py ACCESS_KEY SECRET_KEY")
        print("Example: python test-new-credentials.py AKIA... abcd...")
        sys.exit(1)
    
    access_key = sys.argv[1]
    secret_key = sys.argv[2]
    
    if test_credentials(access_key, secret_key):
        print(f"\n✅ SUCCESS! These credentials work.")
        print(f"\nTo update your .env file:")
        print(f"AWS_ACCESS_KEY_ID={access_key}")
        print(f"AWS_SECRET_ACCESS_KEY={secret_key}")
    else:
        print(f"\n❌ These credentials don't work. Try creating new ones.")
