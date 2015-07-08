__author__ = 'Matt David'

import json
from redis import Redis
from uuid import uuid4

from BaseResolver import BaseResolver
from addressimo.config import config
from addressimo.data import IdObject
from addressimo.util import LogUtil

log = LogUtil.setup_logging()

class RedisResolver(BaseResolver):

    @classmethod
    def get_plugin_name(cls):
        return 'REDIS'

    def get_all_keys(self):
        redis_client = Redis.from_url(config.redis_id_obj_uri)
        return redis_client.keys('*')

    def get_id_obj(self, id):

        redis_client = Redis.from_url(config.redis_id_obj_uri)
        try:
            result = redis_client.get(id)
            if not result:
                log.info('Unable to Get id obj data [ID: %s]' % id)
                return None

        except Exception as e:
            log.info('Unable to Get id obj data [ID: %s]: %s' % (id, str(e)))
            return None

        id_obj = IdObject(id)
        for key, value in json.loads(result).items():
            id_obj[key] = value
        return id_obj

    def save(self, id_obj):

        redis_client = Redis.from_url(config.redis_id_obj_uri)

        if not id_obj.id:
            temp_id = uuid4().hex
            while redis_client.get(temp_id):
                temp_id = uuid4().hex
            id_obj.id = temp_id

        try:
            result = redis_client.set(id_obj.id, json.dumps(id_obj))
            log.info('Saved IdObject to Redis [ID: %s]' % id_obj.id)
            return result
        except Exception as e:
            log.info('Unable to Save IdObject to Redis [ID: %s]: %s' % (id, str(e)))
            raise

    def delete(self, id_obj):

        redis_client = Redis.from_url(config.redis_id_obj_uri)

        try:
            result = redis_client.delete(id_obj.id)
            log.info('Deleted IdObject to Redis [ID: %s]' % id_obj.id)
            return result
        except Exception as e:
            log.info('Unable to Delete IdObject to Redis [ID: %s]: %s' % (id, str(e)))
            raise


if __name__ == '__main__':
    from datetime import datetime, timedelta
    from addressimo.data import IdObject

    #io = IdObject(id=123456)
    rr = RedisResolver()
    io = rr.get_id_obj('123456')
    io.bip70_static_amount = 9878987
    #
    # io.expires = int((datetime.utcnow() + timedelta(minutes=33)).strftime('%s'))
    # io.memo = 'Hi my test memo here'
    # io.payment_url = 'https://www.whosywhat.com'
    # io.merchant_data = 'lang=el&basketId=11252'
    #io.master_public_key = 'xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8'
    rr.save(io)
    #result = rr.get_id_obj('1234')
