#!/usr/bin/env python
# -*- encoding=utf8 -*-
#
# Author 2011 Hsin-Yi Chen
"""Command-line tool adapter library

This module is a command-line adapter library that:

    - transform arguments and options of command-line tool to
      Python arguments and keyword arguments.
    - provide a way to execute command-line tools in Python by OO way.

Here is a example that execute `ls -al` in current directory

    ls = ucltip.Cmd('ls')
    ls(l=True)

and the following is a simple usage example that launching a Zenity info dialog in Python

    zenity = ucltip.CmdDispatcher('zenity')
    zenity.subcmd_prefix = '--'
    zenity.conf.opt_style = 'gnu'
    zenity.info(text="The first example", width=500)

The module contains the following public classes:

    - Cmd -- Object for mapping a command has no sub commands
    - CmdDispatcher -- Object for mapping a command has sub commands
"""

__all__ = ['regcmds',
           'make_optargs',
           'cmdexists',
           'Cmd',
           'SubCmd',
           'CmdDispatcher',
           'CommandNotFound',
           'CommandExecutedError',
           'RequireParentCmd',
           'Pipe']

# global variabl, please use global_config function to access it
# execmode:
#       process - run as process
#       list    - produce command arguments list
#       string  - produce command string
#
__GLOBAL_CONFIGS__ = {'execmode':'process',
                      'dry_run':False,
                      'debug':False}

import subprocess
import syslog
import sys
import os

extra = {}
if sys.platform == 'win32':
    extra = {'shell': True}

# =====================
# Logging functions
# =====================
def ERR(cmdstr, errmsg='None'):
    syslog.syslog(syslog.LOG_ERR,
           'UCLTIP: Executed "{}" failed, Err Msg:{}'.format(cmdstr, errmsg))

def DBG(msg):
    if global_config().get('debug'):
        syslog.syslog(syslog.LOG_DEBUG, 'UCLTIP: {} '.format(msg))

# =============================
# Utility functions and classes
# =============================
def regcmds(*args, **kwargs):
    """register bound object in current environment

    @param cls Cmd or CmdDispatcher
    """
    import __builtin__
    cls = kwargs.get('cls') or Cmd
    assert cls in (Cmd, CmdDispatcher)
    for cmdname in args:
        __builtin__.__dict__[undashify(cmdname)] = cls(cmdname)

def double_dashify(string):
    """add double dashify prefix in a string
    """
    return '--' + string

def dashify(string):
    """covert _ to - of string
    """
    return string.replace('_', '-')

def undashify(string):
    """covert - to _ of string
    """
    return string.replace('-', '_')

def cmdexists(cmdname):
    """check if command exists

    @param str cmdname command name
    @return bool True if command exists otherwise False
    """
    assert 'PATH' in os.environ
    executable = lambda filename: os.path.isfile(filename) and os.access(filename, os.X_OK)
    filenames = [ os.path.join(element, str(cmdname)) \
                  for element in os.environ['PATH'].split(os.pathsep) if element ]
    for f in filenames:
        if executable(f):
            return True

def global_config(query=None, **kwargs):
    """set or get global configure

    @param execmode: config executing mode

                     avliabl value:
                        process - run as process
                        list    - produce command arguments list
                        string  - produce command string
    @param dry_run: same as execmode=list
    @param debug:   enable debug mode

    @return dict __GLOBAL_CONFIGS__
    @example:

        # get value
        >>> global_config('dry_run')
        # set value
        >>> global_config(dry_run=True)
    """
    if kwargs:
        __GLOBAL_CONFIGS__.update(kwargs)
    elif query:
        return __GLOBAL_CONFIGS__.get(query)
    else:
        return __GLOBAL_CONFIGS__

