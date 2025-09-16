locals {
  environments = {
    staging = {
      project_id = var.staging_project_id
    },
    prod = {
      project_id = var.prod_project_id
    }
  }
}

# --- CICD Resources (Created in the CICD Project) ---

resource "google_project_service" "cicd_apis" {
  for_each = toset([
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
  ])
  project                    = var.cicd_runner_project_id
  service                    = each.key
  disable_dependent_services = true
}

resource "google_service_account" "cicd_runner_sa" {
  project      = var.cicd_runner_project_id
  account_id   = "${var.repository_name}-cicd-sa"
  display_name = "CICD Runner Service Account"
  depends_on   = [google_project_service.cicd_apis]
}

resource "google_iam_workload_identity_pool" "wif_pool" {
  project                   = var.cicd_runner_project_id
  workload_identity_pool_id = "${var.repository_name}-pool"
  display_name              = "GitHub Actions WIF Pool"
  depends_on                = [google_project_service.cicd_apis]
}

resource "google_iam_workload_identity_pool_provider" "wif_provider" {
  project                            = var.cicd_runner_project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.wif_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "${var.repository_name}-provider"
  display_name                       = "GitHub OIDC Provider"
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
  attribute_mapping = {
    "google.subject" = "assertion.sub",
    "attribute.repository" = "assertion.repository",
  }
  attribute_condition = "attribute.repository == \"${var.repository_owner}/${var.repository_name}\""
}

resource "google_service_account_iam_member" "wif_user" {
  project              = var.cicd_runner_project_id
  service_account_id = google_service_account.cicd_runner_sa.name
  role                 = "roles/iam.workloadIdentityUser"
  member               = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.wif_pool.name}/attribute.repository/${var.repository_owner}/${var.repository_name}"
}

# --- Per-Environment Resources (Staging & Prod) ---

resource "google_project_service" "env_apis" {
  for_each = local.environments
  provider = google.each.key 

  project  = each.value.project_id
  for_each_api = toset(["run.googleapis.com", "artifactregistry.googleapis.com", "secretmanager.googleapis.com", "cloudbuild.googleapis.com"])
  service  = each.value.for_each_api
  disable_dependent_services = true
}

resource "google_service_account" "app_service_accounts" {
  for_each = local.environments
  provider = google.each.key

  project      = each.value.project_id
  account_id   = "${var.repository_name}-app-sa"
  display_name = "App Runner Service Account"
  depends_on   = [google_project_service.env_apis]
}

# Grant CICD service account permissions on the staging/prod projects
resource "google_project_iam_member" "cicd_permissions" {
  for_each = local.environments
  provider = google.each.key

  project = each.value.project_id
  for_each_role = toset(["roles/run.admin", "roles/cloudbuild.builds.builder", "roles/iam.serviceAccountUser", "roles/secretmanager.admin"])
  role    = each.value.for_each_role
  member  = "serviceAccount:${google_service_account.cicd_runner_sa.email}"
  depends_on = [google_project_service.env_apis]
}

# Create Artifact Registry repos in each environment
resource "google_artifact_registry_repository" "repos" {
  for_each = local.environments
  provider = google.each.key

  project       = each.value.project_id
  location      = var.gcp_region
  repository_id = "${var.repository_name}-repo"
  format        = "DOCKER"
  depends_on    = [google_project_service.env_apis]
}

# Create Cloud Run services in each environment
resource "google_cloud_run_v2_service" "services" {
  for_each = local.environments
  provider = google.each.key

  project             = each.value.project_id
  location            = var.gcp_region
  name                = "${var.repository_name}-main-app" 
  deletion_protection = false

  template {
    service_account = google_service_account.app_service_accounts[each.key].email
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
    }
  }
  depends_on = [google_project_service.env_apis]
}

# Allow public access to the services
resource "google_cloud_run_service_iam_member" "public_access" {
  for_each = google_cloud_run_v2_service.services
  provider = google[each.key]

  project  = each.value.project
  location = each.value.location
  service  = each.value.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}