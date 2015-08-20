__author__ = 'frank'

from flask.ext.testing import LiveServerTestCase

import time
import requests

from addressimo.config import config
from addressimo.data import IdObject
from addressimo.plugin import PluginManager
from addressimo.paymentrequest.paymentrequest_pb2 import Output, PaymentRequest, PaymentDetails, Payment, PaymentACK
from addressimo.util import LogUtil
from ecdsa import SigningKey, curves
from pybitcointools import *
from server import app
from redis import Redis


log = LogUtil.setup_logging()

####################
# Bitcoin OP_CODES #
####################
OP_DUP = 118
OP_HASH160 = 169
OP_EQUALVERIFY = 136
OP_CHECKSIG = 172


TEST_CERT = '''
-----BEGIN CERTIFICATE-----
MIIDjjCCAnYCCQCEYiGXmolUUjANBgkqhkiG9w0BAQsFADCBiDELMAkGA1UEBhMC
VVMxEzARBgNVBAgMCkNhbGlmb3JuaWExFDASBgNVBAcMC0xvcyBBbmdlbGVzMRQw
EgYDVQQKDAtOZXRraSwgSW5jLjETMBEGA1UEAwwKYWRkcmVzc2ltbzEjMCEGCSqG
SIb3DQEJARYUb3BlbnNvdXJjZUBuZXRraS5jb20wHhcNMTUwNzA2MTc0NzU3WhcN
MTYwNzA1MTc0NzU3WjCBiDELMAkGA1UEBhMCVVMxEzARBgNVBAgMCkNhbGlmb3Ju
aWExFDASBgNVBAcMC0xvcyBBbmdlbGVzMRQwEgYDVQQKDAtOZXRraSwgSW5jLjET
MBEGA1UEAwwKYWRkcmVzc2ltbzEjMCEGCSqGSIb3DQEJARYUb3BlbnNvdXJjZUBu
ZXRraS5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQD0mXwQNo1t
+mWmUBOvzQu9c3dNc019NL22MhjQtj5xtloSURpKJEDnkSH9QmiKmwCmCP534fpe
EjjTMnssa211j9CrRjGhlw2utj758+0+fWxNcaw2axBqFaLTZ08kI9325kOmMqj3
ZihzGKl9k6TTa+F/yYBsUg9gWM8R2Kx+TPhDWd2F2qtYEsJ/+FuSmbTbhVK1xyKw
xt6pgnLuON7n012rDzFpWp6xhpnxdwJKT618I6EvzgImQQXwrHcaxMfsYvbIx3t6
WadNwe3DV0onmlP2HWgrZjqlSyZkJtbJNt9M9UNPvHpan2nhM+uFFNYm7Lds3HWn
E80Erde6DUFnAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAO7HuYR3eDQtJfvmqF9z
whduPlI2tcuQaC5qnAuw9QACJ1P7f/JgjBa4ZdUp3ll0Ka9H4XK+zdh9FE8NGSXX
2kOdkJvw3S9rKacXkFKfDqbHOURyrXZ5Qnd7gn9UjStrt7nULYQR2CnND018MXT2
ojK1hGJt5Hh7jGwjKvPQe8Xb4i6u36zOQMNk7t7x+ryhoUxtX5uiiJFOt9ZsTsbn
RmkGxmG3vqq0S4yqClEG8MbRU4XVSu73OL+WM8Eo7eTltHirP81CztR8ki6WrD5W
VaTgdpiY90zRckz8wdX1WsAZs4xOL4ECxdDU9puvwDBWME4Ijt9PRSlzwsukv08B
yfk=
-----END CERTIFICATE-----
'''

