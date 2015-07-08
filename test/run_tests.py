__author__ = 'mdavid'

import os
import sys
from unittest import TestLoader, TextTestRunner

if __name__ == '__main__':

    tl = TestLoader()
    master_test_suite = tl.discover(
        start_dir=os.getcwd(),
        pattern='test_*.py',
        top_level_dir=os.path.join(os.getcwd(), '..')
    )

    result = TextTestRunner(verbosity=2).run(master_test_suite)
    if result.errors or result.failures:
        sys.exit(-1)
    sys.exit(0)