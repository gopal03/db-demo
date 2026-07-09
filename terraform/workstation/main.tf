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

# 1. Create a Service Account for the Workstation VM
resource "google_service_account" "workstation_sa" {
  account_id   = "db-workstation-sa"
  display_name = "Database Demo Workstation Service Account"
}

# 2. Grant Editor role to the Service Account for DB/GCP resources manipulation
resource "google_project_iam_member" "workstation_sa_editor" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.workstation_sa.email}"
}

# 3. Provision the GCE Workstation VM
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
    # No access_config block = No public IP address allocated. Only reachable via IAP.
  }

  metadata_startup_script = templatefile("${path.module}/startup.sh", {
    project_id      = var.project_id
    region          = var.region
    github_repo_url = var.github_repo_url
  })

  service_account {
    email  = google_service_account.workstation_sa.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  depends_on = [
    google_project_iam_member.workstation_sa_editor
  ]
}

# 4. Open SSH firewall port ONLY to Google IAP secure proxy range
resource "google_compute_firewall" "allow_ssh_from_iap" {
  name          = "allow-ssh-from-iap-to-workstation"
  network       = var.network_name
  source_ranges = ["35.235.240.0/20"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  target_tags = ["db-workstation"]
}

# Outputs to help CEs connect easily
output "ssh_connection_command" {
  value       = "gcloud compute ssh ${google_compute_instance.workstation_vm.name} --zone=${var.zone} --tunnel-through-iap -- -L 8501:localhost:8501 -L 8504:localhost:8504"
  description = "Run this command in your local terminal to SSH into the workstation and tunnel the dashboard portals."
}
