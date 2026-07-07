terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_spanner_instance" "spanner_instance" {
  name             = var.instance_id
  config           = "projects/${var.project_id}/instanceConfigs/${var.instance_config}"
  display_name     = var.instance_id
  edition          = var.edition
  processing_units = var.processing_units > 0 ? var.processing_units : null
  node_count       = var.processing_units == 0 ? var.node_count : null
}

resource "google_spanner_database" "spanner_database" {
  instance = google_spanner_instance.spanner_instance.name
  name     = var.database_id
  lifecycle {
    ignore_changes = [ddl]
  }
}
