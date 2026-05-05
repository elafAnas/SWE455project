terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com"
  ])

  service            = each.value
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "repo" {
  depends_on = [google_project_service.apis]

  location      = var.region
  repository_id = var.repo_name
  format        = "DOCKER"
  description   = "Docker images for Student Assignment Tracker"
}

resource "google_service_account" "cloud_run_sa" {
  account_id   = "student-tracker-sa"
  display_name = "Student Tracker Cloud Run Service Account"
}

resource "google_project_iam_member" "firestore_access" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_cloud_run_v2_service" "assignment_api" {
  name     = "assignment-api"
  location = var.region

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = var.assignment_image

      ports {
        container_port = 8080
      }

      env {
        name  = "OVERDUE_SERVICE_URL"
        value = "https://overdue-service-ofb2xhz2nq-uc.a.run.app"
      }
    }
  }
}

resource "google_cloud_run_v2_service" "overdue_service" {
  name     = "overdue-service"
  location = var.region

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = var.overdue_image

      ports {
        container_port = 8080
      }

      env {
        name  = "ASSIGNMENT_API_URL"
        value = "https://assignment-api-ofb2xhz2nq-uc.a.run.app"
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "assignment_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.assignment_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "overdue_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.overdue_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}