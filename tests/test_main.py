import ddt
import json
import unittest
from unittest import mock
from sqlalchemy import delete
from sqlalchemy.sql.functions import count
from sqlalchemy.engine import ResultProxy
from collections import namedtuple

import main
from helpers.db_connector import create_test_table
from helpers.consts import MAX_RECORDS
from tests.data.sample import TABLE_DATA


@ddt.ddt
class TestMain(unittest.TestCase):

    test_table = None
    real_table = main.table

    @classmethod
    def setUpClass(cls):
        """
        Prepares test table, and replaces real table on it during testing
        """
        cls.test_table = create_test_table(main.db, main.table)
        main.table = cls.test_table

    @classmethod
    def tearDownClass(cls):
        """
        Resets real table and removes testing table at all
        """
        main.table = cls.real_table
        cls.test_table.drop(main.db)

    def setUp(self):
        pass

    def tearDown(self):
        with main.db.connect() as conn:
            conn.execute(main.table.delete())
    
    @ddt.data(
        (
            None,
            "Request body isn't JSON!",
            400
        ),
        (
            {
                "fake_param": 15
            },
            "Request has not all required fields!",
            400
        ),
        (
            {
                "url": "        ",
                "lifetime": 15
            },
            "URL field is empty!",
            400
        ),
        (
            {
                "url": "wrong_url",
            },
            "URL isn't valid!",
            400
        ),
        (
            {
                "url": "https://www.google.com.ua/",
                "lifeterm": "156"
            },
            "Lifeterm isn't integer!",
            400
        ),
        (
            {
                "url": "https://www.google.com.ua/",
                "lifeterm": 5000
            },
            "Lifeterm has to be in range [1, 365] days!",
            400
        ),
        (
            {
                "url": "https://www.google.com.ua/",
                "lifeterm": 156
            },
            "URL was shorted!",
            201
        )
    )
    @ddt.unpack
    def test_create_fields_validation(self, req_body, exp_resp_text, exp_code):
        """
        Test checks that all fields validators work as expected
        """
        with main.app.test_client() as _app:
            if req_body is None:
                response = _app.post(
                    '/create_url',
                    data=req_body, 
                    content_type='text/html'
                )
            else:
                response = _app.post(
                    '/create_url', 
                    data=json.dumps(req_body),
                    content_type='application/json'
                )
            self.assertTrue(exp_resp_text in response.get_data(as_text=True))
            self.assertEqual(exp_code, response.status_code)

    def test_create_short_link(self):
        """
        Inserts some records to DB. Ensures, that old one will be removed
        And also checks, that new record will have correct hash
        """
        with main.db.connect() as conn:
            # Paste sampling data
            conn.execute(
                main.table.insert(),
                TABLE_DATA
            )
        
        # Patch hash, to ensure, that there will be shift
        with mock.patch("main.encrypt_url", return_value="aaaaaabc"):
            # Sends creation request
            with main.app.test_client() as _app:
                response = _app.post(
                    '/create_url', 
                    data=json.dumps({
                        "url": "https://www.google.com.ua/"
                    }),
                    content_type='application/json'
                )
                self.assertEqual(201, response.status_code)

        # Check in DB, that everything was set correctly
        with main.db.connect() as conn:  
            # There is no old expired link
            res_with_old_link = conn.execute(
                main.table.select().where(main.table.c.short_url == "dddddd"))
            self.assertEqual(res_with_old_link.rowcount, 0)

            # There is a new record, with shifted short_link
            res_with_shifted_link = conn.execute(
                main.table.select().where(main.table.c.short_url == "aaaabc"))
            self.assertEqual(res_with_shifted_link.rowcount, 1)
    
    def test_links_limit(self):
        """
        Ensures, that application won't add a record, if there will
        be exceeded limit of records
        """
        # Patch MAX_RECORDS count
        with mock.patch.object(main, "MAX_RECORDS", 0):
            # Sends creation request
            with main.app.test_client() as _app:
                response = _app.post(
                    '/create_url', 
                    data=json.dumps({
                        "url": "https://www.google.com.ua/"
                    }),
                    content_type='application/json'
                )
                self.assertEqual(409, response.status_code)
