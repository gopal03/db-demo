variable "project_id" {
  type        = string
  description = "The Google Cloud project ID to deploy to."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP Region."
}

variable "instance_config" {
  type        = string
  default     = "regional-us-central1"
  description = "Spanner instance config."
}

variable "instance_id" {
  type        = string
  default     = "demo-instance-security"
  description = "Spanner instance ID."
}

variable "database_id" {
  type        = string
  default     = "spanner-graph-demo-db-security"
  description = "Spanner database ID."
}

variable "edition" {
  type        = string
  default     = "ENTERPRISE"
  description = "Spanner Edition (ENTERPRISE / ENTERPRISE_PLUS)."
}

variable "node_count" {
  type        = number
  default     = 1
  description = "Number of Spanner nodes."
}

variable "processing_units" {
  type        = number
  default     = 0
  description = "Processing units (if > 0, node_count is ignored)."
}
