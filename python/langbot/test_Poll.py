import unittest
import Firestore.Poll
from google.cloud import firestore

def snapshot(data) -> firestore.DocumentSnapshot:
    return firestore.DocumentSnapshot(
        None,
        data,
        True,
        None,
        None,
        None,
    )

class TestParse(unittest.TestCase):

    def test_empty(self):
        docs = []
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, -1)

    def test_unanswered(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 0,
                "correct_answers": 0,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, -1)

    def test_sole_correct_answered(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 1,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, -1)

    def test_sole_incorrect_answered(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 0,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, -1)

    def test_correct_incorrect_correct(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 1,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 3,
                "total_answers": 1,
                "correct_answers": 1,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, 2)

    def test_incorrect_correct_incorrect(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 1,
            }),
            snapshot({
                "term_index": 3,
                "total_answers": 1,
                "correct_answers": 0,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, 3)

    def test_same_index_first_incorrect_then_correct(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 1,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, 2)

    def test_same_index_first_correct_then_incorrect(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 1,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 0,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, 2)

    def test_same_index_first_incorrect_then_correct_but_not_last(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 1,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 1,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, 2)

    def test_same_index_first_correct_then_incorrect_but_not_last(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 1,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 1,
            }),
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 0,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, 2)

    def test_WhenMultipleOptions_ShouldGetLeastFrequent(self):
        docs = [
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 1,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 1,
            }),
            snapshot({
                "term_index": 3,
                "total_answers": 1,
                "correct_answers": 1,
            }),
            snapshot({
                "term_index": 1,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 0,
            }),
            snapshot({
                "term_index": 2,
                "total_answers": 1,
                "correct_answers": 0,
            }),
        ]
        actual = Firestore.Poll._get_min_correct_term_index(docs)
        self.assertEqual(actual, 3)

if __name__ == '__main__':
    unittest.main()