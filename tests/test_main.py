import unittest
import ddt
import json

import main



@ddt.ddt
class TestMain(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
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
            "HELLO, GUY FROM POST",
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
                    '/create',
                    data=req_body, 
                    content_type='text/html'
                )
            else:
                response = _app.post(
                    '/create', 
                    data=json.dumps(req_body),
                    content_type='application/json'
                )
            self.assertTrue(exp_resp_text in response.get_data(as_text=True))
            self.assertEqual(exp_code, response.status_code)
            
