#!/usr/bin/env python
# -*- encoding=utf8 -*-
#
# Author 2011 Hsin-Yi Chen
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
import os
import unittest
import ucltip

# setup test env
def setup_testenv():
    testbinpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'bin')
    os.environ['PATH'] = "{0}:{1}".format(os.getenv('PATH'), testbinpath)

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
        """raise Exception if commands does not exist"""
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, None)
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, '')
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, 1234.5)
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, '000')

class ExecuteCmdTestCase(unittest.TestCase):

    def setUp(self):
        self.expr = ucltip.SingleCmd('expr')
        self.sed = ucltip.SingleCmd('sed')

    def tearDown(self):
        del self.expr
        del self.sed

    def test_call(self):
        self.assertEquals(self.expr('3', '+', '4'), '7\n')
        self.assertRaises(ucltip.CommandExecutedFalur, self.expr, '3', '5', '4')
        self.assertEquals(self.expr('3', '+', '4', via_shell=True), 0)

    def test_pipe(self):
        """test command pipe line"""
        first_cmd = self.expr('3','+','4', interact=True)
        second_cmd = self.sed
        self.assertEquals('A\n', second_cmd('s/7/A/', stdin=first_cmd.stdout))

    def test_opt(self):
        """test default options setting"""
        self.assertRaises(TypeError, self.expr.opts, 1)
        self.expr.opts(opt1=1,opt2=2)
        self.assertEquals({'opt1': 1, 'opt2': 2}, self.expr.opts())
        self.expr.reset()
        self.assertEquals({}, self.expr.opts())

class SubCmdTestCase(unittest.TestCase):

    def setUp(self):
        self.parent = ucltip.CmdDispatcher('ucltip-apt-get')

    def test_noparent_call(self):
        subcmd = ucltip.SubCmd('mock-cmd')
        self.assertRaises(ucltip.RequireParentCmd, subcmd)

    def test_hasparent_call(self):
        """test executoing sub command which has parent command"""
        subcmd = ucltip.SubCmd('install', self.parent)
        self.assertEquals('ucltip-apt-get install vim\n', subcmd('vim'))
        self.assertEquals('ucltip-apt-get install vim -b\n', subcmd('vim', b=True))
        self.assertEquals('ucltip-apt-get install vim -t maverick\n', subcmd('vim', t='maverick'))
        self.assertEquals('ucltip-apt-get install vim --test maverick\n', subcmd('vim', test='maverick'))
        # check another option style
        subcmd.opt_style = 1
        self.assertEquals('ucltip-apt-get install vim -t=maverick\n', subcmd('vim', t='maverick'))
        self.assertEquals('ucltip-apt-get install vim --test=maverick\n', subcmd('vim', test='maverick'))

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilsTestCase, 'test'))
    suite.addTest(unittest.makeSuite(ExecuteCmdTestCase, 'test'))
    suite.addTest(unittest.makeSuite(SubCmdTestCase, 'test'))
    return suite

if __name__ == '__main__':
    setup_testenv()
    unittest.main(defaultTest='suite')
