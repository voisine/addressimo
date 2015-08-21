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


class TestAddPRR(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')
        self.patcher2 = patch('addressimo.resolvers.RedisResolver.uuid4')

        self.mockRedis = self.patcher1.start()
        self.mockUuid4 = self.patcher2.start()

        self.mockRedis.from_url.return_value.exists.return_value = False
        self.mockRedis.from_url.return_value.hset.return_value = 1
        self.mockUuid4.return_value.hex = 'uuid4'

        self.submit_id = 'endpoint_id'
        self.prr_data = {'key':'value'}

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        result = self.rr.add_prr(self.submit_id, self.prr_data)

        self.assertIsNotNone(result)
        self.assertEqual('uuid4uuid4uuid4', result.get('id'))
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(3, self.mockUuid4.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.exists.call_count)
        self.assertEqual('uuid4uuid4uuid4', self.mockRedis.from_url.return_value.exists.call_args[0][0])
        self.assertEqual(1, self.mockRedis.from_url.return_value.hset.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hset.call_args[0][0])
        self.assertEqual('uuid4uuid4uuid4', self.mockRedis.from_url.return_value.hset.call_args[0][1])
        self.assertEqual('{"id": "uuid4uuid4uuid4", "key": "value"}', self.mockRedis.from_url.return_value.hset.call_args[0][2])

    def test_ppr_id_exists_once(self):

        self.mockRedis.from_url.return_value.exists.side_effect = [True, False]

        result = self.rr.add_prr(self.submit_id, self.prr_data)

        self.assertIsNotNone(result)
        self.assertEqual('uuid4uuid4uuid4', result.get('id'))
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(6, self.mockUuid4.call_count)
        self.assertEqual(2, self.mockRedis.from_url.return_value.exists.call_count)
        self.assertEqual('uuid4uuid4uuid4', self.mockRedis.from_url.return_value.exists.call_args[0][0])
        self.assertEqual(1, self.mockRedis.from_url.return_value.hset.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hset.call_args[0][0])
        self.assertEqual('uuid4uuid4uuid4', self.mockRedis.from_url.return_value.hset.call_args[0][1])
        self.assertEqual('{"id": "uuid4uuid4uuid4", "key": "value"}', self.mockRedis.from_url.return_value.hset.call_args[0][2])

    def test_exists_exception(self):

        self.mockRedis.from_url.return_value.exists.side_effect = Exception()

        self.assertRaises(Exception, self.rr.add_prr, self.submit_id, self.prr_data)

        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(3, self.mockUuid4.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.exists.call_count)
        self.assertEqual('uuid4uuid4uuid4', self.mockRedis.from_url.return_value.exists.call_args[0][0])
        self.assertEqual(0, self.mockRedis.from_url.return_value.hset.call_count)

    def test_hset_returns_not_one(self):

        self.mockRedis.from_url.return_value.hset.return_value = 0

        result = self.rr.add_prr(self.submit_id, self.prr_data)

        self.assertIsNone(result)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(3, self.mockUuid4.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.exists.call_count)
        self.assertEqual('uuid4uuid4uuid4', self.mockRedis.from_url.return_value.exists.call_args[0][0])
        self.assertEqual(1, self.mockRedis.from_url.return_value.hset.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hset.call_args[0][0])
        self.assertEqual('uuid4uuid4uuid4', self.mockRedis.from_url.return_value.hset.call_args[0][1])
        self.assertEqual('{"id": "uuid4uuid4uuid4", "key": "value"}', self.mockRedis.from_url.return_value.hset.call_args[0][2])

    def test_hset_exception(self):

        self.mockRedis.from_url.return_value.hset.side_effect = Exception()

        self.assertRaises(Exception, self.rr.add_prr, self.submit_id, self.prr_data)

        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(3, self.mockUuid4.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.exists.call_count)
        self.assertEqual('uuid4uuid4uuid4', self.mockRedis.from_url.return_value.exists.call_args[0][0])
        self.assertEqual(1, self.mockRedis.from_url.return_value.hset.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hset.call_args[0][0])
        self.assertEqual('uuid4uuid4uuid4', self.mockRedis.from_url.return_value.hset.call_args[0][1])
        self.assertEqual('{"id": "uuid4uuid4uuid4", "key": "value"}', self.mockRedis.from_url.return_value.hset.call_args[0][2])


class TestGetPRRs(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        self.mockRedis.from_url.return_value.hgetall.return_value = {
            "key1": json.dumps({"key1":"value1"}),
            "key2": json.dumps({"key2":"value2"})
        }

        self.submit_id = 'endpoint_id'

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        result = self.rr.get_prrs(self.submit_id)

        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertIn("key2", result[0])
        self.assertIn("key1", result[1])
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hgetall.call_args[0][0])

    def test_go_no_values(self):

        self.mockRedis.from_url.return_value.hgetall.return_value = {}

        result = self.rr.get_prrs(self.submit_id)

        self.assertIsNotNone(result)
        self.assertEqual(0, len(result))
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hgetall.call_args[0][0])

    def test_redis_exception(self):

        self.mockRedis.from_url.return_value.hgetall.side_effect = Exception

        self.assertRaises(Exception, self.rr.get_prrs, self.submit_id)

        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hgetall.call_args[0][0])


