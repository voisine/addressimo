__author__ = 'Matt David'

import json
import requests

from OpenSSL import crypto
from BaseSigner import BaseSigner

from addressimo.config import config
from addressimo.util import LogUtil

log = LogUtil.setup_logging()

# This is example code, which can be used as a boilerplate for integrating with your own
# API-based (and possibly HSM-backed) endpoint.
#
# NOTE: Exchanging Data and Signatures in HEX allows us to use JSON and native text instead of having
# to deal with binary data in the web request / response.

class APISigner(BaseSigner):

    def set_id_obj(self, id_obj):
        self.id_obj = id_obj

    @classmethod
    def get_plugin_name(cls):
        return 'API'

    def sign(self, data):

        if not self.id_obj.private_key_id:
            raise ValueError('APISigner Requires private_key_id')

        try:
            response = requests.post(config.signer_api_endpoint, json.dumps({'private_key_id': self.id_obj.private_key_id, 'data': data.encode('hex'), 'digest': 'SHA256'}))
            json_resp = response.json()
            sig = json_resp.get('signature')
            if not sig:
                log.error('APISigner Endpoint Did Not Return a Signature!')
                return None

            return sig.decode('hex')

        except Exception as e:
            log.error('APISigner Failed: %s' % str(e))
            return None

    def get_pki_type(self):
        return'x509+sha256'