module "langbot" {
    source               = "../function"
    project              = var.project
    function_name        = "${var.language_code}_bot"
    function_entry_point = "app"
    language_code        = var.language_code
    pubsub_topic_name    = "${var.language_code}_bot_trigger"
    source_bucket_name   = var.bucket_name
    source_dir           = abspath("../python/langbot")
    timeout              = 540 # 9 minutes
}

resource "google_storage_bucket_object" "language_dictionary" {
    name   = "${var.language_code}.csv"
    bucket = var.bucket_name
    source = abspath("../${var.language_code}.csv")
}

module "language_token" {
    source     = "../secret"
    acessor    = module.langbot.service_account_email
    id         = "telegram-${var.language_code}-token"
    value      = var.secret_value
    depends_on = [
        module.langbot,
    ]
}

resource "google_cloud_scheduler_job" "langbot_job" {
    name        = "${var.language_code}_bot_job"
    description = "triggers ${var.language_code}_bot every 5th minute"
    schedule    = "*/5 * * * *"
    pubsub_target {
        topic_name = "projects/${var.project}/topics/${var.language_code}_bot_trigger"
        data       = base64encode("test")
    }
    depends_on = [
        module.langbot,
        module.language_token,
        google_storage_bucket_object.language_dictionary
    ]
}