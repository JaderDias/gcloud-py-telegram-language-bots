import Constants
from Logger import logger

from google.cloud import firestore
from datetime import datetime
import sys

db = firestore.Client()

def create(
        language: str,
        chat_id: int,
        poll_id: int,
        correct_option_id: int,
        term: str,
        term_index: str,
) -> None:
    document_reference = db.document(Constants.POLL_COLLECTION, poll_id)
    document_reference.set({
        u"language": language,
        u"chat_id": chat_id,
        u"create_epoch": datetime.now().timestamp(),
        u"update_epoch": datetime.now().timestamp(),
        u"poll_id": poll_id,
        u"correct_option_id": correct_option_id,
        u"total_answers": 0,
        u"correct_answers": 0,
        u"term": term,
        u"term_index": term_index,
    })

def get_and_increment_answer_count(
        poll_id: int,
        options: list,
) -> dict:
    document_reference = db.document(Constants.POLL_COLLECTION, poll_id)
    document_snapshot = document_reference.get()
    obj = {
        "total_answers": 0,
        "update_epoch": datetime.now().timestamp(),
    }
    for i in range(len(options)):
        obj["total_answers"] += options[i]["voter_count"]
        if i == document_snapshot.get(u"correct_option_id"):
            obj["correct_answers"] = options[i]["voter_count"]
    logger.debug(obj)
    document_reference.update(obj)
    return document_snapshot.to_dict()

def get_min_correct_term_index(
        language: str,
        chat_id: int,
) -> int:
    collection = db.collection(Constants.POLL_COLLECTION)
    docs = collection\
        .where(u'language', u'==', language)\
        .where(u'chat_id', u'==', chat_id)\
        .order_by(u'create_epoch', direction=firestore.Query.DESCENDING)\
        .limit(100)
    return _get_min_correct_term_index(docs.get())

def _get_min_correct_term_index(
    docs: list
) -> int:
    if len(docs) == 0:
        return -1
    last_index = docs[0].get(u'term_index')
    last_correct_index = -1
    terms = {}
    for document_snapshot in docs:
        term_index = document_snapshot.get(u'term_index')
        correct_answers = document_snapshot.get(u"correct_answers")
        total_answers = document_snapshot.get(u"total_answers")
        if last_correct_index == -1\
                and total_answers > 0\
                and correct_answers == total_answers:
            last_correct_index = term_index
        term = terms.get(term_index)
        logger.debug(f'term_index {term_index}\ttotal {total_answers}\tcorrect {correct_answers}\tcreate epoch {document_snapshot.get(u"create_epoch")}')
        if term is None:
            terms[term_index] = document_snapshot.to_dict()
            terms[term_index]["total_quizes"] = 1
        else:
            term["total_quizes"] += 1
    min_correct_ratio = sys.maxsize
    min_correct_term_index = -1
    for term_index, value in terms.items():
        if value["total_answers"] == 0:
            continue
        if term_index == last_index or term_index == last_correct_index:
            continue
        ratio = (value["total_quizes"] * value["correct_answers"]) / value["total_answers"]
        if ratio < min_correct_ratio:
            min_correct_ratio = ratio
            min_correct_term_index = term_index
    logger.debug(f"\nlast_index {last_index}\nlast_correct_index {last_correct_index}\nmin correct ratio: {min_correct_ratio}")
    return min_correct_term_index