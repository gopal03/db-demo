variable "project_id" {
  type        = string
  description = "The Google Cloud project ID to deploy to."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP Region."
}

variable "instance_id" {
  type        = string
  default     = "redis-demo-instance"
  description = "Memorystore (Redis) instance ID."
}

variable "tier" {
  type        = string
  default     = "BASIC"
  description = "Service tier: BASIC or STANDARD_HA."
}

variable "memory_size_gb" {
  type        = number
  default     = 1
  description = "Memory capacity in GiB."
}

variable "network_name" {
  type        = string
  default     = "default"
  description = "The name of the VPC network to connect to."
}
