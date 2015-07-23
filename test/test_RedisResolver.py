__author__ = 'frank'

# System Imports
import json
from mock import Mock, patch
from test import AddressimoTestCase

from addressimo.resolvers.RedisResolver import *


class TestGetPluginName(AddressimoTestCase):
    def test_get_plugin_name(self):

        ret_val = RedisResolver.get_plugin_name()
        self.assertEqual('REDIS', ret_val)


class TestGetAllKeys(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        # Setup redis data
        self.mockRedis.from_url.return_value.keys.return_value = ['1', '2', '3']

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        self.assertListEqual(['1', '2', '3'], self.rr.get_all_keys())


class TestGetIdObj(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        # Setup redis data
        self.mockJSONData = {'bip70_enabled': True, 'last_generated_index': 10}
        self.mockRedis.from_url.return_value.get.return_value = json.dumps(self.mockJSONData)

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        ret_obj = self.rr.get_id_obj('id')

        # Validate calls
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual('id', self.mockRedis.from_url.return_value.get.call_args[0][0])

        # Verify id_obj updated with Redis data
        self.assertTrue(ret_obj.bip70_enabled)
        self.assertEqual(10, ret_obj.last_generated_index)

    def test_no_results_for_id_obj(self):

        # Setup test case
        self.mockRedis.from_url.return_value.get.return_value = None

        ret_obj = self.rr.get_id_obj('id')

        # Validate calls
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual('id', self.mockRedis.from_url.return_value.get.call_args[0][0])

        # Verify id_obj is None
        self.assertIsNone(ret_obj)

    def test_exception_retrieving_id_obj(self):

        # Setup test case
        self.mockRedis.from_url.return_value.get.side_effect = Exception()

        ret_obj = self.rr.get_id_obj('id')

        # Validate calls
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual('id', self.mockRedis.from_url.return_value.get.call_args[0][0])

        # Verify id_obj is None
        self.assertIsNone(ret_obj)


class TestGetBranches(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        # Setup redis return data
        self.mockRedis.from_url.return_value.hkeys.return_value = ['123', '456']

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        ret_val = self.rr.get_branches(111)

        self.assertListEqual([123, 456], ret_val)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hkeys.call_count)
        self.assertEqual(111, self.mockRedis.from_url.return_value.hkeys.call_args[0][0])

    def test_no_branches_present(self):

        # Setup test case
        self.mockRedis.from_url.return_value.hkeys.return_value = None

        ret_val = self.rr.get_branches(111)

        self.assertListEqual([], ret_val)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hkeys.call_count)
        self.assertEqual(111, self.mockRedis.from_url.return_value.hkeys.call_args[0][0])

    def test_exception_retrieving_branches(self):

        # Setup test case
        self.mockRedis.from_url.return_value.hkeys.side_effect = Exception('Lookup failed')

        ret_val = self.rr.get_branches(111)

        self.assertListEqual([], ret_val)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hkeys.call_count)
        self.assertEqual(111, self.mockRedis.from_url.return_value.hkeys.call_args[0][0])


class TestGetLGIndex(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        # Setup redis return data
        self.mockRedis.from_url.return_value.hget.return_value = '5'

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        ret_val = self.rr.get_lg_index(111, 1234)

        self.assertEqual(5, ret_val)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hget.call_count)
        self.assertEqual((111, 1234), self.mockRedis.from_url.return_value.hget.call_args[0])

    def test_hget_returns_none(self):

        # Setup Test case
        self.mockRedis.from_url.return_value.hget.return_value = None

        ret_val = self.rr.get_lg_index(111, 1234)

        self.assertEqual(0, ret_val)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hget.call_count)
        self.assertEqual((111, 1234), self.mockRedis.from_url.return_value.hget.call_args[0])

    def test_exception_retrieving_lg_index(self):

        # Setup Test case
        self.mockRedis.from_url.return_value.hget.side_effect = Exception('Exception retrieving lg_index')

        ret_val = self.rr.get_lg_index(111, 1234)

        self.assertEqual(0, ret_val)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hget.call_count)
        self.assertEqual((111, 1234), self.mockRedis.from_url.return_value.hget.call_args[0])


