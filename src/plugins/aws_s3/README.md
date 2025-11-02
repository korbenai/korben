# AWS S3 Plugin

This plugin provides tasks for managing AWS S3 buckets and objects.

## Prerequisites

- AWS credentials configured (via environment variables or AWS CLI)
- boto3 Python library installed
- Appropriate AWS IAM permissions for S3 operations

## Configuration

Copy `config.yml.example` to `config.yml` and customize as needed.

The plugin uses AWS credentials from:
1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS CLI configuration (~/.aws/credentials)
3. IAM role (when running on AWS infrastructure)

The AWS region can be set via:
- `AWS_REGION` environment variable (default: us-east-2)

## Available Tasks

### create_bucket

Creates an S3 bucket if it does not already exist.

**Parameters:**
- `bucket_name` (str, required): The name of the S3 bucket
- `allow_public` (bool, optional): If True, sets the bucket policy to allow public access. Default is False.
- `expiration_days` (int, optional): Number of days after which objects in the bucket expire. Default is None.

**Example:**
```bash
./korben.py aws_s3.create_bucket --bucket_name my-bucket
./korben.py aws_s3.create_bucket --bucket_name my-public-bucket --allow_public True
./korben.py aws_s3.create_bucket --bucket_name my-temp-bucket --expiration_days 7
```

### delete_bucket

Deletes an S3 bucket and all its contents.

**Parameters:**
- `bucket_name` (str, required): The name of the S3 bucket to delete

**Example:**
```bash
./korben.py aws_s3.delete_bucket --bucket_name my-bucket
```

**Warning:** This operation is irreversible and will delete all objects in the bucket!

### upload_file_to_s3

Uploads a stream of bytes to a file in an S3 bucket.

**Parameters:**
- `bucket_name` (str, required): The name of the S3 bucket
- `s3_file_path` (str, required): The path to the file in the S3 bucket
- `content` (bytes, required): The content to be uploaded as a stream of bytes

**Example:**
```python
# From Python code
from src.plugins.aws_s3.tasks import upload_file_to_s3

with open('myfile.txt', 'rb') as f:
    content = f.read()
    
result = upload_file_to_s3(
    bucket_name='my-bucket',
    s3_file_path='path/to/myfile.txt',
    content=content
)
```

### read_file_from_s3

Reads a file from an S3 bucket as a stream of bytes.

**Parameters:**
- `bucket_name` (str, required): The name of the S3 bucket
- `s3_file_path` (str, required): The path to the file in the S3 bucket

**Returns:**
- bytes: The content of the file as a stream of bytes if successful, else None

**Example:**
```python
# From Python code
from src.plugins.aws_s3.tasks import read_file_from_s3

content = read_file_from_s3(
    bucket_name='my-bucket',
    s3_file_path='path/to/myfile.txt'
)

if content:
    # Process the content
    with open('downloaded_file.txt', 'wb') as f:
        f.write(content)
```

## AWS Permissions

The following AWS IAM permissions are required for the respective operations:

### For create_bucket:
- `s3:CreateBucket`
- `s3:PutBucketPolicy` (if using allow_public)
- `s3:PutBucketPublicAccessBlock` (if using allow_public)
- `s3:PutLifecycleConfiguration` (if using expiration_days)

### For delete_bucket:
- `s3:DeleteBucket`
- `s3:DeleteObject`
- `s3:ListBucket`

### For upload_file_to_s3:
- `s3:PutObject`

### For read_file_from_s3:
- `s3:GetObject`

## Security Notes

- **Public Buckets**: Use the `allow_public` parameter with caution. Public buckets can be accessed by anyone on the internet.
- **Credentials**: Never commit AWS credentials to version control. Always use environment variables or AWS CLI configuration.
- **Bucket Deletion**: The `delete_bucket` operation is irreversible. All objects in the bucket will be permanently deleted.
- **Expiration**: When setting `expiration_days`, objects will be automatically deleted after the specified number of days. This cannot be undone once objects expire.

## Environment Variables

- `AWS_REGION`: AWS region for bucket operations (default: us-east-2)
- `AWS_ACCESS_KEY_ID`: AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key

