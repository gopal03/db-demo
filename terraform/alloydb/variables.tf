variable "project_id" {
  type        = string
  description = "The Google Cloud project ID to deploy to."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP Region."
}

variable "cluster_id" {
  type        = string
  default     = "alloydb-demo-cluster"
  description = "AlloyDB Cluster ID."
}

variable "instance_id" {
  type        = string
  default     = "alloydb-demo-primary"
  description = "AlloyDB Primary Instance ID."
}

variable "database_id" {
  type        = string
  default     = "postgres"
  description = "Initial database name to configure."
}

variable "network_name" {
  type        = string
  default     = "default"
  description = "VPC network name for AlloyDB connectivity."
}
