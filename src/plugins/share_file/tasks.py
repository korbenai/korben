"""Share File tasks - create temporary public S3 buckets and share files."""

import os
import logging
import uuid
import boto3
from botocore.exceptions import ClientError
from src.plugins.aws_s3.tasks import create_bucket, upload_file_to_s3

# Declare dependency on aws_s3 plugin
__dependencies__ = ['aws_s3']

logger = logging.getLogger(__name__)


def share_file(**kwargs):
    """
    Read a file, upload it to S3 in a new public bucket, and provide the URL.
    
    This is a convenience task that creates a temporary public bucket with an expiration policy,
    uploads a file, and returns a public URL that can be shared.
    
    Args:
        file (str): Path to the file to be uploaded
        expiration (int, optional): Number of days after which the file will expire (default: 3)
    
    Returns:
        str: Public URL to the uploaded file or error message
    """
    file_path = kwargs.get('file')
    expiration_days = kwargs.get('expiration', 3)
    
    if not file_path:
        error_msg = "ERROR: No file specified. Provide --file."
        logger.error(error_msg)
        return error_msg
    
    # Validate file exists
    if not os.path.exists(file_path):
        error_msg = f"ERROR: File not found: {file_path}"
        logger.error(error_msg)
        return error_msg
    
    # Generate unique bucket name
    bucket_name = f"share-{uuid.uuid4()}"
    s3_file_path = os.path.basename(file_path)
    
    logger.info("=" * 70)
    logger.info("FILE SHARING")
    logger.info("=" * 70)
    logger.info(f"File: {file_path}")
    logger.info(f"Bucket: {bucket_name}")
    logger.info(f"Expiration: {expiration_days} days")
    logger.info("=" * 70)
    
    # Create the S3 bucket with public access and expiration
    logger.info("Creating temporary public bucket...")
    result = create_bucket(
        bucket_name=bucket_name,
        allow_public=True,
        expiration_days=expiration_days
    )
    
    if result.startswith("ERROR"):
        logger.error(f"Failed to create bucket: {result}")
        return result
    
    # Read the file
    try:
        logger.info(f"Reading file: {file_path}")
        with open(file_path, 'rb') as f:
            content = f.read()
        logger.info(f"Read {len(content)} bytes from {file_path}")
    except FileNotFoundError:
        error_msg = f"ERROR: File {file_path} not found"
        logger.error(error_msg)
        return error_msg
    except IOError as e:
        error_msg = f"ERROR: Error reading file {file_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg
    
    # Upload the file to S3
    logger.info("Uploading file to S3...")
    result = upload_file_to_s3(
        bucket_name=bucket_name,
        s3_file_path=s3_file_path,
        content=content
    )
    
    if result.startswith("ERROR"):
        logger.error(f"Failed to upload file: {result}")
        return result
    
    # Set the object as public-read
    region = os.getenv('AWS_REGION', 'us-east-2')
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        logger.info(f"Setting public-read ACL for {s3_file_path}")
        s3_client.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=s3_file_path)
        logger.info(f"File {s3_file_path} in bucket {bucket_name} is now public.")
    except ClientError as e:
        # Log warning but continue - the bucket policy should make it public anyway
        logger.warning(f"Failed to set public-read ACL for {s3_file_path} in bucket {bucket_name}: {e}")
        logger.info("File should still be accessible via bucket policy")
    
    # Generate and return the file's URL
    file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_file_path}"
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("✓ FILE SHARED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"URL: {file_url}")
    logger.info(f"Expires in: {expiration_days} days")
    logger.info("=" * 70)
    
    result = f"File shared successfully!\nURL: {file_url}\nExpires in: {expiration_days} days"
    return result

