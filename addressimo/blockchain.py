__author__ = 'frank'

# Third Party Imports
import bitcoinrpc

from redis import Redis

# Addressimo Imports
from addressimo.config import config


def connect():
    return bitcoinrpc.connect_to_remote(config.bitcoin_user, config.bitcoin_pass)

def current_block_count():
    conn = connect()
    return conn.getblockcount()

def get_redis_last_blockheight():
    redis_conn = Redis.from_url(config.redis_addr_cache_uri)
    try:
        return int(redis_conn.get('last_blockheight'))
    except:
        return None

def cache_up_to_date():
    return current_block_count() - get_redis_last_blockheight() <= config.cache_blockheight_threshold

def get_block(blockheight):
    conn = connect()

    blockhash = conn.getblockhash(blockheight)
    return conn.proxy.getblock(blockhash, False)

def submit_transaction(tx):
    conn = connect()

    return conn.proxy.sendrawtransaction(tx)
