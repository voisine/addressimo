__author__ = 'frank'

# System Imports
import json
from mock import Mock, patch
from test import AddressimoTestCase

from addressimo.signer.LocalSigner import *


class TestSetIdObj(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.signer.LocalSigner.crypto')

        self.mockCrypto = self.patcher1.start()

        self.id_obj = Mock()

        self.ls = LocalSigner()

    def test_go_right(self):

        self.ls.set_id_obj(self.id_obj)

        # Validate calls
        self.assertEqual(self.mockCrypto.load_privatekey.return_value, self.ls.privkey)
        self.assertEqual(1, self.mockCrypto.load_privatekey.call_count)
        self.assertEqual(self.mockCrypto.FILETYPE_PEM, self.mockCrypto.load_privatekey.call_args[0][0])
        self.assertEqual(self.id_obj.private_key, self.mockCrypto.load_privatekey.call_args[0][1])

    def test_id_obj_missing(self):

        self.assertRaisesRegexp(ValueError, 'LocalSigner Requires ID Configuration', self.ls.set_id_obj, '')

    def test_private_key_missing(self):

        self.id_obj.private_key = None

        self.assertRaisesRegexp(ValueError, 'id_obj missing private key', self.ls.set_id_obj, self.id_obj)

class TestFunctions(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.signer.LocalSigner.crypto')

        self.mockCrypto = self.patcher1.start()

        self.id_obj = Mock()
        self.ls = LocalSigner()
        self.ls.set_id_obj(self.id_obj)

    def test_get_plugin_name(self):
        self.assertEqual('LOCAL', self.ls.get_plugin_name())

    def test_sign(self):

        ret_val = self.ls.sign('data')

        self.assertEqual(self.mockCrypto.sign.return_value, ret_val)
        self.assertEqual(self.mockCrypto.load_privatekey.return_value, self.mockCrypto.sign.call_args[0][0])
        self.assertEqual('data', self.mockCrypto.sign.call_args[0][1])
        self.assertEqual('sha256', self.mockCrypto.sign.call_args[0][2])

    def test_get_pki_type(self):
        self.assertEqual('x509+sha256', self.ls.get_pki_type())