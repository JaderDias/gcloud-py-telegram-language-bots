import Constants
from Logger import logger

from google.cloud import firestore
from datetime import datetime
import os

db = firestore.Client()

def get_subscriber(language:str, chat_id: int) -> firestore.DocumentReference:
    return db.document(Constants.SUBSCRIBER_COLLECTION, f"{language}{chat_id}")

def is_subscribed(document_snapshot: firestore.DocumentSnapshot) -> bool:
    if not document_snapshot.exists:
        return False
    return document_snapshot.get(u'next_publication_epoch') < datetime.max.timestamp()

def subscribe(language: str, chat_id: int, interval_s: int, is_quiz: bool) -> dict:
    document_reference = get_subscriber(language, chat_id)
    document_snapshot = document_reference.get()
    publication_count = -1
    if document_snapshot.exists:
        publication_count = document_snapshot.get(u'publication_count')
        if document_snapshot.get(u'next_publication_epoch') < datetime.max.timestamp() \
                and document_snapshot.get(u'interval_s') == interval_s \
                and document_snapshot.get(u'is_quiz') == is_quiz:
            return None
    obj = {
        u'language': language,
        u'is_quiz': is_quiz,
        u'chat_id': chat_id,
        u'created': int(datetime.now().timestamp()),
        u'interval_s': interval_s,
        u'next_publication_epoch': datetime.now().timestamp()+interval_s,
        u'publication_count': publication_count+1,
    }
    document_reference.set(obj)
    return obj

def _get_subscription(language: str, chat_id: int) -> tuple:
    document_reference = get_subscriber(language, chat_id)
    document_snapshot = document_reference.get()
    if document_snapshot.exists:
        return (document_reference, document_snapshot.to_dict())
    obj = {
        u'chat_id': chat_id,
        u'created': int(datetime.now().timestamp()),
        u'interval_s': 86400,
        u'is_quiz': False,
        u'language': language,
        u'next_publication_epoch': datetime.max.timestamp(),
        u'publication_count': 0,
    }
    return (document_reference, obj)

def get_subscription(language: str, chat_id: int) -> dict:
    (_, obj) = _get_subscription(language, chat_id)
    return obj

def get_subscription_and_update_count(language: str, chat_id: int) -> dict:
    (document_reference, obj) = _get_subscription(language, chat_id)
    obj[u'publication_count'] += 1
    document_reference.set(obj)
    return obj

def unsubscribe(language: str, chat_id: int) -> bool:
    document_reference = get_subscriber(language, chat_id)
    document_snapshot = document_reference.get()
    if not is_subscribed(document_snapshot):
        return False
    document_reference.update({
        u'next_publication_epoch': datetime.max.timestamp(),
    })
    return True

def get_pending_messages(language: str) -> list:
    results = []
    collection = db.collection(Constants.SUBSCRIBER_COLLECTION)
    docs = collection\
        .where(u'language', u'==', language)\
        .where(u'next_publication_epoch', u'<', datetime.now().timestamp())\
        .stream()
    for document_snapshot in docs:
        result = document_snapshot.to_dict()
        results.append(result)
        document_reference = get_subscriber(language, result['chat_id'])
        document_reference.update({
            u'last_publication_epoch': datetime.now().timestamp(),
            u'next_publication_epoch': datetime.now().timestamp() + result["interval_s"],
            u'publication_count': result["publication_count"] + 1,
        })
    return results
