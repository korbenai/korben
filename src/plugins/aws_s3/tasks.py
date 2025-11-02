"""AWS S3 tasks - manage buckets and objects."""

import os
import json
import logging
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

logger = logging.getLogger(__name__)


def delete_bucket(**kwargs):
    """
    Deletes an S3 bucket and all its contents.
    
    Args:
        bucket_name (str): The name of the S3 bucket to delete.
    
    Returns:
        str: Success or error message
    """
    bucket_name = kwargs.get('bucket_name')
    
    if not bucket_name:
        error_msg = "ERROR: No bucket_name specified. Provide --bucket_name."
        logger.error(error_msg)
        return error_msg
    
    region = os.getenv('AWS_REGION', 'us-east-2')
    s3_client = boto3.client('s3', region_name=region)
    s3_resource = boto3.resource('s3', region_name=region)
    
    try:
        bucket = s3_resource.Bucket(bucket_name)
        
        # Delete all objects in the bucket
        logger.info(f"Deleting all objects in bucket {bucket_name}")
        bucket.objects.all().delete()
        
        # Delete the bucket itself
        logger.info(f"Deleting bucket {bucket_name}")
        s3_client.delete_bucket(Bucket=bucket_name)
        
        result = f"Bucket {bucket_name} and all its contents have been deleted."
        logger.info(result)
        return result
    except ClientError as e:
        error_msg = f"Failed to delete bucket {bucket_name}: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


def create_bucket(**kwargs):
    """
    Creates an S3 bucket if it does not already exist.
    
    Args:
        bucket_name (str): The name of the S3 bucket.
        allow_public (bool, optional): If True, sets the bucket policy to allow public access. Default is False.
        expiration_days (int, optional): Number of days after which objects in the bucket expire. Default is None.
    
    Returns:
        str: Success or error message
    """
    bucket_name = kwargs.get('bucket_name')
    allow_public = kwargs.get('allow_public', False)
    expiration_days = kwargs.get('expiration_days')
    
    if not bucket_name:
        error_msg = "ERROR: No bucket_name specified. Provide --bucket_name."
        logger.error(error_msg)
        return error_msg
    
    region = os.getenv('AWS_REGION', 'us-east-2')
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Check if the bucket already exists
        s3_client.head_bucket(Bucket=bucket_name)
        result = f"Bucket {bucket_name} already exists."
        logger.info(result)
        return result
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Bucket does not exist, create it
            try:
                logger.info(f"Creating bucket {bucket_name} in region {region}")
                if region is None:
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                logger.info(f"Bucket {bucket_name} created successfully.")
                
                # Set bucket policy to allow public access if specified
                if allow_public:
                    logger.info(f"Setting public access for bucket {bucket_name}")
                    s3_client.put_public_access_block(
                        Bucket=bucket_name,
                        PublicAccessBlockConfiguration={
                            'BlockPublicAcls': False,
                            'IgnorePublicAcls': False,
                            'BlockPublicPolicy': False,
                            'RestrictPublicBuckets': False
                        }
                    )
                    public_policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "PublicReadGetObject",
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": "s3:GetObject",
                                "Resource": f"arn:aws:s3:::{bucket_name}/*"
                            }
                        ]
                    }
                    s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(public_policy))
                    logger.info(f"Bucket {bucket_name} is now public.")
                
                # Set bucket lifecycle configuration to expire objects if specified
                if expiration_days is not None:
                    logger.info(f"Setting expiration policy for bucket {bucket_name}: {expiration_days} days")
                    lifecycle_configuration = {
                        'Rules': [
                            {
                                'ID': 'SetExpirationRule',
                                'Status': 'Enabled',
                                'Expiration': {
                                    'Days': expiration_days
                                },
                                'Filter': {
                                    'Prefix': ''  # Specify a prefix if needed, or leave empty for all objects
                                }
                            }
                        ]
                    }
                    s3_client.put_bucket_lifecycle_configuration(
                        Bucket=bucket_name, 
                        LifecycleConfiguration=lifecycle_configuration
                    )
                    logger.info(f"Bucket {bucket_name} objects will expire after {expiration_days} days.")
                
                result = f"Bucket {bucket_name} created successfully."
                if allow_public:
                    result += " (public access enabled)"
                if expiration_days:
                    result += f" (objects expire after {expiration_days} days)"
                return result
            except ClientError as e:
                error_msg = f"Failed to create bucket {bucket_name}: {e}"
                logger.error(error_msg)
                return f"ERROR: {error_msg}"
        else:
            error_msg = f"Failed to check bucket {bucket_name}: {e}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"


def upload_file_to_s3(**kwargs):
    """
    Uploads a stream of bytes to a file in an S3 bucket.
    
    Args:
        bucket_name (str): The name of the S3 bucket.
        s3_file_path (str): The path to the file in the S3 bucket.
        content (bytes): The content to be uploaded as a stream of bytes.
    
    Returns:
        str: Success or error message
    """
    bucket_name = kwargs.get('bucket_name')
    s3_file_path = kwargs.get('s3_file_path')
    content = kwargs.get('content')
    
    if not bucket_name:
        error_msg = "ERROR: No bucket_name specified. Provide --bucket_name."
        logger.error(error_msg)
        return error_msg
    
    if not s3_file_path:
        error_msg = "ERROR: No s3_file_path specified. Provide --s3_file_path."
        logger.error(error_msg)
        return error_msg
    
    if content is None:
        error_msg = "ERROR: No content specified. Provide --content."
        logger.error(error_msg)
        return error_msg
    
    region = os.getenv('AWS_REGION', 'us-east-2')
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Ensure no ACL is set to avoid AccessControlListNotSupported error
        logger.info(f"Uploading file to {bucket_name}/{s3_file_path}")
        s3_client.put_object(Bucket=bucket_name, Key=s3_file_path, Body=content)
        result = f"File uploaded successfully to {bucket_name}/{s3_file_path}"
        logger.info(result)
        return result
    except NoCredentialsError:
        error_msg = "Credentials not available"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    except ClientError as e:
        error_msg = f"Failed to upload file to S3: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


def read_file_from_s3(**kwargs):
    """
    Reads a file from an S3 bucket as a stream of bytes.
    
    Args:
        bucket_name (str): The name of the S3 bucket.
        s3_file_path (str): The path to the file in the S3 bucket.
    
    Returns:
        bytes: The content of the file as a stream of bytes if successful, else None.
    """
    bucket_name = kwargs.get('bucket_name')
    s3_file_path = kwargs.get('s3_file_path')
    
    if not bucket_name:
        error_msg = "ERROR: No bucket_name specified. Provide --bucket_name."
        logger.error(error_msg)
        return error_msg
    
    if not s3_file_path:
        error_msg = "ERROR: No s3_file_path specified. Provide --s3_file_path."
        logger.error(error_msg)
        return error_msg
    
    region = os.getenv('AWS_REGION', 'us-east-2')
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        logger.info(f"Reading file from {bucket_name}/{s3_file_path}")
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_file_path)
        content = response['Body'].read()
        logger.info(f"File read successfully from {bucket_name}/{s3_file_path} ({len(content)} bytes)")
        return content
    except NoCredentialsError:
        error_msg = "Credentials not available"
        logger.error(error_msg)
        return None
    except ClientError as e:
        error_msg = f"Failed to read file from S3: {e}"
        logger.error(error_msg)
        return None

