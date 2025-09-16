resource "google_secret_manager_secret" "db_password_secret" {
  project   = var.gcp_project_id
  secret_id = "db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password_secret.id
  secret_data = var.db_password
}

resource "google_sql_database_instance" "postgres_instance" {
  project          = var.gcp_project_id
  name             = "${var.gcp_project_id}-pg-instance"
  database_version = "POSTGRES_14"
  region           = var.gcp_region
  root_password    = var.db_password

  settings {
    tier = "db-g1-small"
  }

  # This is required for terraform to be able to destroy the instance.
  deletion_protection = false
}

resource "google_sql_database" "db" {
  project  = var.gcp_project_id
  instance = google_sql_database_instance.postgres_instance.name
  name     = "pdf_processing"
}