class TestDeletePRR(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        self.mockRedis.from_url.return_value.hdel.return_value = 1
        self.submit_id = 'endpoint_id'
        self.prr_id = 'prr_id'

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        result = self.rr.delete_prr(self.submit_id, self.prr_id)

        self.assertTrue(result)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hdel.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hdel.call_args[0][0])
        self.assertEqual(self.prr_id, self.mockRedis.from_url.return_value.hdel.call_args[0][1])

    def test_no_delete(self):

        self.mockRedis.from_url.return_value.hdel.return_value = 0

        result = self.rr.delete_prr(self.submit_id, self.prr_id)

        self.assertFalse(result)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hdel.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hdel.call_args[0][0])
        self.assertEqual(self.prr_id, self.mockRedis.from_url.return_value.hdel.call_args[0][1])

    def test_exception(self):

        self.mockRedis.from_url.return_value.hdel.side_effect = Exception()

        self.assertRaises(Exception, self.rr.delete_prr, self.submit_id, self.prr_id)

        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hdel.call_count)
        self.assertEqual(self.submit_id, self.mockRedis.from_url.return_value.hdel.call_args[0][0])
        self.assertEqual(self.prr_id, self.mockRedis.from_url.return_value.hdel.call_args[0][1])


class TestCleanupStalePRRData(AddressimoTestCase):
    def setUp(self):

        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')
        self.patcher2 = patch('addressimo.resolvers.RedisResolver.datetime', wraps=datetime)

        self.mockRedis = self.patcher1.start()
        self.mockDatetime = self.patcher2.start()

        self.now = self.mockDatetime.utcnow.return_value = datetime.utcnow()

        # Setup redis resolver
        self.rr = RedisResolver()

        # Setup test data
        self.submit_id = 'endpoint_id'
        self.prr_id = 'prr_id'

        self.mockRedis.from_url.return_value.keys.return_value = ['1']
        self.mockRedisData = {
            'submit_date': (self.now - timedelta(days=config.prr_expiration_days + 1)).strftime('%s'),
            'encrypted_payment_request': 'encPR'
        }
        self.mockRedis.from_url.return_value.hgetall.return_value.values.return_value = [json.dumps(self.mockRedisData)]

    def test_delete_one_key(self):

        self.rr.cleanup_stale_prr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.hgetall.call_args[0][0])
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.delete.call_args[0][0])

    def test_delete_two_keys(self):

        # Setup test case
        self.mockRedis.from_url.return_value.keys.return_value = ['1', '2']

        self.rr.cleanup_stale_prr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(2, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.hgetall.call_args_list[0][0][0])
        self.assertEqual('2', self.mockRedis.from_url.return_value.hgetall.call_args_list[1][0][0])
        self.assertEqual(2, self.mockRedis.from_url.return_value.delete.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.delete.call_args_list[0][0][0])
        self.assertEqual('2', self.mockRedis.from_url.return_value.delete.call_args_list[1][0][0])

    def test_no_keys_to_delete(self):

        # Setup test case
        self.mockRedis.from_url.return_value.keys.return_value = []

        self.rr.cleanup_stale_prr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.delete.call_count)

    def test_one_key_not_expired(self):

        # Setup test case
        self.mockRedisData['submit_date'] = self.now.strftime('%s')
        self.mockRedis.from_url.return_value.hgetall.return_value.values.return_value = [json.dumps(self.mockRedisData)]

        self.rr.cleanup_stale_prr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.delete.call_count)

    def test_exception_deleting_key(self):

        # Setup test case
        self.mockRedis.from_url.return_value.delete.side_effect = Exception('Delete failed')

        self.rr.cleanup_stale_prr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)

