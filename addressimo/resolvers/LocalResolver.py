__author__ = 'mdavid'

from BaseResolver import BaseResolver
from addressimo.data import IdObject
from addressimo.util import LogUtil

from uuid import uuid4

log = LogUtil.setup_logging()


class LocalResolver(BaseResolver):
    local_prr = {
        "id": "b17330349ca44abb9c086e81987045b6",
        "requester_pubkey": "a5fcadc9b7444f46ae5e4457746e6f2d8a27ded3714944a4a4d0746ffae8b913e688016d35e84c2e9540fec92c2a519e",
        "amount": 0,
        "notification_url": "https://notify.me/endpoint/Uuid",
        "x509_cert": "--- OPTIONAL x509 Cert ---",
        "sig": "hex encoded x509 signature - REQUIRED if x509_cert is present"
    }

    local_return_pr = {
        "requester_pubkey": "a5fcadc9b7444f46ae5e4457746e6f2d8a27ded3714944a4a4d0746ffae8b913e688016d35e84c2e9540fec92c2a519e",
        "pr": """SXQgd2FzIHRoZSBiZXN0IG9mIHRpbWVzLA0KaXQgd2FzIHRoZSB3b3JzdCBvZiB0aW1lcywNCml0
IHdhcyB0aGUgYWdlIG9mIHdpc2RvbSwNCml0IHdhcyB0aGUgYWdlIG9mIGZvb2xpc2huZXNzLA0K
aXQgd2FzIHRoZSBlcG9jaCBvZiBiZWxpZWYsDQppdCB3YXMgdGhlIGVwb2NoIG9mIGluY3JlZHVs
aXR5LA0KaXQgd2FzIHRoZSBzZWFzb24gb2YgTGlnaHQsDQppdCB3YXMgdGhlIHNlYXNvbiBvZiBE
YXJrbmVzcywNCml0IHdhcyB0aGUgc3ByaW5nIG9mIGhvcGUsDQppdCB3YXMgdGhlIHdpbnRlciBv
ZiBkZXNwYWlyLA0Kd2UgaGFkIGV2ZXJ5dGhpbmcgYmVmb3JlIHVzLCB3ZSBoYWQgbm90aGluZyBi
ZWZvcmUgdXMsIHdlIHdlcmUgYWxsIGdvaW5nIGRpcmVjdCB0byBIZWF2ZW4sIHdlIHdlcmUgYWxs
IGdvaW5nIGRpcmVjdCB0aGUgb3RoZXIgd2F5lyBpbiBzaG9ydCwgdGhlIHBlcmlvZCB3YXMgc28g
ZmFyIGxpa2UgdGhlIHByZXNlbnQgcGVyaW9kLCB0aGF0IHNvbWUgb2YgaXRzIG5vaXNpZXN0IGF1
dGhvcml0aWVzIGluc2lzdGVkIG9uIGl0cyBiZWluZyByZWNlaXZlZCwgZm9yIGdvb2Qgb3IgZm9y
IGV2aWwsIGluIHRoZSBzdXBlcmxhdGl2ZSBkZWdyZWUgb2YgY29tcGFyaXNvbiBvbmx5Lg=="""
    }

    local_payment_request_meta_data = {
        'expiration_date': '2015-08-08 00:56:44.102893',
        'payment_validation_data': '{"2addr": "2value", "1adder": "1value"}'
    }

    local_refund_data = {
        'memo': 'my memo',
        'refund_to': '1addr'
    }

    obj_config = {
        '1234567890abcdef': {
            'wallet_address': '1CpLXM15vjULK3ZPGUTDMUcGATGR9xGitv',
            'bip32_enabled': True,
            'master_public_key': 'xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8',
            'bip70_enabled': True,
            'prr_only': False,
            'bip70_static_amount': 424242,
            'private_key_location': 'HSM1',
            'private_key_id': 'privKey1234',
            'private_key': '''
-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAL5j+dJFa9/OSeLJ
ghO9DXgoT5Da7clwBtulQOTXy0/K7lryPr6WVzE1CpTv69AaGG7iUsTFqoJ2p0jM
8/xzmOSDRbEw6VgAy+UCZ1Tny4k5fujO9FUiMwRXlIcpo+hZIxoZg+Fch7oeBEN4
o/YhvaCzZLSw2l82oeggxxVRKvh7AgMBAAECgYBLehzm1Cig0AoQgywzIQZ+9RQd
6/zKl8PQPaINVtM97cgye8iOC9HDKzDnvHlyxXWcN9LyOR6Qm/NTdBThpv4cIMwc
DUaGz8eAKvMz7RyPRipwwG0Aq+xvscuJIhEESWBug5M3vbRkNGsGo0nIlkzIAqhn
+zq10R2jMlUXY4M5AQJBAPq3EnTAJD8jx8euNwAC+BELpgLru15lkV0o0z/I1hhk
91F8QhTmSFl17a0H//mMBm+w3QFyyExwtxhLHQFasvsCQQDCZ2Apk6WoggMD2Jv+
5QeRh3sXLX2azTnszRWN5xvOiQcBM5q8+RI4wRviU7A8nbrxlySsS0VAfkLq0qSP
6diBAkEAvdXW1K4UA/b8s1ZXcNvOp2Fxjy6dDenL+oUKB3bznT7+ASYcByUizRI9
J9Ix4OtEiFeb0BfwT+jcyjk9uiPJ9wJBALB2p9p1tJzGDziRieCRQxJ92WTLnUVE
Xv0tmBAsJZiP17Tmg+JfcIPl/oquDr6nKoeb++UNmjoVomaHeGtOCIECQBEtmwwj
Eb0xwt9hlPF3ax7mQTH9et/2bMfoCz0PwrnZQCIyIj+xcExkdkoOd8q4kkVyDvI/
9zfKcsYvAmDU4OQ=
-----END PRIVATE KEY-----
''',
            'x509_cert': '''
-----BEGIN CERTIFICATE-----
MIIC9DCCAl2gAwIBAgIJALbvOdiQX4QgMA0GCSqGSIb3DQEBCwUAMIGSMQswCQYD
VQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEUMBIGA1UEBwwLTG9zIEFuZ2Vs
ZXMxFDASBgNVBAoMC05ldGtpLCBJbmMuMQwwCgYDVQQLDANkZXYxDzANBgNVBAMM
Bm1kYXZpZDEjMCEGCSqGSIb3DQEJARYUb3BlbnNvdXJjZUBuZXRraS5jb20wHhcN
MTUwNDIzMDEzMDI2WhcNMTYwNDIyMDEzMDI2WjCBkjELMAkGA1UEBhMCVVMxEzAR
BgNVBAgMCkNhbGlmb3JuaWExFDASBgNVBAcMC0xvcyBBbmdlbGVzMRQwEgYDVQQK
DAtOZXRraSwgSW5jLjEMMAoGA1UECwwDZGV2MQ8wDQYDVQQDDAZtZGF2aWQxIzAh
BgkqhkiG9w0BCQEWFG9wZW5zb3VyY2VAbmV0a2kuY29tMIGfMA0GCSqGSIb3DQEB
AQUAA4GNADCBiQKBgQC+Y/nSRWvfzkniyYITvQ14KE+Q2u3JcAbbpUDk18tPyu5a
8j6+llcxNQqU7+vQGhhu4lLExaqCdqdIzPP8c5jkg0WxMOlYAMvlAmdU58uJOX7o
zvRVIjMEV5SHKaPoWSMaGYPhXIe6HgRDeKP2Ib2gs2S0sNpfNqHoIMcVUSr4ewID
AQABo1AwTjAdBgNVHQ4EFgQUSXzp9Q6toC9mi3qLLr0/YJfhpEEwHwYDVR0jBBgw
FoAUSXzp9Q6toC9mi3qLLr0/YJfhpEEwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0B
AQsFAAOBgQAU6E55fjxi2+C9FXnEHRVDEt1l1Rl/C6UxuzHtCitG7uSNa0NqJsP3
F4J5pF1jFlRnTix8s/5TMJ9+fQwsYu7mlhTN4xB/9DDA13C40pWkNifeoquhE/+0
rFhAxdbeHjwhElfusbIPLl8jNikPKYIjynm3P+4oTU8jzSqF6FiOTA==
-----END CERTIFICATE-----
            '''
        }
    }

    def get_id_obj(self, id):
        config = IdObject(id)
        val = self.obj_config.get(id)
        for key, value in val.items():
            config[key] = value
        return config

    def get_all_keys(self):
        return ['1', '2', '3']

    def get_branches(self, id):
        return [123, 456, 789]

    def get_lg_index(self, id, branch):
        return [123]

    def set_lg_index(self, id, branch, index):
        log.info('Set lg_index called on LocalResolver [ID: %d | Branch: %d | Index: %d' % (id, branch, index))

    def save(self, id_obj):
        if not id_obj.id:
            id_obj.id = uuid4().hex
        log.info('Save called on LocalResolver [ID: %d]' % id_obj.id)

    def delete(self, id_obj):
        log.info('Delete called on LocalResolver [ID: %d]' % id_obj.id)

    # PaymentRequest Request (PRR) Data Handling
    def add_prr(self, id, prr_data):
        return

    def get_prrs(self, id):
        return [self.local_prr]

    def delete_prr(self, id, prr_id):
        return

    # Return PaymentRequest (RPR) Data Handling
    def add_return_pr(self, return_pr):
        return

    def get_return_pr(self, id):
        return self.local_return_pr

    # Payment Data Handling
    def get_payment_request_meta_data(self, uuid):
        return self.local_payment_request_meta_data

    def set_payment_request_meta_data(self, expiration_date, wallet_addr, amount):
        return

    def set_payment_meta_data(self, tx_hash, memo, refund_address):
        return

    def get_refund_address_from_tx_hash(self, tx_hash):
        return self.local_refund_data

    @classmethod
    def get_plugin_name(cls):
        return 'LOCAL'
