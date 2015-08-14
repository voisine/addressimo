__author__ = 'frank'

from addressimo.data import *
from test import AddressimoTestCase

class TestGetExpires(AddressimoTestCase):
    def setUp(self):
        # self.patcher1 = patch('addressimo.data.datetime', wraps=datetime)
        # self.mockDatetime = self.patcher1.start()

        self.id_obj = IdObject()

        self.now = datetime.utcnow()
        config.bip70_default_expiration = 6000

    def test_expires_datetime(self):

        # Setup test case
        self.id_obj.expires = self.now

        ret_val = self.id_obj.get_expires()

        self.assertEqual(int(self.now.strftime('%s')), ret_val)

    def test_expires_number(self):

        # Setup test case
        self.id_obj.expires = 3000

        ret_val = self.id_obj.get_expires()

        self.assertEqual(int((self.now + timedelta(seconds=3000)).strftime('%s')), ret_val)

    def test_expires_from_config(self):

        ret_val = self.id_obj.get_expires()

        self.assertEqual(int((self.now + timedelta(seconds=config.bip70_default_expiration)).strftime('%s')), ret_val)