class TestAddReturnPR(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        self.mockRedis.from_url.return_value.set.return_value = 1
        self.return_pr = {"id":"rpr_id"}

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        result = self.rr.add_return_pr(self.return_pr)

        self.assertIsNone(result)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.set.call_count)
        self.assertEqual('rpr_id', self.mockRedis.from_url.return_value.set.call_args[0][0])
        self.assertEqual('{"id": "rpr_id"}', self.mockRedis.from_url.return_value.set.call_args[0][1])

    def test_set_returns_non_one(self):

        self.mockRedis.from_url.return_value.set.return_value = 0

        self.assertRaises(Exception, self.rr.add_return_pr,self.return_pr)

        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.set.call_count)
        self.assertEqual('rpr_id', self.mockRedis.from_url.return_value.set.call_args[0][0])
        self.assertEqual('{"id": "rpr_id"}', self.mockRedis.from_url.return_value.set.call_args[0][1])

    def test_set_exception(self):

        self.mockRedis.from_url.return_value.set.side_effect = Exception()

        self.assertRaises(Exception, self.rr.add_return_pr,self.return_pr)

        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.set.call_count)
        self.assertEqual('rpr_id', self.mockRedis.from_url.return_value.set.call_args[0][0])
        self.assertEqual('{"id": "rpr_id"}', self.mockRedis.from_url.return_value.set.call_args[0][1])


class TestGetReturnPR(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        self.mockRedis.from_url.return_value.get.return_value = json.dumps({"id":"rpr_id"})
        self.rpr_id = 'rpr_id'

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        result = self.rr.get_return_pr(self.rpr_id)

        self.assertIsNotNone(result)
        self.assertIn('id', result)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual('rpr_id', self.mockRedis.from_url.return_value.get.call_args[0][0])

    def test_exception(self):

        self.mockRedis.from_url.return_value.get.side_effect = Exception()

        self.assertRaises(Exception, self.rr.get_return_pr, self.rpr_id)

        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual('rpr_id', self.mockRedis.from_url.return_value.get.call_args[0][0])


class TestCleanupStaleReturnPRData(AddressimoTestCase):
    def setUp(self):

        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')
        self.patcher2 = patch('addressimo.resolvers.RedisResolver.datetime', wraps=datetime)

        self.mockRedis = self.patcher1.start()
        self.mockDatetime = self.patcher2.start()

        self.now = self.mockDatetime.utcnow.return_value = datetime.utcnow()

        # Setup redis resolver
        self.rr = RedisResolver()

        # Setup test data
        self.submit_id = 'endpoint_id'
        self.prr_id = 'prr_id'

        self.mockRedis.from_url.return_value.keys.return_value = ['1']
        self.mockRedisData = {
            'submit_date': (self.now - timedelta(days=config.rpr_expiration_days + 1)).strftime('%s')
        }
        self.mockRedis.from_url.return_value.get.return_value = json.dumps(self.mockRedisData)

    def test_delete_one_key(self):

        self.rr.cleanup_stale_return_pr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.get.call_args[0][0])
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.delete.call_args[0][0])

    def test_delete_two_keys(self):

        # Setup test case
        self.mockRedis.from_url.return_value.keys.return_value = ['1', '2']

        self.rr.cleanup_stale_return_pr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(2, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.get.call_args_list[0][0][0])
        self.assertEqual('2', self.mockRedis.from_url.return_value.get.call_args_list[1][0][0])
        self.assertEqual(2, self.mockRedis.from_url.return_value.delete.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.delete.call_args_list[0][0][0])
        self.assertEqual('2', self.mockRedis.from_url.return_value.delete.call_args_list[1][0][0])

    def test_no_keys_to_delete(self):

        # Setup test case
        self.mockRedis.from_url.return_value.keys.return_value = []

        self.rr.cleanup_stale_return_pr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.delete.call_count)

    def test_one_key_not_expired(self):

        # Setup test case
        self.mockRedisData['submit_date'] = self.now.strftime('%s')
        self.mockRedis.from_url.return_value.get.return_value = json.dumps(self.mockRedisData)

        self.rr.cleanup_stale_return_pr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.delete.call_count)

    def test_exception_deleting_key(self):

        # Setup test case
        self.mockRedis.from_url.return_value.delete.side_effect = Exception('Delete failed')

        self.rr.cleanup_stale_return_pr_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)


