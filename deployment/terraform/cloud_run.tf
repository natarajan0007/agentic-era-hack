
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

resource "google_artifact_registry_repository" "container_registry" {
  project       = var.prod_project_id
  location      = var.region
  repository_id = "${var.project_name}-repo"
  format        = "DOCKER"
  description   = "Container registry for the agent."
}

resource "google_cloud_run_v2_service" "agent_service" {
  project  = var.prod_project_id
  name     = var.project_name
  location = var.region

  template {
    service_account = google_service_account.app_sa.email
    containers {
      image = "${var.region}-docker.pkg.dev/${var.prod_project_id}/${google_artifact_registry_repository.container_registry.repository_id}/${var.project_name}:latest"
      ports {
        container_port = 8080
      }
    }
  }
}

resource "google_cloud_run_service_iam_member" "allow_public" {
  project  = google_cloud_run_v2_service.agent_service.project
  location = google_cloud_run_v2_service.agent_service.location
  service  = google_cloud_run_v2_service.agent_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
