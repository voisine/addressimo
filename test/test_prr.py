__author__ = 'mdavid'

# System Imports
from mock import MagicMock, Mock, patch
from test import AddressimoTestCase

from addressimo.paymentrequest.prr import *

TEST_PRIVKEY = '9d5a020344dd6dffc8a79e9c0bce8148ab0bce08162b6a44fec40cb113e16647'
TEST_PUBKEY = 'ac79cd6b0ac5f2a6234996595cb2d91fceaa0b9d9a6495f12f1161c074587bd19ae86928bddea635c930c09ea9c7de1a6a9c468f9afd18fbaeed45d09564ded6'

class TestSubmitPrr(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.paymentrequest.prr.PluginManager')
        self.patcher2 = patch('addressimo.paymentrequest.prr.create_json_response')
        self.patcher3 = patch('addressimo.paymentrequest.prr.request')
        self.patcher4 = patch('addressimo.paymentrequest.prr.datetime')
        self.patcher5 = patch('addressimo.paymentrequest.prr.crypto')

        self.mockPluginManager = self.patcher1.start()
        self.mockCreateJsonResponse = self.patcher2.start()
        self.mockRequest = self.patcher3.start()
        self.mockDatetime = self.patcher4.start()
        self.mockCrypto = self.patcher5.start()

        # Setup Go Right Data
        self.request_data = {
            'amount': 75,
            'notification_url': 'https://notify.me/longId',
            'x509_cert': '--- START CERT --- ... --- END CERT ---',
            'signature': 'test_signature'
        }

        self.ret_prr_data = {"id":"prr_id"}

        self.mock_id_obj = Mock()
        self.mock_id_obj.prr_only = True
        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = self.mock_id_obj
        self.mockPluginManager.get_plugin.return_value.add_prr.return_value = self.ret_prr_data
        self.mockDatetime.utcnow.return_value = datetime(2015, 6, 13, 2, 43, 0)

        self.mockRequest.headers = {'X-Identity':'test_pubkey'}
        self.mockRequest.get_json.return_value = self.request_data
        self.mockRequest.url = 'test_url'
        self.mockRequest.data = 'test_data'

        #################################################################
        # Mock to Pass @requires_valid_signature
        self.patcher100 = patch('addressimo.util.get_id')
        self.patcher101 = patch('addressimo.util.VerifyingKey')
        self.patcher102 = patch('addressimo.util.request')

        self.mockGetId = self.patcher100.start()
        self.mockVerifyingKey = self.patcher101.start()
        self.mockUtilRequest = self.patcher102.start()

        self.mockRequest.headers['x-signature'] = 'sigF'.encode('hex')
        self.mockVerifyingKey.from_string.return_value.verify.return_value = True

    def test_go_right(self):

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(1, self.mockDatetime.utcnow.call_count)

        self.assertEqual(1, self.mockCrypto.load_certificate.call_count)
        self.assertEqual(self.mockCrypto.FILETYPE_PEM, self.mockCrypto.load_certificate.call_args[0][0])
        self.assertEqual(self.request_data['x509_cert'], self.mockCrypto.load_certificate.call_args[0][1])

        self.assertEqual(1, self.mockCrypto.verify.call_count)
        self.assertEqual(self.mockCrypto.load_certificate.return_value, self.mockCrypto.verify.call_args[0][0])
        self.assertEqual(self.request_data['signature'], self.mockCrypto.verify.call_args[0][1])
        self.assertEqual("test_urltest_data", self.mockCrypto.verify.call_args[0][2])
        self.assertEqual("sha1", self.mockCrypto.verify.call_args[0][3])

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.add_prr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.add_prr.call_args[0][0])

        prr_data = self.mockPluginManager.get_plugin.return_value.add_prr.call_args[0][1]
        self.assertEqual('test_pubkey', prr_data['sender_pubkey'])
        self.assertEqual(self.request_data['amount'], prr_data['amount'])
        self.assertEqual(self.request_data['notification_url'], prr_data['notification_url'])
        self.assertEqual(self.request_data['x509_cert'], prr_data['x509_cert'])
        self.assertEqual(self.request_data['signature'], prr_data['signature'])
        self.assertEqual(datetime(2015,6,13,2,43,0), prr_data['submit_date'])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertEqual(202, self.mockCreateJsonResponse.call_args[1]['status'])
        self.assertIn('Location', self.mockCreateJsonResponse.call_args[1]['headers'])
        self.assertEqual('https://%s/pr/prr_id' % config.site_url, self.mockCreateJsonResponse.call_args[1]['headers']['Location'])

    def test_id_obj_resolve_exception(self):

        self.mockPluginManager.get_plugin.return_value.get_id_obj.side_effect = Exception()

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(0, self.mockRequest.get_json.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Exception Occurred, Please Try Again Later.', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(500, self.mockCreateJsonResponse.call_args[0][2])

    def test_no_id_obj(self):

        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = None

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(0, self.mockRequest.get_json.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('ID Not Recognized', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

    def test_prr_only_flag_false(self):

        self.mock_id_obj.prr_only = False

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(0, self.mockRequest.get_json.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid PaymentRequest Request Endpoint', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_no_json_data(self):

        self.mockRequest.get_json.return_value = None

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(0, self.mockDatetime.utcnow.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Request', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_missing_signature(self):

        del self.request_data['signature']

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(1, self.mockDatetime.utcnow.call_count)

        self.assertEqual(0, self.mockCrypto.load_certificate.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Requests including x509 cert must include signature', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_cert_load_exception(self):

        self.mockCrypto.load_certificate.side_effect = Exception()

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(1, self.mockDatetime.utcnow.call_count)

        self.assertEqual(1, self.mockCrypto.load_certificate.call_count)
        self.assertEqual(self.mockCrypto.FILETYPE_PEM, self.mockCrypto.load_certificate.call_args[0][0])
        self.assertEqual(self.request_data['x509_cert'], self.mockCrypto.load_certificate.call_args[0][1])

        self.assertEqual(0, self.mockCrypto.verify.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid x509 Certificate', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_signture_verification_failure(self):

        self.mockCrypto.verify.side_effect = Exception()

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(1, self.mockDatetime.utcnow.call_count)

        self.assertEqual(1, self.mockCrypto.load_certificate.call_count)
        self.assertEqual(self.mockCrypto.FILETYPE_PEM, self.mockCrypto.load_certificate.call_args[0][0])
        self.assertEqual(self.request_data['x509_cert'], self.mockCrypto.load_certificate.call_args[0][1])

        self.assertEqual(1, self.mockCrypto.verify.call_count)
        self.assertEqual(self.mockCrypto.load_certificate.return_value, self.mockCrypto.verify.call_args[0][0])
        self.assertEqual(self.request_data['signature'], self.mockCrypto.verify.call_args[0][1])
        self.assertEqual("test_urltest_data", self.mockCrypto.verify.call_args[0][2])
        self.assertEqual("sha1", self.mockCrypto.verify.call_args[0][3])

        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.add_prr.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Signature Verification Error', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(401, self.mockCreateJsonResponse.call_args[0][2])

    def test_add_prr_missing_return_data(self):

        self.mockPluginManager.get_plugin.return_value.add_prr.return_value = None

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(1, self.mockDatetime.utcnow.call_count)

        self.assertEqual(1, self.mockCrypto.load_certificate.call_count)
        self.assertEqual(self.mockCrypto.FILETYPE_PEM, self.mockCrypto.load_certificate.call_args[0][0])
        self.assertEqual(self.request_data['x509_cert'], self.mockCrypto.load_certificate.call_args[0][1])

        self.assertEqual(1, self.mockCrypto.verify.call_count)
        self.assertEqual(self.mockCrypto.load_certificate.return_value, self.mockCrypto.verify.call_args[0][0])
        self.assertEqual(self.request_data['signature'], self.mockCrypto.verify.call_args[0][1])
        self.assertEqual("test_urltest_data", self.mockCrypto.verify.call_args[0][2])
        self.assertEqual("sha1", self.mockCrypto.verify.call_args[0][3])

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.add_prr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.add_prr.call_args[0][0])

        prr_data = self.mockPluginManager.get_plugin.return_value.add_prr.call_args[0][1]
        self.assertEqual('test_pubkey', prr_data['sender_pubkey'])
        self.assertEqual(self.request_data['amount'], prr_data['amount'])
        self.assertEqual(self.request_data['notification_url'], prr_data['notification_url'])
        self.assertEqual(self.request_data['x509_cert'], prr_data['x509_cert'])
        self.assertEqual(self.request_data['signature'], prr_data['signature'])
        self.assertEqual(datetime(2015,6,13,2,43,0), prr_data['submit_date'])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Unknown System Error, Please Try Again Later', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(500, self.mockCreateJsonResponse.call_args[0][2])

    def test_add_prr_exception(self):

        self.mockPluginManager.get_plugin.return_value.add_prr.side_effect = Exception()

        result = PRR.submit_prr('test_id')

        self.assertIsNotNone(result)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(1, self.mockDatetime.utcnow.call_count)

        self.assertEqual(1, self.mockCrypto.load_certificate.call_count)
        self.assertEqual(self.mockCrypto.FILETYPE_PEM, self.mockCrypto.load_certificate.call_args[0][0])
        self.assertEqual(self.request_data['x509_cert'], self.mockCrypto.load_certificate.call_args[0][1])

        self.assertEqual(1, self.mockCrypto.verify.call_count)
        self.assertEqual(self.mockCrypto.load_certificate.return_value, self.mockCrypto.verify.call_args[0][0])
        self.assertEqual(self.request_data['signature'], self.mockCrypto.verify.call_args[0][1])
        self.assertEqual("test_urltest_data", self.mockCrypto.verify.call_args[0][2])
        self.assertEqual("sha1", self.mockCrypto.verify.call_args[0][3])

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.add_prr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.add_prr.call_args[0][0])

        prr_data = self.mockPluginManager.get_plugin.return_value.add_prr.call_args[0][1]
        self.assertEqual('test_pubkey', prr_data['sender_pubkey'])
        self.assertEqual(self.request_data['amount'], prr_data['amount'])
        self.assertEqual(self.request_data['notification_url'], prr_data['notification_url'])
        self.assertEqual(self.request_data['x509_cert'], prr_data['x509_cert'])
        self.assertEqual(self.request_data['signature'], prr_data['signature'])
        self.assertEqual(datetime(2015,6,13,2,43,0), prr_data['submit_date'])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Unknown System Error, Please Try Again Later', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(500, self.mockCreateJsonResponse.call_args[0][2])

class TestGetQueuedPrRequests(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.paymentrequest.prr.PluginManager')
        self.patcher2 = patch('addressimo.paymentrequest.prr.create_json_response')
        self.patcher3 = patch('addressimo.paymentrequest.prr.request')

        self.mockPluginManager = self.patcher1.start()
        self.mockCreateJsonResponse = self.patcher2.start()
        self.mockRequest = self.patcher3.start()

        # Setup Go Right Data
        self.queued_prrs = [{"id":"id1"},{"id":"id2"}]

        self.mock_id_obj = Mock()
        self.mock_id_obj.prr_only = True
        self.mockPluginManager.get_plugin.return_value.get_prrs.return_value = self.queued_prrs

        #################################################################
        # Mock to Pass @requires_valid_signature & @requires_public_key
        self.patcher100 = patch('addressimo.storeforward.get_id')
        self.patcher101 = patch('addressimo.util.VerifyingKey')
        self.patcher102 = patch('addressimo.storeforward.request')
        self.patcher103 = patch('addressimo.storeforward.PluginManager')
        self.patcher104 = patch('addressimo.util.get_id')
        self.patcher105 = patch('addressimo.util.request')

        self.mockGetId = self.patcher100.start()
        self.mockVerifyingKey = self.patcher101.start()
        self.mockIntRequest = self.patcher102.start()
        self.mockIntPluginManager = self.patcher103.start()
        self.mockIntGetId = self.patcher104.start()
        self.mockUtilRequest = self.patcher105.start()

        self.mockUtilRequest.headers = {
            'x-signature': 'sigF'.encode('hex'),
            'x-identity': TEST_PUBKEY
        }
        self.mockVerifyingKey.from_string.return_value.verify.return_value = True
        self.mockIdObj = Mock()
        self.mockIdObj.auth_public_key = TEST_PUBKEY
        self.mockIdObj.presigned_payment_requests = ['pr1', 'pr2']
        self.mockIntPluginManager.get_plugin.return_value.get_id_obj.return_value = self.mockIdObj
        self.mockIntRequest.headers = {"x-identity": TEST_PUBKEY}

    def test_go_right(self):

        PRR.get_queued_pr_requests('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_prrs.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.get_prrs.call_args[0][0])
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)

        resp_data = self.mockCreateJsonResponse.call_args[1]['data']
        self.assertIsNotNone(resp_data)
        self.assertEqual(2, resp_data.get('count'))
        self.assertIn({"id":"id1"}, resp_data.get('requests'))
        self.assertIn({"id":"id2"}, resp_data.get('requests'))

    def test_invalid_id(self):

        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = None

        PRR.get_queued_pr_requests('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_prrs.call_count)
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Identifier', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

    def test_get_prrs_exception(self):

        self.mockPluginManager.get_plugin.return_value.get_prrs.side_effect = Exception()

        PRR.get_queued_pr_requests('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_prrs.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.get_prrs.call_args[0][0])
        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Unable to Retrieve Queued PR Requests', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(500, self.mockCreateJsonResponse.call_args[0][2])

class TestSubmitReturnPr(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.paymentrequest.prr.PluginManager')
        self.patcher2 = patch('addressimo.paymentrequest.prr.create_json_response')
        self.patcher3 = patch('addressimo.paymentrequest.prr.request')
        self.patcher4 = patch('addressimo.paymentrequest.prr.datetime')

        self.mockPluginManager = self.patcher1.start()
        self.mockCreateJsonResponse = self.patcher2.start()
        self.mockRequest = self.patcher3.start()
        self.mockDatetime = self.patcher4.start()

        # Setup Go Right Data
        self.mockRequest.get_json.return_value = {
            "ready_requests": [
                {"id":"id1", "receiver_pubkey":"thisismypubkey", "encrypted_payment_request":"pr1"},
                {"id":"id2", "receiver_pubkey":"alsoThisIsMyPubKey", "encrypted_payment_request":"pr2"},
            ]
        }

        self.mock_id_obj = Mock()
        self.mock_id_obj.prr_only = True
        self.mockDatetime.utcnow.return_value = 'utcnow'

        #################################################################
        # Mock to Pass @requires_valid_signature & @requires_public_key
        self.patcher100 = patch('addressimo.storeforward.get_id')
        self.patcher101 = patch('addressimo.util.VerifyingKey')
        self.patcher102 = patch('addressimo.storeforward.request')
        self.patcher103 = patch('addressimo.storeforward.PluginManager')
        self.patcher104 = patch('addressimo.util.get_id')
        self.patcher105 = patch('addressimo.util.request')

        self.mockGetId = self.patcher100.start()
        self.mockVerifyingKey = self.patcher101.start()
        self.mockIntRequest = self.patcher102.start()
        self.mockIntPluginManager = self.patcher103.start()
        self.mockIntGetId = self.patcher104.start()
        self.mockUtilRequest = self.patcher105.start()

        self.mockUtilRequest.headers = {
            'x-signature': 'sigF'.encode('hex'),
            'x-identity': TEST_PUBKEY
        }
        self.mockVerifyingKey.from_string.return_value.verify.return_value = True
        self.mockIdObj = Mock()
        self.mockIdObj.auth_public_key = TEST_PUBKEY
        self.mockIdObj.presigned_payment_requests = ['pr1', 'pr2']
        self.mockIntPluginManager.get_plugin.return_value.get_id_obj.return_value = self.mockIdObj
        self.mockIntRequest.headers = {"x-identity": TEST_PUBKEY}

    def test_go_right(self):

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.add_return_pr.call_count)

        add_pr_call = self.mockPluginManager.get_plugin.return_value.add_return_pr
        json_data = self.mockRequest.get_json.return_value
        self.assertEqual('test_id', add_pr_call.call_args_list[0][0][0])
        self.assertEqual('utcnow', json_data['ready_requests'][0]['submit_date'])
        self.assertEqual(json_data['ready_requests'][0], add_pr_call.call_args_list[0][0][1])

        self.assertEqual('test_id', add_pr_call.call_args_list[1][0][0])
        self.assertEqual('utcnow', json_data['ready_requests'][1]['submit_date'])
        self.assertEqual(json_data['ready_requests'][1], add_pr_call.call_args_list[1][0][1])

        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.delete_prr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args_list[0][0][0])
        self.assertEqual('id1', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args_list[0][0][1])
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args_list[1][0][0])
        self.assertEqual('id2', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args_list[1][0][1])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertEqual(2, self.mockCreateJsonResponse.call_args[1]['data']['accept_count'])

    def test_missing_id_obj(self):

        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value = None

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(0, self.mockRequest.get_json.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Identifier', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

    def test_not_prr_only(self):

        self.mockPluginManager.get_plugin.return_value.get_id_obj.return_value.prr_only = False

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(0, self.mockRequest.get_json.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid PaymentRequest Request Endpoint', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_request_not_json(self):

        self.mockRequest.get_json.return_value = None

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.add_return_pr.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Invalid Request', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_missing_ready_requests(self):

        del self.mockRequest.get_json.return_value['ready_requests']
        self.mockRequest.get_json.return_value['key'] = 'value'

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.add_return_pr.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Missing or Empty ready_requests list', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_empty_ready_requests(self):

        self.mockRequest.get_json.return_value['ready_requests'] = []

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.add_return_pr.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Missing or Empty ready_requests list', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_ready_requests_non_list(self):

        self.mockRequest.get_json.return_value['ready_requests'] = 'bob'

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.add_return_pr.call_count)

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Missing or Empty ready_requests list', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])

    def test_missing_required_field(self):

        del self.mockRequest.get_json.return_value['ready_requests'][0]['receiver_pubkey']

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.add_return_pr.call_count)

        add_pr_call = self.mockPluginManager.get_plugin.return_value.add_return_pr
        json_data = self.mockRequest.get_json.return_value

        self.assertNotIn('submit_data', json_data['ready_requests'][0])
        self.assertEqual('test_id', add_pr_call.call_args[0][0])
        self.assertEqual('utcnow', json_data['ready_requests'][1]['submit_date'])
        self.assertEqual(json_data['ready_requests'][1], add_pr_call.call_args[0][1])

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.delete_prr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args[0][0])
        self.assertEqual('id2', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args[0][1])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Submitted Return PaymentRequests contain errors, please see failures field for more information', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])
        self.assertEqual(1, self.mockCreateJsonResponse.call_args[0][3]['accept_count'])
        self.assertEqual('Missing Required Fields: id, receiver_pubkey, and/or encrypted_payment_request', self.mockCreateJsonResponse.call_args[0][3]['failures']['id1'][0])

    def test_add_return_pr_exception(self):

        self.mockPluginManager.get_plugin.return_value.add_return_pr.side_effect = [Exception('Test Error'), True]

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.add_return_pr.call_count)

        add_pr_call = self.mockPluginManager.get_plugin.return_value.add_return_pr
        json_data = self.mockRequest.get_json.return_value
        self.assertEqual('test_id', add_pr_call.call_args_list[0][0][0])
        self.assertEqual('utcnow', json_data['ready_requests'][0]['submit_date'])
        self.assertEqual(json_data['ready_requests'][0], add_pr_call.call_args_list[0][0][1])

        self.assertEqual('test_id', add_pr_call.call_args_list[1][0][0])
        self.assertEqual('utcnow', json_data['ready_requests'][1]['submit_date'])
        self.assertEqual(json_data['ready_requests'][1], add_pr_call.call_args_list[1][0][1])

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.delete_prr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args[0][0])
        self.assertEqual('id2', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args[0][1])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('Submitted Return PaymentRequests contain errors, please see failures field for more information', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJsonResponse.call_args[0][2])
        self.assertEqual(1, self.mockCreateJsonResponse.call_args[0][3]['accept_count'])
        self.assertEqual('Unable to Process Return PaymentRequest', self.mockCreateJsonResponse.call_args[0][3]['failures']['id1'][0])

    def test_delete_prr_exception(self):

        self.mockPluginManager.get_plugin.return_value.delete_prr.side_effect = Exception()

        PRR.submit_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockRequest.get_json.call_count)
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.add_return_pr.call_count)

        add_pr_call = self.mockPluginManager.get_plugin.return_value.add_return_pr
        json_data = self.mockRequest.get_json.return_value
        self.assertEqual('test_id', add_pr_call.call_args_list[0][0][0])
        self.assertEqual('utcnow', json_data['ready_requests'][0]['submit_date'])
        self.assertEqual(json_data['ready_requests'][0], add_pr_call.call_args_list[0][0][1])

        self.assertEqual('test_id', add_pr_call.call_args_list[1][0][0])
        self.assertEqual('utcnow', json_data['ready_requests'][1]['submit_date'])
        self.assertEqual(json_data['ready_requests'][1], add_pr_call.call_args_list[1][0][1])

        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.delete_prr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args_list[0][0][0])
        self.assertEqual('id1', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args_list[0][0][1])
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args_list[1][0][0])
        self.assertEqual('id2', self.mockPluginManager.get_plugin.return_value.delete_prr.call_args_list[1][0][1])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertEqual(2, self.mockCreateJsonResponse.call_args[1]['data']['accept_count'])

