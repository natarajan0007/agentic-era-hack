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
