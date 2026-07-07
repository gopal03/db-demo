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
  description = "Zone for the Bigtable cluster."
}

variable "instance_id" {
  type        = string
  default     = "demo-instance-retail"
  description = "Bigtable Instance ID."
}

variable "cluster_id" {
  type        = string
  default     = "demo-cluster-retail"
  description = "Bigtable Cluster ID."
}

variable "num_nodes" {
  type        = number
  default     = 1
  description = "Number of Bigtable nodes (if cluster is standard)."
}

variable "storage_type" {
  type        = string
  default     = "SSD"
  description = "Bigtable storage type (SSD or HDD)."
}
