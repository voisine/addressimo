__author__ = 'Matt David'

from addressimo.config import config
from addressimo.data import IdObject
from addressimo.paymentrequest.paymentrequest_pb2 import PaymentRequest, PaymentDetails
from addressimo.plugin import PluginManager
from addressimo.util import LogUtil, create_json_response, get_id, requires_valid_signature, PAYMENT_REQUEST_SIZE_MAX

from flask import request
from functools import wraps

log = LogUtil.setup_logging()

def requires_public_key(f):

    @wraps(f)
    def is_pubkey_for_id(*args, **kwargs):

        id = get_id()
        if not id:
            log.info('ID Unavailable from request: %s' % request.url)
            return create_json_response(False, 'Unknown Endpoint', 404)

        if not request.headers.get('x-identity'):
            log.info('No Pubkey Exists in Request, Returning False [ID: %s]' % id)
            return create_json_response(False, 'Missing x-identity header', 400)

        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        id_obj = resolver.get_id_obj(id)
        if not id_obj:
            log.info('No Data Exists for Given ID, Failing [ID: %s]' % id)
            return create_json_response(False, 'ID Not Recognized', 404)

        if request.headers.get('x-identity') == id_obj.auth_public_key:
            return f(*args, **kwargs)

        return create_json_response(False, 'ID Not Recognized', 404)

    return is_pubkey_for_id

class StoreForward:

    @staticmethod
    @requires_valid_signature
    def register():

        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)

        id_obj = IdObject()
        id_obj.auth_public_key = request.headers.get('x-identity')
        resolver.save(id_obj)

        return create_json_response(data={'id': id_obj.id, 'endpoint': 'https://%s/resolve/%s' % (config.site_url, id_obj.id)})

    @staticmethod
    @requires_public_key
    @requires_valid_signature
    def add():

        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        id_obj = resolver.get_id_obj(get_id())
        if not id_obj:
            return create_json_response(False, 'Invalid Identifier', 404)

        rdata = None
        try:
            rdata = request.get_json()
        except Exception as e:
            log.warn("Exception Parsing JSON: %s" % str(e))
            return create_json_response(False, 'Invalid Request', 400)

        if not rdata:
            return create_json_response(False, 'Invalid Request', 400)

        pr_list = rdata.get('presigned_payment_requests')

        if not pr_list:
            return create_json_response(False, 'Missing presigned_payment_requests data', 400)

        if not isinstance(pr_list, list):
            return create_json_response(False, 'presigned_payment_requests data must be a list', 400)

        # Validate PaymentRequests
        for pr in pr_list:

            try:
                int(pr, 16)
            except ValueError:
                return create_json_response(False, 'Payment Request Must Be Hex Encoded', 400)

            verify_pr = PaymentRequest()
            try:

                hex_decoded_pr = pr.decode('hex')
                if len(hex_decoded_pr) > PAYMENT_REQUEST_SIZE_MAX:
                    log.warn('Rejecting Payment Request for Size [ACCEPTED: %d bytes | ACTUAL: %d bytes]' % (PAYMENT_REQUEST_SIZE_MAX, len(hex_decoded_pr)))
                    return create_json_response(False, 'Invalid Payment Request Submitted', 400)

                verify_pr.ParseFromString(hex_decoded_pr)
            except Exception as e:
                log.warn('Unable to Parse Submitted Payment Request [ID: %s]: %s' % (id_obj.id, str(e)))
                return create_json_response(False, 'Invalid Payment Request Submitted', 400)

            verify_pd = PaymentDetails()
            try:
                verify_pd.ParseFromString(verify_pr.serialized_payment_details)
            except Exception as e:
                log.warn('Unable to Parse Submitted Payment Request [ID: %s]: %s' % (id_obj.id, str(e)))
                return create_json_response(False, 'Invalid Payment Request Submitted', 400)

        # Validated!
        add_count = 0
        for pr in pr_list:
            id_obj.presigned_payment_requests.append(pr)
            add_count += 1
            if add_count == config.presigned_pr_limit:
                log.info('Presigned Payment Limit Reached [ID: %s]' % id_obj.id)
                break

        log.info('Added %d Pre-Signed Payment Requests [ID: %s]' % (add_count, id_obj.id))
        resolver.save(id_obj)

        return create_json_response(data={'payment_requests_added': add_count})


    @staticmethod
    @requires_public_key
    @requires_valid_signature
    def delete():

        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        id_obj = resolver.get_id_obj(get_id())
        if not id_obj:
            return create_json_response(False, 'Invalid Identifier', 404)

        resolver.delete(id_obj)
        return create_json_response(status=204)

    @staticmethod
    @requires_public_key
    @requires_valid_signature
    def get_count():

        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        id_obj = resolver.get_id_obj(get_id())
        if not id_obj:
            return create_json_response(False, 'Invalid Identifier', 404)

        return create_json_response(data={'payment_request_count': len(id_obj.presigned_payment_requests)})