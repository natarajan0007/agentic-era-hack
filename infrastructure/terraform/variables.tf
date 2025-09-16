variable "prod_project_id" {
  type        = string
  description = "The Google Cloud project ID for the Production environment."
}

variable "staging_project_id" {
  type        = string
  description = "The Google Cloud project ID for the Staging environment."
}

variable "cicd_runner_project_id" {
  type        = string
  description = "The Google Cloud project ID where CI/CD resources like WIF and the CICD service account will live."
}

variable "gcp_region" {
  type        = string
  description = "The Google Cloud region to deploy the resources to."
  default     = "europe-west1"
}

variable "repository_owner" {
  type        = string
  description = "The owner of the GitHub repository (username or organization)."
}

variable "repository_name" {
  type        = string
  description = "The name of the GitHub repository."
}

variable "service_names" {
  type        = list(string)
  description = "A list of names for the services to be created."
  default     = ["adk-agent", "fastapi-backend", "nextjs-frontend", "toolbox"]
}