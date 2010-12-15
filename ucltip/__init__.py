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
    #{{{def __init__(self, status, errmsg):
    def __init__(self, status, errmsg):
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

#{{{def make_callargs(*args, **kwargs):
def make_callargs(cmdname, *args, **kwargs):
    # Prepare the argument list
    opt_args = transform_kwargs(**kwargs)
    ext_args = map(str, args)
    args = opt_args + ext_args
    return [cmdname] + args
#}}}

#{{{def transform_kwargs(**kwargs):
def transform_kwargs(**kwargs):
    """
    Transforms Python style kwargs into command line options.

    @param int opt_style 
    """
    try:
        opt_style = kwargs.pop('opt_style')
    except KeyError:
        opt_style = 0

    args = []
    for k, v in kwargs.items():
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
    cmdname = str(cmdname)
    try:
        p = subprocess.Popen(['whereis', cmdname], stdout=subprocess.PIPE)
        return True if p.communicate()[0].strip()[len(cmdname)+1:] else False
    except IndexError:
        return False
#}}}

class SingleCmd(object):

    ## used for debug what command string be executed
    __DEBUG__ = False

    execute_kwargs = ('stdin','interact', 'via_shell')

    #{{{def __init__(self, cmdname, opt_style=0):
    def __init__(self, cmdname, opt_style=0):
        self.cmdname = cmdname
        if not cmdname or not cmdexists(cmdname):
            raise CommandNotFound()
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
        _kwargs = {}
        for kwarg in self.execute_kwargs:
            try:
                _kwargs[kwarg] = kwargs.pop(kwarg)
            except KeyError:
                pass
        # Prepare the argument list
        call = make_callargs(self.cmdname, *args, **kwargs)
        if self.__DEBUG__: 
            print "DBG: execute cmd '%s'" % ' '.join(call)
        return self.execute(call, **_kwargs)
    #}}}

    #{{{def execute(self, command, stdin=None, interact=False, via_shell=False):
    def execute(self, command, stdin=None, interact=False, via_shell=False):
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
        # Start the process
        proc = subprocess.Popen(command,
                                stdin=stdin,
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                **extra
                                )

        if via_shell:
            return os.system(' '.join(command))

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

        if status != 0:
            raise CommandExecutedFalur(status, stderr_value)
        return stdout_value
    #}}}

    #{{{def __repr__(self):
    def __repr__(self):
        return "%s object bound '%s'" % (self.__class__.__name__, self.cmdname)
    #}}}
pass

class CmdDispatcher(SingleCmd):

    ## prefix of sub command
    subcmd_prefix = None

    #{{{def __init__(self, cmdname, opt_style=0, subcmd_prefix=None):
    def __init__(self, cmdname, opt_style=0, subcmd_prefix=None):
        """Constructor

        @param str cmdname command name
        @param str opt_style option style
        @param str subcmd_prefix prefix of sub command
        """
        self.subcmd_prefix = subcmd_prefix
        super(CmdDispatcher, self).__init__(cmdname, opt_style)
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
