resource "google_storage_bucket" "cloudbuild_logs" {
  project  = var.gcp_project_id
  name     = "${var.gcp_project_id}-cloudbuild-logs"
  location = "US"

  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "cloudbuild_logs_writer" {
  bucket = google_storage_bucket.cloudbuild_logs.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cicd_runner_sa.email}"
}

data "google_project" "project" {}

resource "google_storage_bucket_iam_member" "cloudbuild_sa_logs_writer" {
  bucket = google_storage_bucket.cloudbuild_logs.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}