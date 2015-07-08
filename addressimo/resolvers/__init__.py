__author__ = 'mdavid'

from flask import request, Response
from redis import Redis

from addressimo.blockchain import cache_up_to_date
from addressimo.config import config
from addressimo.crypto import generate_bip32_address_from_extended_pubkey, generate_payment_request, get_unused_presigned_payment_request
from addressimo.signer.LocalSigner import LocalSigner
from addressimo.plugin import PluginManager
from addressimo.util import create_json_response, create_bip72_response
from addressimo.util import LogUtil

log = LogUtil.setup_logging()

redis_conn = Redis.from_url(config.redis_addr_cache_uri)

# Constants
PR_MIMETYPE = 'application/bitcoin-paymentrequest'

def resolve(id):

    ###################################
    # Verify Resolver and Request Data
    ###################################
    if not cache_up_to_date():
        log.critical('Address cache not up to date. Refresh Redis cache.')
        return create_json_response(False, 'Address cache not up to date. Please try again later.', 500)

    try:
        id_obj = PluginManager.get_plugin('RESOLVER', config.resolver_type).get_id_obj(id)
    except Exception as e:
        log.error('Exception retrieving id_obj [ID: %s | Exception: %s]' % (id, str(e)))
        return create_json_response(False, 'Exception occurred when retrieving id_obj from database', 500)

    if not id_obj:
        log.error('Unable to retrieve id_obj [ID: %s]' % id)
        return create_json_response(False, 'Unable to retrieve id_obj from database', 404)

    #################################################################################
    # Determine Wallet Address to Return or Use in BIP70 PaymentRequest Generation
    #################################################################################
    if not id_obj.bip32_enabled and not id_obj.wallet_address:
        log.error('bip32_enabled is False and static wallet_address is missing [ID: %s]' % id)
        return create_json_response(False, 'Unable to retrieve wallet_address', 400)

    if id_obj.bip32_enabled:
        try:
            waddr = get_unused_bip32_address(id_obj)
        except Exception as e:
            log.error('Exception occurred retrieving unused bip32 address [EXCEPTION: %s | ID: %s]' % (str(e), id))
            return create_json_response(False, 'Unable to retrieve wallet_address', 500)
    else:
        waddr = id_obj.wallet_address

    ###########################
    # Determine Response Type
    ###########################
    bip70_arg = request.args.get('bip70','').lower()

    # BIP70 Forced Request, but endpoint is not BIP70 capable
    if bip70_arg == 'true' and not id_obj.bip70_enabled:
        log.error('Required bip70_enabled value is missing or disabled [ID: %s | bip70_enabled: %s]' % (id, id_obj.get('bip70_enabled', None)))
        return create_json_response(False, 'Required bip70_enabled value is missing or disabled', 400)

    # BIP70-enabled Endpoint and BIP70 Request Forced or Accept-able by Client
    if id_obj.bip70_enabled and (bip70_arg == 'true' or PR_MIMETYPE in request.headers.get('accept')):

        # Handle Pre-signed PaymentRequests
        if id_obj.presigned_payment_requests:

            valid_pr = get_unused_presigned_payment_request(id_obj)
            if not valid_pr:
                return create_json_response(False, 'No PaymentRequests available for this ID', 404)

            return Response(response=valid_pr, status=200, content_type=PR_MIMETYPE, headers={'Content-Transfer-Encoding': 'binary', 'Access-Control-Allow-Origin': '*'})

        elif id_obj.presigned_only:
            log.warn('Presigned PaymentRequests list empty [ID: %s]' % id)
            return create_json_response(False, 'No PaymentRequests available for this ID', 404)

        # Handle Non-Presigned PaymentRequests
        log.info('Creating bip70 payment request [ADDRESS: %s | AMOUNT: %s | ID: %s]' % (waddr, get_bip70_amount(id_obj), id))
        try:
            return create_payment_request_response(waddr, get_bip70_amount(id_obj), id_obj)
        except Exception as e:
            log.error('Exception occurred creating payment request [EXCEPTION: %s | ID: %s]' % (str(e), id_obj.id))
            return create_json_response(False, 'Unable to create payment request', 500)

    # BIP70-enabled Endpoint, but not BIP70-specific Request
    if id_obj.bip70_enabled and bip70_arg != 'false':

        # Handle Pre-signed Payment Requests
        if not id_obj.presigned_payment_requests and id_obj.presigned_only:

            log.warn('Presigned PaymentRequests list empty [ID: %s]' % id)
            return create_json_response(False, 'No PaymentRequests available for this ID', 404)

        elif id_obj.presigned_payment_requests:
            valid_pr = get_unused_presigned_payment_request(id_obj)
            if not valid_pr:
                return create_json_response(False, 'No PaymentRequests available for this ID', 404)
            return create_bip72_response(None, None, 'https://%s/resolve/%s?bip70=true' % (config.site_url, id))

        # Handle Non-Presigned PaymentRequests
        log.info('Returning BIP72 URI [Address: %s | ID: %s]' % (waddr, id))
        return create_bip72_response(waddr, get_bip70_amount(id_obj), 'https://%s/resolve/%s?bip70=true&amount=%s' % (config.site_url, id_obj.id, get_bip70_amount(id_obj)))

    # Return Standard BIP72 URI Response without a PaymentRequest URI
    log.info('Returning Wallet Address [Address: %s | ID: %s]' % (waddr, id))
    return create_bip72_response(waddr, 0)

def get_bip70_amount(id_obj):
    if id_obj.bip70_static_amount is not None:
        return id_obj.bip70_static_amount
    elif request.args.get('amount'):
        return int(request.args.get('amount'))
    return 0

def get_unused_bip32_address(id_obj):

    if not id_obj.master_public_key:
        raise ValueError('Master public key missing. Unable to generate bip32 address.')

    lg_index = id_obj.last_generated_index

    while True:
        wallet_addr = generate_bip32_address_from_extended_pubkey(id_obj.master_public_key, lg_index)

        if not redis_conn.get(wallet_addr):
            log.info('New Wallet Address created [Address: %s | GenIndex: %s]' % (wallet_addr, lg_index))
            id_obj.last_generated_index = lg_index
            PluginManager.get_plugin('RESOLVER', config.resolver_type).save(id_obj)
            return wallet_addr
        else:
            log.debug('Used Wallet Address found! Trying next index [GenIndex: %s]' % lg_index)
            id_obj.last_used_index = lg_index
            lg_index += 1

def create_payment_request_response(wallet_addr, amount, id_obj):

    # TODO: This might not work with remote keys
    if not id_obj.x509_cert:
        raise ValueError('id_obj missing x509_cert')

    signer = PluginManager.get_plugin('SIGNER', config.signer_type)
    signer.set_id_obj(id_obj)

    # Setup PaymentRequest
    pr = generate_payment_request(
        wallet_addr,
        id_obj.x509_cert,
        signer,
        amount,
        id_obj.expires,
        id_obj.memo,
        id_obj.payment_url,
        id_obj.merchant_data
    )

    return Response(response=pr, status=200, content_type=PR_MIMETYPE, headers={'Content-Transfer-Encoding': 'binary', 'Access-Control-Allow-Origin': '*'})

def create_wallet_address_response(wallet_addr):
    return create_json_response(data={'wallet_address': wallet_addr})