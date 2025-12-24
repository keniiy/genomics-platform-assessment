variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g., dev, prod)"
  type        = string
}

variable "input_bucket_arn" {
  description = "ARN of the input S3 bucket"
  type        = string
}

variable "output_bucket_arn" {
  description = "ARN of the output S3 bucket"
  type        = string
}

variable "user_a_principal_arn" {
  description = "ARN of the principal (user/role) that can assume User A role. Empty string means account root."
  type        = string
  default     = ""
}

variable "user_b_principal_arn" {
  description = "ARN of the principal (user/role) that can assume User B role. Empty string means account root."
  type        = string
  default     = ""
}

variable "tags" {
  description = "A map of tags to assign to resources"
  type        = map(string)
  default     = {}
}

