resource "google_secret_manager_secret" "secret" {
  secret_id = "${var.id}"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "secret-version" {
  secret = google_secret_manager_secret.secret.id
  secret_data = "${var.value}"
}

data "google_iam_policy" "acessor" {
  binding {
    role = "roles/secretmanager.secretAccessor"
    members = [
      "serviceAccount:${var.acessor}",
    ]
  }
}

resource "google_secret_manager_secret_iam_policy" "policy" {
  project = google_secret_manager_secret.secret.project
  secret_id = google_secret_manager_secret.secret.secret_id
  policy_data = data.google_iam_policy.acessor.policy_data
}