class TestGetPaymentRequestMetaData(AddressimoTestCase):

    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        self.mockRedis.from_url.return_value.hgetall.return_value = json.dumps({"key": "value"})

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        ret_val = self.rr.get_payment_request_meta_data('uuid')

        self.assertDictEqual({'key': 'value'}, json.loads(ret_val))
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual('uuid', self.mockRedis.from_url.return_value.hgetall.call_args[0][0])


class TestSetPaymentRequestMetaData(AddressimoTestCase):

    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')
        self.patcher2 = patch('addressimo.resolvers.RedisResolver.uuid4')
        self.patcher3 = patch('addressimo.resolvers.RedisResolver.datetime')

        self.mockRedis = self.patcher1.start()
        self.mockUUID = self.patcher2.start()
        self.mockDatetime = self.patcher3.start()

        self.mockUUID.return_value.hex = 'abc123'
        self.mockRedis.from_url.return_value.hkeys.return_value = False

        self.now = self.mockDatetime.utcnow.return_value = datetime.utcnow()

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right_one_iteration(self):

        ret_val = self.rr.set_payment_request_meta_data(int(self.now.strftime('%s')), 'wallet_addr', 'amount')

        # Validate return data
        self.assertEqual('abc123abc123', ret_val)

        # Validate call count
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hkeys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hmset.call_count)

        # Validate Redis call data
        self.assertEqual('abc123abc123', self.mockRedis.from_url.return_value.hkeys.call_args[0][0])

        self.assertEqual('abc123abc123', self.mockRedis.from_url.return_value.hmset.call_args[0][0])
        self.assertDictEqual(
            {'expiration_date': int(self.now.strftime('%s')), 'payment_validation_data': '%s' % json.dumps({'wallet_addr': 'amount'})},
            self.mockRedis.from_url.return_value.hmset.call_args[0][1]
        )

    def test_go_right_two_iterations(self):

        # Setup test case
        self.mockRedis.from_url.return_value.hkeys.side_effect = [True, False]

        ret_val = self.rr.set_payment_request_meta_data(int(self.now.strftime('%s')), 'wallet_addr', 'amount')

        # Validate return data
        self.assertEqual('abc123abc123', ret_val)

        # Validate call count
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(2, self.mockRedis.from_url.return_value.hkeys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hmset.call_count)

        # Validate Redis call data
        self.assertEqual('abc123abc123', self.mockRedis.from_url.return_value.hkeys.call_args_list[0][0][0])
        self.assertEqual('abc123abc123', self.mockRedis.from_url.return_value.hkeys.call_args_list[1][0][0])

        self.assertEqual('abc123abc123', self.mockRedis.from_url.return_value.hmset.call_args[0][0])
        self.assertDictEqual(
            {'expiration_date': int(self.now.strftime('%s')), 'payment_validation_data': '%s' % json.dumps({'wallet_addr': 'amount'})},
            self.mockRedis.from_url.return_value.hmset.call_args[0][1]
        )

    def test_exception_saving_to_redis(self):

        # Setup Test Case
        self.mockRedis.from_url.return_value.hmset.side_effect = Exception('Save Failed')

        self.assertRaises(
            Exception,
            self.rr.set_payment_request_meta_data,
            int(self.now.strftime('%s')),
            'wallet_addr',
            'amount'
        )

        # Validate call count
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hkeys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hmset.call_count)

        # Validate Redis call data
        self.assertEqual('abc123abc123', self.mockRedis.from_url.return_value.hkeys.call_args[0][0])

        self.assertEqual('abc123abc123', self.mockRedis.from_url.return_value.hmset.call_args[0][0])
        self.assertDictEqual(
            {'expiration_date': int(self.now.strftime('%s')), 'payment_validation_data': '%s' % json.dumps({'wallet_addr': 'amount'})},
            self.mockRedis.from_url.return_value.hmset.call_args[0][1]
        )


