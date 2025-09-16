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
  secret_data = templatefile("${path.module}/../../../services/toolbox/tools.yaml.tftpl", {
    gcp_project_id   = var.gcp_project_id
    gcp_region       = var.gcp_region
    db_instance_name = google_sql_database_instance.postgres_instance.name
    db_password      = var.db_password
  })
}

# Create a Cloud Run service for each application
resource "google_cloud_run_v2_service" "services" {
  for_each = toset(var.service_names)

  project             = var.gcp_project_id
  location            = var.gcp_region
  name                = each.key
  deletion_protection = false

  template {
    annotations = {
      "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.postgres_instance.connection_name
    }
    service_account = google_service_account.app_service_accounts[each.key].email

    containers {
      image = each.key == "toolbox" ? "us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest" : "us-docker.pkg.dev/cloudrun/container/hello"
      
      command = null
      args    = each.key == "toolbox" ? ["--address", "0.0.0.0", "--port", "5000"] : null

      ports {
        container_port = each.key == "nextjs-frontend" ? 3000 : (each.key == "toolbox" ? 5000 : 8080)
      }

      dynamic "env" {
        for_each = each.key == "toolbox" ? [1] : []
        content {
          name = "DB_PASSWORD"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.db_password_secret.secret_id
              version = "latest"
            }
          }
        }
      }

      dynamic "volume_mounts" {
        for_each = each.key == "toolbox" ? [1] : []
        content {
          name       = "config-volume"
          mount_path = "/app"
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

# Grant the toolbox service account access to the secret
resource "google_project_iam_member" "toolbox_secret_accessor" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.app_service_accounts["toolbox"].email}"
}

# Grant the toolbox service account access to Cloud SQL
resource "google_project_iam_member" "toolbox_sql_client" {
  project = var.gcp_project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.app_service_accounts["toolbox"].email}"
}

# --- CICD Resources (Created only in the Prod/CICD Project) ---

resource "google_service_account" "cicd_runner_sa" {
  project      = var.gcp_project_id # Assumes prod project is the cicd project
  account_id   = "ae-cicd-sa-prod"
  display_name = "CICD Runner Service Account Prod"
  depends_on   = [google_project_service.apis]
}

resource "google_iam_workload_identity_pool" "wif_pool" {
  project                   = var.gcp_project_id
  workload_identity_pool_id = "ae-pool-prod"
  display_name              = "GitHub Actions WIF Pool Prod"
  depends_on                = [google_project_service.apis]
  lifecycle {
    prevent_destroy = true
    ignore_changes  = all
  }
}

resource "google_iam_workload_identity_pool_provider" "wif_provider" {
  project                            = var.gcp_project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.wif_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "ae-provider-prod"
  display_name                       = "GitHub OIDC Provider Prod"
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
  attribute_mapping = {
    "google.subject"       = "assertion.sub",
    "attribute.repository" = "assertion.repository",
  }
  attribute_condition = "attribute.repository == \"${var.repository_owner}/${var.repository_name}\""
}

resource "google_service_account_iam_member" "wif_user" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role                 = "roles/iam.workloadIdentityUser"
  member               = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.wif_pool.name}/attribute.repository/${var.repository_owner}/${var.repository_name}"
}

# Grant CICD service account permissions on this project
resource "google_project_iam_member" "cicd_permissions" {
  project = var.gcp_project_id
  for_each = toset(["roles/run.admin", "roles/cloudbuild.builds.builder", "roles/iam.serviceAccountUser", "roles/secretmanager.admin"])
  role    = each.value
  member  = "serviceAccount:${google_service_account.cicd_runner_sa.email}"
  depends_on = [google_project_service.apis]
}

# For PRODUCTION environment - same fixes
resource "google_project_iam_member" "prod_cicd_logging_viewer" {
  project = var.prod_project_id
  role    = "roles/logging.viewer"
  member  = "serviceAccount:ae-cicd-sa-prod@${var.prod_project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "prod_cicd_cloudbuild_viewer" {
  project = var.prod_project_id
  role    = "roles/cloudbuild.builds.viewer"
  member  = "serviceAccount:ae-cicd-sa-prod@${var.prod_project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "prod_cicd_cloudbuild_editor" {
  project = var.prod_project_id
  role    = "roles/cloudbuild.builds.editor"
  member  = "serviceAccount:ae-cicd-sa-prod@${var.prod_project_id}.iam.gserviceaccount.com"
}