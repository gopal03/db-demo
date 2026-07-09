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

# 1. Provision the GCE Workstation VM (Private-only, no external public IP)
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

  # Automatically uses the pre-created default Compute Engine service account
  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

# 2. Create a Cloud Router in the target network/region
resource "google_compute_router" "router" {
  name    = "${var.vm_name}-router"
  network = var.network_name
  region  = var.region
}

# 3. Create a Cloud NAT Gateway attached to the Router
resource "google_compute_router_nat" "nat" {
  name                               = "${var.vm_name}-nat"
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# Outputs to help connection
output "ssh_connection_command" {
  value       = "gcloud compute ssh ${google_compute_instance.workstation_vm.name} --zone=${var.zone} --tunnel-through-iap -- -L 8501:localhost:8501 -L 8504:localhost:8504"
  description = "Run this command in your local terminal to SSH into the workstation and tunnel the dashboard portals."
}
