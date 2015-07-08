__author__ = 'Matt David'

from addressimo.util import LogUtil
from OpenSSL import crypto
from BaseSigner import BaseSigner

log = LogUtil.setup_logging()

class LocalSigner(BaseSigner):

    def set_id_obj(self, id_obj):

        if not id_obj:
            log.error('LocalSigner Requires ID Configuration')
            raise ValueError('LocalSigner Requires ID Configuration')

        if not id_obj.private_key:
            log.error('id_obj missing private key [id_obj: %s]' % id_obj.id)
            raise ValueError('id_obj missing private key')

        self.privkey = crypto.load_privatekey(crypto.FILETYPE_PEM, id_obj.private_key)

    @classmethod
    def get_plugin_name(cls):
        return 'LOCAL'

    def sign(self, data):
        return crypto.sign(self.privkey, data, 'sha256')

    def get_pki_type(self):
        return'x509+sha256'
