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

    def setUp(self):
        self.optcreator = ucltip.OptionCreator()

    def test_kwargsname_to_optionname(self):
        """test transform keyword arguments's name to command's option name.
        """
        # POSIX and GNU Style
        for style in ('posix', 'gnu', 'POSIX', 'GNU'):
            self.optcreator.set_opt_style(style)
            self.assertEquals(self.optcreator.optname('k'), '-k')
            self.assertEquals(self.optcreator.optname('key'), '--key')
            self.assertEquals(self.optcreator.optname('key_one'), '--key-one')

        # Java Style
        self.optcreator.set_opt_style('java')
        self.assertEquals(self.optcreator.optname('k'), '-k')
        self.assertEquals(self.optcreator.optname('key'), '-key')
        self.assertEquals(self.optcreator.optname('key_one'), '-key-one')

    def test_transform_kwargs_to_booloption(self):
        """test transform keyword to command's boolean style option.
        """
        # POSIX and GNU
        for style in ('posix', 'gnu'):
            self.optcreator.set_opt_style(style)
            self.assertEquals(self.optcreator.transform_kwargs(k=True), ['-k'])
            self.assertEquals(self.optcreator.transform_kwargs(key=True), ['--key'])

        # Java Style
        self.optcreator.set_opt_style('java')
        self.assertEquals(self.optcreator.transform_kwargs(key=True), ['-key'])

    def test_transform_kwargs_to_keyvauleoption(self):
        """test transform keyword to command's key-value style option name.
        """
        self.optcreator.set_opt_style('posix')
        self.assertEquals(self.optcreator.transform_kwargs(k=123), ['-k', '123'])
        self.assertEquals(self.optcreator.transform_kwargs(key=123), ['--key', '123'])

        self.optcreator.set_opt_style('gnu')
        self.assertEquals(self.optcreator.transform_kwargs(k=123), ['-k=123'])
        self.assertEquals(self.optcreator.transform_kwargs(key=123), ['--key=123'])

        self.optcreator.set_opt_style('java')
        self.assertEquals(self.optcreator.transform_kwargs(k=123), ['-k=123'])
        self.assertEquals(self.optcreator.transform_kwargs(key=123), ['-key=123'])

    def test_make_multi_options(self):
        """test make multi option string with the same option name
        """
        self.assertEquals(ucltip.make_optargs('colum', ('first','second'), 'posix'),
                          ['--colum','first', '--colum', 'second'])
        self.assertEquals(ucltip.make_optargs('colum', ('first','second'), 'gnu'),
                          ['--colum=first','--colum=second'])
        self.assertEquals(ucltip.make_optargs('colum', ('first','second'), 'java'),
                          ['-colum=first','-colum=second'])
        # exception check
        self.assertRaises(ucltip.NotValideOptStyle, ucltip.make_optargs, 'colum', ('first','second'), 0)
        self.assertRaises(ucltip.NotValideOptStyle, ucltip.make_optargs, 'colum', ('first','second'), 1)

    def test_cmdexist(self):
        """check commands exists """
        self.assertFalse(ucltip.cmdexists(None))
        self.assertFalse(ucltip.cmdexists(''))
        self.assertFalse(ucltip.cmdexists(1234.5))
        self.assertFalse(ucltip.cmdexists(1234))

    def test_command_not_found(self):
        """raise Exception if commands does not exist"""
        self.assertRaises(ucltip.CommandNotFound, ucltip.Cmd, None)
        self.assertRaises(ucltip.CommandNotFound, ucltip.Cmd, '')
        self.assertRaises(ucltip.CommandNotFound, ucltip.Cmd, 1234.5)
        self.assertRaises(ucltip.CommandNotFound, ucltip.Cmd, '000')

class ExecuteCmdTestCase(unittest.TestCase):

    def setUp(self):
        self.expr = ucltip.Cmd('expr')
        self.sed = ucltip.Cmd('sed')

    def test_call(self):
        self.assertEquals(self.expr('3', '+', '4'), '7\n')
        self.assertRaises(ucltip.CommandExecutedError, self.expr, '3', '5', '4')
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

    def test_dry_run(self):
        """test dry_run """
        self.expr.conf.dry_run = True
        self.assertEquals(['expr', '1', '+', '2'], self.expr(1, '+', 2))

    def test_repr(self):
        self.assertEquals("Cmd object bound 'expr'", "{0}".format(self.expr))
        self.expr.opts(a=True)
        self.assertEquals("Cmd object bound 'expr -a'", "{0}".format(self.expr))

