# the ideas and a lot of codes from GitPython project
# @author Hsin-Yi Chen (hychen)
import subprocess
import sys
import os

extra = {}
if sys.platform == 'win32':
    extra = {'shell': True}

class CommandNotFound(Exception):   pass

class CommandExecutedFalur(Exception):
    #{{{def __init__(self, status, errmsg=None):
    def __init__(self, status, errmsg=None):
        self.status = status
        self.errmsg = errmsg
    #}}}

    #{{{def __str__(self):
    def __str__(self):
        return self.errmsg
    #}}}
pass

#{{{def double_dashify(string):
def double_dashify(string):
    return '--' + string
#}}}

#{{{def dashify(string):
def dashify(string):
    return string.replace('_', '-')
#}}}

#{{{def make_optargs(optname, values, opt_style=0):
def make_optargs(optname, values, opt_style=0):
    """create command line options, same key but different values

    @param str optname
    @param list values
    @param int option style
    @return list combined option args
    """
    ret = []
    for v in values:
        ret = _append_opt(ret, optname, v, opt_style)
    return ret
#}}}

#{{{def transform_kwargs(opt_style, **kwargs):
def transform_kwargs(opt_style, **kwargs):
    """
    Transforms Python style kwargs into command line options.

    @param int opt_style
    """
    args = []
    for k, v in kwargs.items():
        args = _append_opt(args, k, v, opt_style)
    return args
#}}}

#{{{def _append_opt(k, v, opt_style):
def _append_opt(args, k, v, opt_style):
    """append option value transformed from kwargs to inputed args list

    @param str k option name
    @param str v option value
    @param int option style
    @return list combined args list
    """
    if len(k) == 1:
        if v is True:
            args.append("-%s" % k)
        elif type(v) is not bool:
            args.append("-%s" % k)
            args.append("%s" % v)
    else:
        if v is True:
            args.append("--%s" % dashify(k))
        elif type(v) is not bool:
            if opt_style == 1:
                args.append("--%s=%s" % (dashify(k), v))
            else:
                args.append("--%s" % dashify(k))
                args.append("%s" % v)
    return args
#}}}

#{{{def cmdexists(cmdname):
def cmdexists(cmdname):
    """check if command exists

    @param str cmdname command name
    @return bool True if command exists otherwise False
    """
    """Is command on the executable search path?"""
    if 'PATH' not in os.environ:
        return False
    path = os.environ['PATH']
    for element in path.split(os.pathsep):
        if not element:
            continue
        filename = os.path.join(element, str(cmdname))
        if os.path.isfile(filename) and os.access(filename, os.X_OK):
            return True
    return False
#}}}

class SingleCmd(object):

    opt_style = 0
    execute_kwargs = ('stdin','interact', 'via_shell', 'with_extend_output')

    #{{{def __init__(self, cmdname=None, opt_style=None):
    def __init__(self, cmdname=None, opt_style=None):
        ## used for debug what command string be executed
        self.__DEBUG__ = False
        self.dry_run = False
        self.default_opts = {}
        self.cmdname = cmdname or self.__class__.__name__.lower()
        if not self.cmdname or not cmdexists(self.cmdname):
            raise CommandNotFound()
        if opt_style:
            self.opt_style = opt_style
    #}}}

    #{{{def __call__(self, *args, **kwargs):
    def __call__(self, *args, **kwargs):
        return self._callProcess(*args, **kwargs)
    #}}}

    #{{{def _callProcess(self, *args, **kwargs):
    def _callProcess(self, *args, **kwargs):
        # Handle optional arguments prior to calling transform_kwargs
        # otherwise these'll end up in args, which is bad.
        self.default_opts.update(kwargs)
        kwargs = self.default_opts
        _kwargs = {}
        for kwarg in self.execute_kwargs:
            try:
                _kwargs[kwarg] = kwargs.pop(kwarg)
            except KeyError:
                pass
        # Prepare the argument list
        call = self.make_callargs(*args, **kwargs)
        if self.__DEBUG__ or self.dry_run:
            print "DBG: execute cmd '%s'" % ' '.join(call)
        return call if self.dry_run else self.execute(call, **_kwargs)
    #}}}

    #{{{def execute(self, command, stdin=None, interact=False, via_shell=False, with_extend_output=False):
    def execute(self, command, stdin=None, interact=False, via_shell=False, with_extend_output=False):
        """execute command

        @param subprocess.PIPE stdin
        @param bool interact retrun Popen instance if interact is True for
               more control
        @param bool via_shell use os.system instead of subprocess.call
        @return str execited result (interact musc be False)

        @example
            # the same as echo `ls -al|grep Dox`
            ls = ucltip.SingleCmd('ls')
            grep = ucltip.SingleCmd('grep')
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
    #}}}

    #{{{def make_callargs(*args, **kwargs):
    def make_callargs(self, *args, **kwargs):
        # Prepare the argument list
        opt_args = transform_kwargs(self.opt_style, **kwargs)
        ext_args = map(str, args)
        args = ext_args + opt_args
        return [self.cmdname] + args
    #}}}

    #{{{def opts(self, **kwargs):
    def opts(self, **kwargs):
        """set default options of command

        @param dict kwargs options dict
        @return dict default options if no kwargs input
        @example

            obj.opts(t=3)
            # the result is {'t':3}
            obj.opts()
        """
        if kwargs:
            self.default_opts.update(kwargs)
        else:
            return self.default_opts
    #}}}

    #{{{def reset(self):
    def reset(self):
        """reset default options"""
        self.default_opts = {}
    #}}}

    #{{{def __repr__(self):
    def __repr__(self):
        return "%s object bound '%s'" % (self.__class__.__name__, self.cmdname)
    #}}}
pass

class CmdDispatcher(SingleCmd):

    subcmd_prefix = None

    #{{{def __init__(self, cmdname=None, opt_style=0, subcmd_prefix=None):
    def __init__(self, cmdname=None, opt_style=0, subcmd_prefix=None):
        """Constructor

        @param str cmdname command name
        @param str opt_style option style
        @param str subcmd_prefix prefix of sub command
        """
        if subcmd_prefix:
            self.subcmd_prefix = subcmd_prefix
        SingleCmd.__init__(self, cmdname, opt_style)
    #}}}

    #{{{def __getattr__(self, name):
    def __getattr__(self, name):
        if name[:1] == '_':
            raise AttributeError(name)
        self.subcmd = dashify(name)
        return lambda *args, **kwargs: self._callProcess(*args, **kwargs)
    #}}}

    #{{{def _callProcess(self, *args, **kwargs):
    def _callProcess(self, *args, **kwargs):
        if self.subcmd_prefix:
            self.subcmd = self.subcmd_prefix + self.subcmd
        args = list(args)
        args.insert(0, self.subcmd)
        return super(CmdDispatcher, self)._callProcess(*args, **kwargs)
    #}}}
pass

#{{{def use_helper():
def use_helper():
    """allow to use a shortcut functions for creating Cmd
    """
    import __builtin__
    __builtin__.__dict__['_c'] = SingleCmd
    __builtin__.__dict__['_d'] = CmdDispatcher
#}}}

#{{{def reg_singlecmds():
def reg_singlecmds(*args):
    """register bound object in current env
    """
    import __builtin__
    for cmdname in args:
        __builtin__.__dict__[cmdname] = SingleCmd(cmdname)
#}}}
