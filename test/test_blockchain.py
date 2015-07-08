__author__ = 'frank'

# System Imports
from mock import Mock, patch
from test import AddressimoTestCase

from addressimo.blockchain import *


class TestConnect(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.blockchain.bitcoinrpc')

        self.mockBitcoinRpc = self.patcher1.start()

    def test_go_right(self):

        ret_val = connect()

        self.assertEqual(self.mockBitcoinRpc.connect_to_remote.return_value, ret_val)


class TestCurrentBlockCount(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.blockchain.connect')

        self.mockConnect = self.patcher1.start()

    def test_go_right(self):

        ret_val = current_block_count()

        self.assertEqual(self.mockConnect.return_value.getblockcount.return_value, ret_val)
        self.assertEqual(1, self.mockConnect.call_count)


class TestGetRedisLastBlockheight(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.blockchain.Redis')

        self.mockRedis = self.patcher1.start()

    def test_go_right(self):

        ret_val = get_redis_last_blockheight()

        self.assertEqual(int(self.mockRedis.from_url.return_value.get.return_value), ret_val)
        self.assertEqual(1, self.mockRedis.from_url.call_count)

    def test_exception_retrieving_last_blockheight(self):

        # Setup test case
        self.mockRedis.from_url.return_value.get.side_effect = Exception()

        ret_val = get_redis_last_blockheight()

        self.assertIsNone(ret_val)
        self.assertEqual(1, self.mockRedis.from_url.call_count)


class TestCacheUpToDate(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.blockchain.current_block_count')
        self.patcher2 = patch('addressimo.blockchain.get_redis_last_blockheight')

        self.mockCurrentBlockCount = self.patcher1.start()
        self.mockGetRedisLastblockheight = self.patcher2.start()

        # Setup go right where cache is up to date
        config.cache_blockheight_threshold = 10
        self.mockCurrentBlockCount.return_value = 100
        self.mockGetRedisLastblockheight.return_value = 101

    def test_go_right(self):

        ret_val = cache_up_to_date()

        self.assertTrue(ret_val)

    def test_difference_exceeds_threshold(self):

        # Setup test case
        self.mockCurrentBlockCount.return_value = 1000

        ret_val = cache_up_to_date()

        self.assertFalse(ret_val)


class TestGetBlock(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.blockchain.connect')

        self.mockConnect = self.patcher1.start()

        self.mockConnect.return_value.getblockhash.return_value = 'here it is'

    def test_go_right(self):

        ret_val = get_block(10000)

        self.assertEqual(self.mockConnect.return_value.proxy.getblock.return_value, ret_val)