class TestCleanupStalePaymentRequestMetaData(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')
        self.patcher2 = patch('addressimo.resolvers.RedisResolver.datetime', wraps=datetime)

        self.mockRedis = self.patcher1.start()
        self.mockDatetime = self.patcher2.start()

        self.now = self.mockDatetime.utcnow.return_value = datetime.utcnow()

        # Setup redis resolver
        self.rr = RedisResolver()

        # Setup test data
        self.mockRedis.from_url.return_value.keys.return_value = ['1']
        self.mockRedisData = {'expiration_date': (self.now - timedelta(days=1)).strftime('%s')}
        self.mockRedis.from_url.return_value.hgetall.return_value = self.mockRedisData

    def test_delete_one_key(self):

        self.rr.cleanup_stale_payment_request_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.hgetall.call_args[0][0])
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.delete.call_args[0][0])

    def test_delete_two_keys(self):

        # Setup test case
        self.mockRedis.from_url.return_value.keys.return_value = ['1', '2']

        self.rr.cleanup_stale_payment_request_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(2, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.hgetall.call_args_list[0][0][0])
        self.assertEqual('2', self.mockRedis.from_url.return_value.hgetall.call_args_list[1][0][0])
        self.assertEqual(2, self.mockRedis.from_url.return_value.delete.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.delete.call_args_list[0][0][0])
        self.assertEqual('2', self.mockRedis.from_url.return_value.delete.call_args_list[1][0][0])

    def test_no_keys_to_delete(self):

        # Setup test case
        self.mockRedis.from_url.return_value.keys.return_value = []

        self.rr.cleanup_stale_payment_request_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.delete.call_count)

    def test_one_key_not_expired(self):

        # Setup test case
        self.mockRedisData = {'expiration_date': (self.now + timedelta(days=1)).strftime('%s')}
        self.mockRedis.from_url.return_value.hgetall.return_value = self.mockRedisData

        self.rr.cleanup_stale_payment_request_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.delete.call_count)

    def test_exception_deleting_key(self):

        # Setup test case
        self.mockRedis.from_url.return_value.delete.side_effect = Exception('Delete failed')

        self.rr.cleanup_stale_payment_request_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)


