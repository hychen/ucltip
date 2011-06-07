# the ideas and a lot of codes from GitPython project
# @author Hsin-Yi Chen (hychen)
import subprocess
import sys
import os

__all__ = ['reg_singlecmds',
           'cmdexists',
           'SingleCmd',
           'SubCmd',
           'CmdDispatcher',
           'CommandNotFound',
           'CommandExecutedFalur']

extra = {}
if sys.platform == 'win32':
    extra = {'shell': True}

def reg_singlecmds(*args):
    """register bound object in current env
    """
    import __builtin__
    for name in args:
        __builtin__.__dict__[name] = SingleCmd(name)

def double_dashify(string):
    """add double dashify prefix in a string
    """
    return '--' + string

def dashify(string):
    """covert _ to - of string
    """
    return string.replace('_', '-')

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

def cmdexists(name):
    """check if command exists

    @param str name command name
    @return bool True if command exists otherwise False
    """
    assert 'PATH' in os.environ
    executable = lambda filename: os.path.isfile(filename) and os.access(filename, os.X_OK)
    filenames = [ os.path.join(element, str(name)) \
                  for element in os.environ['PATH'].split(os.pathsep) if element ]
    return len(filter(executable, filenames)) >= 1

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

class BaseCmd(object):

    #FIXME: removed me
    __DEBUG__ = False
    dry_run = False

    def __init__(self, name=None):
        self.name = name or self.__class__.__name__.lower()
        if not self.name or not cmdexists(self.name):
            raise CommandNotFound()

        # init attributes
        self.default_opts = {}
        self.opt_style = 0

    def opts(self, **kwargs):
        """set default options of command

        @param dict kwargs options dict
        @return dict default options if no kwargs input
        @example

            obj.opts(t=3)
            # the result is {'t':3}
            obj.opts()
        """
        return kwargs and self.default_opts.update(kwargs) or self.default_opts

    def reset(self):
        """reset default options"""
        self.default_opts = {}

class SingleCmd(BaseCmd):

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
        if self.__DEBUG__ or self.dry_run:
            print "DBG: execute cmd '{0}'".format(' '.join(call))
        return call if self.dry_run else self.execute(call, **_kwargs)

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
        opt_args = transform_kwargs(self.opt_style, **kwargs)
        ext_args = map(str, args)
        args = ext_args + opt_args
        return [self.name] + args

    def __repr__(self):
        opt = "'{0}' ".join(transform_kwargs(self.opt_style, **self.default_opts))
        return "{0} object bound '{1}' {2}".format(self.__class__.__name__, self.name, opt)

class SubCmd(SingleCmd):

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.default_opts = parent and parent.default_opts or {}
        self.opt_style = parent and parent.opt_style or 0

    def make_callargs(self, *args, **kwargs):
        if not self.parent:
            raise RequireParentCmd
        if self.parent.subcmd_prefix:
            self.name = subcmd_prefix + self.name
        args = super(SubCmd, self).make_callargs(*args, **kwargs)
        args.insert(0, self.parent.name)
        return args

class CmdDispatcher(BaseCmd):

    subcmd_prefix = None

    def __init__(self, name=None, opt_style=0, subcmd_prefix=None):
        """Constructor

        @param str name command name
        @param str opt_style option style
        @param str subcmd_prefix prefix of sub command
        """
        self._subcmds = {}
        if subcmd_prefix:
            self.subcmd_prefix = subcmd_prefix
        BaseCmd.__init__(self, name)

    def __getattr__(self, name):
        if name[:1] == '_':
            raise AttributeError(name)
        return self._subcmds.setdefault(name, SubCmd(name, self))
