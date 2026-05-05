output "assignment_api_url" {
  description = "Assignment API Cloud Run URL"
  value       = google_cloud_run_v2_service.assignment_api.uri
}

output "overdue_service_url" {
  description = "Overdue Service Cloud Run URL"
  value       = google_cloud_run_v2_service.overdue_service.uri
}

output "artifact_registry_repo" {
  description = "Artifact Registry Docker repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repo_name}"
}
