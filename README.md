# Genomics Platform - Image Sanitization Pipeline

A serverless AWS infrastructure solution for automatically sanitizing image EXIF metadata using Lambda and S3 event-driven architecture.

## 1. What Problem Does This System Solve?

This system addresses the privacy and security concern of EXIF metadata in images. EXIF data can contain sensitive information such as:

- GPS coordinates (location where photo was taken)
- Camera model and settings
- Timestamps
- Software used to edit the image
- Potentially other embedded metadata

**The Problem**: When images are shared or stored, this metadata can leak sensitive information about users, locations, and workflows.

**The Solution**: An automated pipeline that strips all EXIF metadata from images as soon as they are uploaded, ensuring only sanitized images are available for downstream consumption.

## 2. How Does Data Flow End to End?

```text
User A → Input S3 Bucket → S3 Event → Lambda Function → Output S3 Bucket → User B
```

**Detailed Flow**:

1. **Upload**: User A uploads an image to the input S3 bucket (`genomics-platform-input-dev`)
2. **Event Trigger**: S3 automatically sends an event notification to the Lambda function when the object is created
3. **Processing**: Lambda function:
   - Downloads the image from the input bucket
   - Uses Pillow (PIL) library to strip all EXIF metadata
   - Converts image to RGB format (removes transparency and additional metadata)
   - Saves sanitized image to memory
4. **Storage**: Lambda uploads the sanitized image to the output bucket (`genomics-platform-output-dev`) with the same key name
5. **Access**: User B can read sanitized images from the output bucket
6. **Logging**: All processing outcomes are logged to CloudWatch Logs for audit and debugging

**Key Design Decision**: Synchronous processing via S3 events is appropriate for low-to-medium volume. For high-volume production, consider adding an SQS queue for async processing and better error handling.

## 3. Why Lambda + S3 Events?

**Lambda**:

- **Serverless**: No infrastructure to manage, scales automatically
- **Cost-effective**: Pay only for execution time (millions of requests free tier)
- **Event-driven**: Perfect fit for S3 object creation events
- **Fast cold starts**: Python runtime has minimal cold start latency
- **Managed runtime**: AWS handles Python environment and dependencies

**S3 Events**:

- **Native integration**: Built-in event notifications, no polling required
- **Reliable**: AWS manages event delivery with retries
- **Zero infrastructure**: No message queues or event buses needed for basic use case
- **Immediate processing**: Images are processed as soon as they're uploaded

**Alternative Considered**: SQS + Lambda would provide better durability and retry logic, but adds complexity. For this assessment scope, S3 events provide the simplest, most maintainable solution.

## 4. How Is Security Handled?

### IAM - Least Privilege Principle

**Lambda Execution Role**:

- ✅ Read objects from input bucket only
- ✅ Write objects to output bucket only
- ✅ Write CloudWatch Logs
- ❌ No access to other buckets, services, or resources

**User A Role**:

- ✅ Read + write access to input bucket only
- ✅ List bucket contents (input bucket)
- ❌ No access to output bucket
- ❌ No access to Lambda or other services

**User B Role**:

- ✅ Read-only access to output bucket only
- ✅ List bucket contents (output bucket)
- ❌ No access to input bucket
- ❌ No write permissions anywhere

### S3 Security

- **Public Access Block**: All buckets have public access completely blocked
- **Server-Side Encryption**: AES256 encryption at rest for all objects
- **Versioning**: Enabled for data protection and recovery
- **Bucket Policies**: Access controlled exclusively through IAM roles (no public policies)

### Data Privacy

- **EXIF Removal**: All metadata is stripped, including GPS coordinates, timestamps, and camera information
- **No Cross-Contamination**: Users cannot access each other's buckets
- **Audit Trail**: CloudWatch Logs capture all processing events

## 5. What Did You Intentionally NOT Build, and Why?

**CI/CD Pipeline**: Not included because this is an infrastructure assessment focused on Terraform design and security. In production, you'd add GitHub Actions or AWS CodePipeline.

**Remote State Backend**: Using local state for simplicity. Production would use S3 + DynamoDB for state locking and team collaboration.

**Monitoring & Alerting**: Basic CloudWatch Logs included, but no CloudWatch Alarms, SNS notifications, or dashboards. Production would need alerts for Lambda errors, processing delays, and bucket access anomalies.

**SQS Queue**: Direct S3-to-Lambda integration chosen for simplicity. High-volume production would benefit from SQS for better error handling, dead-letter queues, and rate limiting.

**Multi-Region/DR**: Single region deployment. Production genomics data might require cross-region replication for compliance.

**Image Format Validation**: Lambda processes any file type. Production should validate file types, sizes, and scan for malware before processing.