# =====================
# Options and Arguments
# =====================
class OptionCreator(object):
    """Object for creating command options string from Python
       keyword arguments

    Support options style:

    - POSIX like options (ie. tar -zxvf foo.tar.gz)
    - GNU like long options (ie. du --human-readable --max-depth=1)
    - Java like properties (ie. java -Djava.awt.headless=true -Djava.net.useSystemProxies=true Foo)

        p.s Java like is not fully supported.

    Unsupport options style:

    - Short options with value attached (ie. gcc -O2 foo.c)
    - long options with single hyphen (ie. ant -projecthelp)

    """

    """Support Option Styles, posix is default"""
    VALIDE_OPTSTYLES = ('posix', 'gnu', 'java')

    def __init__(self, opt_style='posix'):
        self._result = []
        self.set_opt_style(opt_style)

    def set_opt_style(self, opt_style):
        self.opt_style = str(opt_style).lower()
        if not self.opt_style in self.VALIDE_OPTSTYLES:
            raise NotValideOptStyle(opt_style)

    def make_optargs(self, optname, values):
        """create command line options, same key but different values

        @param str optname
        @param list values
        @return list combined option args
        """
        self._result = []
        for v in values:
            self.__append_opt(optname, v)
        return self._result

    def transform_kwargs(self, **kwargs):
        """
        Transforms Python style kwargs into command line options.

        @return list args for subprocess.call
        """
        self._result = []
        for k, v in kwargs.items():
            self.__append_opt(k, v)
        DBG('Trasform Kwargs:input:{}, result:{}'.format(kwargs,
                                                         self._result))
        return self._result

    def __append_opt(self, k, v):
        """append option value transformed from kwargs to inputed args list

        @param str k option name
        @param str v option value
        """
        if type(v) is not bool:
            v=str(v)
            if self.opt_style in ('gnu', 'java'):
                self._result.append('{0}={1}'.format(self.optname(k),v))
            else:
                self._result.append(self.optname(k))
                self._result.append(v)
        elif v == True:
            self._result.append(self.optname(k))

    def optname(self, k):
        """get option name"""
        return (len(k) == 1 or self.opt_style == 'java') and \
               '-{0}'.format(dashify(k)) or \
               '--{0}'.format(dashify(k))

def make_optargs(optname, values, opt_style='posix'):
    """create command line options, same key but different values

    @param str optname
    @param list values
    @param int option style
    @return list combined option args
    """
    return OptionCreator(opt_style).make_optargs(optname, values)

    syslog.syslog(syslog.LOG_ERR,
                  'Executed "{}" failed, Err Msg:{}'.format(cmdstr, errmsg))

# =====================
# Exceptions Clasees
# =====================
class CommandNotFound(Exception):
    pass

class CommandExecutedError(Exception):

    def __init__(self, status, errmsg=None):
        self.status = status
        self.errmsg = errmsg

    def __str__(self):
        return self.errmsg

class RequireParentCmd(Exception):
    pass

class NotValideOptStyle(Exception):
    def __init__(self, opt_style):
        self.opt_style = opt_style

    def __str__(self):
        return self.opt_style

# =======================
# Command Adpater Classes
# =======================
class CmdConfiguration(object):
    """Object for sharing common configurations
    """
    def __init__(self):
        self.dry_run = global_config('dry_run')
        self.default_opts = {}
        self.opt_style = 'posix'

class BaseCmd(object):

    def __init__(self, name=None):
        self.name = name or self.__class__.__name__.lower()
        self.conf = CmdConfiguration()
        DBG("Created a {}".format(repr(self)))

    @property
    def opt_style(self):
        return self.conf.opt_style
    @opt_style.setter
    def opt_style(self, value):
        self.conf.opt_style = value

    def opts(self, **kwargs):
        """set default options of command

        @param dict kwargs options dict
        @return dict default options if no kwargs input
        @example

            obj.opts(t=3)
            # the result is {'t':3}
            obj.opts()
        """
        return kwargs and self.conf.default_opts.update(kwargs) or self.conf.default_opts

    def reset(self):
        """reset default options"""
        self.conf.default_opts = {}

class ExecutableCmd(BaseCmd):

    execute_kwargs = ('stdin','as_process', 'via_shell', 'with_extend_output')

    def __call__(self, *args, **kwargs):
        return self._callProcess(*args, **kwargs)

    def _callProcess(self, *args, **in_kwargs):
        # Handle optional arguments prior to calling transform_kwargs
        # otherwise these'll end up in args, which is bad.
        kwargs = {}
        kwargs.update(self.opts())
        kwargs.update(in_kwargs)
        _kwargs = {}
        for kwarg in self.execute_kwargs:
            try:
                _kwargs[kwarg] = kwargs.pop(kwarg)
            except KeyError:
                pass

        # Prepare the argument list
        call = self.make_callargs(*args, **kwargs)
        DBG('Builded command string:{}'.format(call))

        # Execute
        mode = global_config('execmode')
        if self.conf.dry_run or mode == 'list':
            return call
        if mode == 'string':
            return ' '.join(call)
        return self.execute(call, **_kwargs)

    def execute(self, command, stdin=None, as_process=False, via_shell=False, with_extend_output=False):
        """execute command

        @param subprocess.PIPE stdin
        @param bool as_process retrun Popen instance if as_process is True for
               more control
        @param bool via_shell use os.system instead of subprocess.call
        @return str execited result (as_process musc be False)

        @example
            # the same as echo `ls -al|grep Dox`
            ls = ucltip.Cmd('ls')
            grep = ucltip.Cmd('grep')
            print grep('Dox', stdin=ls(a=True, l=True, as_process=True).stdout)
        """
        assert not (as_process and via_shell),\
            "You can not get a Popen instance when you want to execute command in shell."
        assert not (stdin and via_shell),\
            "You can not use stdin and via_shell in the same time."
        if via_shell:
            status = os.system(' '.join(command))
            if status != 0:
                ERR(' '.join(command))
                raise CommandExecutedError(status)
            return status
        else:
            # Start the process
            proc = subprocess.Popen(command,
                                    stdin=stdin,
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    **extra
                                    )
            if as_process:
                return proc

            # Wait for the process to return
            try:
                stdout_value = proc.stdout.read()
                stderr_value = proc.stderr.read()
                status = proc.wait()
            finally:
                proc.stdout.close()
                proc.stderr.close()

            if not with_extend_output:
                if status != 0:
                    ERR(' '.join(command), stderr_value)
                    raise CommandExecutedError(status, stderr_value)
                return stdout_value
            else:
                return (status, stdout_value)

    def make_callargs(self, *args, **kwargs):
        # Prepare the argument list
        opt_args = OptionCreator(self.conf.opt_style).transform_kwargs(**kwargs)
        ext_args = map(str, args)
        args = ext_args + opt_args
        return [self.name] + args

    def __repr__(self):
        opt = self.opts() and ' ' + " ".join(OptionCreator(self.conf.opt_style).transform_kwargs(**self.opts())) or ''
        return "{0} object bound '{1}{2}'".format(self.__class__.__name__, self.name, opt)