TEST_CERT_PRIVKEY = '''
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA9Jl8EDaNbfplplATr80LvXN3TXNNfTS9tjIY0LY+cbZaElEa
SiRA55Eh/UJoipsApgj+d+H6XhI40zJ7LGttdY/Qq0YxoZcNrrY++fPtPn1sTXGs
NmsQahWi02dPJCPd9uZDpjKo92YocxipfZOk02vhf8mAbFIPYFjPEdisfkz4Q1nd
hdqrWBLCf/hbkpm024VStccisMbeqYJy7jje59Ndqw8xaVqesYaZ8XcCSk+tfCOh
L84CJkEF8Kx3GsTH7GL2yMd7elmnTcHtw1dKJ5pT9h1oK2Y6pUsmZCbWyTbfTPVD
T7x6Wp9p4TPrhRTWJuy3bNx1pxPNBK3Xug1BZwIDAQABAoIBAQDZvRf3xtg3osOC
PZ6IzNs6luMJCy9b2etXmVkF0nXb/BxKWfAxN/yfJ08+iDNPz5PQOgls5rldrJLx
TurfK/KQyKlVDnN4CWOgt5NwJnh3PGeAuUQ4XS6LgR8lWb3Vyif5dhmahVZshYBU
lQusQhZkLpDalKHBy3rspaIPnPZQpq6FwGuLoOb469Evv1HdXT1CsSQKoPnQaWnv
l1IwYAOtbsQOYIL3xqEpMXqMwFOx/5V4qzCkrgZYhRTlJ5MJJgNZ60EswP6cm9AG
PIoYtelqQiYVlcLXc4fSLzT7QN94ncX5Qf0Xs0hDpCENxJsiiHzIARa3dz7C+fx9
lPpROW/hAoGBAPpyLukh24j4Hc+RD9dSt02ISFaeeI98EvwesEl73HFTB5w9QrA6
dLIG4cT7RHMI3vUMj/BUN3cyEMCRyibdnulAmoQhvBy6dSMnRKdbHmdXCKEA8Nkx
JSYcgFgPP6hqMDVtC2jmkERb8UTjIXQyN5ly1HSWaVtd0bMcthlYGJS9AoGBAPoG
HC//eQYAmcFwDkO08ckS+AKEJOdqZgNBW/CCKn3YiXi9adrbRaaHSDEr7hGSM5aT
jmJh0PGJKELMVoa3zHTQQ0PgKuWUQ7wLnUV4qy1XSOiCyVnk5nYDHknNF8n7sTUs
foc5IWYcQQ3VKwSNmIXgdW8nnsxPJwm1D0gfjnrzAoGBANxMdFc+IQ5qsk5TG8wc
RoE8z+ThoMsWKNz9YbRB77b/gkI84NyDjwLKau4K2DsYIocLddHBQsjmkTXTCC8H
4zDqUwDHa+EZYtB5SjqsPCJKvJxjZ3ilcjgD+iF7yFMslRtpwA+WQHDhL2mZIWRE
iAPCrn+fjy1/aWZUaxoAFB9BAoGAafobCpFMOCobAi5ALZzN+7/plg9zIRAta2XR
1bEm167oHmCTNOxKqpqfFBCd2Z7R9RpYeQUjLq5HfYDlkDbqF/2K9YNYS3W7/EIk
CKVsUUy1H7EILe1jblRGC1w+oCPqajKQ8zpZGNITFQztLgHiy6RnwpTVr55BWtD/
SD/wAdcCgYBUMjnggyFXCBlatQwJ0x0kvSts9ssoYAHPjnrM6E4PpG9okSrlCBQ0
zSc+dbwv1qsO2j4i2PlHShMSoR/Vrv+69a9d6S2D2hZzl6L/B4Na+250xdyHyfGS
TWeo5LnGCgNnyl/Mfte1mYjJLJ/A1QAK/NEpddrF2TNMzOiVw9cBWQ==
-----END RSA PRIVATE KEY-----
'''


