import Constants
from Logger import logger

from google.cloud import storage
from datetime import datetime, timedelta
import io

storage_client = storage.Client()

def get_blob(blob_name: str) -> storage.blob:
    bucket = storage_client.get_bucket(f"{storage_client.project}-bucket")
    return bucket.blob(blob_name)

def get_dictionary(language: str) -> None:
    blob = get_blob(f"{language}.csv")
    blob.download_to_filename(f"/tmp/{language}")