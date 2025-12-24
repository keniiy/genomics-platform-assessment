# Architecture Overview

## System Components

### S3 Buckets
- **Input Bucket**: Receives images from User A
- **Output Bucket**: Stores sanitized images for User B

### Lambda Function
- **Image Sanitizer**: Processes images on S3 event trigger
- Removes all EXIF metadata using Pillow library
- Uploads sanitized images to output bucket

### IAM Roles
- **Lambda Execution Role**: Least privilege access to read input, write output, and log
- **User A Role**: Read + write access to input bucket only
- **User B Role**: Read-only access to output bucket only

## Data Flow

1. User A uploads image to input bucket
2. S3 event notification triggers Lambda function
3. Lambda downloads image, strips EXIF, uploads to output bucket
4. User B can read sanitized images from output bucket

## Security

- All buckets have public access blocked
- Server-side encryption enabled (AES256)
- IAM roles follow least privilege principle
- No cross-bucket access between users

