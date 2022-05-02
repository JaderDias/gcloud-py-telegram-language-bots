locals {
    timestamp = formatdate("YYMMDDhhmmss", timestamp())
}

# Compress source code
data "archive_file" "source" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "/tmp/function-${var.function_name}-${local.timestamp}.zip"
}

# Add source code zip to bucket
resource "google_storage_bucket_object" "zip" {
  # Append file MD5 to force bucket to be recreated
  name   = "source.zip#${data.archive_file.source.output_md5}"
  bucket = var.source_bucket_name
  source = data.archive_file.source.output_path
}

# Create Cloud Function
resource "google_cloudfunctions_function" "function" {
  name                  = var.function_name
  runtime               = var.runtime
  available_memory_mb   = var.available_memory_mb
  max_instances         = var.max_instances
  source_archive_bucket = var.source_bucket_name
  source_archive_object = google_storage_bucket_object.zip.name
  environment_variables = {
    LANGUAGE_CODE = var.language_code
  }
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = var.pubsub_topic_name
  }
  entry_point = var.function_entry_point
  timeout = var.timeout
}