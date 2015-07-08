__author__ = 'Matt David'

import json
import requests
from datetime import datetime
from redis import Redis

from addressimo.config import config
from addressimo.util import LogUtil
from BaseLogger import BaseLogger

log = LogUtil.setup_logging()

class APILogger(BaseLogger):

    @classmethod
    def get_plugin_name(cls):
        return 'API'

    def log_payment_request(self, address, signer, amount, expires, memo, payment_url, merchant_data):

        if isinstance(expires, datetime.__class__):
            expires = expires.strftime('%s')

        req_data = {
            'address': address,
            'signer': signer,
            'amount': amount,
            'expires': expires,
            'memo': memo,
            'payment_url': payment_url,
            'merchant_data': merchant_data
        }

        response = requests.post(config.logger_api_endpoint, data=json.dumps(req_data))

        if requests.codes.ok <= response.status_code <= requests.codes.accepted:
            log.info('Successfully Logged PaymentRequest Generation to API [ENDPOINT: %s]' % config.logger_api_endpoint)
        else:

            error_str = ''
            if response.headers.get('content-type') == 'application/json':
                try:
                    json_data = response.json()
                    error_str = json_data.get('error') if not error_str else error_str
                    error_str = json_data.get('message') if not error_str else error_str
                    error_str = json_data.get('failure') if not error_str else error_str
                except Exception as e:
                    log.warn('Unable to get any error message from JSON response')

            log.error('PaymentRequest API Logging FAILED [ENDPOINT: %s | CODE: %s | ERROR: %s]' % (config.logger_api_endpoint, response.status_code, error_str))
