__author__ = 'Matt David'

import ssl
from datetime import datetime, timedelta
from pybitcointools import serialize_script, b58check_to_hex, hex_to_b58check, deserialize_script
from pycoin.key.BIP32Node import BIP32Node
from redis import Redis

from addressimo.paymentrequest.paymentrequest_pb2 import PaymentRequest, PaymentDetails, X509Certificates
from addressimo.config import config
from addressimo.plugin import PluginManager
from addressimo.util import LogUtil

####################
# Bitcoin OP_CODES #
####################
OP_DUP = 118
OP_HASH160 = 169
OP_EQUALVERIFY = 136
OP_CHECKSIG = 172

log = LogUtil.setup_logging()

def generate_bip32_address_from_extended_pubkey(extended_pubkey, index):

    ext_key = BIP32Node.from_wallet_key(extended_pubkey)
    return ext_key.subkey(index, is_hardened=False).address()

def get_certs(x509_pem_format):

    certs = []
    loading_cert = ''
    for line in x509_pem_format.split('\n'):
        if not line:
            pass

        loading_cert += line
        if line == '-----END CERTIFICATE-----':
            if loading_cert:
                der_cert = ssl.PEM_cert_to_DER_cert(loading_cert)
                certs.append(der_cert)
            loading_cert = ''

    return certs

def generate_payment_request(crypto_addr, x509_cert, signer=None, amount=0, expires=None, memo=None, payment_url=None, merchant_data=None):

    # Setup & Populate PaymentDetails
    payment_details = PaymentDetails()

    # Setup Single PaymentDetails Output
    output = payment_details.outputs.add()
    output.amount = amount * 100000000 # BTC to Satoshis

    if crypto_addr[0] == '1':
        output.script = serialize_script([OP_DUP, OP_HASH160, b58check_to_hex(crypto_addr), OP_EQUALVERIFY, OP_CHECKSIG]).decode('hex')
    else:
        try:
            int(crypto_addr, 16)
            output.script = str(crypto_addr).decode('hex')
        except ValueError:
            output.script = str(crypto_addr)

    # Add current and expiration epoch time values
    payment_details.time = int(datetime.utcnow().strftime('%s'))

    if expires:
        if isinstance(expires, int) or isinstance(expires, long):
            payment_details.expires = int((datetime.utcnow() + timedelta(seconds=expires)).strftime('%s'))
        elif isinstance(expires, datetime.__class__):
            payment_details.expires = int(expires.strftime('%s'))
    else:
        payment_details.expires = int((datetime.utcnow() + timedelta(seconds=config.bip70_default_expiration)).strftime('%s'))

    # Handle Various Optional Fields in PaymentDetails
    payment_details.memo = memo if memo else ''
    payment_details.payment_url = payment_url if payment_url else ''
    payment_details.merchant_data = str(merchant_data) if merchant_data else ''

    # Setup & Populate PaymentRequest
    payment_request = PaymentRequest()
    payment_request.payment_details_version = 1
    payment_request.serialized_payment_details = payment_details.SerializeToString()

    # Set PKI Type / Data
    if not x509_cert or not signer:
        payment_request.pki_type = 'none'
        payment_request.pki_data = None
    else:

        payment_request.pki_type = signer.get_pki_type()
        pki_data = X509Certificates()

        for cert in get_certs(x509_cert):
            pki_data.certificate.append(cert)

        payment_request.pki_data = pki_data.SerializeToString()

    # Sign PaymentRequest
    if signer and x509_cert:
        payment_request.signature = ''
        payment_request.signature = signer.sign(payment_request.SerializeToString())

    # Log Payment Request to Logging System
    logger = PluginManager.get_plugin('LOGGER', config.logger_type)
    logger.log_payment_request(crypto_addr, signer.__class__.__name__, amount, expires, memo, payment_url, merchant_data)

    log.debug('Generated Payment Request [Address: %s | Signer: %s | Amount: %s | Expires: %s | Memo: %s | Payment URL: %s | Merchant Data: %s]' %
              (crypto_addr, signer.__class__.__name__, amount, expires, memo, payment_url, merchant_data))

    return payment_request.SerializeToString()

def get_unused_presigned_payment_request(id_obj):

    redis_conn = Redis.from_url(config.redis_addr_cache_uri)

    return_pr = None
    used_pr = []

    for pr in id_obj.presigned_payment_requests:

        if any([redis_conn.get(x) for x in get_addrs_from_paymentrequest(pr.decode('hex'))]):
            used_pr.append(pr)
            continue

        return_pr = pr
        break

    for pr in used_pr:
        id_obj.presigned_payment_requests.remove(pr)

    if used_pr:
        resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        resolver.save(id_obj)

    return return_pr


def get_addrs_from_paymentrequest(pr):

    ret_list = []
    pr_obj = PaymentRequest()
    pr_obj.ParseFromString(pr)

    pd = PaymentDetails()
    pd.ParseFromString(pr_obj.serialized_payment_details)

    for output in pd.outputs:
        script = deserialize_script(output.script)
        if script[0] == OP_DUP and script[1] == OP_HASH160 and script[3] == OP_EQUALVERIFY and script[4] == OP_CHECKSIG:
            ret_list.append(hex_to_b58check(script[2].encode('hex')))

    return ret_list