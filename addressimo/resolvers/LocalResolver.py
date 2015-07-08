__author__ = 'mdavid'

from BaseResolver import BaseResolver
from addressimo.data import IdObject
from addressimo.util import LogUtil

from uuid import uuid4

log = LogUtil.setup_logging()

class LocalResolver(BaseResolver):

    obj_config = {
        '1234567890abcdef': {
            'wallet_address': '1CpLXM15vjULK3ZPGUTDMUcGATGR9xGitv',
            'bip32_enabled': True,
            'master_public_key': 'xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8',
            'bip70_enabled': True,
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

    @classmethod
    def get_plugin_name(cls):
        return 'LOCAL'

    def get_config(self, id):
        config = IdObject(id)
        val = self.obj_config.get(id)
        for key, value in val.items():
            config[key] = value
        return config

    def save(self, id_obj):
        if not id_obj.id:
            id_obj.id = uuid4().hex
        log.info('Save called on LocalResolver [ID: %d]' % id_obj.id)

    def delete(self, id_obj):
        log.inf('Delete called on LocalResolver [ID: %d]' % id_obj.id)