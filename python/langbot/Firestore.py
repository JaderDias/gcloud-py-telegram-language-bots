import Constants
from Logger import logger

from google.cloud import firestore
from datetime import datetime

db = firestore.Client()

def get_language() -> str:
    collection = db.collection(Constants.LANGUAGE_COLLECTION)
    docs = collection.stream()
    for document_snapshot in docs:
        if document_snapshot.get(u"next_run_epoch") > datetime.now().timestamp():
            continue
        document_reference = db.document(Constants.LANGUAGE_COLLECTION, document_snapshot.get(u"id"))
        document_reference.update({
            u'last_run_epoch': datetime.now().timestamp(),
            u'next_run_epoch': datetime.now().timestamp() + 600,
        })
        global language
        language = document_snapshot.get(u"id")
        logger.info(f"got language {language}")
        return language
    return ""

def release_lock():
    document_reference = db.document(Constants.LANGUAGE_COLLECTION, language)
    document_reference.update({
        u'next_run_epoch': datetime.now().timestamp(),
    })

def get_subscriber(chat_id: int) -> firestore.DocumentReference:
    return db.document(Constants.WORD_SUBSCRIBER_COLLECTION, f"{language}{chat_id}")

def is_subscribed(document_snapshot: firestore.DocumentSnapshot) -> bool:
    if not document_snapshot.exists:
        return False
    return document_snapshot.get(u'next_publication_epoch') < datetime.max.timestamp()

def subscribe(chat_id: int, interval_s: int) -> dict:
    document_reference = get_subscriber(chat_id)
    document_snapshot = document_reference.get()
    publication_count = -1
    if document_snapshot.exists:
        publication_count = document_snapshot.get(u'publication_count')
        if document_snapshot.get(u'next_publication_epoch') < datetime.max.timestamp()\
                and document_snapshot.get(u'interval_s') == interval_s:
            return None
    obj = {
        u'language': language,
        u'chat_id': chat_id,
        u'created': int(datetime.now().timestamp()),
        u'interval_s': interval_s,
        u'next_publication_epoch': datetime.now().timestamp()+interval_s,
        u'publication_count': publication_count+1,
    }
    document_reference.set(obj)
    return obj

def next(chat_id: int) -> dict:
    document_reference = get_subscriber(chat_id)
    document_snapshot = document_reference.get()
    if not document_snapshot.exists:
        return None
    publication_count = document_snapshot.get(u'publication_count')
    obj = {
        u'language': language,
        u'chat_id': chat_id,
        u'interval_s': document_snapshot.get(u'interval_s'),
        u'publication_count': publication_count+1,
    }
    document_reference.update(obj)
    return obj

def unsubscribe(chat_id: int) -> bool:
    document_reference = get_subscriber(chat_id)
    document_snapshot = document_reference.get()
    if not is_subscribed(document_snapshot):
        return False
    document_reference.update({
        u'next_publication_epoch': datetime.max.timestamp(),
    })
    return True

def read() -> list:
    results = []
    collection = db.collection(Constants.WORD_SUBSCRIBER_COLLECTION)
    docs = collection\
        .where(u'language', u'==', language)\
        .where(u'next_publication_epoch', u'<', datetime.now().timestamp())\
        .stream()
    for document_snapshot in docs:
        result = {
            'chat_id': document_snapshot.get(u'chat_id'),
            'interval_s': document_snapshot.get(u'interval_s'),
            'publication_count': document_snapshot.get(u'publication_count'),
        }
        results.append(result)
        document_reference = get_subscriber(result['chat_id'])
        document_reference.update({
            u'last_publication_epoch': datetime.now().timestamp(),
            u'next_publication_epoch': datetime.now().timestamp() + result["interval_s"],
            u'publication_count': result["publication_count"] + 1,
        })
    return results
