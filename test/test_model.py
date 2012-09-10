"""
scanner unit tests
"""
from common import TestDB
import unittest
import datetime
from spazzer.collection.model import FileRecord
from spazzer.collection import manage

UNICODE_ID3 = {'album': u'Me\xf0 su\xf0 \xed eyrum vi\xf0 spilum end',
               'artist': u'Sigur R\xf3s',
               'create_date': datetime.datetime(2012, 9, 9, 9, 14, 43),
               'year': u'2008',
               'file_name': u'test.mp3',
               'modify_date': datetime.datetime(2009, 12, 15, 15, 8, 47),
               'title': u'Vi\xf0 spilum endalaust',
               'track': u'04'}


class TestModel(unittest.TestCase):
    def setUp(self):
        self.db = TestDB()

    def tearDown(self):
        self.db.tearDown()

    def test_unicode(self):
        r = FileRecord(**UNICODE_ID3)
        s = manage.meta._s()
        s.add(r)
        s.commit()
