__author__ = 'frank'

# System Imports
import json
from datetime import datetime
from mock import Mock, patch
from test import AddressimoTestCase

from addressimo.logger.APILogger import *


class TestAPILogger(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.logger.APILogger.requests')
        self.patcher2 = patch('addressimo.logger.APILogger.datetime', wraps=datetime, spec=datetime)

        self.mockRequests = self.patcher1.start()
        self.mockDatetime = self.patcher2.start()

        self.now = self.mockDatetime.utcnow.return_value = datetime.utcnow()

        self.expected_data = {
            'address': 'address',
            'signer': 'signer',
            'amount': 'amount',
            'expires': 'expires',
            'memo': 'memo',
            'payment_url': 'payment_url',
            'merchant_data': 'merchant_data'
        }

        self.mockRequests.post.return_value.status_code = 200
        self.mockRequests.codes.ok = 200

    def test_get_plugin_name(self):

        self.assertEqual('API', APILogger.get_plugin_name())

    def test_log_payment_expires_string(self):

        al = APILogger()
        al.log_payment_request(
            'address',
            'signer',
            'amount',
            'expires',
            'memo',
            'payment_url',
            'merchant_data'
        )

        self.assertEqual(1, self.mockRequests.post.call_count)
        call_args = self.mockRequests.post.call_args
        self.assertEqual(config.logger_api_endpoint, call_args[0][0])
        self.assertEqual(json.dumps(self.expected_data), call_args[1]['data'])

    def test_log_payment_request_expires_datetime_obj(self):

        # Setup test case
        self.expected_data['expires'] = self.now.strftime('%s')

        rl = APILogger()
        rl.log_payment_request(
            'address',
            'signer',
            'amount',
            self.now,
            'memo',
            'payment_url',
            'merchant_data'
        )

        self.assertEqual(1, self.mockRequests.post.call_count)
        call_args = self.mockRequests.post.call_args
        self.assertEqual(config.logger_api_endpoint, call_args[0][0])
        self.assertEqual(json.dumps(self.expected_data), call_args[1]['data'])
