__author__ = 'frank'

from flask import request, Response
from time import sleep

import json
import pybitcointools

from addressimo.config import config
from addressimo.blockchain import submit_transaction
from addressimo.plugin import PluginManager
from addressimo.paymentrequest.paymentrequest_pb2 import Payment, PaymentACK
from addressimo.storeforward import requires_public_key
from addressimo.util import create_json_response, LogUtil, PAYMENT_SIZE_MAX, requires_valid_signature

log = LogUtil.setup_logging()


class Payments:

    @staticmethod
    def process_payment(id):

        # Validate Payment POST request follows bip-0070 specification
        if not request.data:
            log.warn('Serialized Payment Data Missing')
            return create_json_response(False, 'Serialized Payment Data Missing', 400)

        if not request.headers.get('Content-Type') == 'application/bitcoin-payment':
            log.warn('Invalid Content-Type Header: %s' % request.headers.get('Content-Type'))
            return create_json_response(False, 'Invalid Content-Type Header. Expecting application/bitcoin-payment', 400)

        if not request.headers.get('Accept') == 'application/bitcoin-paymentack':
            log.warn('Invalid Accept Header: %s' % request.headers.get('Accept'))
            return create_json_response(False, 'Invalid Accept header. Expect application/bitcoin-paymentack', 400)

        if len(request.data) > PAYMENT_SIZE_MAX:
            log.warn('Rejecting Payment for Size [ACCEPTED: %d bytes | ACTUAL: %d bytes]' %
                     (PAYMENT_SIZE_MAX, len(request.data)))
            return create_json_response(False, 'Invalid Payment Submitted', 400)

        # Parse Payment
        payment = Payment()
        try:
            payment.ParseFromString(request.data)
        except Exception as e:
            log.error('Exception Parsing Payment data: %s' % str(e))
            return create_json_response(False, 'Exception Parsing Payment data.', 500)

        if not payment.merchant_data:
            log.warn('Received Payment with Missing merchant_data')
            return create_json_response(False, 'Payment missing merchant_data field.', 400)

        # Validate Payment satisfies associated PaymentRequest conditions
        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)

        try:
            payment_request = resolver.get_payment_request_meta_data(id)

        except Exception as e:
            log.error('Error Retrieving PaymentRequest for Payment validation [PR ID: %s]: %s' % (payment.merchant_data, str(e)))
            return create_json_response(False, 'Error Retrieving PaymentRequest.', 500)

        if not payment_request:
            log.warn('Received Payment for Unknown PaymentRequest [PR ID: %s]' % payment.merchant_data)
            return create_json_response(False, 'Unable to Retrieve PaymentRequest associated with Payment.', 404)

        try:
            payment_validation_addresses = json.loads(payment_request['payment_validation_data'])
        except Exception as e:
            log.warn('Error parsing payment_validation_data [PR ID: %s]: %s' % (payment.merchant_data, str(e)))
            return create_json_response(False, 'Unable to validate Payment.', 400)

        # Validate transactions match addresses and amounts requested in PaymentRequest
        for payment_tx in payment.transactions:
            result = pybitcointools.deserialize(payment_tx)
            for vout in result.get('outs', []):
                address = pybitcointools.script_to_address(vout['script'])
                amount = vout['value']

                if address in payment_validation_addresses.keys() and int(payment_validation_addresses[address]) == int(amount):
                    del payment_validation_addresses[address]

        if payment_validation_addresses:
            log.warn('Payment Does Not Satisfy Requirements of PaymentRequest. Rejecting. [PR ID: %s]' % payment.merchant_data)
            return create_json_response(False, 'Payment Does Not Satisfy Requirements of PaymentRequest.', 400)

        bitcoin_tx_hashes = []
        for payment_tx in payment.transactions:
            for _ in range(config.payment_submit_tx_retries):
                try:
                    # Necessary evil test code to allow functional testing without submitting (fail) real transactions
                    if not request.headers.get('Test-Transaction'):
                        bitcoin_tx_hashes.append(submit_transaction(payment_tx))
                    else:
                        bitcoin_tx_hashes.append('testtxhash')

                    break
                except Exception as e:
                    log.error('Exception Submitting Bitcoin Transaction: %s' % str(e))
                    sleep(.3)

        if len(bitcoin_tx_hashes) != len(payment.transactions):
            log.error(
                'Unable To Submit All Payment Transactions To Bitcoin [Payment TX Count: %d | Submitted TX Count: %d]' %
                (len(payment.transactions), len(bitcoin_tx_hashes))
            )

            return create_json_response(
                False,
                'Unable to submit all transactions to the Bitcoin network. Please resubmit Payment.',
                500
            )

        # Store Payment meta data used for Refund request
        for tx_hash in bitcoin_tx_hashes:
            refund_list = [x.script.encode('hex') for x in payment.refund_to]
            resolver.set_payment_meta_data(tx_hash, payment.memo, refund_list)

        return Payments.create_payment_ack(request.data)

    @staticmethod
    def create_payment_ack(payment_data, memo=''):
        headers = {
            'Content-Transfer-Encoding': 'binary'
        }

        payment_ack = PaymentACK()
        payment_ack.payment.ParseFromString(payment_data)
        payment_ack.memo = memo

        log.info('Sending PaymentACK')

        return Response(response=payment_ack.SerializeToString(), status=200, mimetype='application/bitcoin-paymentack', headers=headers)

    @staticmethod
    @requires_public_key
    @requires_valid_signature
    def retrieve_refund_address(id, tx):

        result = PluginManager.get_plugin('RESOLVER', config.resolver_type).get_refund_address_from_tx_hash(tx)

        return create_json_response(success=True, data=result, status=200)
