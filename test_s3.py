# test_s3.py
import os
import boto3
import time
from dotenv import load_dotenv

load_dotenv()

# Test loading environment variables
print("=== Environment Variables ===")
print("AWS_ACCESS_KEY_ID:", os.getenv('AWS_ACCESS_KEY_ID'))
print("AWS_STORAGE_BUCKET_NAME:", os.getenv('AWS_STORAGE_BUCKET_NAME'))
print("AWS_S3_REGION_NAME:", os.getenv('AWS_S3_REGION_NAME'))
print()

# Test S3 connection
print("=== Testing S3 Connection ===")
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_S3_REGION_NAME')
)

try:
    # Try to upload a test file
    print("Creating test file...")
    with open('test.txt', 'w') as f:
        f.write('hello world')
    
    print("Uploading to S3...")
    s3.upload_file('test.txt', os.getenv('AWS_STORAGE_BUCKET_NAME'), 'test-upload.txt')
    print("✅ Direct upload successful!")
    
    # List bucket contents
    print("\n=== Bucket Contents ===")
    resp = s3.list_objects_v2(Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'))
    if 'Contents' in resp:
        print("Files in bucket:")
        for obj in resp['Contents']:
            print(f"  - {obj['Key']} (size: {obj['Size']} bytes)")
    else:
        print("No files found in bucket")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}")

# Try to check if file exists in S3
try:
    # Wait a moment for S3 upload to complete
    time.sleep(2)
    
    # Check if file exists in S3
    s3.head_object(Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'), Key='test-upload.txt')
    print(f"✅ File confirmed to exist in S3: test-upload.txt")
    
except Exception as s3_check_error:
    print(f"❌ File NOT found in S3 (might be timing): {s3_check_error}")