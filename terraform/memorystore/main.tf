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

resource "google_redis_instance" "redis" {
  name               = var.instance_id
  tier               = var.tier
  memory_size_gb     = var.memory_size_gb
  region             = var.region
  authorized_network = data.google_compute_network.network.id
}

output "db_host_ip" {
  value       = google_redis_instance.redis.host
  description = "The IP address of the Memorystore Redis instance"
}
