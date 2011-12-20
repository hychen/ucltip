#!/usr/bin/env python
# -*- encoding=utf8 -*-
#
# Author 2011 Hsin-Yi Chen
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
        first_cmd = self.expr('3','+','4', as_process=True)
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

    def test_cmdd(self):
        class Zenity(ucltip.CmdDispatcher):
            def __init__(self):
                super(Zenity, self).__init__()
                self.subcmd_prefix = '--'
                self.conf.opt_style = 'gnu'
                self.conf.dry_run = True

                self.error = lambda *args, **kwargs:    self.call('error', *args, **kwargs)

            def info(self, *args, **kwargs):
                kwargs['text']='hi'
                return self.getsubcmd('info')(*args, **kwargs)

            def call(self, name, *args, **kwargs):
                return args, kwargs

        self.assertEquals(['zenity', '--info', '--text=hi'], Zenity().info())
        self.assertEquals(((1,2,3), {'a':1}), Zenity().error(1,2,3, a=1))

class PipeTestCase(unittest.TestCase):

    def setUp(self):
        self.pipe = ucltip.Pipe()

    def tearDown(self):
        del self.pipe

    def test_cmd_obj_param(self):
        self.pipe.add(ucltip.Cmd('expr'), 1, '+', 3)
        self.pipe.add(ucltip.Cmd('sed'), 's/4/8/', posix=True)
        self.pipe.wait()
        self.assertEquals('8\n', self.pipe.stdout.read())

    def test_cmdd_obj_param(self):
        self.pipe.add(ucltip.CmdDispatcher('apt-cache').search, 'vim-common', q=True)
        self.pipe.add(ucltip.Cmd('awk'), '{ print $1 }')
        self.pipe.wait()
        self.assertEquals('vim-common\n', self.pipe.stdout.read())

    def test_cmd_str_param(self):
        self.pipe.add('expr', 1, '+', 3)
        self.pipe.add('sed', 's/4/8/', '--posix')
        self.pipe.wait()
        self.assertEquals('8\n', self.pipe.stdout.read())

    def test_exception(self):
        self.assertRaises(ucltip.PipeError, self.pipe.wait)

class HelperTestCase(unittest.TestCase):

    def setUp(self):
        self._cmds = []

    def tearDown(self):
        import __builtin__
        for varname in self._cmds:
            del __builtin__.__dict__[varname]

    def _regcmds(self, *args, **kwargs):
        for cmd in args:
            if cmd not in self._cmds:
                self._cmds.append(ucltip.undashify(cmd))
        ucltip.regcmds(*args, **kwargs)

    def test_call(self):
        self._regcmds('ls', 'sed')
        self.assertEquals(type(ls), ucltip.Cmd)
        self.assertEquals(type(sed), ucltip.Cmd)
        self._regcmds('apt-get', 'apt-cache', cls=ucltip.CmdDispatcher)
        self.assertEquals(type(apt_get), ucltip.CmdDispatcher)
        self.assertEquals(type(apt_cache), ucltip.CmdDispatcher)
        self.assertRaises(AssertionError, self._regcmds, 'ls', cls=type)

    def test_regcmddispatcher(self):
        self._regcmds('apt-get')
        self.assertEquals(type(apt_get), ucltip.CmdDispatcher)

class GlobalConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.default_config = ucltip.global_config()

    def tearDown(self):
        ucltip.__GLOBAL_CONFIG__ = self.default_config
        self.assertEquals(self.default_config, ucltip.global_config())

    def test_execmode_list(self):
        ucltip.global_config(execmode='list')
        self.assertEquals(['ls','-a','-l'], ucltip.Cmd('ls')(a=True, l=True))

    def test_execmode_string(self):
        ucltip.global_config(execmode='string')
        self.assertEquals('apt-get install vim -t maverick',
                          ucltip.CmdDispatcher('apt-get').install('vim',t='maverick'))

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilsTestCase, 'test'))
    suite.addTest(unittest.makeSuite(ExecuteCmdTestCase, 'test'))
    suite.addTest(unittest.makeSuite(SubCmdTestCase, 'test'))
    suite.addTest(unittest.makeSuite(CmdDispatcherTestCase, 'test'))
    suite.addTest(unittest.makeSuite(CustomClassTestCase, 'test'))
    suite.addTest(unittest.makeSuite(PipeTestCase, 'test'))
    suite.addTest(unittest.makeSuite(HelperTestCase, 'test'))
    suite.addTest(unittest.makeSuite(GlobalConfigTestCase, 'test'))
    return suite

if __name__ == '__main__':
    setup_testenv()
    unittest.main(defaultTest='suite')
