# Image Sanitizer Lambda Function

This Lambda function processes images by removing EXIF metadata.

## Dependencies

- Python 3.11
- Pillow (PIL) for image processing
- boto3 for AWS SDK (provided by Lambda runtime)

## Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Format code
make format

# Type checking
make type-check

# Run tests
make test

# Run tests with coverage
make test-cov
```

## Code Quality

This project uses:

- **Black**: Code formatting (line length 100)
- **isort**: Import sorting (compatible with Black)
- **mypy**: Static type checking (strict mode)
- **pytest**: Unit testing with coverage

Configuration is in `pyproject.toml`.

## Deployment

To create the deployment package:

```bash
# Using Makefile (recommended)
make package

# Or manually
pip install -r requirements.txt -t .
zip -r deployment.zip . -x "*.pyc" "__pycache__/*" "*.git*" "README.md" "tests/*" "*.toml" "Makefile" "requirements-dev.txt"
```

The `deployment.zip` file should be referenced in the Terraform Lambda module.

## Function Logic

1. **Event Reception**: Receives S3 event when object is created in input bucket
2. **Download**: Retrieves image from input bucket
3. **Sanitization**: Strips all EXIF metadata using Pillow
4. **Upload**: Saves sanitized image to output bucket
5. **Logging**: Records processing outcome in CloudWatch Logs

## Testing

Unit tests are located in `tests/test_handler.py` and cover:

- EXIF metadata stripping functionality
- Image format conversion (RGBA to RGB)
- Error handling for invalid images
- S3 event processing (single and multiple records)
- Error handling for S3 failures

Run tests with:

```bash
pytest
# or
make test
```
