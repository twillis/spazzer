"""
test scanner
"""
import unittest
from common import TestDB
from spazzer.collection.scanner import Scanner

#FIXME
DIR = "/home/twillis/music/mp3s/S/Swans"


class TestScanner(unittest.TestCase):
    def setUp(self):
        self.db = TestDB()

    def tearDown(self):
        self.db.tearDown()

    def test_scan(self):
        scanner = Scanner(dirs=[DIR, ])
        scanner()
