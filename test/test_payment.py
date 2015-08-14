__author__ = 'frank'

from mock import Mock, patch
from test import AddressimoTestCase

from addressimo.paymentrequest.payment import *
from addressimo.util import PAYMENT_SIZE_MAX


class TestProcessPayment(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.paymentrequest.payment.request')
        self.patcher2 = patch('addressimo.paymentrequest.payment.create_json_response')
        self.patcher3 = patch('addressimo.paymentrequest.payment.Payment')
        self.patcher4 = patch('addressimo.paymentrequest.payment.PluginManager')
        self.patcher5 = patch('addressimo.paymentrequest.payment.pybitcointools')
        self.patcher6 = patch('addressimo.paymentrequest.payment.submit_transaction')
        self.patcher7 = patch('addressimo.paymentrequest.payment.Payments.create_payment_ack')

        self.mockRequest = self.patcher1.start()
        self.mockCreateJSONResponse = self.patcher2.start()
        self.mockPayment = self.patcher3.start()
        self.mockPluginManager = self.patcher4.start()
        self.mockPyBitcoinTools = self.patcher5.start()
        self.mockSubmitBitcoinTransaction = self.patcher6.start()
        self.mockCreatePaymentAck = self.patcher7.start()

        # Setup request data
        self.mockRequest.headers = {
            'Content-Type': 'application/bitcoin-payment',
            'Accept': 'application/bitcoin-paymentack'
        }

        # Setup payment_request data for validation of Payment
        self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.return_value = {
            'payment_validation_data': '%s' % json.dumps({'address': 100})
        }

        # Setup Payment object
        self.mockPaymentObj = Mock()
        self.mockPaymentObj.merchant_data = 'uuid'
        self.mockPaymentObj.transactions = ['tx1', 'tx2']
        self.mockPaymentObj.memo = 'memo'

        refund_obj = Mock()
        refund_obj.script = 'script'

        self.mockPaymentObj.refund_to = [refund_obj]
        self.mockPayment.return_value = self.mockPaymentObj

        # Setup data for Payment <> PaymentRequest Validation
        outs = {
            'outs': [
                {
                    'script': 'script',
                    'value': 100
                }
            ]
        }
        self.mockPyBitcoinTools.deserialize.return_value = outs
        self.mockPyBitcoinTools.script_to_address.return_value = 'address'

        # Setup return data from submit_transaction for testing set_payment_meta_data
        self.mockSubmitBitcoinTransaction.side_effect = ['txhash1', 'txhash2']

    def test_go_right(self):

        Payments.process_payment('id')

        # Validate calls and counts
        self.assertEqual(0, self.mockCreateJSONResponse.call_count)
        self.assertEqual(1, self.mockPayment.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual('id', self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_args[0][0])

        self.assertEqual(2, self.mockPyBitcoinTools.script_to_address.call_count)

        self.assertEqual(2, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual('tx1', self.mockSubmitBitcoinTransaction.call_args_list[0][0][0])
        self.assertEqual('tx2', self.mockSubmitBitcoinTransaction.call_args_list[1][0][0])

        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual('txhash1', self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_args_list[0][0][0])
        self.assertEqual('memo', self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_args_list[0][0][1])
        self.assertEqual(['script'.encode('hex')], self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_args_list[0][0][2])
        self.assertEqual('txhash2', self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_args_list[1][0][0])
        self.assertEqual('memo', self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_args_list[1][0][1])
        self.assertEqual(['script'.encode('hex')], self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_args_list[1][0][2])

        self.assertEqual(1, self.mockCreatePaymentAck.call_count)
        self.assertEqual(self.mockRequest.data, self.mockCreatePaymentAck.call_args[0][0])

    def test_request_data_missing(self):

        # Setup test case
        self.mockRequest.data = None

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(0, self.mockPayment.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual('Serialized Payment Data Missing', self.mockCreateJSONResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJSONResponse.call_args[0][2])

    def test_invalid_content_type_header(self):

        # Setup test case
        del self.mockRequest.headers['Content-Type']

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(0, self.mockPayment.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual(
            'Invalid Content-Type Header. Expecting application/bitcoin-payment',
            self.mockCreateJSONResponse.call_args[0][1]
        )
        self.assertEqual(400, self.mockCreateJSONResponse.call_args[0][2])

    def test_invalid_accept_header(self):

        # Setup test case
        del self.mockRequest.headers['Accept']

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(0, self.mockPayment.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual(
            'Invalid Accept header. Expect application/bitcoin-paymentack',
            self.mockCreateJSONResponse.call_args[0][1]
        )
        self.assertEqual(400, self.mockCreateJSONResponse.call_args[0][2])

    def test_request_too_large(self):

        # Setup test case
        from os import urandom
        self.mockRequest.data = '%s' % bytearray(urandom(PAYMENT_SIZE_MAX + 1))

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(0, self.mockPayment.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual('Invalid Payment Submitted', self.mockCreateJSONResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJSONResponse.call_args[0][2])

    def test_exception_parsing_payment_data(self):

        # Setup test case
        self.mockPayment.return_value.ParseFromString.side_effect = Exception()

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(1, self.mockPayment.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual('Exception Parsing Payment data.', self.mockCreateJSONResponse.call_args[0][1])
        self.assertEqual(500, self.mockCreateJSONResponse.call_args[0][2])

    def test_merchant_data_missing(self):

        # Setup test case
        self.mockPaymentObj.merchant_data = None

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(1, self.mockPayment.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual('Payment missing merchant_data field.', self.mockCreateJSONResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJSONResponse.call_args[0][2])

    def test_exception_retrieving_payment_request(self):

        # Setup test case
        self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.side_effect = Exception()

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(1, self.mockPayment.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual('Error Retrieving PaymentRequest.', self.mockCreateJSONResponse.call_args[0][1])
        self.assertEqual(500, self.mockCreateJSONResponse.call_args[0][2])

    def test_unknown_payment_request(self):

        # Setup test case
        self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.return_value = None

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(1, self.mockPayment.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual(
            'Unable to Retrieve PaymentRequest associated with Payment.',
            self.mockCreateJSONResponse.call_args[0][1]
        )
        self.assertEqual(404, self.mockCreateJSONResponse.call_args[0][2])

    def test_exception_loading_payment_validation_data(self):

        # Setup test case
        self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.return_value = {'key': 'value'}

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(1, self.mockPayment.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual('Unable to validate Payment.', self.mockCreateJSONResponse.call_args[0][1])
        self.assertEqual(400, self.mockCreateJSONResponse.call_args[0][2])

    def test_payment_not_satisfying_payment_request(self):

        # Setup test case
        self.mockPyBitcoinTools.deserialize.return_value = {}

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(1, self.mockPayment.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(0, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(0, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual(
            'Payment Does Not Satisfy Requirements of PaymentRequest.',
            self.mockCreateJSONResponse.call_args[0][1]
        )
        self.assertEqual(400, self.mockCreateJSONResponse.call_args[0][2])

    def test_exception_submitting_payment_transactions_one_retry(self):

        # Setup test case
        self.mockSubmitBitcoinTransaction.side_effect = [Exception('Failed to connect'), 'txhash1', 'txhash2']

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(0, self.mockCreateJSONResponse.call_count)
        self.assertEqual(1, self.mockPayment.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(2, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(3, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(2, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(1, self.mockCreatePaymentAck.call_count)

    def test_exception_submitting_payment_transactions_retries_exceeded(self):

        # Setup test case
        config.payment_submit_tx_retries = 1
        self.mockSubmitBitcoinTransaction.side_effect = Exception('Failed to connect')

        Payments.process_payment('id')

        # Validate call counts
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)
        self.assertEqual(1, self.mockPayment.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_payment_request_meta_data.call_count)
        self.assertEqual(2, self.mockPyBitcoinTools.script_to_address.call_count)
        self.assertEqual(2, self.mockSubmitBitcoinTransaction.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.return_value.set_payment_meta_data.call_count)
        self.assertEqual(0, self.mockCreatePaymentAck.call_count)

        # Validate create_json_response args
        self.assertFalse(self.mockCreateJSONResponse.call_args[0][0])
        self.assertEqual(
            'Unable to submit all transactions to the Bitcoin network. Please resubmit Payment.',
            self.mockCreateJSONResponse.call_args[0][1]
        )
        self.assertEqual(500, self.mockCreateJSONResponse.call_args[0][2])


class TestCreatePaymentAck(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.paymentrequest.payment.Response')

        self.mockResponse = self.patcher1.start()

        from addressimo.paymentrequest.paymentrequest_pb2 import Payment
        self.payment_details = Payment()
        self.payment_details.memo = 'foo'

    def test_go_right_with_memo(self):

        Payments.create_payment_ack(self.payment_details.SerializeToString(), 'memo')

        self.assertEqual(1, self.mockResponse.call_count)
        self.assertEqual('\n\x05"\x03foo\x12\x04memo', self.mockResponse.call_args[1]['response'])
        self.assertEqual(200, self.mockResponse.call_args[1]['status'])
        self.assertEqual('application/bitcoin-paymentack', self.mockResponse.call_args[1]['mimetype'])
        self.assertDictEqual({'Content-Transfer-Encoding': 'binary'}, self.mockResponse.call_args[1].get('headers'))

    def test_go_right_without_memo(self):

        Payments.create_payment_ack(self.payment_details.SerializeToString())

        self.assertEqual(1, self.mockResponse.call_count)
        self.assertEqual('\n\x05"\x03foo\x12\x00', self.mockResponse.call_args[1]['response'])
        self.assertEqual(200, self.mockResponse.call_args[1]['status'])
        self.assertEqual('application/bitcoin-paymentack', self.mockResponse.call_args[1]['mimetype'])
        self.assertDictEqual({'Content-Transfer-Encoding': 'binary'}, self.mockResponse.call_args[1].get('headers'))


class TestRetrieveRefundAddress(AddressimoTestCase):

    def setUp(self):
        self.patcher1 = patch('addressimo.paymentrequest.payment.PluginManager')
        self.patcher2 = patch('addressimo.paymentrequest.payment.create_json_response')

        self.mockPluginManager = self.patcher1.start()
        self.mockCreateJSONResponse = self.patcher2.start()

        self.mockPluginManager.get_plugin.return_value.get_refund_address_from_tx_hash.return_value = {'key': 'value'}

        #################################################################
        # Mock to Pass @requires_valid_signature & @requires_public_key
        self.patcher100 = patch('addressimo.util.get_id')
        self.patcher101 = patch('addressimo.util.VerifyingKey')
        self.patcher102 = patch('addressimo.util.request')
        self.patcher103 = patch('addressimo.storeforward.request')
        self.patcher104 = patch('addressimo.storeforward.get_id')
        self.patcher105 = patch('addressimo.storeforward.PluginManager')

        self.mockGetId = self.patcher100.start()
        self.mockVerifyingKey = self.patcher101.start()
        self.mockUtilRequest = self.patcher102.start()
        self.mockSFRequest = self.patcher103.start()
        self.mockSFGetId = self.patcher104.start()
        self.mockSFPluginManager = self.patcher105.start()

        self.mockSFRequest.headers = {
            'x-identity': self.mockSFPluginManager.get_plugin.return_value.get_id_obj.return_value.auth_public_key
        }

        self.mockVerifyingKey.from_string.return_value.verify.return_value = True
        #################################################################

    def test_go_right(self):

        Payments.retrieve_refund_address('id', 'tx')

        # Validate call counts
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.get_refund_address_from_tx_hash.call_count)
        self.assertEqual(1, self.mockCreateJSONResponse.call_count)

        # Validate call args
        self.assertEqual(
            'tx',
            self.mockPluginManager.get_plugin.return_value.get_refund_address_from_tx_hash.call_args[0][0]
        )

        self.assertTrue(self.mockCreateJSONResponse.call_args[1].get('success'))
        self.assertEqual(
            self.mockPluginManager.get_plugin.return_value.get_refund_address_from_tx_hash.return_value,
            self.mockCreateJSONResponse.call_args[1].get('data')
        )
        self.assertEqual(200, self.mockCreateJSONResponse.call_args[1].get('status'))



