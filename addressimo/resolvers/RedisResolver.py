__author__ = 'Matt David'

import json
from datetime import datetime, timedelta
from time import mktime
from redis import Redis
from uuid import uuid4

from BaseResolver import BaseResolver
from addressimo.config import config
from addressimo.data import IdObject
from addressimo.util import LogUtil, CustomJSONEncoder

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
            result = redis_client.set(id_obj.id, json.dumps(id_obj, cls=CustomJSONEncoder))
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

    # PaymentRequest Request (PRR) Data Handling
    def add_prr(self, id, prr_data):

        redis_client = Redis.from_url(config.redis_prr_queue)

        if 'id' not in prr_data:
            while True:
                prr_data['id'] =  "%s%s%s" % (uuid4().hex, uuid4().hex, uuid4().hex)
                try:
                    if not redis_client.exists(prr_data['id']):
                        break
                except:
                    log.warn("Unable to Validate New ID for PRR")
                    raise

        try:
            result = redis_client.hset(id, prr_data['id'], json.dumps(prr_data, cls=CustomJSONEncoder))
            if result != 1:
                return None

            log.info('Added PRR to Queue %s' % id)
            return prr_data
        except Exception as e:
            log.info('Unable to Add PRR to Queue %s: %s' % (id, str(e)))
            raise

    def get_prrs(self, id):

        redis_client = Redis.from_url(config.redis_prr_queue)

        try:
            result = redis_client.hgetall(id)
            return [json.loads(x) for x in result.values()]
        except Exception as e:
            log.info('Unable to Get PRRs from Queue %s: %s' % (id, str(e)))
            raise

    def delete_prr(self, id, prr_id):

        redis_client = Redis.from_url(config.redis_prr_queue)

        try:
            result = redis_client.hdel(id, prr_id)
            return True if result > 0 else False
        except Exception as e:
            log.info('Unable to Delete PRR from Queue %s: %s' % (id, str(e)))
            raise

    def cleanup_stale_prr_data(self):

        redis_client = Redis.from_url(config.redis_prr_queue)

        prr_keys = redis_client.keys()
        log.info('Found %d PRR Keys' % len(prr_keys))

        for key in prr_keys:
            try:
                prr = json.loads(redis_client.hgetall(key).values()[0])

                if datetime.fromtimestamp(int(prr.get('submit_date'))) + timedelta(days=config.prr_expiration_days) < datetime.utcnow():
                    log.info('Deleting Stale PRR [ID: %s]' % key)
                    redis_client.delete(key)
            except Exception as e:
                log.error('Exception Occurred Cleaning Up Stale PRR [ID: %s]: %s' % (key, str(e)))

    # Return PaymentRequest (RPR) Data Handling
    def add_return_pr(self, return_pr):

        redis_client = Redis.from_url(config.redis_rpr_data)

        try:
            result = redis_client.set(return_pr['id'], json.dumps(return_pr, cls=CustomJSONEncoder))
            if result != 1:
                raise Exception('Redis Set Command Failed')
        except Exception as e:
            log.info('Unable to Add Return PR %s: %s' % (return_pr['id'], str(e)))
            raise

    def get_return_pr(self, id):

        redis_client = Redis.from_url(config.redis_rpr_data)

        try:
            return json.loads(redis_client.get(id))
        except Exception as e:
            log.info('Unable to Get Return PR %s: %s' % (id, str(e)))
            raise

    def cleanup_stale_return_pr_data(self):

        redis_client = Redis.from_url(config.redis_rpr_data)

        return_pr_keys = redis_client.keys()
        log.info('Found %d Return PR Keys' % len(return_pr_keys))

        for key in return_pr_keys:
            try:
                return_pr = json.loads(redis_client.get(key))

                if datetime.fromtimestamp(int(return_pr.get('submit_date'))) + timedelta(days=config.rpr_expiration_days) < datetime.utcnow():
                    log.info('Deleting Stale Return PR [ID: %s]' % key)
                    redis_client.delete(key)
            except Exception as e:
                log.error('Exception Occurred Cleaning Up Stale Return PR [ID: %s]: %s' % (key, str(e)))

    # Payment Data Handling
    def get_payment_request_meta_data(self, uuid):

        redis_client = Redis.from_url(config.redis_pr_store)

        return redis_client.hgetall(uuid)

    def set_payment_request_meta_data(self, expiration_date, wallet_addr, amount):

        redis_client = Redis.from_url(config.redis_pr_store)

        # Only continue if uuid doesn't already exist in Redis
        while True:
            payment_url_uuid = '%s%s' % (uuid4().hex, uuid4().hex)
            if not redis_client.hkeys(payment_url_uuid):
                break

        payment_addresses = {
            wallet_addr: amount
        }

        try:
            redis_client.hmset(payment_url_uuid, {
                'expiration_date': expiration_date,
                'payment_validation_data': json.dumps(payment_addresses)
            })

        except Exception as e:
            log.info('Exception Saving PaymentRequest Meta Data: %s' % str(e))
            raise

        return payment_url_uuid

    def cleanup_stale_payment_request_meta_data(self):

        redis_client = Redis.from_url(config.redis_pr_store)

        payment_request_keys = redis_client.keys()
        log.info('Found %d Payment Request Meta Data Keys' % len(payment_request_keys))

        for key in payment_request_keys:
            try:
                payment_request = redis_client.hgetall(key)
                if datetime.utcnow() > datetime.fromtimestamp(int(payment_request.get('expiration_date'))):
                    log.info('Deleting Stale Payment Request [UUID: %s]' % key)
                    redis_client.delete(key)
            except Exception as e:
                log.error('Exception Occurred Cleaning Up Stale Payment Request Meta Data [UUID: %s]: %s' % (key, str(e)))

    def set_payment_meta_data(self, tx_hash, memo, refund_address):

        redis_client = Redis.from_url(config.redis_payment_store)

        try:
            redis_client.hmset(tx_hash, {
                'memo': memo,
                'refund_to': refund_address,
                'expiration_date': int(
                    mktime((datetime.utcnow() + timedelta(days=config.bip70_payment_expiration_days)).timetuple())
                )
            })

        except Exception as e:
            log.info('Exception Saving Payment Meta Data: %s' % str(e))
            raise

    def cleanup_stale_payment_meta_data(self):

        redis_client = Redis.from_url(config.redis_payment_store)

        payment_keys = redis_client.keys()
        log.info('Found %d Payment Meta Data Keys' % len(payment_keys))

        for key in payment_keys:
            try:
                payment = redis_client.hgetall(key)
                if datetime.utcnow() > datetime.fromtimestamp(int(payment.get('expiration_date'))):
                    log.info('Deleting Stale Payment [UUID: %s]' % key)
                    redis_client.delete(key)
            except Exception as e:
                log.error('Exception Occurred Cleaning Up Stale Payment Meta Data [UUID: %s]: %s' % (key, str(e)))

    def get_refund_address_from_tx_hash(self, tx_hash):

        redis_client = Redis.from_url(config.redis_payment_store)

        result = redis_client.hgetall(tx_hash)
        del(result['expiration_date'])

        return result
