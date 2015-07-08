__author__ = 'mdavid'

# System Imports
import binascii
from datetime import datetime
import multiprocessing
from multiprocessing.queues import Empty
import os
import pybitcointools
from redis import Redis
import resource
import simpleflock
import socket
import struct
import sys
import time

# Addressimo Imports
from addressimo.blockchain import *
from addressimo.config import config
from addressimo.util import LogUtil

# Setup Shared Data
manager = multiprocessing.Manager()
addr_queue = manager.Queue()
block_queue = manager.Queue()
queue_proc_stop = manager.Value('i', 0)
used_count = 0

# Setup Global Data
PROCESSED_BLOCK_LIST = []

log = LogUtil.setup_logging()

# Setup Limits
try:
    resource.setrlimit(resource.RLIMIT_NOFILE, (8192, 16384))
except ValueError as e:
    log.debug('Unable to Raise NOFILE Limit: %s' % str(e))

max_proc_tuple = resource.getrlimit(resource.RLIMIT_NPROC)
log.info('SystemInfo: MAX PROCS [SOFT: %d | HARD: %d]' % (max_proc_tuple[0], max_proc_tuple[1]))

class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
import multiprocessing.pool
class NoDaemonPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

# Utility Functions
class RanOutOfData(Exception):
    pass

def _intFromBytes_LittleByteOrder(data):
    multiplier = 1
    result = 0
    for i in range(len(data)):
        byteValue = struct.unpack('<B', data[i:i + 1])[0]
        result += byteValue * multiplier
        multiplier = multiplier << 8
    return result

def DecodeVarInt(data, pos):
    if pos >= len(data):
        raise RanOutOfData()
    result = _intFromBytes_LittleByteOrder(data[pos:pos + 1])
    pos += 1
    if result < 253:
        return pos, result
    byteSize = 2 ** (result - 252)
    if pos + byteSize > len(data):
        raise RanOutOfData()
    return pos + byteSize, _intFromBytes_LittleByteOrder(data[pos:pos + byteSize])

def GetTransactionsInBlock(data):
    try:
        pos = 80 # skip block header
        pos, numberOfTransactions = DecodeVarInt(data, pos)
        result = []
        for i in range(numberOfTransactions):
            startPos = pos
            pos += 4 # skip version
            pos, numberOfInputs = DecodeVarInt(data, pos)
            for i in range(numberOfInputs):
                pos += 32 # txid
                pos += 4 # vout
                pos, scriptLen = DecodeVarInt(data, pos)
                pos += scriptLen
                pos += 4 # sequence
            pos, numberOfOutputs = DecodeVarInt(data, pos)
            for i in range(numberOfOutputs):
                pos += 8 # output amount
                pos, scriptLen = DecodeVarInt(data, pos)
                pos += scriptLen
            pos += 4 # lock time
            result.append(data[startPos:pos])
        if pos != len(data):
            raise Exception('invalid block data')
        return result
    except RanOutOfData:
        raise Exception('invalid block data')

def get_largest_consecutive_integer(my_list):

    maxrun = -1
    rl = {}
    for x in sorted(my_list):
        run = rl[x] = rl.get(x-1, 0) + 1
        if run > maxrun:
            maxend, maxrun = x, run
    return maxend

def get_redis_last_blockheight():
    try:
        redis_conn = Redis.from_url(config.redis_addr_cache_uri)
        return int(redis_conn.get('last_blockheight'))
    except:
        return None

def process_tx(addr_queue, blockheight, tx):

    tx_obj = pybitcointools.deserialize(tx.encode('hex'))

    for vout in tx_obj['outs']:
        addr_temp = pybitcointools.script_to_address(vout['script'])
        if addr_temp and addr_temp[0] in ['1','3']:
            addr_queue.put((blockheight, addr_temp))

