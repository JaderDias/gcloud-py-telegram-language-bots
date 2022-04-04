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

module "langbot" {
  source               = "./modules/function"
  project              = var.project
  function_name        = "langbot"
  function_entry_point = "app"
  pubsub_topic_name    = "langbot_trigger"
  source_bucket_name   = google_storage_bucket.bucket.name
  source_dir           = abspath("../python/langbot")
  timeout              = 540 # 9 minutes
  depends_on = [
    google_app_engine_application.app,
  ]
}

module "de_language" {
    source        = "./modules/language"
    acessor       = module.langbot.service_account_email
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "de"
    project       = var.project
    secret_value  = var.de_token
    depends_on = [
        google_storage_bucket.bucket,
        module.langbot,
    ]
}

module "es_language" {
    source        = "./modules/language"
    acessor       = module.langbot.service_account_email
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "es"
    project       = var.project
    secret_value  = var.es_token
    depends_on = [
        google_storage_bucket.bucket,
        module.langbot,
    ]
}

module "fr_language" {
    source        = "./modules/language"
    acessor       = module.langbot.service_account_email
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "fr"
    project       = var.project
    secret_value  = var.fr_token
    depends_on = [
        google_storage_bucket.bucket,
        module.langbot,
    ]
}

module "it_language" {
    source        = "./modules/language"
    acessor       = module.langbot.service_account_email
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "it"
    project       = var.project
    secret_value  = var.it_token
    depends_on = [
        google_storage_bucket.bucket,
        module.langbot,
    ]
}

module "nl_language" {
    source        = "./modules/language"
    acessor       = module.langbot.service_account_email
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "nl"
    project       = var.project
    secret_value  = var.nl_token
    depends_on = [
        google_storage_bucket.bucket,
        module.langbot,
    ]
}

module "pt_language" {
    source        = "./modules/language"
    acessor       = module.langbot.service_account_email
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "pt"
    project       = var.project
    secret_value  = var.pt_token
    depends_on = [
        google_storage_bucket.bucket,
        module.langbot,
    ]
}

module "sh_language" {
    source        = "./modules/language"
    acessor       = module.langbot.service_account_email
    bucket_name   = google_storage_bucket.bucket.name
    language_code = "sh"
    project       = var.project
    secret_value  = var.sh_token
    depends_on = [
        google_storage_bucket.bucket,
        module.langbot,
    ]
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

resource "google_cloud_scheduler_job" "langbot_job" {
  name        = "langbot_job"
  description = "triggers langbot every minute"
  schedule    = "* * * * *"

  pubsub_target {
    topic_name = "projects/${var.project}/topics/langbot_trigger"
    data       = base64encode("test")
  }
  depends_on = [
    module.de_language,
    module.es_language,
    module.fr_language,
    module.it_language,
    module.nl_language,
    module.pt_language,
    module.sh_language,
    google_firestore_index.subscriber_language,
  ]
}