class TestSetPaymentMetaData(AddressimoTestCase):

    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')
        self.patcher2 = patch('addressimo.resolvers.RedisResolver.datetime')

        self.mockRedis = self.patcher1.start()
        self.mockDatetime = self.patcher2.start()

        self.now = self.mockDatetime.utcnow.return_value = datetime.utcnow()

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        self.rr.set_payment_meta_data('tx_hash', 'memo', 'refund_address')

        # Validate call count
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hmset.call_count)

        # Validate Redis call data
        self.assertEqual('tx_hash', self.mockRedis.from_url.return_value.hmset.call_args[0][0])
        self.assertDictEqual(
            {'memo': 'memo', 'refund_to': 'refund_address', 'expiration_date': int(mktime((self.now + timedelta(days=61)).timetuple()))},
            self.mockRedis.from_url.return_value.hmset.call_args[0][1]
        )

    def test_exception_saving_to_redis(self):

        # Setup test case
        self.mockRedis.from_url.return_value.hmset.side_effect = Exception('Save Failed')

        self.assertRaises(Exception, self.rr.set_payment_meta_data, 'tx_hash', 'memo', 'refund_address')

        # Validate call count
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hmset.call_count)

        # Validate Redis call data
        self.assertEqual('tx_hash', self.mockRedis.from_url.return_value.hmset.call_args[0][0])
        self.assertDictEqual(
            {'memo': 'memo', 'refund_to': 'refund_address', 'expiration_date': int(mktime((self.now + timedelta(days=61)).timetuple()))},
            self.mockRedis.from_url.return_value.hmset.call_args[0][1]
        )


class TestCleanupStalePaymentMetaData(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')
        self.patcher2 = patch('addressimo.resolvers.RedisResolver.datetime', wraps=datetime)

        self.mockRedis = self.patcher1.start()
        self.mockDatetime = self.patcher2.start()

        self.now = self.mockDatetime.utcnow.return_value = datetime.utcnow()

        # Setup redis resolver
        self.rr = RedisResolver()

        # Setup test data
        self.mockRedis.from_url.return_value.keys.return_value = ['1']
        self.mockRedisData = {'expiration_date': (self.now - timedelta(days=1)).strftime('%s')}
        self.mockRedis.from_url.return_value.hgetall.return_value = self.mockRedisData

    def test_delete_one_key(self):

        self.rr.cleanup_stale_payment_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.hgetall.call_args[0][0])
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.delete.call_args[0][0])

    def test_delete_two_keys(self):

        # Setup test case
        self.mockRedis.from_url.return_value.keys.return_value = ['1', '2']

        self.rr.cleanup_stale_payment_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(2, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.hgetall.call_args_list[0][0][0])
        self.assertEqual('2', self.mockRedis.from_url.return_value.hgetall.call_args_list[1][0][0])
        self.assertEqual(2, self.mockRedis.from_url.return_value.delete.call_count)
        self.assertEqual('1', self.mockRedis.from_url.return_value.delete.call_args_list[0][0][0])
        self.assertEqual('2', self.mockRedis.from_url.return_value.delete.call_args_list[1][0][0])

    def test_no_keys_to_delete(self):

        # Setup test case
        self.mockRedis.from_url.return_value.keys.return_value = []

        self.rr.cleanup_stale_payment_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.delete.call_count)

    def test_one_key_not_expired(self):

        # Setup test case
        self.mockRedisData = {'expiration_date': (self.now + timedelta(days=1)).strftime('%s')}
        self.mockRedis.from_url.return_value.hgetall.return_value = self.mockRedisData

        self.rr.cleanup_stale_payment_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(0, self.mockRedis.from_url.return_value.delete.call_count)

    def test_exception_deleting_key(self):

        # Setup test case
        self.mockRedis.from_url.return_value.delete.side_effect = Exception('Delete failed')

        self.rr.cleanup_stale_payment_meta_data()

        # Validate calls and counts
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.keys.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.delete.call_count)


class TestGetRefundAddressFromTxHash(AddressimoTestCase):

    def setUp(self):
        self.patcher1 = patch('addressimo.resolvers.RedisResolver.Redis')

        self.mockRedis = self.patcher1.start()

        self.mockRedis.from_url.return_value.hgetall.return_value = {'key': 'value', 'expiration_date': 'thedate'}

        # Setup redis resolver
        self.rr = RedisResolver()

    def test_go_right(self):

        ret_val = self.rr.get_refund_address_from_tx_hash('tx_hash')

        # Validate Return value
        self.assertDictEqual({'key': 'value'}, ret_val)

        # Validate call count
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.hgetall.call_count)

        # Validate Redis call data
        self.assertEqual('tx_hash', self.mockRedis.from_url.return_value.hgetall.call_args[0][0])

