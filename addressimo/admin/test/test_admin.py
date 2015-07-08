__author__ = 'frank'

# System Imports
from attrdict import AttrDict
from mock import Mock, patch
from test import AddressimoTestCase

from addressimo.admin.admin import *
from addressimo.data import IdObject


class TestGetIdObjs(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.admin.admin.Redis')
        self.patcher2 = patch('addressimo.admin.admin.PluginManager')
        self.patcher3 = patch('addressimo.admin.admin.create_json_response')

        self.mockRedis = self.patcher1.start()
        self.mockPluginManager = self.patcher2.start()
        self.mockCreateJSONResponse = self.patcher3.start()

        self.mockRedisData = {'private_key': 'priv_key', 'bip32': True}
        self.mockRedisKeyData = ['1', '2', '3']
        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = self.mockRedisData
        self.mockPluginManager.get_plugin.return_value.get_all_keys.return_value = self.mockRedisKeyData

    def test_go_right_id(self):

        get_id_objs('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_all_keys.call_count)

        # Remove private_key from mock data for validation below
        self.mockRedisData['private_key'] = ''

        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertTrue(call_args[0])
        self.assertEqual('', call_args[1])
        self.assertEqual(200, call_args[2])
        self.assertDictEqual(self.mockRedisData, call_args[3].get('data'))

    def test_go_right_all_keys(self):

        get_id_objs(None)

        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_all_keys.call_count)

        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertTrue(call_args[0])
        self.assertEqual('', call_args[1])
        self.assertEqual(200, call_args[2])
        self.assertListEqual(self.mockRedisKeyData, call_args[3].get('keys'))

    def test_id_obj_not_found(self):

        # Setup test case
        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = None

        get_id_objs('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_all_keys.call_count)


        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertFalse(call_args[0])
        self.assertEqual('Object not found for this ID.', call_args[1])
        self.assertEqual(404, call_args[2])


class TestUpdateIdObj(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.admin.admin.Redis')
        self.patcher2 = patch('addressimo.admin.admin.PluginManager')
        self.patcher3 = patch('addressimo.admin.admin.create_json_response')
        self.patcher4 = patch('addressimo.admin.admin.request')
        self.patcher5 = patch('addressimo.admin.admin.IdObject', wraps=IdObject)

        self.mockRedis = self.patcher1.start()
        self.mockPluginManager = self.patcher2.start()
        self.mockCreateJSONResponse = self.patcher3.start()
        self.mockRequest = self.patcher4.start()
        self.mockIdObject = self.patcher5.start()

        # Mock rdata
        self.mockRequestData = {
            'auth_public_key': None,
            'bip32_enabled': True,
            'bip70_enabled': False,
            'bip70_static_amount': None,
            'expires': None,
            'id': 'id',
            'last_generated_index': 0,
            'last_used_index': 0,
            'master_public_key': None,
            'memo': None,
            'merchant_data': None,
            'payment_url': None,
            'presigned_only': False,
            'presigned_payment_requests': [],
            'private_key': 'priv_key',
            'wallet_address': None,
            'x509_cert': None
        }

        self.mockRequest.get_json.return_value = self.mockRequestData

        # Mock id_obj returned from get_id_obj
        self.id_obj = IdObject()
        self.id_obj.id = 'myid'
        self.id_obj.private_key = 'old_priv_key'
        self.id_obj.bip32_enabled = False
        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = self.id_obj

        # This handles the ID being generated when save() is called on a newly created id_obj
        def mocksave(id_obj):
            if not id_obj.id:
                id_obj.id = 'generatedid'

        self.mockPluginManager.get_plugin.return_value.save.side_effect = mocksave

    def test_go_right_create(self):

        # Setup Test case
        self.id_obj = IdObject()
        self.mockIdObject.return_value = self.id_obj

        update_id_obj(None)

        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate data passed to save
        call_args = self.mockPluginManager.get_plugin.return_value.save.call_args[0][0]
        self.assertEqual(self.id_obj, call_args)

        # Validate id_obj data
        self.assertTrue(self.id_obj.bip32_enabled)
        self.assertEqual('priv_key', self.id_obj.private_key)
        self.assertEqual('generatedid', self.id_obj.id)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertTrue(call_args[0])
        self.assertEqual('Update succeeded', call_args[1])
        self.assertEqual(200, call_args[2])
        self.assertDictEqual({'id': 'generatedid'}, call_args[3])

    def test_go_right_update_private_key_change(self):

        update_id_obj('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate data passed to save
        call_args = self.mockPluginManager.get_plugin.return_value.save.call_args[0][0]
        self.assertEqual(self.id_obj, call_args)

        # Validate id_obj data
        self.assertTrue(self.id_obj.bip32_enabled)
        self.assertEqual('priv_key', self.id_obj.private_key)
        self.assertEqual('myid', self.id_obj.id)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertTrue(call_args[0])
        self.assertEqual('Update succeeded', call_args[1])
        self.assertEqual(200, call_args[2])
        self.assertDictEqual({'id': 'myid'}, call_args[3])

    def test_go_right_update_no_private_key_change(self):

        # Setup Test Case
        self.mockRequestData['private_key'] = ''

        update_id_obj('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate data passed to save
        call_args = self.mockPluginManager.get_plugin.return_value.save.call_args[0][0]
        self.assertEqual(self.id_obj, call_args)

        # Validate id_obj data
        self.assertTrue(self.id_obj.bip32_enabled)
        self.assertEqual('old_priv_key', self.id_obj.private_key)
        self.assertEqual('myid', self.id_obj.id)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertTrue(call_args[0])
        self.assertEqual('Update succeeded', call_args[1])
        self.assertEqual(200, call_args[2])
        self.assertDictEqual({'id': 'myid'}, call_args[3])

    def test_id_obj_lookup_returns_none(self):

        # Setup Test case
        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = None

        update_id_obj('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertFalse(call_args[0])
        self.assertEqual('Object not found for this ID.', call_args[1])
        self.assertEqual(404, call_args[2])

    def test_unknown_key_in_rdata(self):

        # Setup Test case
        self.mockRequestData['badkey'] = 'badvalue'

        update_id_obj('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertFalse(call_args[0])
        self.assertEqual('Unknown key submitted', call_args[1])
        self.assertEqual(400, call_args[2])

    def test_exception_saving_id_obj(self):

        # Setup Test case
        self.mockPluginManager.get_plugin.return_value.save.side_effect = Exception()

        update_id_obj('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertFalse(call_args[0])
        self.assertEqual('Exception occurred attempting to save id object', call_args[1])
        self.assertEqual(500, call_args[2])


class TestDeleteIdObj(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.admin.admin.Redis')
        self.patcher2 = patch('addressimo.admin.admin.PluginManager')
        self.patcher3 = patch('addressimo.admin.admin.create_json_response')

        self.mockRedis = self.patcher1.start()
        self.mockPluginManager = self.patcher2.start()
        self.mockCreateJSONResponse = self.patcher3.start()

    def test_go_right(self):

        delete_id_obj('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.delete.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate data passed to delete
        call_args = self.mockPluginManager.get_plugin.return_value.delete.call_args[0][0]
        self.assertEqual(self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value, call_args)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertTrue(call_args[0])
        self.assertEqual('Delete succeeded', call_args[1])
        self.assertEqual(204, call_args[2])

    def test_id_obj_lookup_returns_none(self):

        # Setup Test case
        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = None

        delete_id_obj('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.delete.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertFalse(call_args[0])
        self.assertEqual('Object not found for this ID.', call_args[1])
        self.assertEqual(404, call_args[2])

    def test_exception_deleting_object(self):

        # Setup Test case
        self.mockPluginManager.get_plugin.return_value.delete.side_effect = Exception()

        delete_id_obj('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.delete.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertFalse(call_args[0])
        self.assertEqual('Exception occurred attempting to delete id object', call_args[1])
        self.assertEqual(500, call_args[2])


class TestDeleteIdObjPrivKey(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.admin.admin.Redis')
        self.patcher2 = patch('addressimo.admin.admin.PluginManager')
        self.patcher3 = patch('addressimo.admin.admin.create_json_response')

        self.mockRedis = self.patcher1.start()
        self.mockPluginManager = self.patcher2.start()
        self.mockCreateJSONResponse = self.patcher3.start()

        # Mock id_obj returned from get_id_obj
        self.id_obj = IdObject()
        self.id_obj.private_key = 'old_priv_key'
        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = self.id_obj

    def test_go_right(self):

        delete_id_obj_priv_key('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate data passed to save
        call_args = self.mockPluginManager.get_plugin.return_value.save.call_args[0][0]
        self.assertEqual(self.id_obj, call_args)

        # Validate id_obj data
        self.assertIsNone(self.id_obj.private_key)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertTrue(call_args[0])
        self.assertEqual('Delete private key succeeded', call_args[1])
        self.assertEqual(204, call_args[2])

    def test_id_obj_lookup_returns_none(self):

        # Setup Test case
        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = None

        delete_id_obj_priv_key('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertFalse(call_args[0])
        self.assertEqual('Object not found for this ID.', call_args[1])
        self.assertEqual(404, call_args[2])

    def test_exception_saving_id_obj(self):

        # Setup Test case
        self.mockPluginManager.get_plugin.return_value.save.side_effect = Exception()

        delete_id_obj_priv_key('id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_id_obj.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate JSON Response Data
        call_args = self.mockCreateJSONResponse.call_args[0]
        self.assertFalse(call_args[0])
        self.assertEqual('Exception occurred attempting to save id object', call_args[1])
        self.assertEqual(500, call_args[2])
