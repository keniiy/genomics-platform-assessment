# Lambda Module - Image Sanitization Function
#
# This module creates a Lambda function that:
# 1. Triggers on S3 object creation in the input bucket
# 2. Downloads the image
# 3. Strips EXIF metadata
# 4. Uploads sanitized image to output bucket

# Lambda function
resource "aws_lambda_function" "image_sanitizer" {
  function_name = "${var.project_name}-image-sanitizer-${var.environment}"
  role          = var.lambda_execution_role_arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300 # 5 minutes max for large images
  memory_size   = 512

  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  environment {
    variables = {
      OUTPUT_BUCKET = var.output_bucket_name
    }
  }

  tags = var.tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.image_sanitizer.function_name}"
  retention_in_days = 7
  tags              = var.tags
}

# S3 Event Notification Permission
resource "aws_lambda_permission" "s3_invoke" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.image_sanitizer.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.input_bucket_arn
}

# S3 Bucket Notification - triggers Lambda on object creation
# Note: filter_prefix and filter_suffix omitted to process all objects
resource "aws_s3_bucket_notification" "lambda_trigger" {
  bucket = var.input_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.image_sanitizer.arn
    events              = ["s3:ObjectCreated:*"]
    # No filters - process all objects uploaded to the bucket
  }

  depends_on = [aws_lambda_permission.s3_invoke]
}