class SubCmdTestCase(unittest.TestCase):

    def setUp(self):
        self.parent = ucltip.CmdDispatcher('ucltip-apt-get')
        self.subcmd = ucltip.SubCmd('mock-cmd')
        self.psubcmd = ucltip.SubCmd('install', self.parent)

    def test_noparent_call(self):
        self.assertRaises(ucltip.RequireParentCmd, self.subcmd)

    def test_hasparent_call(self):
        """test executoing sub command which has parent command"""
        self.assertEquals('ucltip-apt-get install vim\n', self.psubcmd('vim'))
        self.assertEquals('ucltip-apt-get install vim -b\n', self.psubcmd('vim', b=True))
        self.assertEquals('ucltip-apt-get install vim -t maverick\n', self.psubcmd('vim', t='maverick'))
        self.assertEquals('ucltip-apt-get install vim --test maverick\n', self.psubcmd('vim', test='maverick'))
        # check another option style
        self.parent.opt_style = 'gnu'
        self.assertEquals('ucltip-apt-get install vim -t=maverick\n', self.psubcmd('vim', t='maverick'))
        self.assertEquals('ucltip-apt-get install vim --test=maverick\n', self.psubcmd('vim', test='maverick'))

    def test_hasparent_opts(self):
        self.parent.opts(def_opt=True, def_opt2=1)
        self.assertEquals({'def_opt':True, 'def_opt2':1}, self.psubcmd.parent.opts())
        self.assertEquals({'def_opt':True, 'def_opt2':1}, self.psubcmd.opts())

class CmdDispatcherTestCase(unittest.TestCase):

    def setUp(self):
        self.cmdd = ucltip.CmdDispatcher('ucltip-apt-get')

    def test_callsubcmd(self):
        """test call subcmd by cmd dispatcher"""
        self.assertEquals('ucltip-apt-get install vim\n', self.cmdd.install('vim'))
        self.assertEquals('ucltip-apt-get install vim -t maverick\n', self.cmdd.install('vim', t='maverick'))
        self.assertEquals('ucltip-apt-get install vim --test maverick\n', self.cmdd.install('vim', test='maverick'))
        # check another option style
        self.cmdd.opt_style = 'gnu'
        self.assertEquals('ucltip-apt-get install vim -t=maverick\n', self.cmdd.install('vim', t='maverick'))
        self.assertEquals('ucltip-apt-get install vim --test=maverick\n', self.cmdd.install('vim', test='maverick'))
        # check another sub command prefix
        self.cmdd.subcmd_prefix = '--'
        self.assertEquals('ucltip-apt-get --install vim -t=maverick\n', self.cmdd.install('vim', t='maverick'))

    def test_opts(self):
        """test setting default options of cmd dispatcher"""
        self.cmdd.opts(def_opt=1)
        self.assertEquals('ucltip-apt-get install vim --def-opt 1 -t maverick\n', self.cmdd.install('vim', t='maverick'))
        self.cmdd.opts(def_opt=False)
        self.assertEquals('ucltip-apt-get install vim -t maverick\n', self.cmdd.install('vim', t='maverick'))

    def test_subcmd_prefix(self):
        """test setting subcmd_prefix of cmd dispatcher"""
        self.cmdd.subcmd_prefix = '--'
        self.assertEquals('ucltip-apt-get --install\n', self.cmdd.install())

    def test_opt_style(self):
        """test setting option style of cmd dispatcher"""
        self.cmdd.conf.opt_style = 'gnu'
        self.assertEquals('ucltip-apt-get install --test=1\n', self.cmdd.install(test=1))
        self.cmdd.conf.opt_style = 'java'
        self.assertEquals('ucltip-apt-get install -test=1\n', self.cmdd.install(test=1))

class CustomClassTestCase(unittest.TestCase):

    def test_cmd(self):
        class LS(ucltip.Cmd):
            pass
        self.assertEquals(LS().name, 'ls')

class HelperTestCase(unittest.TestCase):

    def test_call(self):
        ucltip.regcmds('ls', 'sed')
        self.assertEquals(type(ls), ucltip.Cmd)
        self.assertEquals(type(sed), ucltip.Cmd)
        ucltip.regcmds('apt-get', 'apt-cache', cls=ucltip.CmdDispatcher)
        self.assertEquals(type(apt_get), ucltip.CmdDispatcher)
        self.assertEquals(type(apt_cache), ucltip.CmdDispatcher)
        self.assertRaises(AssertionError, ucltip.regcmds, 'ls', cls=type)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilsTestCase, 'test'))
    suite.addTest(unittest.makeSuite(ExecuteCmdTestCase, 'test'))
    suite.addTest(unittest.makeSuite(SubCmdTestCase, 'test'))
    suite.addTest(unittest.makeSuite(CmdDispatcherTestCase, 'test'))
    suite.addTest(unittest.makeSuite(CustomClassTestCase, 'test'))
    suite.addTest(unittest.makeSuite(HelperTestCase, 'test'))
    return suite

if __name__ == '__main__':
    setup_testenv()
    unittest.main(defaultTest='suite')
