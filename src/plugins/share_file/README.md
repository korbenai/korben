# Share File Plugin

This plugin provides a convenient way to quickly share files via temporary public S3 buckets with automatic expiration.

**Dependencies:** This plugin requires the `aws_s3` plugin.

## Overview

The `share_file` task creates a unique public S3 bucket, uploads your file, sets it to be publicly accessible, and returns a URL you can share with anyone. The bucket and file are automatically configured to expire after a specified number of days (default: 3 days).

## Prerequisites

- AWS credentials configured (via environment variables or AWS CLI)
- boto3 Python library installed
- Appropriate AWS IAM permissions for S3 operations
- The `aws_s3` plugin must be available

## Configuration

Copy `config.yml.example` to `config.yml` and customize as needed.

The plugin uses AWS credentials from:
1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS CLI configuration (~/.aws/credentials)
3. IAM role (when running on AWS infrastructure)

The AWS region can be set via:
- `AWS_REGION` environment variable (default: us-east-2)

## Available Tasks

### share_file

Read a file, upload it to S3 in a new public bucket, and provide a shareable URL.

**Parameters:**
- `file` (str, required): Path to the file to be uploaded
- `expiration` (int, optional): Number of days after which the file will expire (default: 3)

**Example:**
```bash
# Share a file with default 3-day expiration
./korben.py share_file.share_file --file /path/to/myfile.pdf

# Share a file with custom expiration
./korben.py share_file.share_file --file /path/to/document.pdf --expiration 7

# Share a file with 1-day expiration
./korben.py share_file.share_file --file /tmp/screenshot.png --expiration 1
```

**Output:**
```
File shared successfully!
URL: https://share-abc123.s3.us-east-2.amazonaws.com/myfile.pdf
Expires in: 3 days
```

## How It Works

1. **Creates a unique bucket**: Generates a bucket name like `share-<uuid>`
2. **Sets bucket as public**: Configures the bucket to allow public read access
3. **Configures expiration**: Sets up lifecycle rules to delete objects after N days
4. **Uploads file**: Uploads your file to the bucket
5. **Returns URL**: Provides a direct HTTPS URL to the file

## Security Notes

- **Temporary by design**: Buckets and files are automatically deleted after the expiration period
- **Public access**: Anyone with the URL can access the file. Don't share sensitive information unless you trust the recipients.
- **Unique URLs**: Each share creates a new bucket with a unique UUID, making URLs hard to guess
- **No authentication**: The shared files are accessible without any authentication

## AWS Permissions

The following AWS IAM permissions are required:
- `s3:CreateBucket`
- `s3:PutObject`
- `s3:PutObjectAcl`
- `s3:PutBucketPolicy`
- `s3:PutBucketPublicAccessBlock`
- `s3:PutLifecycleConfiguration`

## Cost Considerations

- Each share creates a new S3 bucket
- Standard S3 storage costs apply until expiration
- Buckets and objects are automatically deleted after expiration
- Minimal cost for small files and short expiration periods

## Use Cases

- Quickly share files with colleagues or clients
- Send large files that won't fit in email
- Create temporary download links for reports or documents
- Share screenshots or logs for debugging
- Distribute files without setting up file sharing infrastructure

## Environment Variables

- `AWS_REGION`: AWS region for bucket operations (default: us-east-2)
- `AWS_ACCESS_KEY_ID`: AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key

