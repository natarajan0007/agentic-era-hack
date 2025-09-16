terraform {
  backend "gcs" {
    bucket = "qwiklabs-gcp-02-b02e3ca6f413-terraform-state"
    prefix = "agentic-era-hack/dev"
  }
}
