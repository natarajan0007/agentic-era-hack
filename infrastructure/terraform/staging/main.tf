# Enable necessary Google Cloud APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
  ])
  project                    = var.gcp_project_id
  service                    = each.key
  disable_dependent_services = true
}

# Create a dedicated service account for each service
resource "google_service_account" "app_service_accounts" {
  for_each = toset(var.service_names)

  project      = var.gcp_project_id
  account_id   = "${each.key}-sa"
  display_name = "Service Account for ${each.key}"
  depends_on   = [google_project_service.apis]
}

# Create Artifact Registry repositories for services built from source
resource "google_artifact_registry_repository" "repos" {
  for_each = toset(["adk-agent", "fastapi-backend", "nextjs-frontend"])

  project       = var.gcp_project_id
  location      = var.gcp_region
  repository_id = "${each.key}-repo"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

# Store the toolbox config file in Secret Manager
resource "google_secret_manager_secret" "toolbox_config_secret" {
  project   = var.gcp_project_id
  secret_id = "toolbox-tools-yaml"

  replication {
    auto {}
  }
  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "toolbox_config_version" {
  secret      = google_secret_manager_secret.toolbox_config_secret.id
  secret_data = file("${path.module}/../../../services/toolbox/tools.yaml")
}

# Create a Cloud Run service for each application
resource "google_cloud_run_v2_service" "services" {
  for_each = toset(var.service_names)

  project             = var.gcp_project_id
  location            = var.gcp_region
  name                = each.key
  deletion_protection = false

  template {
    service_account = google_service_account.app_service_accounts[each.key].email

    containers {
      image = each.key == "toolbox" ? "us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest" : "us-docker.pkg.dev/cloudrun/container/hello"
      
      command = each.key == "toolbox" ? ["toolbox"] : null
      args    = each.key == "toolbox" ? ["--tools-file", "/config/tools.yaml", "--address", "0.0.0.0"] : null

      ports {
        container_port = each.key == "nextjs-frontend" ? 3000 : (each.key == "toolbox" ? 5000 : 8080)
      }

      dynamic "volume_mounts" {
        for_each = each.key == "toolbox" ? [1] : []
        content {
          name       = "config-volume"
          mount_path = "/config"
        }
      }
    }

    dynamic "volumes" {
      for_each = each.key == "toolbox" ? [1] : []
      content {
        name = "config-volume"
        secret {
          secret = google_secret_manager_secret.toolbox_config_secret.secret_id
          items {
            path    = "tools.yaml"
            version = "latest"
          }
        }
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# Grant public access to the Cloud Run services
resource "google_cloud_run_service_iam_member" "public_access" {
  for_each = google_cloud_run_v2_service.services

  project  = each.value.project
  location = each.value.location
  service  = each.value.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
