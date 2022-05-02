provider "google" {
  project = var.project
  region  = var.region
}

resource "google_app_engine_application" "app" {
  project       = var.project
  location_id   = var.location_id
  database_type = "CLOUD_FIRESTORE"
}

resource "google_storage_bucket" "bucket" {
  name     = "${var.project}-bucket"
  location = "US"
}

resource "google_firestore_index" "subscriber_language" {
  project    = var.project
  collection = "Subscriber"
  fields {
    field_path = "language"
    order      = "ASCENDING"
  }
  fields {
    field_path = "next_publication_epoch"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "poll_language_chat_epoch" {
  project    = var.project
  collection = "Poll"
  fields {
    field_path = "language"
    order      = "ASCENDING"
  }
  fields {
    field_path = "chat_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "create_epoch"
    order      = "DESCENDING"
  }
}

module "nl_language" {
    source        = "./modules/language"
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "nl"
    project       = var.project
    secret_value  = var.nl_token
    depends_on = [
        google_app_engine_application.app,
        google_storage_bucket.bucket,
        google_firestore_index.subscriber_language,
        google_firestore_index.poll_language_chat_epoch,
    ]
}

module "pt_language" {
    source        = "./modules/language"
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "pt"
    project       = var.project
    secret_value  = var.pt_token
    depends_on = [
        google_app_engine_application.app,
        google_storage_bucket.bucket,
        google_firestore_index.subscriber_language,
        google_firestore_index.poll_language_chat_epoch,
    ]
}

module "sh_language" {
    source        = "./modules/language"
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "sh"
    project       = var.project
    secret_value  = var.sh_token
    depends_on = [
        google_app_engine_application.app,
        google_storage_bucket.bucket,
        google_firestore_index.subscriber_language,
        google_firestore_index.poll_language_chat_epoch,
    ]
}