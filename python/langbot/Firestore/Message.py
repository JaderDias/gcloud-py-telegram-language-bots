import Constants
from Logger import logger

from google.cloud import firestore
from datetime import datetime
import os

db = firestore.Client()

def add(language: str, chat_id: int, is_answer: bool) -> None:
    epoch = datetime.now().timestamp()
    document_reference = db.document(Constants.MESSAGE_COLLECTION, f"{language}_{chat_id}_{epoch}")
    document_reference.set({
        u"language": language,
        u"chat_id": chat_id,
        u"epoch": epoch,
        u"is_answer": is_answer,
    })

def is_answered(language: str, chat_id: int) -> bool:
    collection = db.collection(Constants.MESSAGE_COLLECTION)
    query = collection\
        .where(u'language', u'==', language)\
        .where(u'chat_id', u'==', chat_id)\
        .order_by(u'epoch')\
        .limit_to_last(1)
    results = query.get()
    if len(results) == 0:
        return True
    document_snapshot = results[1]
    return document_snapshot.get(u'is_answer')
