import unittest

from ..utils import UserMistake, get_id

class GetIdTest(unittest.TestCase):
    def test_good_doi(self):
        dep_id = get_id('10.5281/zenodo.3357455')
        self.assertEqual(dep_id, '3357455') 

    def test_empty_doi(self):
        with self.assertRaises(Exception): get_id('')

#def setUp(self):
#def tearDown(self):
