# Outputs for the dev environment

output "input_bucket_name" {
  description = "Name of the input S3 bucket"
  value       = module.input_bucket.bucket_name
}

output "output_bucket_name" {
  description = "Name of the output S3 bucket"
  value       = module.output_bucket.bucket_name
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda.lambda_function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.lambda.lambda_function_arn
}

output "user_a_role_arn" {
  description = "ARN of User A role (read + write input bucket)"
  value       = module.iam.user_a_role_arn
}

output "user_b_role_arn" {
  description = "ARN of User B role (read output bucket only)"
  value       = module.iam.user_b_role_arn
}

