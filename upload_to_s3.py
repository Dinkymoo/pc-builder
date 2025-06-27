import boto3
import os
from pathlib import Path
from botocore.exceptions import ClientError

# Set these with your AWS credentials and bucket info
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
BUCKET_NAME = os.environ.get('S3_BUCKET', 'pc-builder-data')

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_csv():
    s3.upload_file('data-results/graphics-cards.csv', BUCKET_NAME, 'graphics-cards.csv')
    print('Uploaded graphics-cards.csv')

def image_exists_in_s3(key):
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise

def upload_images():
    image_dir = Path('cdn-images')
    for img_path in image_dir.glob('*'):
        if img_path.is_file():
            s3_key = f'images/{img_path.name}'
            if image_exists_in_s3(s3_key):
                print(f'Skipping {img_path.name} (already exists in S3)')
            else:
                s3.upload_file(str(img_path), BUCKET_NAME, s3_key)
                print(f'Uploaded {img_path.name}')

def main():
    upload_csv()
    upload_images()

if __name__ == '__main__':
    main()
