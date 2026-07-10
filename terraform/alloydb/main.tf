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

data "google_compute_network" "network" {
  name = var.network_name
}

resource "google_alloydb_cluster" "cluster" {
  cluster_id = var.cluster_id
  location   = var.region
  network_config {
    network = data.google_compute_network.network.id
  }

  initial_user {
    password = "alloydb_password_123"
  }
}

resource "google_alloydb_instance" "instance" {
  cluster       = google_alloydb_cluster.cluster.name
  instance_id   = var.instance_id
  instance_type = "PRIMARY"

  machine_config {
    cpu_count = 2
  }
}

output "db_host_ip" {
  value       = google_alloydb_cluster.cluster.ip_address
  description = "The private IP address of the AlloyDB cluster"
}
