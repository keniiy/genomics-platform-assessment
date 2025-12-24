# IAM Module - Least Privilege Roles and Policies
#
# This module creates IAM roles and policies following the principle of least privilege:
# - Lambda execution role: read input bucket, write output bucket, write logs
# - User A role: read + write input bucket only
# - User B role: read output bucket only

# Lambda Execution Role
resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-execution-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

# Lambda execution policy - least privilege
resource "aws_iam_role_policy" "lambda_execution" {
  name = "${var.project_name}-lambda-execution-policy-${var.environment}"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${var.input_bucket_arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "${var.output_bucket_arn}/*"
      }
    ]
  })
}

# User A Role - Read + Write Input Bucket Only
resource "aws_iam_role" "user_a" {
  name = "${var.project_name}-user-a-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = var.user_a_principal_arn != "" ? var.user_a_principal_arn : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "user_a" {
  name = "${var.project_name}-user-a-policy-${var.environment}"
  role = aws_iam_role.user_a.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:DeleteObject"
        ]
        Resource = "${var.input_bucket_arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = var.input_bucket_arn
        Condition = {
          StringEquals = {
            "s3:prefix" = [""]
          }
        }
      }
    ]
  })
}

# User B Role - Read Output Bucket Only
resource "aws_iam_role" "user_b" {
  name = "${var.project_name}-user-b-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = var.user_b_principal_arn != "" ? var.user_b_principal_arn : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "user_b" {
  name = "${var.project_name}-user-b-policy-${var.environment}"
  role = aws_iam_role.user_b.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${var.output_bucket_arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = var.output_bucket_arn
        Condition = {
          StringEquals = {
            "s3:prefix" = [""]
          }
        }
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

