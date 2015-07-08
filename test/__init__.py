__author__ = 'mdavid'

from mock import _patch
from unittest import TestCase

class AddressimoTestCase(TestCase):

    def tearDown(self):

        for item, value in self.__dict__.iteritems():
            if item.startswith('patcher') and isinstance(value, _patch):
                try:
                    value.stop()
                except RuntimeError as e:
                    if e.message != 'stop called on unstarted patcher':
                        raise
                    print "TEST ERROR: Patcher Not Started [%s - %s]" % (self.__class__.__name__, self._testMethodName)
                    raise
