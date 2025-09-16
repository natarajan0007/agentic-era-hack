
resource "google_artifact_registry_repository" "container_registry" {
  for_each = local.deploy_project_ids

  project       = each.value
  location      = var.region
  repository_id = "${var.project_name}-repo"
  format        = "DOCKER"
  description   = "Container registry for the agent in ${each.key}."
}

resource "google_cloud_run_v2_service" "agent_service" {
  for_each = local.deploy_project_ids

  project  = each.value
  name     = var.project_name
  location = var.region
  deletion_protection = false

  template {
    service_account = google_service_account.app_sa[each.key].email
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      ports {
        container_port = 8080
      }
    }
  }
}

resource "google_cloud_run_service_iam_member" "allow_public" {
  for_each = google_cloud_run_v2_service.agent_service

  project  = each.value.project
  location = each.value.location
  service  = each.value.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
