__author__ = 'Matt David'

from mock import patch, Mock
from test import AddressimoTestCase

from addressimo.util import *

class Test_create_json_response(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.util.request')
        self.patcher2 = patch('addressimo.util.current_app')
        self.patcher3 = patch('addressimo.util.Response')

        self.mockRequest = self.patcher1.start()
        self.mockCurrentApp = self.patcher2.start()
        self.mockResponse = self.patcher3.start()

        # Setup Referrer
        self.mockRequest.referrer = 'http://127.0.0.1'
        self.mockRequest.url_rule.rule = '/mockrule'

        # Setup App
        rule_obj = Mock()
        rule_obj.rule = '/mockrule'
        rule_obj.methods = ['POST', 'PUT', 'OPTIONS']

        app_obj = Mock()
        app_obj.url_map = Mock()
        app_obj.url_map._rules = [rule_obj]

        self.mockCurrentApp._get_current_object.return_value = app_obj

    def test_goright(self):

        # Run create_json_response
        ret_val = create_json_response(success=True, message='test message', data={'key':'value'})

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('{"message": "test message", "key": "value", "success": true}', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('application/json', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])

    def test_no_matching_methods(self):

        # Setup Testcase
        self.mockCurrentApp._get_current_object.return_value.url_map._rules = []

        # Run create_json_response
        ret_val = create_json_response(success=True, message='test message', data={'key':'value'})

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('{"message": "test message", "key": "value", "success": true}', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('application/json', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])

    def test_open_origin_for_now_TODO(self):

        # Setup Testcase
        self.mockRequest.referrer = 'http://google.com'

        # Run create_json_response
        ret_val = create_json_response(success=True, message='test message', data={'key':'value'})

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('{"message": "test message", "key": "value", "success": true}', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('application/json', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertNotIn('Access-Control-Allow-Origin', respargs['headers'])

    def test_message_message_success_override(self):

        # Run create_json_response
        ret_val = create_json_response(success=True, message='test message', data={'message':'value', 'success': False, 'key': 'value'})

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('{"message": "test message", "key": "value", "success": true}', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('application/json', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])

    def test_status_204(self):

        # Run create_json_response
        ret_val = create_json_response(success=True, message='test message', data={'key':'value'}, status=204)

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertIsNone(respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(204, respargs['status'])
        self.assertEqual('application/json', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])

# TODO: Finish this up...placeholder
class Test_create_bip72_response(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.util.request')
        self.patcher2 = patch('addressimo.util.current_app')
        self.patcher3 = patch('addressimo.util.Response')

        self.mockRequest = self.patcher1.start()
        self.mockCurrentApp = self.patcher2.start()
        self.mockResponse = self.patcher3.start()

        # Setup Referrer
        self.mockRequest.referrer = 'http://127.0.0.1'
        self.mockRequest.url_rule.rule = '/mockrule'

        # Setup App
        rule_obj = Mock()
        rule_obj.rule = '/mockrule'
        rule_obj.methods = ['POST', 'PUT', 'OPTIONS']

        app_obj = Mock()
        app_obj.url_map = Mock()
        app_obj.url_map._rules = [rule_obj]

        self.mockCurrentApp._get_current_object.return_value = app_obj

        self.mockWalletAddress = '1kjhdslkjghlsfdgkjhsdflgkhj'
        self.mockAmount = '75.4'
        self.mockPaymentRequestURL = 'https://site_url/resolve/id?bip70=true&amount=75.4'

    def test_goright(self):

        # Run create_bip72_response
        ret_val = create_bip72_response(self.mockWalletAddress, self.mockAmount, self.mockPaymentRequestURL)

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('bitcoin:1kjhdslkjghlsfdgkjhsdflgkhj?amount=75.4&r=https%3A%2F%2Fsite_url%2Fresolve%2Fid%3Fbip70%3Dtrue%26amount%3D75.4', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('text/plain', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])

    def test_no_matching_methods(self):

        # Setup Testcase
        self.mockCurrentApp._get_current_object.return_value.url_map._rules = []

        # Run create_bip72_response
        ret_val = create_bip72_response(self.mockWalletAddress, self.mockAmount, self.mockPaymentRequestURL)

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('bitcoin:1kjhdslkjghlsfdgkjhsdflgkhj?amount=75.4&r=https%3A%2F%2Fsite_url%2Fresolve%2Fid%3Fbip70%3Dtrue%26amount%3D75.4', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('text/plain', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])

    def test_open_origin_for_now_TODO(self):

        # Setup Testcase
        self.mockRequest.referrer = 'http://google.com'

        # Run create_bip72_response
        ret_val = create_bip72_response(self.mockWalletAddress, self.mockAmount, self.mockPaymentRequestURL)

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('bitcoin:1kjhdslkjghlsfdgkjhsdflgkhj?amount=75.4&r=https%3A%2F%2Fsite_url%2Fresolve%2Fid%3Fbip70%3Dtrue%26amount%3D75.4', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('text/plain', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertNotIn('Access-Control-Allow-Origin', respargs['headers'])

    def test_no_wallet_address(self):

        # Run create_bip72_response
        ret_val = create_bip72_response(None, self.mockAmount, self.mockPaymentRequestURL)

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('bitcoin:?amount=75.4&r=https%3A%2F%2Fsite_url%2Fresolve%2Fid%3Fbip70%3Dtrue%26amount%3D75.4', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('text/plain', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])

    def test_no_amount(self):

        # Run create_bip72_response
        ret_val = create_bip72_response(self.mockWalletAddress, None, self.mockPaymentRequestURL)

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('bitcoin:1kjhdslkjghlsfdgkjhsdflgkhj?r=https%3A%2F%2Fsite_url%2Fresolve%2Fid%3Fbip70%3Dtrue%26amount%3D75.4', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('text/plain', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])

    def test_no_payment_request_url(self):

        # Run create_bip72_response
        ret_val = create_bip72_response(self.mockWalletAddress, self.mockAmount)

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('bitcoin:1kjhdslkjghlsfdgkjhsdflgkhj?amount=75.4', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('text/plain', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])

    def test_only_payment_request_url(self):

        # Run create_bip72_response
        ret_val = create_bip72_response(None, None, self.mockPaymentRequestURL)

        # Verify Response Data
        respdata = self.mockResponse.call_args[0]
        self.assertEqual('bitcoin:?r=https%3A%2F%2Fsite_url%2Fresolve%2Fid%3Fbip70%3Dtrue%26amount%3D75.4', respdata[0])

        # Verify Response Arguments
        respargs = self.mockResponse.call_args[1]
        self.assertEqual(200, respargs['status'])
        self.assertEqual('text/plain', respargs['mimetype'])
        self.assertEqual('X-Requested-With, accept, content-type', respargs['headers']['Access-Control-Allow-Headers'])
        self.assertEqual('PUT, POST, OPTIONS', respargs['headers']['Access-Control-Allow-Methods'])
        self.assertEqual('http://127.0.0.1', respargs['headers']['Access-Control-Allow-Origin'])


class TestSetupLogging(AddressimoTestCase):

    def setUp(self):
        self.patcher1 = patch('addressimo.util.LogUtil.loggers')
        self.patcher2 = patch('addressimo.util.os')
        self.patcher3 = patch('addressimo.util.logging')

        self.mockLoggers = self.patcher1.start()
        self.mockOS = self.patcher2.start()
        self.mockLogging = self.patcher3.start()

    def test_app_name_exists(self):

        LogUtil.setup_logging(app_name='my_test_app')

        self.assertEqual(self.mockLoggers.get.call_count, 2)
        self.assertFalse(self.mockOS.path.exists.called)
        self.assertEqual(self.mockLoggers.get.call_args_list[1][0][0], 'my_test_app')

    def test_log_path_exists(self):
        self.mockLoggers.get.return_value = None
        self.mockOS.path.exists.return_value = True

        LogUtil.setup_logging()

        self.assertEqual(self.mockLoggers.get.call_count, 1)
        self.assertTrue(self.mockOS.path.exists.called)
        self.assertFalse(self.mockOS.mkdir.called)
        self.assertEqual(self.mockOS.path.abspath.call_args_list[0][0][0], '/var/log/addressimo')

        self.assertEqual(1, self.mockLogging.getLogger.return_value.addFilter.call_count)
        self.assertTrue(isinstance(self.mockLogging.getLogger.return_value.addFilter.call_args[0][0], ContextFilter))

    def test_log_path_does_not_exist(self):
        self.mockLoggers.get.return_value = None
        self.mockOS.path.exists.return_value = False

        LogUtil.setup_logging()

        self.assertEqual(self.mockLoggers.get.call_count, 1)
        self.assertTrue(self.mockOS.path.exists.called)
        self.assertTrue(self.mockOS.mkdir.called)
        self.assertEqual(self.mockOS.path.abspath.call_args_list[0][0][0], '/var/log/addressimo')

        self.assertEqual(1, self.mockLogging.getLogger.return_value.addFilter.call_count)
        self.assertTrue(isinstance(self.mockLogging.getLogger.return_value.addFilter.call_args[0][0], ContextFilter))

    def test_log_to_file_false(self):
        self.mockLoggers.get.return_value = None

        LogUtil.setup_logging(log_to_file=False)

        self.assertEqual(self.mockLogging.StreamHandler.call_args_list[0][0][0].name, '<stdout>')
        self.assertTrue('handlers' not in dir(self.mockLogging))

        self.assertEqual(1, self.mockLogging.getLogger.return_value.addFilter.call_count)
        self.assertTrue(isinstance(self.mockLogging.getLogger.return_value.addFilter.call_args[0][0], ContextFilter))

    def test_log_to_file_true(self):
        self.mockLoggers.get.return_value = None
        LogUtil.setup_logging(log_to_file=True)

        self.assertEqual(self.mockLogging.StreamHandler.call_args_list[0][0][0].name, '<stdout>')
        self.assertEqual(self.mockLogging.handlers.TimedRotatingFileHandler.call_args_list[0][0][0], '/var/log/addressimo/app.log')

        self.assertEqual(1, self.mockLogging.getLogger.return_value.addFilter.call_count)
        self.assertTrue(isinstance(self.mockLogging.getLogger.return_value.addFilter.call_args[0][0], ContextFilter))