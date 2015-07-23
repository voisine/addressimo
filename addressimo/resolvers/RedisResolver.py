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

    def get_branches(self, id):

        redis_client = Redis.from_url(config.redis_address_branch_uri)

        try:
            result = redis_client.hkeys(id)

            if not result:
                log.info('No branches are present [ID: %s]' % id)
                return []

            result = map(int, result)
        except Exception as e:
            log.error('Exception retrieving branches [ID: %s]: %s' % (id, str(e)))
            return []

        return result

    def get_lg_index(self, id, branch):

        lg_index = 0
        redis_client = Redis.from_url(config.redis_address_branch_uri)

        try:
            lg_index = redis_client.hget(id, branch)
        except Exception as e:
            log.error('Exception retrieving lg_index from Redis [ID: %s | Branch: %s]: %s' % (id, branch, str(e)))

        return int(lg_index) if lg_index else 0

    def set_lg_index(self, id, branch, index):

        redis_client = Redis.from_url(config.redis_address_branch_uri)

        try:
            result = redis_client.hset(id, branch, index)
        except Exception as e:
            log.error('Exception setting lg_index in Redis [ID: %s | Branch: %s] %s' % (id, branch, str(e)))
            return None

        return result

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
            log.info('Unable to Delete IdObject to Redis [ID: %s]: %s' % (id_obj.id, str(e)))
            raise

