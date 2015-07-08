__author__ = 'Matt David'

from addressimo.util import LogUtil

from BaseLogger import BaseLogger

log = LogUtil.setup_logging()

class LocalLogger(BaseLogger):

    @classmethod
    def get_plugin_name(cls):
        return 'LOCAL'

    def log_payment_request(self, address, signer, amount, expires, memo, payment_url, mechant_data):

        log.info('PaymentRequest Generated [ADDRESS: %s | SIGNER: %s | AMOUNT: %s | EXPIRES: %s | MEMO: %s | PAYMENT_URL: %s | MERCHANT_DATA: %s' % (
            address,
            signer,
            amount,
            expires,
            memo,
            payment_url,
            mechant_data
        ))