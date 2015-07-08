__author__ = 'Matt David'

from datetime import datetime
from redis import Redis

from addressimo.config import config
from addressimo.util import LogUtil
from BaseLogger import BaseLogger

log = LogUtil.setup_logging()

class RedisLogger(BaseLogger):

    @classmethod
    def get_plugin_name(cls):
        return 'REDIS'

    def log_payment_request(self, address, signer, amount, expires, memo, payment_url, merchant_data):

        redis_client = Redis.from_url(config.redis_logdb_uri)

        if isinstance(expires, datetime.__class__):
            expires = expires.strftime('%s')

        key_name = '%s-%s-%s' % (address, datetime.utcnow().strftime('%s'), expires)

        log.info('Logging PaymentRequest Generation to REDIS [KEY: %s]' % key_name)

        redis_client.hmset(key_name, {
            'address': address,
            'signer': signer,
            'amount': amount,
            'expires': expires,
            'memo': memo,
            'payment_url': payment_url,
            'merchant_data': merchant_data
        })