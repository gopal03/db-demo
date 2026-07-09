terraform {
  required_version = ">= 1.0.0"
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

# Provision the GCE Workstation VM using the project's default service account
resource "google_compute_instance" "workstation_vm" {
  name         = var.vm_name
  machine_type = var.machine_type
  zone         = var.zone

  tags = ["db-workstation"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 50 # 50GB space for databases configuration and data
    }
  }

  network_interface {
    network    = var.network_name
    subnetwork = var.subnet_name
  }

  metadata_startup_script = templatefile("${path.module}/startup.sh", {
    project_id      = var.project_id
    region          = var.region
    github_repo_url = var.github_repo_url
  })

  # Automatically uses the pre-created default Compute Engine service account
  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

# Outputs to help connection
output "ssh_connection_command" {
  value       = "gcloud compute ssh ${google_compute_instance.workstation_vm.name} --zone=${var.zone} --tunnel-through-iap -- -L 8501:localhost:8501 -L 8504:localhost:8504"
  description = "Run this command in your local terminal to SSH into the workstation and tunnel the dashboard portals."
}
