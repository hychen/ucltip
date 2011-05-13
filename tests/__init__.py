#!/usr/bin/env python
# -*- encoding=utf8 -*-
#
# Author 2010 Hsin-Yi Chen
#
# This is a free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this software; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA

import unittest
import ucltip

class UtilsTestCase(unittest.TestCase):

    def test_kwargsname_to_optionname(self):
        """test transform keyword arguments's name to command's option name.
        """
        self.assertEquals(ucltip.optname('k'), '-k')
        self.assertEquals(ucltip.optname('key'), '--key')
        self.assertEquals(ucltip.optname('key_one'), '--key-one')

    def test_transform_kwargs_to_booloption(self):
        """test transform keyword to command's boolean style option.
        """
        self.assertEquals(ucltip.transform_kwargs(0, k=True), ['-k'])
        self.assertEquals(ucltip.transform_kwargs(1, k=True), ['-k'])
        self.assertEquals(ucltip.transform_kwargs(0, key=True), ['--key'])
        self.assertEquals(ucltip.transform_kwargs(1, key=True), ['--key'])

    def test_transform_kwargs_to_keyvauleoption(self):
        """test transform keyword to command's key-value style option name.
        """
        self.assertEquals(ucltip.transform_kwargs(0, k=123), ['-k', '123'])
        self.assertEquals(ucltip.transform_kwargs(1, k=123), ['-k=123'])
        self.assertEquals(ucltip.transform_kwargs(0, key=123), ['--key', '123'])
        self.assertEquals(ucltip.transform_kwargs(1, key=123), ['--key=123'])

    def test_make_multi_options(self):
        """test make multi option string with the same option name
        """
        self.assertEquals(ucltip.make_optargs('colum', ('first','second'), 0),
                          ['--colum','first', '--colum', 'second'])
        self.assertEquals(ucltip.make_optargs('colum', ('first','second'), 1),
                          ['--colum=first','--colum=second'])

    def test_cmdexist(self):
        """check commands exists """
        self.assertFalse(ucltip.cmdexists(None))
        self.assertFalse(ucltip.cmdexists(''))
        self.assertFalse(ucltip.cmdexists(1234.5))
        self.assertFalse(ucltip.cmdexists(1234))

    def test_command_not_found(self):
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, None)
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, '')
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, 1234.5)
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, '000')

class ExecuteCmdTestCase(unittest.TestCase):

    def setUp(self):
        self.expr = ucltip.SingleCmd('expr')

    def tearDown(self):
        pass

    def test_call(self):
        self.assertEquals(self.expr('3', '+', '4'), '7\n')
        self.assertRaises(ucltip.CommandExecutedFalur, self.expr, '3', '5', '4')
        self.assertEquals(self.expr('3', '+', '4', via_shell=True), 0)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilsTestCase, 'test'))
    suite.addTest(unittest.makeSuite(ExecuteCmdTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
