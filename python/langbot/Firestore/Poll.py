import Constants

from google.cloud import firestore
from datetime import datetime

db = firestore.Client()

def create(language: str,\
           chat_id: int,\
           poll_id: int,\
           term: str) -> None:
    document_reference = db.document(Constants.POLL_COLLECTION, poll_id)
    document_reference.set({
        u"language": language,
        u"chat_id": chat_id,
        u"epoch": datetime.now().timestamp(),
        u"poll_id": poll_id,
        u"answer_count": 0,
        u"term": term,
    })

def get_and_increment_answer_count(poll_id: int) -> dict:
    document_reference = db.document(Constants.POLL_COLLECTION, poll_id)
    document_snapshot = document_reference.get()
    document_reference.update({
        u"answer_count": document_snapshot.get(u"answer_count") + 1,
    })
    return document_snapshot.to_dict()