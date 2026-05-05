variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Deployment region"
  type        = string
  default     = "us-central1"
}

variable "repo_name" {
  description = "Artifact Registry repo name"
  type        = string
  default     = "student-tracker-repo"
}

variable "assignment_image" {
  description = "Docker image for assignment API"
  type        = string
}

variable "overdue_image" {
  description = "Docker image for overdue service"
  type        = string
}