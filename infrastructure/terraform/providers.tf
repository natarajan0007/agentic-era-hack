terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.51.0"
    }
  }
}

provider "google" {
  alias   = "staging"
  project = var.staging_project_id
  region  = var.gcp_region
}

provider "google" {
  alias   = "prod"
  project = var.prod_project_id
  region  = var.gcp_region
}

# Default provider for CICD resources
provider "google" {
  project = var.cicd_runner_project_id
  region  = var.gcp_region
}