class TestSetLGIndex(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        ret_val = self.rr.set_lg_index(10, 123456, 7)

        self.assertIsNotNone(ret_val)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hset.call_count)
        self.assertEqual((10, 123456, 7), self.mockRedis.from_url.return_value.hset.call_args[0])

    def test_exception_saving_lg_index(self):

        # Setup Test case
        self.mockRedis.from_url.return_value.hset.side_effect = Exception('Exception saving lg_index')

        ret_val = self.rr.set_lg_index(10, 123456, 7)

        self.assertIsNone(ret_val)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hset.call_count)
        self.assertEqual((10, 123456, 7), self.mockRedis.from_url.return_value.hset.call_args[0])


class TestSave(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')
        self.patcher2 = patch('addressimo.resolvers.RedisResolver.uuid4')

        self.mockRedis = self.patcher1.start()
        self.mockUuid4 = self.patcher2.start()

        from addressimo.data import IdObject

        # Setup redis data
        self.mock_id_obj = IdObject('id')
        self.mock_id_obj.id = 'id'
        self.mock_id_obj.bip70_enabled = True
        self.mock_id_obj.last_generated_index = 10

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        ret_val = self.rr.save(self.mock_id_obj)

        # Validate calls
        self.assertEqual(self.mockRedis.from_url.return_value.set.return_value, ret_val)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.set.call_count)
        call_args = self.mockRedis.from_url.return_value.set.call_args[0]
        self.assertEqual(self.mock_id_obj.id, call_args[0])
        self.assertEqual(json.dumps(self.mock_id_obj), call_args[1])
        self.assertFalse(self.mockUuid4.called)

    def test_no_id(self):

        self.mock_id_obj.id = None
        self.mockRedis.from_url.return_value.get.side_effect = [True, None]
        self.mockUuid4.return_value.hex = '0123456789abcdef'

        ret_val = self.rr.save(self.mock_id_obj)

        # Validate calls
        self.assertEqual(self.mockRedis.from_url.return_value.set.return_value, ret_val)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.set.call_count)
        call_args = self.mockRedis.from_url.return_value.set.call_args[0]
        self.assertEqual('0123456789abcdef', call_args[0])
        self.assertEqual(json.dumps(self.mock_id_obj), call_args[1])

        self.assertEqual(2, self.mockUuid4.call_count)

    def test_exception_saving_redis_data(self):

        # Setup test case
        self.mockRedis.from_url.return_value.set.side_effect = Exception()

        self.assertRaises(Exception, self.rr.save, self.mock_id_obj)

        # Validate calls
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.set.call_count)
        call_args = self.mockRedis.from_url.return_value.set.call_args[0]
        self.assertEqual(self.mock_id_obj.id, call_args[0])
        self.assertEqual(json.dumps(self.mock_id_obj), call_args[1])


class TestDelete(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        from addressimo.data import IdObject

        # Setup redis data
        self.mock_id_obj = IdObject('id')
        self.mock_id_obj.id = 'id'

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        ret_val = self.rr.delete(self.mock_id_obj)

        # Validate calls
        self.assertEqual(self.mockRedis.from_url.return_value.delete.return_value, ret_val)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)
        call_args = self.mockRedis.from_url.return_value.delete.call_args[0]
        self.assertEqual(self.mock_id_obj.id, call_args[0])

    def test_exception_saving_redis_data(self):

        # Setup test case
        self.mockRedis.from_url.return_value.delete.side_effect = Exception()

        self.assertRaises(Exception, self.rr.delete, self.mock_id_obj)

        # Validate calls
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)
        call_args = self.mockRedis.from_url.return_value.delete.call_args[0]
        self.assertEqual(self.mock_id_obj.id, call_args[0])