**Cost Optimization**: No lifecycle policies, intelligent tiering, or cleanup jobs. Production would archive old images and optimize storage costs.

**Testing**: No unit tests or integration tests included. Production would require comprehensive test coverage.

**Documentation**: Minimal docs focused on architecture. Production would need runbooks, operational procedures, and troubleshooting guides.

**Why These Trade-offs**: This assessment evaluates infrastructure design thinking, security posture, and architectural decisions—not production completeness. Adding all production features would obscure the core assessment criteria.

## 6. What Would You Do Next in Real Production?

### Immediate Priorities (Week 1-2)

1. **Add SQS Queue**: Decouple S3 events from Lambda for better reliability and error handling
2. **Implement Dead-Letter Queue**: Capture failed processing attempts for manual review
3. **Add CloudWatch Alarms**: Alert on Lambda errors, high latency, or processing failures
4. **Image Validation**: Validate file types, sizes, and scan for malicious content
5. **Cost Monitoring**: Set up billing alerts and analyze Lambda/S3 costs

### Short-Term (Month 1)

1. **CI/CD Pipeline**: Automated Terraform validation and deployment via GitHub Actions
2. **Remote State Backend**: Migrate to S3 + DynamoDB for state management
3. **Enhanced Logging**: Structured JSON logging with correlation IDs for tracing
4. **Performance Optimization**:
   - Lambda memory tuning based on image sizes
   - Consider Lambda Layers for Pillow dependency
   - Add image format detection and optimization
5. **Security Hardening**:
    - Enable VPC endpoints for S3 (if in VPC)
    - Add AWS WAF if exposing via API Gateway
    - Implement bucket policies as defense-in-depth

### Medium-Term (Quarter 1)

1. **Multi-Format Support**: Handle PNG, WebP, TIFF, and other formats beyond JPEG
2. **Batch Processing**: For large backlogs, add S3 batch operations integration
3. **Cost Optimization**:
    - S3 lifecycle policies (move to Glacier after 90 days)
    - Lambda provisioned concurrency for consistent performance
    - Reserved capacity planning
4. **Observability**:
    - Distributed tracing with AWS X-Ray
    - Custom CloudWatch dashboards
    - S3 access logging and analysis
5. **Compliance**:
    - Enable S3 access logging for audit
    - Add data retention policies
    - Document data processing procedures (GDPR/HIPAA considerations)

### Long-Term (Quarter 2+)

1. **Multi-Region**: Cross-region replication for disaster recovery
2. **Advanced Features**:
    - Image resizing/optimization options
    - Watermarking capabilities
    - Format conversion (e.g., JPEG to WebP)
3. **Machine Learning**: Optional ML-based content moderation or classification
4. **API Gateway**: If external access needed, add API Gateway with authentication
5. **Cost Analytics**: Detailed cost allocation tags and reporting

**Production Philosophy**: Start minimal, measure everything, iterate based on real usage patterns. This infrastructure provides a solid, secure foundation that can scale and evolve.

---

## Repository Structure

```text
genomics-platform-assessment/
├── infra/
│   ├── envs/dev/          # Development environment configuration
│   └── modules/
│       ├── s3-bucket/      # Reusable S3 bucket module
│       ├── iam/            # IAM roles and policies
│       └── lambda/         # Lambda function and triggers
├── services/
│   └── image-sanitiser/    # Lambda function code
├── docs/
│   └── ARCHITECTURE.md     # Detailed architecture documentation
└── README.md               # This file
```

## Deployment

### Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- Python 3.11 (for Lambda deployment package)

### Steps

1. **Build Lambda Deployment Package**:

   ```bash
   cd services/image-sanitiser
   pip install -r requirements.txt -t .
   zip -r deployment.zip . -x "*.pyc" "__pycache__/*" "*.git*" "README.md"
   ```

2. **Deploy Infrastructure**:

   ```bash
   cd infra/envs/dev
   terraform init
   terraform plan
   terraform apply
   ```

3. **Configure User Access**:
   - Update `user_a_principal_arn` and `user_b_principal_arn` in `variables.tf` or via `terraform.tfvars`
   - Users can assume their respective roles to access buckets

## Testing

Upload an image to the input bucket and verify:

1. Image appears in output bucket
2. EXIF metadata is removed (check with `exiftool` or similar)
3. CloudWatch Logs show successful processing

## Security Notes

- All buckets are private by default
- IAM roles follow least privilege
- No public access is permitted
- All data is encrypted at rest

---

**Assessment Focus**: This solution demonstrates production-grade infrastructure thinking with emphasis on security, maintainability, and clear architectural decisions—not feature completeness.