def process_block(addr_queue, block_queue, blockheight):

    log = LogUtil.setup_logging('block_logger')

    while True:
        try:
            block_get_start = datetime.utcnow()
            block = get_block(blockheight)
            block_get_end = datetime.utcnow()
            break
        except socket.timeout:
            log.error('Timeout Connecting to Bitcoin Server, Retrying...')
            time.sleep(5)
            continue

    try:
        tx_pool = multiprocessing.Pool(config.cache_loader_blocktx_pool_size)

        get_tx_in_block_start = datetime.utcnow()
        rawTransactions = GetTransactionsInBlock(binascii.unhexlify(block))
        get_tx_in_block_end = datetime.utcnow()

        start = datetime.utcnow()
        for tx in rawTransactions:
            tx_pool.apply_async(process_tx, args=(addr_queue, blockheight, tx))

        tx_pool.close()
        tx_pool.join()
        end = datetime.utcnow()
        log.debug('Processed Block [BLOCK: %d | TX COUNT: %d | PROCESS TIME: %.2fs | GET BLOCK TIME: %.2fs | GET TX TIME: %.2fs]' % (blockheight, len(rawTransactions), (end - start).total_seconds(), (block_get_end-block_get_start).total_seconds(), (get_tx_in_block_end-get_tx_in_block_start).total_seconds()))
    except Exception as e:
        log.error('Process Block Exception: %s' % str(e))

    block_queue.put(blockheight)

def process_block_queue(block_queue):

    block_drain = []

    while True:
        try:
            temp_height = block_queue.get(block=True, timeout=0.01)
            try:
                block_drain.append(int(temp_height))
                if len(block_drain) > 1000:
                    break
            except:
                pass
        except Empty:
            break

    if block_drain:

        for x in block_drain:
            PROCESSED_BLOCK_LIST.append(x)

        last_block_height = get_largest_consecutive_integer(PROCESSED_BLOCK_LIST)
        last_height = get_redis_last_blockheight()
        if not last_height or last_height < int(last_block_height):

            redis_conn = Redis.from_url(config.redis_addr_cache_uri)
            log.info('%s Current Cache Build Status [BLOCK HEIGHT: %d | TOTAL ADDRESSES: %d]' % (datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), last_block_height, int(redis_conn.dbsize())))
            redis_conn.set('last_blockheight', int(last_block_height))

def process_queue(block_queue, addr_queue, queue_proc_stop):

    log = LogUtil.setup_logging('block_logger')

    while not queue_proc_stop.value:

        process_block_queue(block_queue)

        addr_drain = set()
        while True:
            try:
                temp_value = addr_queue.get(block=True, timeout=0.01)
                addr_drain.add(temp_value)
                if len(addr_drain) > 1000:
                    break
            except Empty:
                break

        redis_conn = Redis.from_url(config.redis_addr_cache_uri)
        for blockheight, addr in addr_drain:
            if not redis_conn.get(addr):
                    redis_conn.set(addr, blockheight)

        time.sleep(2)

try:

    with simpleflock.SimpleFlock('/tmp/build_address_cache.lock', timeout=1):

        last_processed = get_redis_last_blockheight() or 0

        try:
            current_block = current_block_count()
        except Exception as e:
            log.error('Unable to connect to bitcoin node: %s' % str(e))
            sys.exit(-1)

        if last_processed == current_block:
            log.info('No New Bitcoin Blockchain Blocks, Nothing to be done here')
            sys.exit(0)

        queue_proc = multiprocessing.Process(target=process_queue, args=(block_queue, addr_queue, queue_proc_stop))
        queue_proc.daemon = True
        queue_proc.start()

        log.info('Starting Scan at Blockheight: %d -> %d' % (last_processed + 1, current_block))
        block_pool = NoDaemonPool(config.cache_loader_process_pool_size)

        job_start = datetime.utcnow()
        blocks_processed = 0
        for i in xrange(last_processed + 1, current_block + 1):
            block_pool.apply_async(process_block, args=(addr_queue, block_queue, i))
            blocks_processed += 1
            if block_pool._taskqueue.qsize() > 20:
                time.sleep(2)

        block_pool.close()
        block_pool.join()
        job_end = datetime.utcnow()

        log.info('Block Scan Complete [BLOCKS PROCESSED: %d | LAST BLOCK: %d | JOB TIME: %.2fs]' % (blocks_processed, i, (job_end - job_start).total_seconds()))
        queue_proc_stop.value = 1
        queue_proc.join(timeout=10)
        if queue_proc.is_alive():
            queue_proc.terminate()

        process_block_queue(block_queue)
        sys.exit(0)

except IOError:
    log.warn('Unable to lock lockfile, process is running already or lockfile is stale [/tmp/build_address_cache.lock]')
    sys.exit(0)

except Exception as e:
    log.warn('Unknown Top-Level Exception Caught: %s' % str(e))
    # if os.path.exists('/tmp/build_address_cache.lock'):
    #     os.unlink('/tmp/build_address_cache.lock')