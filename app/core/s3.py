import os
import aioboto3
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# S3 configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

# Create aioboto3 session
session = aioboto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION
)

async def upload_to_s3(file_obj, filename):
    """
    Upload a file to S3 bucket using aioboto3
    
    Args:
        file_obj: File-like object to upload
        filename: Name to give the file in S3
        
    Returns:
        str: S3 path of the uploaded file
    """
    try:
        async with session.client('s3') as s3_client:
            await s3_client.upload_fileobj(
                file_obj,
                S3_BUCKET,
                filename
            )
        
        s3_path = f"s3://{S3_BUCKET}/{filename}"
        logger.info(f"File uploaded successfully to {s3_path}")
        return s3_path
    
    except Exception as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        raise

async def get_from_s3(s3_path):
    """
    Get a file from S3 bucket using aioboto3
    
    Args:
        s3_path: S3 path of the file (s3://bucket/key)
        
    Returns:
        bytes: File content
    """
    try:
        bucket_name, object_key = s3_path.replace("s3://", "").split("/", 1)
        
        file_content = None
        async with session.client('s3') as s3_client:
            response = await s3_client.get_object(Bucket=bucket_name, Key=object_key)
            async with response['Body'] as stream:
                file_content = await stream.read()
                
        return file_content
    
    except Exception as e:
        logger.error(f"Error getting file from S3: {str(e)}")
        raise 