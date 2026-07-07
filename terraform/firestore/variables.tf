variable "project_id" {
  type        = string
  description = "The Google Cloud project ID to deploy to."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP Region."
}

variable "database_id" {
  type        = string
  default     = "firestore-demo-db"
  description = "Firestore Database ID. Use '(default)' or a custom name."
}

variable "type" {
  type        = string
  default     = "FIRESTORE_NATIVE"
  description = "The type of the database: FIRESTORE_NATIVE or DATASTORE_MODE."
}

variable "location_id" {
  type        = string
  default     = "nam5"
  description = "The location of the database."
}
