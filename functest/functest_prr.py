__author__ = 'Matt David'

import hashlib
import json
import requests
import time
import unittest

from datetime import datetime, timedelta
from ecdsa import SigningKey, curves, VerifyingKey
from flask.ext.testing import LiveServerTestCase
from OpenSSL import crypto
from Crypto.Cipher import AES

from addressimo.config import config
from addressimo.data import IdObject
from addressimo.plugin import PluginManager
from addressimo.paymentrequest.paymentrequest_pb2 import PaymentRequest, PaymentDetails
from addressimo.util import LogUtil
from server import app

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

log = LogUtil.setup_logging()

# Crypto Utility Functions
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]

class PRRFunctionalTest(LiveServerTestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 47294
        app.config['DEBUG'] = True
        return app

    def setUp(self):

        log.info('Generating ECDSA Keypairs for Testing')
        self.sender_sk = SigningKey.generate(curve=curves.SECP256k1)
        self.receiver_sk = SigningKey.generate(curve=curves.SECP256k1)

        log.info('Setup IdObj for testid')
        self.test_id_obj = IdObject()
        self.test_id_obj.auth_public_key = self.receiver_sk.get_verifying_key().to_string().encode('hex')
        self.test_id_obj.id = 'testid'
        self.test_id_obj.prr_only = True

        self.resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)
        self.resolver.save(self.test_id_obj)
        log.info('Save testid IdObj')

    def tearDown(self):

        time.sleep(1)

        log.info('Clean Up Functest')

        log.info('Deleting All testid PRRs if any exist')
        for prr in self.resolver.get_prrs('testid'):
            log.info('Deleting PRR [ID: %s]' % prr.get('id'))
            self.resolver.delete_prr('testid', prr.get('id'))

        log.info('Deleting Test IdObj')
        self.resolver.delete(self.test_id_obj)

    def test_prr_flow(self):

        # Load Crypto Keys
        self.x509_cert = crypto.load_certificate(crypto.FILETYPE_PEM, TEST_CERT)
        self.x509_cert_privkey = crypto.load_privatekey(crypto.FILETYPE_PEM, TEST_CERT_PRIVKEY)

        #######################
        # Create PRR
        #######################
        prr_data = {
            'amount': 75,
            'notification_url': 'https://notify.me/longId',
            'x509_cert': TEST_CERT
        }

        # Handle x509 Signature
        sign_url = "%s/address/testid/resolve" % self.get_server_url()
        sig = crypto.sign(self.x509_cert_privkey, sign_url + json.dumps(prr_data), 'sha1')
        prr_data['signature'] = sig.encode('hex')

        # Sign Request
        msg_sig = self.sender_sk.sign(sign_url + json.dumps(prr_data))

        prr_headers = {
            'X-Identity': self.sender_sk.get_verifying_key().to_string().encode('hex'),
            'X-Signature': msg_sig.encode('hex'),
            'Content-Type': 'application/json'
        }
        response = requests.post(sign_url, headers=prr_headers, data=json.dumps(prr_data))

        # Validate Response
        self.assertEqual(202, response.status_code)
        self.assertTrue(response.headers.get('Location').startswith('https://%s/paymentrequest' % config.site_url))
        self.payment_id = response.headers.get('Location').rsplit('/', 1)[1]

        #######################
        # Get PRRs
        #######################
        sign_url = "%s/address/testid/prr" % self.get_server_url()
        msg_sig = self.receiver_sk.sign(sign_url)

        prr_req_headers = {
            'X-Identity': self.receiver_sk.get_verifying_key().to_string().encode('hex'),
            'X-Signature': msg_sig.encode('hex')
        }
        response = requests.get(sign_url, headers=prr_req_headers)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.text)
        resp_json = response.json()

        # TODO: See why the test case is running twice - there is a bug in Flask-Testing, but the test works as of now
        self.assertGreaterEqual(resp_json.get('count'), 1)

        #######################
        # Create RPR
        #######################
        pd = PaymentDetails()
        pd.network = 'main'
        output = pd.outputs.add()
        output.amount = resp_json.get('requests')[0]['amount']
        output.script = 'paymesomemoneyhere'.encode('hex')
        pd.time = int(datetime.utcnow().strftime('%s'))
        pd.expires = int((datetime.utcnow() + timedelta(seconds=3600)).strftime('%s'))
        pd.memo = ''
        pd.payment_url = ''
        pd.merchant_data = ''

        pr = PaymentRequest()
        pr.payment_details_version = 1
        pr.pki_type = 'none'
        pr.pki_data = ''
        pr.serialized_payment_details = pd.SerializeToString()
        pr.signature = 'testforme'

        self.serialized_pr = pr.SerializeToString()

        # Determine ECDH Shared Key
        sending_pubkey = VerifyingKey.from_string(resp_json.get('requests')[0]['sender_pubkey'].decode('hex'), curve=curves.SECP256k1)
        ecdh_point = self.receiver_sk.privkey.secret_multiplier * sending_pubkey.pubkey.point

        # Encrypt PR
        # TODO: Perhaps we should use ECIES here? Unfortunately it's not as secure as AES256
        secret_key = hashlib.sha256(str(ecdh_point.x())).digest()

        encrypt_obj = AES.new(secret_key, AES.MODE_ECB)
        ciphertext = encrypt_obj.encrypt(pad(self.serialized_pr))

        self.assertEqual(self.payment_id, resp_json.get('requests')[0]['id'])

        submit_rpr_data = {
            "ready_requests": [
                {
                    "id": resp_json.get('requests')[0]['id'],
                    "receiver_pubkey": self.receiver_sk.get_verifying_key().to_string().encode('hex'),
                    "encrypted_payment_request": ciphertext.encode('hex')
                }
            ]
        }
        sign_url = "%s/address/testid/prr" % self.get_server_url()
        msg_sig = self.receiver_sk.sign(sign_url + json.dumps(submit_rpr_data))

        prr_req_headers = {
            'X-Identity': self.receiver_sk.get_verifying_key().to_string().encode('hex'),
            'X-Signature': msg_sig.encode('hex'),
            'Content-Type': 'application/json'
        }
        response = requests.post(sign_url, data=json.dumps(submit_rpr_data), headers=prr_req_headers)
        self.assertEqual(200, response.status_code)

        # Verify the PRR was deleted after submission occurred
        for prr in self.resolver.get_prrs('testid'):
            self.assertFalse(prr['id'] == resp_json.get('requests')[0]['id'])

        # Make Sure One RPR Was Accepted
        resp_json = response.json()
        self.assertEqual(1, resp_json['accept_count'])

        #######################
        # Retrieve RPR
        #######################
        sign_url = "%s/paymentrequest/%s" % (self.get_server_url(), self.payment_id)
        response = requests.get(sign_url)
        self.assertIsNotNone(response)

        resp_json = response.json()
        log.info(resp_json)
        self.assertEqual(self.receiver_sk.get_verifying_key().to_string().encode('hex'), resp_json['receiver_pubkey'])
        self.assertEqual(ciphertext.encode('hex'), resp_json['encrypted_payment_request'])

        # Decrypt Response

        # Determine ECDH Shared Key
        receiving_pubkey = VerifyingKey.from_string(resp_json.get('receiver_pubkey').decode('hex'), curve=curves.SECP256k1)
        decrypt_ecdh_point = self.sender_sk.privkey.secret_multiplier * receiving_pubkey.pubkey.point

        # Decrypt PR
        # TODO: Perhaps we should use ECIES here? Unfortunately it's not as secure as AES256
        secret_key = hashlib.sha256(str(decrypt_ecdh_point.x())).digest()

        decrypt_obj = AES.new(secret_key, AES.MODE_ECB)
        decrypt_ciphertext = unpad(decrypt_obj.decrypt(resp_json.get('encrypted_payment_request').decode('hex')))
        self.assertEqual(self.serialized_pr, decrypt_ciphertext)

        rpr = PaymentRequest()
        rpr.ParseFromString(decrypt_ciphertext)
        self.assertEqual(1, rpr.payment_details_version)
        self.assertEqual('none', rpr.pki_type)
        self.assertEqual('', rpr.pki_data)
        self.assertEqual(pd.SerializeToString(), rpr.serialized_payment_details)
        self.assertEqual('testforme', rpr.signature)

if __name__ == '__main__':
    unittest.main()