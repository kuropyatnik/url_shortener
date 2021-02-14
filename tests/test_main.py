import unittest
import ddt
import os, sys
import main



@ddt.ddt
class TestMain(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello(self):
        with main.app.test_client() as _app:
            res = _app.get('/')
            res_text = res.get_data(as_text=True)
            self.assertTrue("Your" in res_text)