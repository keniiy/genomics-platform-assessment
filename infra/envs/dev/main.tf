# Input S3 Bucket - where users upload images
module "input_bucket" {
  source = "../../modules/s3-bucket"

  bucket_name       = "${var.project_name}-input-${var.environment}"
  versioning_enabled = true
  tags              = var.common_tags
}

# Output S3 Bucket - where sanitized images are stored
module "output_bucket" {
  source = "../../modules/s3-bucket"

  bucket_name       = "${var.project_name}-output-${var.environment}"
  versioning_enabled = true
  tags              = var.common_tags
}

# IAM Roles and Policies - least privilege access
module "iam" {
  source = "../../modules/iam"

  project_name      = var.project_name
  environment       = var.environment
  input_bucket_arn  = module.input_bucket.bucket_arn
  output_bucket_arn = module.output_bucket.bucket_arn
  user_a_principal_arn = var.user_a_principal_arn
  user_b_principal_arn = var.user_b_principal_arn
  tags              = var.common_tags
}

# Lambda Function - image sanitization processor
module "lambda" {
  source = "../../modules/lambda"

  project_name            = var.project_name
  environment             = var.environment
  lambda_execution_role_arn = module.iam.lambda_execution_role_arn
  input_bucket_id         = module.input_bucket.bucket_id
  input_bucket_arn        = module.input_bucket.bucket_arn
  output_bucket_name      = module.output_bucket.bucket_name
  tags                    = var.common_tags
}
