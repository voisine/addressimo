__author__ = 'frank'

# System Imports
import json
from datetime import datetime
from mock import Mock, patch
from test import AddressimoTestCase

from addressimo.logger.RedisLogger import *


class TestRedisLogger(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.logger.RedisLogger.Redis')
        self.patcher2 = patch('addressimo.logger.RedisLogger.datetime', wraps=datetime, spec=datetime)

        self.mockRedis = self.patcher1.start()
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

    def test_get_plugin_name(self):

        self.assertEqual('REDIS', RedisLogger.get_plugin_name())

    def test_log_payment_expires_string(self):

        rl = RedisLogger()
        rl.log_payment_request(
            'address',
            'signer',
            'amount',
            'expires',
            'memo',
            'payment_url',
            'merchant_data'
        )

        call_args = self.mockRedis.from_url.return_value.hmset.call_args[0]
        self.assertEqual('address-%s-expires' % self.now.strftime('%s'), call_args[0])
        self.assertDictEqual(self.expected_data, call_args[1])

    def test_log_payment_request_expires_datetime_obj(self):

        # Setup test case
        self.expected_data['expires'] = self.now.strftime('%s')

        rl = RedisLogger()
        rl.log_payment_request(
            'address',
            'signer',
            'amount',
            self.now,
            'memo',
            'payment_url',
            'merchant_data'
        )

        call_args = self.mockRedis.from_url.return_value.hmset.call_args[0]
        self.assertEqual('address-%s-%s' % (self.now.strftime('%s'), self.now.strftime('%s')), call_args[0])
        self.assertDictEqual(self.expected_data, call_args[1])