class PRFunctionalTest(LiveServerTestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 47295
        app.config['DEBUG'] = True
        return app

    def setUp(self):

        # Generate a signing key used for refund output retrieval in get_refund_addresses()
        self.receiver_sk = SigningKey.generate(curve=curves.SECP256k1)

        log.info('Setup IdObj for testid')
        self.test_id_obj = IdObject()
        self.test_id_obj.id = 'testid'
        self.test_id_obj.bip70_enabled = True
        self.test_id_obj.wallet_address = '1MSK1PMnDZN4SLDQ6gB4c6GKRExfGD6Gb3'
        self.test_id_obj.x509_cert = TEST_CERT
        self.test_id_obj.private_key = TEST_CERT_PRIVKEY
        self.test_id_obj.auth_public_key = self.receiver_sk.get_verifying_key().to_string().encode('hex')

        self.resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        self.resolver.save(self.test_id_obj)
        log.info('Save testid IdObj')

        # Keep track of PaymentRequest meta data stored in Redis so it can be cleaned up later
        self.redis_pr_store_cleanup = []

    def tearDown(self):

        time.sleep(1)

        log.info('Clean Up Functest')

        log.info('Deleting Test IdObj')
        self.resolver.delete(self.test_id_obj)

        log.info('Deleting Redis PaymentRequest Meta Data')
        pr_redis = Redis.from_url(config.redis_pr_store)
        for pr in self.redis_pr_store_cleanup:
            pr_redis.delete(pr)

        log.info('Deleting Redis Payment Meta Data')
        payment_redis = Redis.from_url(config.redis_payment_store)
        payment_redis.delete('testtxhash')

    def fetch_payment_request(self):

        pr_url = '%s/address/testid/resolve?bip70=true&amount=33000' % self.get_server_url()

        response = requests.get(pr_url)

        self.assertEqual(200, response.status_code)
        self.assertEqual('binary', response.headers.get('content-transfer-encoding'))
        self.assertEqual('application/bitcoin-paymentrequest', response.headers.get('content-type'))

        return response.content

    def create_and_send_payment_message(self, payment_request):
        pr = PaymentRequest()
        pr.ParseFromString(payment_request)

        pd = PaymentDetails()
        pd.ParseFromString(pr.serialized_payment_details)

        # Retrieve unique payment_url created by Addressimo and replace with Flask LiveServerTestCase server URL
        payment_uuid = pd.payment_url.rsplit('/', 1)[1]
        payment_url = '%s/payment/%s' % (self.get_server_url(), payment_uuid)

        # Add to payment_uuid Redis cleanup list
        self.redis_pr_store_cleanup.append(payment_uuid)

        # Create Payment output to satisfy PaymentRequest
        priv = sha256('random')
        ins = [{'output': '35d49e1833a20baffae35fb1423427d0c23e83b428a933eebde95ac7fd1c967a:0', 'value': 10000, 'script': 'random_script'}]
        outs = [{'value': pd.outputs[0].amount, 'address': '%s' % script_to_address(pd.outputs[0].script)}]
        tx = sign(mktx(ins, outs), 0, priv)

        refund_address = '1CpLXM15vjULK3ZPGUTDMUcGATGR9xGitv'

        self.payment = Payment()
        self.payment.merchant_data = pd.merchant_data
        self.payment.memo = 'Payment memo'
        self.payment.transactions.append(tx)

        output = self.payment.refund_to.add()
        output.amount = pd.outputs[0].amount
        output.script = serialize_script([OP_DUP, OP_HASH160, b58check_to_hex(refund_address), OP_EQUALVERIFY, OP_CHECKSIG]).decode('hex')

        # Set appropriate headers for Payment
        headers = {
            'Content-Type': 'application/bitcoin-payment',
            'Accept': 'application/bitcoin-paymentack',
            'Test-Transaction': True
        }

        response = requests.post(payment_url, data=self.payment.SerializeToString(), headers=headers)

        #######################
        # Validation
        #######################

        # PaymentRequest data used for Payment Creation
        self.assertTrue(pd.payment_url.startswith('https://%s/payment/' % config.site_url))
        self.assertEqual((33000 * 100000000), pd.outputs[0].amount)
        self.assertEqual(payment_uuid, pd.merchant_data)

        # PaymentRequest meta data used later for Payment validation
        pr_redis = Redis.from_url(config.redis_pr_store)
        pr_data = pr_redis.hgetall(payment_uuid)

        self.assertIsNotNone(pr_data.get('expiration_date'))
        payment_data = json.loads(pr_data.get('payment_validation_data'))
        self.assertEqual(self.test_id_obj.wallet_address, payment_data.keys()[0])
        self.assertEqual((33000 * 100000000), payment_data[self.test_id_obj.wallet_address])

        # Payment meta data used for refund endpoint
        payment_redis = Redis.from_url(config.redis_payment_store)
        payment_data = payment_redis.hgetall('testtxhash')

        self.assertIsNotNone(payment_data.get('expiration_date'))
        self.assertEqual('Payment memo', payment_data.get('memo'))
        self.assertEqual("['76a914819d3b204b99f252da2ef21293c621e75dd1444f88ac']", payment_data.get('refund_to'))

        return response

    def verify_paymentack(self, response):

        self.assertEqual(200, response.status_code)
        self.assertEqual('binary', response.headers.get('content-transfer-encoding'))
        self.assertEqual('application/bitcoin-paymentack', response.headers.get('content-type'))

        ack = PaymentACK()
        ack.ParseFromString(response.content)

        self.assertEqual(self.payment, ack.payment)
        self.assertEqual('', ack.memo)

    def get_refund_addresses(self):

        refund_url = '%s/payment/%s/refund/testtxhash' % (self.get_server_url(), self.test_id_obj.id)
        msg_sig = self.receiver_sk.sign(refund_url)

        headers = {
            'x-identity': self.receiver_sk.get_verifying_key().to_string().encode('hex'),
            'x-signature': msg_sig.encode('hex')
        }

        result = requests.get(refund_url, headers=headers)
        self.assertEqual(200, result.status_code)
        rdata = json.loads(result.text)
        self.assertTrue(rdata.get('success'))
        self.assertEqual('Payment memo', rdata.get('memo'))
        self.assertEqual("['76a914819d3b204b99f252da2ef21293c621e75dd1444f88ac']", rdata.get('refund_to'))

    def test_payment_paymentack(self):

        payment_request = self.fetch_payment_request()

        paymentack = self.create_and_send_payment_message(payment_request)

        self.verify_paymentack(paymentack)

        self.get_refund_addresses()


