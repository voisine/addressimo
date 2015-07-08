__author__ = 'frank'

# System Imports
import json
from mock import Mock, patch
from test import AddressimoTestCase

from addressimo.signer.APISigner import *


class TestSetIdObj(AddressimoTestCase):
    def test_go_right(self):

        # Setup test case
        id_obj = Mock()
        apis = APISigner()

        # Run
        apis.set_id_obj(id_obj)

        # Validate response
        self.assertEqual(apis.id_obj, id_obj)


class TestGetPluginName(AddressimoTestCase):
    def test_go_right(self):
        self.assertEqual('API', APISigner().get_plugin_name())


class TestSign(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.signer.APISigner.requests')

        self.mockRequests = self.patcher1.start()

        # Create id_obj data to validate post
        self.id_obj = Mock()
        self.id_obj.private_key_id = 'privkeyid'

        # Instantiate signer and set id_obj
        self.apis = APISigner()
        self.apis.set_id_obj(self.id_obj)

        # Set config value for mocked endpoint
        config.signer_api_endpoint = 'https://signer.mydomain.com/sign'

        # Setup expected post data for validation
        self.expected_post_data = {
            'private_key_id': self.id_obj.private_key_id,
            'data': 'data'.encode('hex'),
            'digest': 'SHA256'
        }

    def test_go_right(self):

        ret_val = self.apis.sign('data')

        # Validate return value and calls
        self.assertEqual(
            ret_val,
            self.mockRequests.post.return_value.json.return_value.get.return_value.decode.return_value
        )
        self.assertEqual(1, self.mockRequests.post.call_count)

        # Validate post call data
        call_args = self.mockRequests.post.call_args[0]
        self.assertEqual(config.signer_api_endpoint, call_args[0])
        self.assertEqual(json.dumps(self.expected_post_data), call_args[1])

    def test_private_key_id_missing(self):

        # Setup test case
        self.id_obj.private_key_id = None

        self.assertRaisesRegexp(ValueError, 'APISigner Requires private_key_id', self.apis.sign, 'data')
        self.assertEqual(0, self.mockRequests.post.call_count)

    def test_sig_missing(self):

        # Setup test case
        self.mockRequests.post.return_value.json.return_value.get.return_value = None

        ret_val = self.apis.sign('data')

        self.assertIsNone(ret_val)
        self.assertEqual(1, self.mockRequests.post.call_count)

    def test_exception_retrieving_signature(self):

        # Setup test case
        self.mockRequests.post.side_effect = Exception()

        ret_val = self.apis.sign('data')

        self.assertIsNone(ret_val)
        self.assertEqual(1, self.mockRequests.post.call_count)