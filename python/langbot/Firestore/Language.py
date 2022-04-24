import Constants
from Logger import logger

from google.cloud import firestore
from datetime import datetime
import os

db = firestore.Client()

def get() -> str:
    language = os.getenv('LANGUAGE_CODE')
    logger.info(f"Language: {language}")
    document_reference = db.document(Constants.LANGUAGE_COLLECTION, language)
    document_snapshot = document_reference.get()
    if document_snapshot.exists:
        obj = document_snapshot.to_dict()
        logger.info(obj)
        if document_snapshot.get(u"next_run_epoch") > datetime.now().timestamp():
            return ""
    obj = {
        u"id": language,
        u"last_run_epoch": datetime.now().timestamp(),
        u"next_run_epoch": datetime.now().timestamp() + 600,
    }
    logger.info(obj)
    document_reference.set(obj)
    return language

def release_lock(language: str):
    document_reference = db.document(Constants.LANGUAGE_COLLECTION, language)
    document_reference.update({
        u'next_run_epoch': datetime.now().timestamp(),
    })