class Cmd(ExecutableCmd):
    """Object for mapping a command has no sub commands

    Keyword Arguments:
        - name -- A string indicating the command name will be executed
        - opt_style -- A string to indicate what options style be used , avaliable values
                      are `posix`, `gnu`, `java`, the default is posix
    """

    def __init__(self, name=None):
        super(Cmd, self).__init__(name)
        if not cmdexists(self.name):
            raise CommandNotFound

class SubCmd(ExecutableCmd):
    """Object for mapping a sub command, this object can not be executed without
       a CmdDispatcher parent object.

    Keyword Arguments:
        - name -- A string indicating the sub command name will be executed
        - parent -- A CmdDispatcher provides main command name, default opt_style,
           options, and subcmd_prefix.
        - opt_style -- delegate to Parent Command opt_style (read only)
    """

    def __init__(self, name, parent=None):
        super(SubCmd, self).__init__(name)
        self.parent = parent

        # data delegations
        if parent:
            self.set_parent(parent)

    def set_parent(self, parent):
        """set parent and the common configuration will be override by the parent

        @param CmdDispatcher
        """
        self.conf = self.parent.conf

    def make_callargs(self, *args, **kwargs):
        if not self.parent:
            raise RequireParentCmd
        if self.parent.subcmd_prefix and not self.parent.subcmd_prefix in self.name:
            self.name = self.parent.subcmd_prefix + self.name
        args = super(SubCmd, self).make_callargs(*args, **kwargs)
        args.insert(0, self.parent.name)
        return args

class CmdDispatcher(BaseCmd):
    """Object for mapping a command has sub commands

    Keyword Arguments:
        - name -- A string indicating the sub command name will be executed
        - subcmd_prefix -- A string indicating prefix string of a sub command if required
        - opt_style - A string to indicate what options style be used , avaliable values are
          `posix`, `gnu`, `java`, the default is posix
    """
    def __init__(self, name=None):
        self.subcmd_prefix = None
        self._subcmds = {}
        super(CmdDispatcher, self).__init__(name)
        if not cmdexists(self.name):
            raise CommandNotFound

    def __getattr__(self, name):
        if name[:1] == '_':
            raise AttributeError(name)
        return self.getsubcmd(name)

    def getsubcmd(self, name):
        return self._subcmds.setdefault(name, SubCmd(name, self))

    def __repr__(self):
        return "{0} object bound '{1}'".format(self.__class__.__name__, self.name)

# ============
# Pipe Classes
# ============
class PipeError(Exception):
    pass

class Pipe(object):
    """Object for handling command pipeline
    """

    def __init__(self):
        # last process
        self._last_proc = None

    def add(self, cmd, *args, **opts):
        """add command arguments in this pipe

        @param cmd command name
        @param args command arguments
        @param opts command options
        """
        if type(cmd) is str and not opts:
            cmd = Cmd(cmd)

        opts['as_process'] = True
        if self._last_proc:
            opts['stdin'] = self._last_proc.stdout
        self._last_proc =  cmd(*args, **opts)

    def wait(self):
        """Wait for the process to terminate.  Returns returncode attribute.
        """
        if not self._last_proc:
            raise PipeError("theres is no any process inside")
        status = self._last_proc.wait()
        if status != 0:
            raise PipeError()
        return status

    def __getattr__(self, k):
        if self._last_proc and k in ('status', 'stdout', 'stderr'):
            try:
                return getattr(self._last_proc, k)
            except AttributeError:
                return None
