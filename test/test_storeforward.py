__author__ = 'Matt David'

# System Imports
from mock import MagicMock, Mock, patch
from test import AddressimoTestCase

from addressimo.storeforward import *

TEST_PRIVKEY = '9d5a020344dd6dffc8a79e9c0bce8148ab0bce08162b6a44fec40cb113e16647'
TEST_PUBKEY = 'ac79cd6b0ac5f2a6234996595cb2d91fceaa0b9d9a6495f12f1161c074587bd19ae86928bddea635c930c09ea9c7de1a6a9c468f9afd18fbaeed45d09564ded6'

class TestGetId(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.storeforward.request')
        self.mockRequest = self.patcher1.start()
        self.mockRequest.url = 'http://addressimo.com/sf/0123456789abcdef'

    def test_go_right(self):

        ret_val = get_id()
        self.assertEqual('0123456789abcdef', ret_val)

    def test_no_id(self):

        self.mockRequest.url = 'http://addressimo.com/random'
        ret_val = get_id()
        self.assertEqual('random', ret_val)

class TestRequiresPublicKey(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.storeforward.get_id')
        self.patcher2 = patch('addressimo.storeforward.create_json_response')
        self.patcher3 = patch('addressimo.storeforward.request')
        self.patcher4 = patch('addressimo.storeforward.PluginManager')

        self.mockGetId = self.patcher1.start()
        self.mockCreateJsonResponse = self.patcher2.start()
        self.mockRequest = self.patcher3.start()
        self.mockPluginManager = self.patcher4.start()

        self.mockRequest.headers = {
            'x-identity': TEST_PUBKEY,

        }

        self.mockIdObj = Mock()
        self.mockIdObj.auth_public_key = TEST_PUBKEY

        self.mockPluginManager.get_plugin.return_value.get_config.return_value = self.mockIdObj

        # Mock the decorator function -> We run self.decorated
        self.mock_func = MagicMock(return_value='fake_response')
        self.mock_func.__name__ = 'mock_func'
        self.decorated = requires_public_key(self.mock_func)

    def test_go_right(self):

        ret_val = self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(self.mockGetId.return_value, self.mockPluginManager.get_plugin.return_value.get_config.call_args[0][0])
        self.assertEqual(1, self.mock_func.call_count)
        self.assertFalse(self.mockCreateJsonResponse.called)

    def test_no_id(self):

        self.mockGetId.return_value = None

        ret_val = self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Unknown Endpoint', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

    def test_missing_x_identity_header(self):

        del self.mockRequest.headers['x-identity']

        ret_val = self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Missing x-identity header', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_no_id_obj(self):

        self.mockPluginManager.get_plugin.return_value.get_config.return_value = None

        ret_val = self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(self.mockGetId.return_value, self.mockPluginManager.get_plugin.return_value.get_config.call_args[0][0])
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('ID Not Recognized', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

    def test_mismatched_pubkey(self):

        self.mockRequest.headers['x-identity'] = 'WRONG'

        ret_val = self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(self.mockGetId.return_value, self.mockPluginManager.get_plugin.return_value.get_config.call_args[0][0])
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('ID Not Recognized', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

# NOTE: Since we're also verifying the functionality of the ECDSA library and args passed, we cannot
# mock the VerifyingKey itself, just the way it's created
class TestRequiresValidSignature(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.storeforward.get_id')
        self.patcher2 = patch('addressimo.storeforward.create_json_response')
        self.patcher3 = patch('addressimo.storeforward.request')
        self.patcher4 = patch('addressimo.storeforward.VerifyingKey', wraps=VerifyingKey)

        self.mockGetId = self.patcher1.start()
        self.mockCreateJsonResponse = self.patcher2.start()
        self.mockRequest = self.patcher3.start()
        self.mockVerifyingKey = self.patcher4.start()

        self.mockRequest.url = 'http://addressimo.com/sf/0123456789abcdef'
        self.mockRequest.data = 'this is some crazy random data, dude! you know you gotta love this!'

        from ecdsa.keys import SigningKey
        from ecdsa.curves import SECP256k1

        sk = SigningKey.from_string(TEST_PRIVKEY.decode('hex'), curve=SECP256k1)
        sig = sk.sign(self.mockRequest.url + self.mockRequest.data)

        self.mockRequest.headers = {
            'x-identity': TEST_PUBKEY,
            'x-signature': sig.encode('hex')
        }

        self.mockIdObj = Mock()
        self.mockIdObj.auth_public_key = TEST_PUBKEY

        # Mock the decorator function -> We run self.decorated
        self.mock_func = MagicMock(return_value='fake_response')
        self.mock_func.__name__ = 'mock_func'
        self.decorated = requires_valid_signature(self.mock_func)

    def test_go_right(self):

        self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(1, self.mockVerifyingKey.from_string.call_count)
        self.assertEqual(TEST_PUBKEY.decode('hex'), self.mockVerifyingKey.from_string.call_args[0][0])
        self.assertEqual(curves.SECP256k1, self.mockVerifyingKey.from_string.call_args[1]['curve'])
        self.assertEqual(1, self.mock_func.call_count)
        self.assertEqual(0, self.mockCreateJsonResponse.call_count)

    def test_missing_id(self):

        self.mockGetId.return_value = None

        self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(0, self.mockVerifyingKey.from_string.call_count)
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Unknown Endpoint', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

    def test_missing_sig(self):

        del self.mockRequest.headers['x-signature']

        self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(0, self.mockVerifyingKey.from_string.call_count)
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Missing x-signature header', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_verifying_key_creation_exception(self):

        self.mockVerifyingKey.from_string.side_effect = UnexpectedDER()

        self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(1, self.mockVerifyingKey.from_string.call_count)
        self.assertEqual(TEST_PUBKEY.decode('hex'), self.mockVerifyingKey.from_string.call_args[0][0])
        self.assertEqual(curves.SECP256k1, self.mockVerifyingKey.from_string.call_args[1]['curve'])
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Bad Public Key Format', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_bad_signature(self):

        self.mockRequest.headers['x-signature'] = 'thisreallydoesntwork,butihopeyouthinkitdoesfdfdfd423324fff5555FF'.encode('hex')

        self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(1, self.mockVerifyingKey.from_string.call_count)
        self.assertEqual(TEST_PUBKEY.decode('hex'), self.mockVerifyingKey.from_string.call_args[0][0])
        self.assertEqual(curves.SECP256k1, self.mockVerifyingKey.from_string.call_args[1]['curve'])
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Signature Verification Error', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(401, self.mockCreateJsonResponse.call_args[0][2])

    def test_bad_digest_error(self):

        self.mockVerifyingKey.from_string.return_value.verify.side_effect = BadDigestError()

        self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(1, self.mockVerifyingKey.from_string.call_count)
        self.assertEqual(TEST_PUBKEY.decode('hex'), self.mockVerifyingKey.from_string.call_args[0][0])
        self.assertEqual(curves.SECP256k1, self.mockVerifyingKey.from_string.call_args[1]['curve'])
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Signature Verification Error', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(401, self.mockCreateJsonResponse.call_args[0][2])

    def test_bad_signature_error(self):

        self.mockVerifyingKey.from_string.return_value.verify.side_effect = BadSignatureError()

        self.decorated()

        self.assertEqual(1, self.mockGetId.call_count)
        self.assertEqual(1, self.mockVerifyingKey.from_string.call_count)
        self.assertEqual(TEST_PUBKEY.decode('hex'), self.mockVerifyingKey.from_string.call_args[0][0])
        self.assertEqual(curves.SECP256k1, self.mockVerifyingKey.from_string.call_args[1]['curve'])
        self.assertEqual(0, self.mock_func.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Signature Verification Error', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(401, self.mockCreateJsonResponse.call_args[0][2])

class TestRegister(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.storeforward.PluginManager')
        self.patcher2 = patch('addressimo.storeforward.IdObject')
        self.patcher3 = patch('addressimo.storeforward.create_json_response')
        self.patcher4 = patch('addressimo.storeforward.request')

        self.mockPluginManager = self.patcher1.start()
        self.mockIdObject = self.patcher2.start()
        self.mockCreateJsonResponse = self.patcher3.start()
        self.mockRequest = self.patcher4.start()

        self.mockRequest.headers = {'x-identity': TEST_PUBKEY}
        self.mockIdObject.return_value.id = 'my_id'

        #################################################################
        # Mock to Pass @requires_valid_signature
        self.patcher100 = patch('addressimo.storeforward.get_id')
        self.patcher101 = patch('addressimo.storeforward.VerifyingKey')

        self.mockGetId = self.patcher100.start()
        self.mockVerifyingKey = self.patcher101.start()

        self.mockRequest.headers['x-signature'] = 'sigF'.encode('hex')
        self.mockVerifyingKey.from_string.return_value.verify.return_value = True

    def test_go_right(self):

        StoreForward.register()

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockIdObject.call_count)
        self.assertEqual(TEST_PUBKEY, self.mockIdObject.return_value.auth_public_key)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertEqual({'id': 'my_id', 'endpoint': 'https://%s/resolve/my_id' % config.site_url}, self.mockCreateJsonResponse.call_args[1]['data'])

class TestAdd(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.storeforward.PluginManager')
        self.patcher2 = patch('addressimo.storeforward.get_id')
        self.patcher3 = patch('addressimo.storeforward.create_json_response')
        self.patcher4 = patch('addressimo.storeforward.request')
        self.patcher5 = patch('addressimo.storeforward.PaymentRequest')
        self.patcher6 = patch('addressimo.storeforward.PaymentDetails')

        self.mockPluginManager = self.patcher1.start()
        self.mockGetId = self.patcher2.start()
        self.mockCreateJsonResponse = self.patcher3.start()
        self.mockRequest = self.patcher4.start()
        self.mockPaymentRequest = self.patcher5.start()
        self.mockPaymentDetails = self.patcher6.start()

        self.mockRequest.get_json.return_value = {
            'presigned_payment_requests': [
                'pr1'.encode('hex')
            ]
        }

        config.presigned_pr_limit = 100

        self.mockResolver = Mock()
        self.mockPluginManager.get_plugin.return_value = self.mockResolver

        #################################################################
        # Mock to Pass @requires_valid_signature & @requires_public_key
        self.patcher100 = patch('addressimo.storeforward.get_id')
        self.patcher101 = patch('addressimo.storeforward.VerifyingKey')

        self.mockGetId = self.patcher100.start()
        self.mockVerifyingKey = self.patcher101.start()

        self.mockRequest.headers = {
            'x-signature': 'sigF'.encode('hex'),
            'x-identity': TEST_PUBKEY
        }
        self.mockVerifyingKey.from_string.return_value.verify.return_value = True
        self.mockIdObj = Mock()
        self.mockIdObj.auth_public_key = TEST_PUBKEY
        self.mockIdObj.presigned_payment_requests = []
        self.mockPluginManager.get_plugin.return_value.get_config.return_value = self.mockIdObj

    def test_go_right(self):

        StoreForward.add()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(1, self.mockRequest.get_json.call_count)

        self.assertEqual(1, self.mockPaymentRequest.call_count)
        self.assertEqual(1, self.mockPaymentRequest.return_value.ParseFromString.call_count)
        self.assertEqual('pr1', self.mockPaymentRequest.return_value.ParseFromString.call_args[0][0])
        self.assertEqual(1, self.mockPaymentDetails.call_count)
        self.assertEqual(1, self.mockPaymentDetails.return_value.ParseFromString.call_count)
        self.assertEqual(self.mockPaymentRequest.return_value.serialized_payment_details, self.mockPaymentDetails.return_value.ParseFromString.call_args[0][0])

        self.assertEqual(1, len(self.mockIdObj.presigned_payment_requests))
        self.assertEqual(1, self.mockResolver.save.call_count)
        self.assertEqual(self.mockIdObj, self.mockResolver.save.call_args[0][0])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertEqual({'payment_requests_added': 1}, self.mockCreateJsonResponse.call_args[1]['data'])

    def test_no_id(self):

        self.mockResolver.get_config.side_effect = [self.mockIdObj, None]

        StoreForward.add()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(0, self.mockRequest.get_json.call_count)

        self.assertEqual(0, len(self.mockIdObj.presigned_payment_requests))
        self.assertEqual(0, self.mockResolver.save.call_count)

        self.assertEqual(0, self.mockPaymentRequest.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Identifier', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

    def test_no_json(self):

        self.mockRequest.get_json.return_value = None

        StoreForward.add()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(1, self.mockRequest.get_json.call_count)

        self.assertEqual(0, len(self.mockIdObj.presigned_payment_requests))
        self.assertEqual(0, self.mockResolver.save.call_count)

        self.assertEqual(0, self.mockPaymentRequest.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Request', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_no_presigned_requests(self):

        self.mockRequest.get_json.return_value = {'key':'value'}

        StoreForward.add()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(1, self.mockRequest.get_json.call_count)

        self.assertEqual(0, len(self.mockIdObj.presigned_payment_requests))
        self.assertEqual(0, self.mockResolver.save.call_count)

        self.assertEqual(0, self.mockPaymentRequest.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Missing presigned_payment_requests data', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_presigned_requests_datapoint_invalid_type(self):

        self.mockRequest.get_json.return_value = {'presigned_payment_requests':{'key':'value'}}

        StoreForward.add()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(1, self.mockRequest.get_json.call_count)

        self.assertEqual(0, len(self.mockIdObj.presigned_payment_requests))
        self.assertEqual(0, self.mockResolver.save.call_count)

        self.assertEqual(0, self.mockPaymentRequest.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('presigned_payment_requests data must be a list', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_invalid_nonhex_pr(self):

        self.mockRequest.get_json.return_value = {'presigned_payment_requests':['test']}

        StoreForward.add()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(1, self.mockRequest.get_json.call_count)

        self.assertEqual(0, len(self.mockIdObj.presigned_payment_requests))
        self.assertEqual(0, self.mockResolver.save.call_count)

        self.assertEqual(0, self.mockPaymentRequest.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Payment Request Must Be Hex Encoded', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_payment_request_parse_exception(self):

        self.mockPaymentRequest.return_value.ParseFromString.side_effect = Exception

        StoreForward.add()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(1, self.mockRequest.get_json.call_count)

        self.assertEqual(1, self.mockPaymentRequest.call_count)
        self.assertEqual(1, self.mockPaymentRequest.return_value.ParseFromString.call_count)
        self.assertEqual('pr1', self.mockPaymentRequest.return_value.ParseFromString.call_args[0][0])
        self.assertEqual(0, self.mockPaymentDetails.call_count)

        self.assertEqual(0, len(self.mockIdObj.presigned_payment_requests))
        self.assertEqual(0, self.mockResolver.save.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Payment Request Submitted', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_payment_details_parse_exception(self):

        self.mockPaymentDetails.return_value.ParseFromString.side_effect = Exception

        StoreForward.add()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(1, self.mockRequest.get_json.call_count)

        self.assertEqual(1, self.mockPaymentRequest.call_count)
        self.assertEqual(1, self.mockPaymentRequest.return_value.ParseFromString.call_count)
        self.assertEqual('pr1', self.mockPaymentRequest.return_value.ParseFromString.call_args[0][0])
        self.assertEqual(1, self.mockPaymentDetails.call_count)
        self.assertEqual(1, self.mockPaymentDetails.return_value.ParseFromString.call_count)
        self.assertEqual(self.mockPaymentRequest.return_value.serialized_payment_details, self.mockPaymentDetails.return_value.ParseFromString.call_args[0][0])

        self.assertEqual(0, len(self.mockIdObj.presigned_payment_requests))
        self.assertEqual(0, self.mockResolver.save.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Payment Request Submitted', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_too_many_payment_requests(self):

        config.presigned_pr_limit = 2

        self.mockRequest.get_json.return_value = {
            'presigned_payment_requests' : [
                'pr1'.encode('hex'),
                'pr2'.encode('hex'),
                'pr3'.encode('hex'),
                'pr4'.encode('hex'),
            ]
        }

        StoreForward.add()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.get_config.call_count)
        self.assertEqual(1, self.mockRequest.get_json.call_count)

        self.assertEqual(4, self.mockPaymentRequest.call_count)
        self.assertEqual(4, self.mockPaymentRequest.return_value.ParseFromString.call_count)

        self.assertEqual('pr1', self.mockPaymentRequest.return_value.ParseFromString.call_args_list[0][0][0])
        self.assertEqual('pr2', self.mockPaymentRequest.return_value.ParseFromString.call_args_list[1][0][0])
        self.assertEqual('pr3', self.mockPaymentRequest.return_value.ParseFromString.call_args_list[2][0][0])
        self.assertEqual('pr4', self.mockPaymentRequest.return_value.ParseFromString.call_args_list[3][0][0])

        self.assertEqual(4, self.mockPaymentDetails.call_count)
        self.assertEqual(4, self.mockPaymentDetails.return_value.ParseFromString.call_count)
        self.assertEqual(self.mockPaymentRequest.return_value.serialized_payment_details, self.mockPaymentDetails.return_value.ParseFromString.call_args[0][0])

        self.assertEqual(2, len(self.mockIdObj.presigned_payment_requests))
        self.assertEqual(1, self.mockResolver.save.call_count)
        self.assertEqual(self.mockIdObj, self.mockResolver.save.call_args[0][0])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertEqual({'payment_requests_added': 2}, self.mockCreateJsonResponse.call_args[1]['data'])

class TestDelete(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.storeforward.PluginManager')
        self.patcher2 = patch('addressimo.storeforward.get_id')
        self.patcher3 = patch('addressimo.storeforward.create_json_response')
        self.patcher4 = patch('addressimo.storeforward.request')
        self.patcher5 = patch('addressimo.storeforward.PaymentRequest')
        self.patcher6 = patch('addressimo.storeforward.PaymentDetails')

        self.mockPluginManager = self.patcher1.start()
        self.mockGetId = self.patcher2.start()
        self.mockCreateJsonResponse = self.patcher3.start()
        self.mockRequest = self.patcher4.start()
        self.mockPaymentRequest = self.patcher5.start()
        self.mockPaymentDetails = self.patcher6.start()

        self.mockRequest.get_json.return_value = {
            'presigned_payment_requests': [
                'pr1'.encode('hex')
            ]
        }

        config.presigned_pr_limit = 100

        self.mockResolver = Mock()
        self.mockPluginManager.get_plugin.return_value = self.mockResolver

        #################################################################
        # Mock to Pass @requires_valid_signature & @requires_public_key
        self.patcher100 = patch('addressimo.storeforward.get_id')
        self.patcher101 = patch('addressimo.storeforward.VerifyingKey')

        self.mockGetId = self.patcher100.start()
        self.mockVerifyingKey = self.patcher101.start()

        self.mockRequest.headers = {
            'x-signature': 'sigF'.encode('hex'),
            'x-identity': TEST_PUBKEY
        }
        self.mockVerifyingKey.from_string.return_value.verify.return_value = True
        self.mockIdObj = Mock()
        self.mockIdObj.auth_public_key = TEST_PUBKEY
        self.mockIdObj.presigned_payment_requests = []
        self.mockPluginManager.get_plugin.return_value.get_config.return_value = self.mockIdObj

    def test_go_right(self):

        StoreForward.delete()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockResolver.get_config.call_count)
        self.assertEqual(3, self.mockGetId.call_count)
        self.assertEqual(1, self.mockResolver.delete.call_count)
        self.assertEqual(self.mockIdObj, self.mockResolver.delete.call_args[0][0])
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertEqual(204, self.mockCreateJsonResponse.call_args[1]['status'])

    def test_no_id_obj(self):

        self.mockResolver.get_config.side_effect = [self.mockIdObj, None]

        StoreForward.delete()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockResolver.get_config.call_count)
        self.assertEqual(3, self.mockGetId.call_count)
        self.assertEqual(0, self.mockResolver.delete.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Identifier', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

class TestGetCount(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.storeforward.PluginManager')
        self.patcher2 = patch('addressimo.storeforward.get_id')
        self.patcher3 = patch('addressimo.storeforward.create_json_response')
        self.patcher4 = patch('addressimo.storeforward.request')
        self.patcher5 = patch('addressimo.storeforward.PaymentRequest')
        self.patcher6 = patch('addressimo.storeforward.PaymentDetails')

        self.mockPluginManager = self.patcher1.start()
        self.mockGetId = self.patcher2.start()
        self.mockCreateJsonResponse = self.patcher3.start()
        self.mockRequest = self.patcher4.start()
        self.mockPaymentRequest = self.patcher5.start()
        self.mockPaymentDetails = self.patcher6.start()

        self.mockRequest.get_json.return_value = {
            'presigned_payment_requests': [
                'pr1'.encode('hex')
            ]
        }

        self.mockResolver = Mock()
        self.mockPluginManager.get_plugin.return_value = self.mockResolver

        #################################################################
        # Mock to Pass @requires_valid_signature & @requires_public_key
        self.patcher100 = patch('addressimo.storeforward.get_id')
        self.patcher101 = patch('addressimo.storeforward.VerifyingKey')

        self.mockGetId = self.patcher100.start()
        self.mockVerifyingKey = self.patcher101.start()

        self.mockRequest.headers = {
            'x-signature': 'sigF'.encode('hex'),
            'x-identity': TEST_PUBKEY
        }
        self.mockVerifyingKey.from_string.return_value.verify.return_value = True
        self.mockIdObj = Mock()
        self.mockIdObj.auth_public_key = TEST_PUBKEY
        self.mockIdObj.presigned_payment_requests = ['pr1', 'pr2']
        self.mockPluginManager.get_plugin.return_value.get_config.return_value = self.mockIdObj

    def test_go_right(self):

        StoreForward.get_count()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockResolver.get_config.call_count)
        self.assertEqual(3, self.mockGetId.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertEqual({'payment_request_count': 2}, self.mockCreateJsonResponse.call_args[1]['data'])

    def test_no_id_obj(self):

        self.mockResolver.get_config.side_effect = [self.mockIdObj, None]

        StoreForward.get_count()

        self.assertEqual(2, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args_list[1][0][0])
        self.assertEqual(2, self.mockResolver.get_config.call_count)
        self.assertEqual(3, self.mockGetId.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Identifier', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])