__author__ = 'Matt David'

from mock import patch, Mock
from test import AddressimoTestCase

from addressimo.crypto import *

class TestDeriveBranch(AddressimoTestCase):
    def setUp(self):
        self.patcher1 = patch('addressimo.crypto.iptools')
        self.patcher2 = patch('addressimo.crypto.request')

        self.mockIpTools = self.patcher1.start()
        self.mockRequest = self.patcher2.start()

    def testGoRightAbove2147483648(self):

        # Setup Test Case
        self.mockIpTools.ipv4.ip2long.return_value = 3000000000

        ret_val = derive_branch()

        self.assertEqual(24064, ret_val)
        self.assertEqual(1, self.mockIpTools.ipv4.ip2long.call_count)
        self.assertEqual(self.mockRequest.remote_addr, self.mockIpTools.ipv4.ip2long.call_args[0][0])

    def testGoRightBelow2147483648(self):

        # Setup Test Case
        self.mockIpTools.ipv4.ip2long.return_value = 1000000000

        ret_val = derive_branch()

        self.assertEqual(51712, ret_val)
        self.assertEqual(1, self.mockIpTools.ipv4.ip2long.call_count)
        self.assertEqual(self.mockRequest.remote_addr, self.mockIpTools.ipv4.ip2long.call_args[0][0])

