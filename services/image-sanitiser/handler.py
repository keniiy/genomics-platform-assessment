"""
Lambda Handler for Image EXIF Metadata Sanitization

This Lambda function processes images uploaded to an S3 input bucket by:
1. Receiving S3 event notifications when objects are created
2. Downloading the image from the input bucket
3. Stripping all EXIF metadata using Pillow (PIL)
4. Uploading the sanitized image to the output bucket
5. Logging the processing outcome

Architecture Decision:
- Uses Pillow (PIL) library for image processing as it's the industry standard
  for Python image manipulation and EXIF handling
- Processes images synchronously (suitable for low-to-medium volume)
- For high-volume production, consider SQS queue for async processing

Security Considerations:
- Lambda role has least privilege: read input bucket, write output bucket only
- No EXIF data is preserved, ensuring privacy compliance
- CloudWatch logs capture processing outcomes for audit trail
"""

import json
import logging
import os
from io import BytesIO
from typing import Any, Dict, List

import boto3
from botocore.client import BaseClient

# Initialize clients
s3_client: BaseClient = boto3.client("s3")
logger: logging.Logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Output bucket from environment variable
OUTPUT_BUCKET: str = os.environ["OUTPUT_BUCKET"]


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function.

    Args:
        event: S3 event notification containing bucket and object key
        context: Lambda context object (unused but required by Lambda runtime)

    Returns:
        dict: Processing result with status and details
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # Process each S3 event record
    results: List[Dict[str, Any]] = []
    for record in event.get("Records", []):
        object_key: str = ""
        try:
            # Extract S3 event details
            bucket_name: str = record["s3"]["bucket"]["name"]
            object_key: str = record["s3"]["object"]["key"]

            logger.info(f"Processing image: s3://{bucket_name}/{object_key}")

            # Step 1: Download image from input bucket
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            image_data: bytes = response["Body"].read()

            logger.info(f"Downloaded image: {len(image_data)} bytes")

            # Step 2: Strip EXIF metadata using Pillow
            # Pillow automatically removes EXIF when saving images without metadata
            sanitized_image: bytes = strip_exif_metadata(image_data)

            logger.info(f"Sanitized image: {len(sanitized_image)} bytes")

            # Step 3: Upload sanitized image to output bucket
            # Preserve original key name for traceability
            output_key: str = object_key
            s3_client.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=output_key,
                Body=sanitized_image,
                ContentType=response.get("ContentType", "image/jpeg"),
            )

            logger.info(
                f"Uploaded sanitized image to: s3://{OUTPUT_BUCKET}/{output_key}"
            )

            results.append(
                {
                    "status": "success",
                    "input_key": object_key,
                    "output_key": output_key,
                    "input_size": len(image_data),
                    "output_size": len(sanitized_image),
                }
            )

        except Exception as e:
            logger.error(f"Error processing {object_key}: {str(e)}", exc_info=True)
            results.append(
                {"status": "error", "input_key": object_key, "error": str(e)}
            )

    return {
        "statusCode": 200,
        "body": json.dumps({"processed": len(results), "results": results}),
    }


def strip_exif_metadata(image_data: bytes) -> bytes:
    """
    Strip all EXIF metadata from an image.

    Process:
    1. Load image from bytes into Pillow Image object
    2. Convert to RGB (removes transparency and some metadata)
    3. Save to bytes without EXIF data

    Args:
        image_data: Raw image bytes

    Returns:
        bytes: Image bytes with all EXIF metadata removed

    Raises:
        RuntimeError: If Pillow is not available or image processing fails
    """
    try:
        from PIL import Image

        # Load image from bytes
        image = Image.open(BytesIO(image_data))

        # Convert to RGB to ensure compatibility and remove transparency
        # This also helps remove some metadata formats
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Save to bytes buffer without EXIF data
        output_buffer = BytesIO()
        image.save(output_buffer, format="JPEG", quality=95, exif=b"")

        return output_buffer.getvalue()

    except ImportError:
        # Fallback if Pillow is not available (should not happen in deployment)
        logger.error("Pillow library not available")
        raise RuntimeError("Image processing library not available")
    except Exception as e:
        logger.error(f"Error stripping EXIF: {str(e)}")
        raise

