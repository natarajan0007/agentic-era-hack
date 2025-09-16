resource "random_password" "db_password" {
  length           = 16
  special          = false
}

resource "google_secret_manager_secret" "db_password_secret" {
  project   = var.gcp_project_id
  secret_id = "db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password_secret.id
  secret_data = random_password.db_password.result
}

resource "google_sql_database_instance" "postgres_instance" {
  project          = var.gcp_project_id
  name             = "${var.gcp_project_id}-pg-instance"
  database_version = "POSTGRES_14"
  region           = var.gcp_region

  settings {
    tier = "db-g1-small"
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0" # WARNING: This allows all IPs. Not for production use.
      }
    }
  }

  # This is required for terraform to be able to destroy the instance.
  deletion_protection = false
}

resource "google_sql_database" "db" {
  project  = var.gcp_project_id
  instance = google_sql_database_instance.postgres_instance.name
  name     = "pdf_processing"
}

resource "google_sql_user" "db_user" {
  project  = var.gcp_project_id
  instance = google_sql_database_instance.postgres_instance.name
  name     = "postgres"
  password = random_password.db_password.result
}
