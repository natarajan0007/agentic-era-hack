variable "gcp_project_id" {
  type        = string
  description = "The Google Cloud project ID for the Production environment."
}

variable "gcp_region" {
  type        = string
  description = "The Google Cloud region for the resources."
}

variable "service_names" {
  type        = list(string)
  description = "A list of names for the services to be created."
  default     = ["adk-agent", "fastapi-backend", "nextjs-frontend", "toolbox"]
}

variable "db_password" {
  type        = string
  description = "The password for the PostgreSQL database."
  sensitive   = true
}

variable "repository_owner" {
  type        = string
  description = "The owner of the GitHub repository (username or organization)."
}

variable "repository_name" {
  type        = string
  description = "The name of the GitHub repository."
}
