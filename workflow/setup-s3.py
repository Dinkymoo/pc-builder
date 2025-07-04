#!/usr/bin/env python3
"""
Complete S3 setup for PC Builder project
- Creates S3 bucket if it doesn't exist
- Uploads CSV file
- Uploads all images
- Tests image access
"""
import boto3
import os
from botocore.exceptions import ClientError

def setup_s3_bucket(access_key, secret_key, region='eu-west-3', bucket_name='pc-builder-bucket-dvg-2025'):
    print("🔧 Setting up S3 for PC Builder")
    print("=" * 50)
    
    # Create S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    
    # 1. Create bucket if it doesn't exist
    print(f"📦 Checking bucket: {bucket_name}")
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket {bucket_name} already exists")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"🔨 Creating bucket: {bucket_name}")
            try:
                if region == 'us-east-1':
                    s3.create_bucket(Bucket=bucket_name)
                else:
                    s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                print(f"✅ Created bucket: {bucket_name}")
            except Exception as create_error:
                print(f"❌ Failed to create bucket: {create_error}")
                return False
        else:
            print(f"❌ Error checking bucket: {e}")
            return False
    
    # 2. Upload CSV file
    csv_file = 'data-results/graphics-cards.csv'
    if os.path.exists(csv_file):
        print(f"📄 Uploading CSV: {csv_file}")
        try:
            s3.upload_file(csv_file, bucket_name, 'graphics-cards.csv')
            print(f"✅ Uploaded CSV file")
        except Exception as e:
            print(f"❌ Failed to upload CSV: {e}")
    else:
        print(f"⚠️  CSV file not found: {csv_file}")
    
    # 3. Upload images
    images_dir = 'cdn-images'
    if os.path.exists(images_dir):
        image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png'))]
        print(f"🖼️  Uploading {len(image_files)} images...")
        
        uploaded = 0
        for image_file in image_files:
            try:
                local_path = os.path.join(images_dir, image_file)
                s3_key = f'images/{image_file}'
                s3.upload_file(local_path, bucket_name, s3_key)
                uploaded += 1
                if uploaded % 5 == 0:  # Progress indicator
                    print(f"   Uploaded {uploaded}/{len(image_files)} images...")
            except Exception as e:
                print(f"❌ Failed to upload {image_file}: {e}")
        
        print(f"✅ Uploaded {uploaded}/{len(image_files)} images")
    else:
        print(f"⚠️  Images directory not found: {images_dir}")
    
    # 4. Test access
    print(f"🧪 Testing S3 access...")
    try:
        # Test CSV access
        response = s3.get_object(Bucket=bucket_name, Key='graphics-cards.csv')
        csv_content = response['Body'].read().decode('utf-8')
        lines = csv_content.split('\n')
        print(f"✅ CSV accessible: {len(lines)} lines")
        
        # Test image access
        objects = s3.list_objects_v2(Bucket=bucket_name, Prefix='images/')
        if 'Contents' in objects:
            image_count = len(objects['Contents'])
            print(f"✅ Images accessible: {image_count} files")
            
            # Test presigned URL for first image
            if image_count > 0:
                first_image = objects['Contents'][0]['Key']
                presigned_url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': first_image},
                    ExpiresIn=3600
                )
                print(f"✅ Presigned URL generated for: {first_image}")
                print(f"   URL: {presigned_url[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ S3 access test failed: {e}")
        return False

def main():
    import sys
    if len(sys.argv) != 3:
        print("Usage: python setup-s3.py ACCESS_KEY SECRET_KEY")
        sys.exit(1)
    
    access_key = sys.argv[1]
    secret_key = sys.argv[2]
    
    if setup_s3_bucket(access_key, secret_key):
        print(f"\n🎉 SUCCESS! S3 is fully set up for PC Builder")
        print(f"\n📋 Next steps:")
        print(f"1. Update your .env file with working credentials")
        print(f"2. Restart your backend")
        print(f"3. Test image serving from S3")
    else:
        print(f"\n❌ S3 setup failed. Check credentials and try again.")

if __name__ == "__main__":
    main()
