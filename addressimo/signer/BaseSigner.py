__author__ = 'Matt David'

from addressimo.plugin import BasePlugin

class BaseSigner(BasePlugin):

    def sign(self, data):
        raise NotImplementedError

    def get_pki_type(self):
        raise NotImplementedError

    def set_id_obj(self, id_obj):
        raise NotImplementedError

    @classmethod
    def get_plugin_category(cls):
        return 'SIGNER'

    @classmethod
    def get_plugin_name(cls):
        raise NotImplementedError