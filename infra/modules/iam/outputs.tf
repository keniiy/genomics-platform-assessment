output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution.arn
}

output "lambda_execution_role_name" {
  description = "Name of the Lambda execution role"
  value       = aws_iam_role.lambda_execution.name
}

output "user_a_role_arn" {
  description = "ARN of User A role (read + write input bucket)"
  value       = aws_iam_role.user_a.arn
}

output "user_b_role_arn" {
  description = "ARN of User B role (read output bucket only)"
  value       = aws_iam_role.user_b.arn
}

