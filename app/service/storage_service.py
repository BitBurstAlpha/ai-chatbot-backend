from flask import current_app
import boto3 
import os
from botocore.exceptions import NoCredentialsError, ClientError

import logging

# Set up logger
logger = logging.getLogger(__name__)

def get_s3_client():
    """Get an S3 client instance."""

    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['S3_SECRET_KEY'],
        region_name=current_app.config['S3_REGION']
    )

def upload_to_s3(file_path, s3_key):
    
    try:
        bucket = current_app.config['S3_BUCKET']
        s3_client = get_s3_client()
        s3_client.upload_file(file_path, bucket, s3_key)
        return True
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False
    
def download_from_s3(s3_key, local_path):
    """Download a file from S3 bucket.
    
    Args:
        s3_key (str): S3 object key
        local_path (str): Local path to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download from S3
        bucket = current_app.config['S3_BUCKET']
        s3_client = get_s3_client()
        s3_client.download_file(bucket, s3_key, local_path)
        return True
    except NoCredentialsError:
        logger.error("AWS credentials not available")
        return False
    except ClientError as e:
        logger.error(f"AWS S3 error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error downloading from S3: {str(e)}")
        return False