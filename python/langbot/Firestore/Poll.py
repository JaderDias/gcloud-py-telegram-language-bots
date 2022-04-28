import Constants

from google.cloud import firestore
from datetime import datetime

db = firestore.Client()

def create(language: str,\
           chat_id: int,\
           poll_id: int,\
           correct_option_id: int,\
           term: str,\
           term_index: str) -> None:
    document_reference = db.document(Constants.POLL_COLLECTION, poll_id)
    document_reference.set({
        u"language": language,
        u"chat_id": chat_id,
        u"epoch": datetime.now().timestamp(),
        u"poll_id": poll_id,
        u"correct_option_id": correct_option_id,
        u"total_answers": 0,
        u"correct_answers": 0,
        u"term": term,
        u"term_index": term_index,
    })

def get_and_increment_answer_count(poll_id: int, options: list) -> dict:
    document_reference = db.document(Constants.POLL_COLLECTION, poll_id)
    document_snapshot = document_reference.get()
    obj = {
        "total_answers": 0,
    }
    for i in range(len(options)):
        obj["total_answers"] += options[i]["voter_count"]
        if i == document_snapshot.get(u"correct_option_id"):
            obj["correct_answers"] = options[i]["voter_count"]
    document_reference.update(obj)
    return document_snapshot.to_dict()

def get_min_correct_term_index(language: str, chat_id: int) -> dict:
    collection = db.collection(Constants.POLL_COLLECTION)
    docs = collection\
        .where(u'language', u'==', language)\
        .where(u'chat_id', u'==', chat_id)\
        .order_by(u'epoch')\
        .limit_to_last(100)
    terms = {}
    for document_snapshot in docs.get():
        term = document_snapshot.get(u'term')
        if term in terms.keys():
            terms[term]["correct_answers"] += document_snapshot.get(u"correct_answers")
            terms[term]["total_answers"] += document_snapshot.get(u"total_answers")
        else:
            terms[term] = document_snapshot.to_dict()
    min_correct_ratio = 2
    min_correct_term_index = -1
    for value in terms.values():
        ratio = value["correct_answers"] / value["total_answers"]
        if ratio < min_correct_ratio:
            min_correct_ratio = ratio
            min_correct_term_index = value["term_index"]
    return min_correct_term_index
    
    
