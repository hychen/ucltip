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
"""Command-line tool adapter library

This module is a command-line adapter library that:

    - transform arguments and options of command-line tool to
      Python arguments and keyword arguments.
    - provide a way to execute command-line tools in Python by OO way.

Here is a example that execute `ls -al` in current directory

    ls = ucltip.Cmd('ls')
    ls(al=True)

and the following is a simple usage example that launching a Zenity info dialog in Python

    zenity = ucltip.CmdDispatcher('zenity')
    zenity.subcmd_prefix = '--'
    zenity.opt_style = 1
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
           'CommandExecutedFalur',
           'RequireParentCmd']

import subprocess
import sys
import os

extra = {}
if sys.platform == 'win32':
    extra = {'shell': True}

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

# =====================
# Options and Arguments
# =====================
def transform_kwargs(opt_style, **kwargs):
    """
    Transforms Python style kwargs into command line options.

    @param int opt_style
    @return list args
    """
    args = []
    for k, v in kwargs.items():
        __append_opt(args, k, v, opt_style)
    return args

def __append_opt(args, k, v, opt_style):
    """append option value transformed from kwargs to inputed args list

    @param str k option name
    @param str v option value
    @param int option style
    """
    if type(v) is not bool:
        v=str(v)
        if opt_style:
            args.append('{0}={1}'.format(optname(k),v))
        else:
            args.append(optname(k))
            args.append(v)
    elif v == True:
        args.append(optname(k))

def optname(k):
    """get option name"""
    return len(k) == 1 and '-{0}'.format(k) or '--{0}'.format(dashify(k))

def make_optargs(optname, values, opt_style=0):
    """create command line options, same key but different values

    @param str optname
    @param list values
    @param int option style
    @return list combined option args
    """
    ret = []
    for v in values:
        __append_opt(ret, optname, v, opt_style)
    return ret

# =====================
# Exceptions Clasees
# =====================
class CommandNotFound(Exception):
    pass

class CommandExecutedFalur(Exception):

    def __init__(self, status, errmsg=None):
        self.status = status
        self.errmsg = errmsg

    def __str__(self):
        return self.errmsg

class RequireParentCmd(Exception):
    pass

# =======================
# Command Adpater Classes
# =======================
class CmdConfiguration(object):
    """Object for sharing common configurations
    """
    def __init__(self):
        self.dry_run = False
        self.debug = False
        self.default_opts = {}
        self.opt_style = 0

class BaseCmd(object):

    def __init__(self, name=None):
        self.name = name or self.__class__.__name__.lower()
        self.conf = CmdConfiguration()

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

    execute_kwargs = ('stdin','interact', 'via_shell', 'with_extend_output')

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
        return self.conf.dry_run and call or self.execute(call, **_kwargs)

    def execute(self, command, stdin=None, interact=False, via_shell=False, with_extend_output=False):
        """execute command

        @param subprocess.PIPE stdin
        @param bool interact retrun Popen instance if interact is True for
               more control
        @param bool via_shell use os.system instead of subprocess.call
        @return str execited result (interact musc be False)

        @example
            # the same as echo `ls -al|grep Dox`
            ls = ucltip.Cmd('ls')
            grep = ucltip.Cmd('grep')
            print grep('Dox', stdin=ls(a=True, l=True, interact=True).stdout)
        """
        assert not (interact and via_shell),\
            "You can not get a Popen instance when you want to execute command in shell."
        assert not (stdin and via_shell),\
            "You can not use stdin and via_shell in the same time."
        if via_shell:
            status = os.system(' '.join(command))
            if status != 0:
                raise CommandExecutedFalur(status)
            return status
        else:
            # Start the process
            proc = subprocess.Popen(command,
                                    stdin=stdin,
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    **extra
                                    )
            if interact:
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
                    raise CommandExecutedFalur(status, stderr_value)
                return stdout_value
            else:
                return (status, stdout_value)

    def make_callargs(self, *args, **kwargs):
        # Prepare the argument list
        opt_args = transform_kwargs(self.conf.opt_style, **kwargs)
        ext_args = map(str, args)
        args = ext_args + opt_args
        return [self.name] + args

    def __repr__(self):
        opt = self.opts() and ' ' + " ".join(transform_kwargs(self.conf.opt_style, **self.opts())) or ''
        return "{0} object bound '{1}{2}'".format(self.__class__.__name__, self.name, opt)

class Cmd(ExecutableCmd):
    """Object for mapping a command has no sub commands

    Keyword Arguments:
        - name -- A string indicating the command name will be executed
        - opt_style - A interger number indicating the option style, if
           the vaule is 1, then the option string will be --$opt=$value,
           otherwise the option string is --$opt $value
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
        - opt_style - A interger number indicating the option style, if
           the vaule is 1, then the option string will be --$opt=$value,
           otherwise the option string is --$opt $value
    """
    def __init__(self, name=None):
        self.subcmd_prefix = None
        self._subcmds = {}
        BaseCmd.__init__(self, name)
        if not cmdexists(name):
            raise CommandNotFound

    def __getattr__(self, name):
        if name[:1] == '_':
            raise AttributeError(name)
        return self._subcmds.setdefault(name, SubCmd(name, self))
