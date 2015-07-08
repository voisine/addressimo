__author__ = 'Matt David'

from addressimo.plugin import BasePlugin

class BaseLogger(BasePlugin):

    def log_payment_request(self, address, signer, amount, expires, memo, payment_url, mechant_data):
        raise NotImplementedError

    @classmethod
    def get_plugin_category(cls):
        return 'LOGGER'