class TestGenerateBIP32AddressFromExtendedPublicKey(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.crypto.BIP32Node')
        self.mockBIP32Node = self.patcher1.start()

    def test_go_right(self):

        ret_val = generate_bip32_address_from_extended_pubkey('xpub_extended_pubkey', 1231244, 3)

        self.assertEqual(self.mockBIP32Node.from_wallet_key.return_value.subkey_for_path.return_value.address.return_value, ret_val)

        self.assertEqual(1, self.mockBIP32Node.from_wallet_key.call_count)
        self.assertEqual('xpub_extended_pubkey', self.mockBIP32Node.from_wallet_key.call_args[0][0])

        self.assertEqual(1, self.mockBIP32Node.from_wallet_key.return_value.subkey_for_path.call_count)
        self.assertEqual('1231244/3', self.mockBIP32Node.from_wallet_key.return_value.subkey_for_path.call_args[0][0])
        self.assertEqual(1, self.mockBIP32Node.from_wallet_key.return_value.subkey_for_path.return_value.address.call_count)

class TestGetCerts(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.crypto.ssl')
        self.mockSsl = self.patcher1.start()

    def test_go_right_single_cert(self):

        data = '''
test-data
-----END CERTIFICATE-----
                '''

        ret_val = get_certs(data)

        self.assertIn(self.mockSsl.PEM_cert_to_DER_cert.return_value, ret_val)
        self.assertEqual(1, len(ret_val))

        self.assertEqual(1, self.mockSsl.PEM_cert_to_DER_cert.call_count)
        self.assertEqual(data.replace('\n','').strip(), self.mockSsl.PEM_cert_to_DER_cert.call_args[0][0])

    def test_go_right_multiple_certs(self):

        data = '''
test-data
-----END CERTIFICATE-----
test-data2
-----END CERTIFICATE-----
test-data3
-----END CERTIFICATE-----
                '''

        ret_val = get_certs(data)

        self.assertIn(self.mockSsl.PEM_cert_to_DER_cert.return_value, ret_val)
        self.assertEqual(3, len(ret_val))

        self.assertEqual(3, self.mockSsl.PEM_cert_to_DER_cert.call_count)
        self.assertEqual('test-data-----END CERTIFICATE-----', self.mockSsl.PEM_cert_to_DER_cert.call_args_list[0][0][0])
        self.assertEqual('test-data2-----END CERTIFICATE-----', self.mockSsl.PEM_cert_to_DER_cert.call_args_list[1][0][0])
        self.assertEqual('test-data3-----END CERTIFICATE-----', self.mockSsl.PEM_cert_to_DER_cert.call_args_list[2][0][0])

class GeneratePaymentRequest(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.crypto.serialize_script')
        self.patcher2 = patch('addressimo.crypto.b58check_to_hex')
        self.patcher3 = patch('addressimo.crypto.PluginManager')
        self.patcher4 = patch('addressimo.crypto.get_certs')
        self.patcher5 = patch('addressimo.crypto.datetime', wraps=datetime, spec=datetime)

        self.mockSerializeScript = self.patcher1.start()
        self.mockB58CheckToHex = self.patcher2.start()
        self.mockPluginManager = self.patcher3.start()
        self.mockGetCerts = self.patcher4.start()
        self.mockDatetime = self.patcher5.start()

        self.mockSerializeScript.return_value = 'BFFBFFBFFBFF'

        self.mockSigner = Mock()
        self.mockSigner.sign.return_value = 'signature'
        self.mockSigner.get_pki_type.return_value = 'pki_type'

        self.mockGetCerts.return_value = ['cert1', 'cert2']

        self.crypto_addr = '1abdcdefg123456789'
        self.x509_cert = 'x509_cert'

        self.mockDatetime.utcnow.return_value = datetime(2015, 6, 13, 9, 0, 0)

    def test_go_right_defaults(self):

        ret_val = generate_payment_request(self.crypto_addr, self.x509_cert, self.mockSigner)

        self.assertIsNotNone(ret_val)

        self.assertEqual(1, self.mockSerializeScript.call_count)
        self.assertEqual([OP_DUP, OP_HASH160, self.mockB58CheckToHex.return_value, OP_EQUALVERIFY, OP_CHECKSIG], self.mockSerializeScript.call_args[0][0])

        self.assertEqual(1, self.mockB58CheckToHex.call_count)
        self.assertEqual(self.crypto_addr, self.mockB58CheckToHex.call_args[0][0])

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('LOGGER', self.mockPluginManager.get_plugin.call_args[0][0])

        self.assertEqual(1, self.mockGetCerts.call_count)
        self.assertEqual(self.x509_cert, self.mockGetCerts.call_args[0][0])

        self.assertEqual(2, self.mockDatetime.utcnow.call_count)
        self.assertEqual(1, self.mockSigner.sign.call_count)

        pr = PaymentRequest()
        pr.ParseFromString(ret_val)
        self.assertEqual(1, pr.payment_details_version)
        self.assertEqual('\n\x05cert1\n\x05cert2', pr.pki_data)
        self.assertEqual('pki_type', pr.pki_type)
        self.assertEqual('signature', pr.signature)

        pd = PaymentDetails()
        pd.ParseFromString(pr.serialized_payment_details)
        self.assertEqual(1434212100, pd.expires)
        self.assertEqual('', pd.memo)
        self.assertEqual('', pd.merchant_data)
        self.assertEqual('main', pd.network)
        self.assertEqual('', pd.payment_url)
        self.assertEqual(1434211200, pd.time)

        for output in pd.outputs:
            self.assertEqual(0, output.amount)
            self.assertEqual('\xbf\xfb\xff\xbf\xfb\xff', output.script)

    def test_go_right_all_args(self):

        ret_val = generate_payment_request(
            self.crypto_addr,
            self.x509_cert,
            self.mockSigner,
            amount=9999,
            expires=datetime(2015,7,1),
            memo='memo',
            payment_url='https://payme.domain.com/path?query',
            merchant_data='merchant_data'
        )

        self.assertIsNotNone(ret_val)

        self.assertEqual(1, self.mockSerializeScript.call_count)
        self.assertEqual([OP_DUP, OP_HASH160, self.mockB58CheckToHex.return_value, OP_EQUALVERIFY, OP_CHECKSIG], self.mockSerializeScript.call_args[0][0])

        self.assertEqual(1, self.mockB58CheckToHex.call_count)
        self.assertEqual(self.crypto_addr, self.mockB58CheckToHex.call_args[0][0])

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('LOGGER', self.mockPluginManager.get_plugin.call_args[0][0])

        self.assertEqual(1, self.mockGetCerts.call_count)
        self.assertEqual(self.x509_cert, self.mockGetCerts.call_args[0][0])

        self.assertEqual(1, self.mockDatetime.utcnow.call_count)
        self.assertEqual(1, self.mockSigner.sign.call_count)

        pr = PaymentRequest()
        pr.ParseFromString(ret_val)
        self.assertEqual(1, pr.payment_details_version)
        self.assertEqual('\n\x05cert1\n\x05cert2', pr.pki_data)
        self.assertEqual('pki_type', pr.pki_type)
        self.assertEqual('signature', pr.signature)

        pd = PaymentDetails()
        pd.ParseFromString(pr.serialized_payment_details)
        self.assertEqual(1435734000, pd.expires)
        self.assertEqual('memo', pd.memo)
        self.assertEqual('merchant_data', pd.merchant_data)
        self.assertEqual('main', pd.network)
        self.assertEqual('https://payme.domain.com/path?query', pd.payment_url)
        self.assertEqual(1434211200, pd.time)

        for output in pd.outputs:
            self.assertEqual(999900000000, output.amount)
            self.assertEqual('\xbf\xfb\xff\xbf\xfb\xff', output.script)

    def test_no_signer(self):

        ret_val = generate_payment_request(self.crypto_addr, self.x509_cert)

        self.assertIsNotNone(ret_val)

        self.assertEqual(1, self.mockSerializeScript.call_count)
        self.assertEqual([OP_DUP, OP_HASH160, self.mockB58CheckToHex.return_value, OP_EQUALVERIFY, OP_CHECKSIG], self.mockSerializeScript.call_args[0][0])

        self.assertEqual(1, self.mockB58CheckToHex.call_count)
        self.assertEqual(self.crypto_addr, self.mockB58CheckToHex.call_args[0][0])

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('LOGGER', self.mockPluginManager.get_plugin.call_args[0][0])

        self.assertEqual(0, self.mockGetCerts.call_count)

        self.assertEqual(2, self.mockDatetime.utcnow.call_count)
        self.assertEqual(0, self.mockSigner.sign.call_count)

        pr = PaymentRequest()
        pr.ParseFromString(ret_val)
        self.assertEqual(1, pr.payment_details_version)
        self.assertEqual('', pr.pki_data)
        self.assertEqual('none', pr.pki_type)
        self.assertEqual('', pr.signature)

        pd = PaymentDetails()
        pd.ParseFromString(pr.serialized_payment_details)
        self.assertEqual(1434212100, pd.expires)
        self.assertEqual('', pd.memo)
        self.assertEqual('', pd.merchant_data)
        self.assertEqual('main', pd.network)
        self.assertEqual('', pd.payment_url)
        self.assertEqual(1434211200, pd.time)

        for output in pd.outputs:
            self.assertEqual(0, output.amount)
            self.assertEqual('\xbf\xfb\xff\xbf\xfb\xff', output.script)

    def test_go_right_non_P2KH_non_hex_addr(self):

        ret_val = generate_payment_request('addr', self.x509_cert, self.mockSigner)

        self.assertIsNotNone(ret_val)

        self.assertEqual(0, self.mockSerializeScript.call_count)
        self.assertEqual(0, self.mockB58CheckToHex.call_count)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('LOGGER', self.mockPluginManager.get_plugin.call_args[0][0])

        self.assertEqual(1, self.mockGetCerts.call_count)
        self.assertEqual(self.x509_cert, self.mockGetCerts.call_args[0][0])

        self.assertEqual(2, self.mockDatetime.utcnow.call_count)
        self.assertEqual(1, self.mockSigner.sign.call_count)

        pr = PaymentRequest()
        pr.ParseFromString(ret_val)
        self.assertEqual(1, pr.payment_details_version)
        self.assertEqual('\n\x05cert1\n\x05cert2', pr.pki_data)
        self.assertEqual('pki_type', pr.pki_type)
        self.assertEqual('signature', pr.signature)

        pd = PaymentDetails()
        pd.ParseFromString(pr.serialized_payment_details)
        self.assertEqual(1434212100, pd.expires)
        self.assertEqual('', pd.memo)
        self.assertEqual('', pd.merchant_data)
        self.assertEqual('main', pd.network)
        self.assertEqual('', pd.payment_url)
        self.assertEqual(1434211200, pd.time)

        for output in pd.outputs:
            self.assertEqual(0, output.amount)
            self.assertEqual('addr', output.script)

    def test_go_right_non_P2KH_hex_addr(self):

        ret_val = generate_payment_request('abcf9975', self.x509_cert, self.mockSigner)

        self.assertIsNotNone(ret_val)

        self.assertEqual(0, self.mockSerializeScript.call_count)
        self.assertEqual(0, self.mockB58CheckToHex.call_count)

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('LOGGER', self.mockPluginManager.get_plugin.call_args[0][0])

        self.assertEqual(1, self.mockGetCerts.call_count)
        self.assertEqual(self.x509_cert, self.mockGetCerts.call_args[0][0])

        self.assertEqual(2, self.mockDatetime.utcnow.call_count)
        self.assertEqual(1, self.mockSigner.sign.call_count)

        pr = PaymentRequest()
        pr.ParseFromString(ret_val)
        self.assertEqual(1, pr.payment_details_version)
        self.assertEqual('\n\x05cert1\n\x05cert2', pr.pki_data)
        self.assertEqual('pki_type', pr.pki_type)
        self.assertEqual('signature', pr.signature)

        pd = PaymentDetails()
        pd.ParseFromString(pr.serialized_payment_details)
        self.assertEqual(1434212100, pd.expires)
        self.assertEqual('', pd.memo)
        self.assertEqual('', pd.merchant_data)
        self.assertEqual('main', pd.network)
        self.assertEqual('', pd.payment_url)
        self.assertEqual(1434211200, pd.time)

        for output in pd.outputs:
            self.assertEqual(0, output.amount)
            self.assertEqual('\xab\xcf\x99u', output.script)

    def test_expires_datetime(self):

        ret_val = generate_payment_request(self.crypto_addr, self.x509_cert, self.mockSigner, expires=datetime(2015,7,1))

        self.assertIsNotNone(ret_val)

        self.assertEqual(1, self.mockSerializeScript.call_count)
        self.assertEqual([OP_DUP, OP_HASH160, self.mockB58CheckToHex.return_value, OP_EQUALVERIFY, OP_CHECKSIG], self.mockSerializeScript.call_args[0][0])

        self.assertEqual(1, self.mockB58CheckToHex.call_count)
        self.assertEqual(self.crypto_addr, self.mockB58CheckToHex.call_args[0][0])

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('LOGGER', self.mockPluginManager.get_plugin.call_args[0][0])

        self.assertEqual(1, self.mockGetCerts.call_count)
        self.assertEqual(self.x509_cert, self.mockGetCerts.call_args[0][0])

        self.assertEqual(1, self.mockDatetime.utcnow.call_count)
        self.assertEqual(1, self.mockSigner.sign.call_count)

        pr = PaymentRequest()
        pr.ParseFromString(ret_val)
        self.assertEqual(1, pr.payment_details_version)
        self.assertEqual('\n\x05cert1\n\x05cert2', pr.pki_data)
        self.assertEqual('pki_type', pr.pki_type)
        self.assertEqual('signature', pr.signature)

        pd = PaymentDetails()
        pd.ParseFromString(pr.serialized_payment_details)
        self.assertEqual(1435734000, pd.expires)
        self.assertEqual('', pd.memo)
        self.assertEqual('', pd.merchant_data)
        self.assertEqual('main', pd.network)
        self.assertEqual('', pd.payment_url)
        self.assertEqual(1434211200, pd.time)

        for output in pd.outputs:
            self.assertEqual(0, output.amount)
            self.assertEqual('\xbf\xfb\xff\xbf\xfb\xff', output.script)

    def test_expires_number(self):

        ret_val = generate_payment_request(self.crypto_addr, self.x509_cert, self.mockSigner, expires=3600)

        self.assertIsNotNone(ret_val)

        self.assertEqual(1, self.mockSerializeScript.call_count)
        self.assertEqual([OP_DUP, OP_HASH160, self.mockB58CheckToHex.return_value, OP_EQUALVERIFY, OP_CHECKSIG], self.mockSerializeScript.call_args[0][0])

        self.assertEqual(1, self.mockB58CheckToHex.call_count)
        self.assertEqual(self.crypto_addr, self.mockB58CheckToHex.call_args[0][0])

        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('LOGGER', self.mockPluginManager.get_plugin.call_args[0][0])

        self.assertEqual(1, self.mockGetCerts.call_count)
        self.assertEqual(self.x509_cert, self.mockGetCerts.call_args[0][0])

        self.assertEqual(2, self.mockDatetime.utcnow.call_count)
        self.assertEqual(1, self.mockSigner.sign.call_count)

        pr = PaymentRequest()
        pr.ParseFromString(ret_val)
        self.assertEqual(1, pr.payment_details_version)
        self.assertEqual('\n\x05cert1\n\x05cert2', pr.pki_data)
        self.assertEqual('pki_type', pr.pki_type)
        self.assertEqual('signature', pr.signature)

        pd = PaymentDetails()
        pd.ParseFromString(pr.serialized_payment_details)
        self.assertEqual(1434214800, pd.expires)
        self.assertEqual('', pd.memo)
        self.assertEqual('', pd.merchant_data)
        self.assertEqual('main', pd.network)
        self.assertEqual('', pd.payment_url)
        self.assertEqual(1434211200, pd.time)

        for output in pd.outputs:
            self.assertEqual(0, output.amount)
            self.assertEqual('\xbf\xfb\xff\xbf\xfb\xff', output.script)

class TestGetUnusedPresignedPaymentRequest(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.crypto.Redis')
        self.patcher2 = patch('addressimo.crypto.get_addrs_from_paymentrequest')
        self.patcher3 = patch('addressimo.crypto.PluginManager')

        self.mockRedis = self.patcher1.start()
        self.mockGetAddressFromPR = self.patcher2.start()
        self.mockPluginManager = self.patcher3.start()

        self.mockGetAddressFromPR.return_value = ['123456789']

        self.id_obj = Mock()
        self.id_obj.presigned_payment_requests = [
            'PR1'.encode('hex'),
            'PR2'.encode('hex')
        ]

        self.mockRedis.from_url.return_value.get.return_value = False

    def test_go_right_no_pr_used(self):

        ret_val = get_unused_presigned_payment_request(self.id_obj)

        self.assertEqual('PR1'.encode('hex'), ret_val)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(1, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual(1, self.mockGetAddressFromPR.call_count)
        self.assertEqual(0, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual(0, self.id_obj.save.call_count)

    def test_go_right_first_pr_used(self):

        self.mockRedis.from_url.return_value.get.side_effect = [True, None]

        ret_val = get_unused_presigned_payment_request(self.id_obj)

        self.assertEqual('PR2'.encode('hex'), ret_val)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(2, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual(2, self.mockGetAddressFromPR.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual('REDIS', self.mockPluginManager.get_plugin.call_args[0][1])

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(self.id_obj, self.mockPluginManager.get_plugin.return_value.save.call_args[0][0])
        self.assertNotIn('PR1'.encode('hex'), self.id_obj.presigned_payment_requests)


    def test_go_right_all_pr_used(self):

        self.mockRedis.from_url.return_value.get.side_effect = [True, True]

        ret_val = get_unused_presigned_payment_request(self.id_obj)

        self.assertIsNone(ret_val)
        self.assertEqual(1, self.mockRedis.from_url.call_count)
        self.assertEqual(2, self.mockRedis.from_url.return_value.get.call_count)
        self.assertEqual(2, self.mockGetAddressFromPR.call_count)
        self.assertEqual(1, self.mockPluginManager.get_plugin.call_count)
        self.assertEqual('RESOLVER', self.mockPluginManager.get_plugin.call_args[0][0])
        self.assertEqual('REDIS', self.mockPluginManager.get_plugin.call_args[0][1])

        self.assertEqual(1, self.mockPluginManager.get_plugin.return_value.save.call_count)
        self.assertEqual(self.id_obj, self.mockPluginManager.get_plugin.return_value.save.call_args[0][0])
        self.assertNotIn('PR1'.encode('hex'), self.id_obj.presigned_payment_requests)
        self.assertNotIn('PR2'.encode('hex'), self.id_obj.presigned_payment_requests)

class TestGetAddrsFromPaymentRequest(AddressimoTestCase):

    def setUp(self):

        self.crypto_addr1 = '1HjDauL2kth6KJUz5vX198Nvp1xN1hgYRb'
        self.crypto_addr2 = '13HFqPr9Ceh2aBvcjxNdUycHuFG7PReGH4'

        self.pd = PaymentDetails()
        output1 = self.pd.outputs.add()
        output1.script = serialize_script([OP_DUP, OP_HASH160, b58check_to_hex(self.crypto_addr1), OP_EQUALVERIFY, OP_CHECKSIG]).decode('hex')
        output2 = self.pd.outputs.add()
        output2.script = serialize_script([OP_DUP, OP_HASH160, b58check_to_hex(self.crypto_addr2), OP_EQUALVERIFY, OP_CHECKSIG]).decode('hex')
        self.pd.time = int(datetime.utcnow().strftime('%s'))

        self.pr = PaymentRequest()
        self.pr.serialized_payment_details = self.pd.SerializeToString()

    def test_go_right(self):

        ret_val = get_addrs_from_paymentrequest(self.pr.SerializeToString())

        self.assertIn('1HjDauL2kth6KJUz5vX198Nvp1xN1hgYRb', ret_val)
        self.assertIn('13HFqPr9Ceh2aBvcjxNdUycHuFG7PReGH4', ret_val)