class TestGetReturnPr(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.paymentrequest.prr.PluginManager')
        self.patcher2 = patch('addressimo.paymentrequest.prr.create_json_response')

        self.mockPluginManager = self.patcher1.start()
        self.mockCreateJsonResponse = self.patcher2.start()

        self.mockPluginManager.get_plugin.return_value.get_return_pr.return_value = {
            'encrypted_payment_request': 'im_encrypted',
            'receiver_pubkey': 'HereIsMyPubkey'
        }

    def test_go_right(self):

        PRR.get_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_return_pr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.get_return_pr.call_args[0][0])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertIn('encrypted_payment_request', self.mockCreateJsonResponse.call_args[1]['data'])
        self.assertEqual('im_encrypted', self.mockCreateJsonResponse.call_args[1]['data']['encrypted_payment_request'])
        self.assertIn('receiver_pubkey', self.mockCreateJsonResponse.call_args[1]['data'])
        self.assertEqual('HereIsMyPubkey', self.mockCreateJsonResponse.call_args[1]['data']['receiver_pubkey'])

    def test_no_return_pr(self):

        self.mockPluginManager.get_plugin.return_value.get_return_pr.return_value = None

        PRR.get_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_return_pr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.get_return_pr.call_args[0][0])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('PaymentRequest Not Found or Not Yet Ready', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(404, self.mockCreateJsonResponse.call_args[0][2])

    def test_get_return_pr_exceptiodirectn(self):

        self.mockPluginManager.get_plugin.return_value.get_return_pr.side_effect = Exception()

        PRR.get_return_pr('test_id')

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_return_pr.call_count)
        self.assertEqual('test_id', self.mockPluginManager.get_plugin.return_value.get_return_pr.call_args[0][0])

        self.assertEqual(1, self.mockCreateJsonResponse.call_count)
        self.assertFalse(self.mockCreateJsonResponse.call_args[0][0])
        self.assertEqual('PaymentRequest Not Found', self.mockCreateJsonResponse.call_args[0][1])
        self.assertEqual(500, self.mockCreateJsonResponse.call_args[0][2])