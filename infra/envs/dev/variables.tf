variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "genomics-platform"
}

variable "environment" {
  description = "The deployment environment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    "Project"     = "Genomics Platform"
    "Environment" = "Development"
    "Owner"       = "DevOps Team"
  }
}

variable "user_a_principal_arn" {
  description = "ARN of the principal (user/role) that can assume User A role. Leave empty to allow account root."
  type        = string
  default     = ""
}

variable "user_b_principal_arn" {
  description = "ARN of the principal (user/role) that can assume User B role. Leave empty to allow account root."
  type        = string
  default     = ""
}


