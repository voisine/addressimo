__author__ = 'Matt David'

from collections import defaultdict
from datetime import datetime
from flask import request
from addressimo.config import config
from addressimo.plugin import PluginManager
from addressimo.storeforward import requires_public_key
from addressimo.util import requires_valid_signature, create_json_response, get_id, LogUtil

log = LogUtil.setup_logging()

class PRR:

    # TODO: Update requires_valid_signature decorator with a parameter to not require an identity/sig combo to have a
    # value S&F endpoint configured

    @staticmethod
    def submit_prr(id):

        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        try:
            id_obj = resolver.get_id_obj(id)
        except Exception as e:
            log.error('Exception retrieving id_obj [ID: %s | Exception: %s]' % (id, str(e)))
            return create_json_response(False, 'Exception Occurred, Please Try Again Later.', 500)

        if not id_obj:
            log.error('Unable to retrieve id_obj [ID: %s]' % id)
            return create_json_response(False, 'ID Not Recognized', 404)

        # Handle PRRs
        if not id_obj.prr_only:
            log.warn("PaymentRequest Request Endpoint POST Submitted to Non-PRR Endpoint")
            return create_json_response(False, 'Invalid PaymentRequest Request Endpoint', 400)

        # Process PRR
        rdata = request.get_json()
        if not rdata:
            return create_json_response(False, 'Invalid Request', 400)

        # Setup internally stored PRR Data
        prr_data = {
            'sender_pubkey': request.headers.get('X-Identity'),
            'amount': int(rdata.get('amount', 0)),
            'notification_url': rdata.get('notification_url'),
            'x509_cert': rdata.get('x509_cert'),
            'signature': rdata.get('signature'),
            'submit_date': datetime.utcnow()
        }

        if prr_data['x509_cert'] and not prr_data['signature']:
            return create_json_response(False, 'Requests including x509 cert must include signature', 400)

        # TODO: Validate Signature

        try:
            ret_prr_data = resolver.add_prr(id, prr_data)
            if not ret_prr_data:
                log.error("Unexpected Add PRR Failure [ID: %s]" % (id))
                return create_json_response(False, 'Unknown System Error, Please Try Again Later', 500)

            rpr_url = 'https://%s/pr/%s' % (config.site_url, ret_prr_data['id'])
            return create_json_response(status=202, headers={'Location':rpr_url})
        except Exception as e:
            log.error("Unexpected exception adding PRR [ID: %s]: %s" % (id, str(e)))
            return create_json_response(False, 'Unknown System Error, Please Try Again Later', 500)

    @staticmethod
    @requires_public_key
    @requires_valid_signature
    def get_queued_pr_requests(id):

        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        id_obj = resolver.get_config(get_id())
        if not id_obj:
            return create_json_response(False, 'Invalid Identifier', 404)

        try:
            queued_prrs = resolver.get_prrs(id)
            return create_json_response(data={"count":len(queued_prrs), "requests": queued_prrs})
        except Exception as e:
            log.error('Unable to Retrieve Queued PR Requests [ID: %s]: %s' % (id, str(e)))
            return create_json_response(False, 'Unable to Retrieve Queued PR Requests', status=500)

    @staticmethod
    @requires_public_key
    @requires_valid_signature
    def submit_return_pr(id):

        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        id_obj = resolver.get_config(get_id())
        if not id_obj:
            return create_json_response(False, 'Invalid Identifier', 404)

        rdata = request.get_json()
        if not rdata:
            return create_json_response(False, 'Invalid Request', 400)

        ready_request_list = rdata.get('ready_requests')
        if not ready_request_list or not isinstance(ready_request_list, list):
            log.warn('Submitted Response Has Invalid ready_requests list')
            return create_json_response(False, 'Missing or Empty ready_requests list')

        failures = defaultdict(list)
        for ready_request in ready_request_list:

            # Validate Ready Request
            required_fields = {'id', 'receiver_pubkey', 'encrypted_payment_request'}
            if not required_fields.issubset(set(ready_request.keys())):
                log.warn("Ready Request Missing Required Fields: id and/or encrypted_payment_request")
                failures[ready_request['id']].append('Missing Required Fields: id, receiver_pubkey, and/or encrypted_payment_request')
                continue

            # Add Return PR to Redis for later retrieval
            try:
                ready_request['submit_date'] = datetime.utcnow()
                resolver.add_return_pr(id, ready_request)
            except Exception as e:
                log.error("Unable to Add Return PR: %s" % str(e))
                failures[ready_request['id']].append('Unable to Process Return PaymentRequest')
                continue

            # Delete Original PRR as it's been fulfilled
            try:
                resolver.delete_prr(id, ready_request['id'])
            except Exception as e:
                log.warn("Unable to Delete Original PRR [ID: %s]: %s" % (ready_request.get('id'), str(e)))

        if not failures:
            log.info("Accepted %d Return Payment Requests [ID: %s]" % (len(ready_request_list), id))
            return create_json_response(data={"accept_count":len(ready_request_list)})

        error_data = {
            "accept_count": len(ready_request_list) - len(failures.keys()),
            "failures": failures
        }
        return create_json_response(False, 'Submitted Return PaymentRequests contain errors, please see failures field for more information', 400, error_data)


    @staticmethod
    def get_return_pr(id):

        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        try:
            return_pr = resolver.get_return_pr(id)
            if not return_pr:
                return create_json_response(False, 'PaymentRequest Not Found or Not Yet Ready', 404)

            return_data = {
                "encrypted_payment_request": return_pr['encrypted_payment_request'],
                "receiver_pubkey": return_pr['receiver_pubkey']
            }

            return create_json_response(data=return_data)
        except Exception as e:
            log.warn("Unable to Get Return PR %s: %s" % (id, str(e)))
            return create_json_response(False, 'PaymentRequest Not Found', 500)

