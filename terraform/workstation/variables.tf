variable "project_id" {
  type        = string
  description = "The Google Cloud project ID to deploy to."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP Region."
}

variable "zone" {
  type        = string
  default     = "us-central1-a"
  description = "GCP Availability Zone."
}

variable "vm_name" {
  type        = string
  default     = "db-workstation"
  description = "The GCE instance name for the Workstation."
}

variable "machine_type" {
  type        = string
  default     = "e2-standard-4"
  description = "Machine type for the demo workstation."
}

variable "network_name" {
  type        = string
  default     = "default"
  description = "VPC network name."
}

variable "subnet_name" {
  type        = string
  default     = "default"
  description = "VPC subnet name."
}

variable "github_repo_url" {
  type        = string
  default     = "https://github.com/gopal03/db-demo.git"
  description = "The database demo repository URL to clone on startup."
}
