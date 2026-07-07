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
  default     = "cloudsql-postgres-demo"
  description = "Cloud SQL instance ID."
}

variable "database_id" {
  type        = string
  default     = "postgres"
  description = "Initial database name."
}

variable "database_version" {
  type        = string
  default     = "POSTGRES_15"
  description = "Database version."
}

variable "tier" {
  type        = string
  default     = "db-f1-micro"
  description = "The machine tier for Cloud SQL."
}

variable "db_username" {
  type        = string
  default     = "postgres"
  description = "Database username."
}

variable "db_password" {
  type        = string
  default     = "postgres_password_123"
  description = "Database password."
}
