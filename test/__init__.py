import unittest

# load testsuites from module.
import core

def suite():
    suite = unittest.TestSuite()
    suite.addTest(core.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
