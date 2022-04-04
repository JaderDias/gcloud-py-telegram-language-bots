resource "google_storage_bucket_object" "language_dictionary" {
  name   = "${var.language_code}.csv"
  bucket = var.bucket_name
  source = abspath("../${var.language_code}.csv")
}

resource "google_firestore_document" "language_doc" {
  project     = var.project
  collection  = "Language"
  document_id = var.language_code
  fields      = "{\"id\":{\"stringValue\":\"${var.language_code}\"},\"next_run_epoch\":{\"integerValue\":\"0\"}}"
}

module "language_token" {
    source     = "../secret"
    acessor    = var.acessor
    id         = "telegram-${var.language_code}-token"
    value      = var.secret_value
}