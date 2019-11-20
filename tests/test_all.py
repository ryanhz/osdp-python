import unittest

from .test_command import CommandTestCase
from .test_reply import ReplyTestCase
from .test_bus import BusTestCase

def create_suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(CommandTestCase())
    test_suite.addTest(ReplyTestCase())
    test_suite.addTest(BusTestCase())
    return test_suite

if __name__ == '__main__':
   suite = create_suite()

   runner=unittest.TextTestRunner()
   runner.run(suite)