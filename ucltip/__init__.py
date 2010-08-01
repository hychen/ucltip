# most of codes from GitPython project
import commands
import subprocess
import sys
import re

extra = {}
if sys.platform == 'win32':
    extra = {'shell': True}

def double_dashify(string):
    return '--' + string

def dashify(string):
    return string.replace('_', '-')

class CommandNotFound(Exception):   pass
class CommandExecutedFalur(Exception):  pass

execute_kwargs = ('istream',
                  'with_keep_cwd',
                  'with_raw_output',
                  'with_exception',
                  'with_extended_output',
                  'post_output')

class SingleCmd(object):

    cmd = None
    subcmd_prefix = None
    pre_subcmd = None

    def __init__(self, cmd=None):
        if cmd:
            self.cmd = str(cmd)

        if not self.cmd:
            self.cmd = self.__class__.__name__.lower()

        if not self.cmd or \
           not commands.getoutput('whereis %s' % self.cmd)[len(self.cmd)+1:]:
            raise CommandNotFound()

    def __repr__(self):
        return "command object bound '%s'" % self.cmd

    def execute(self, command,
                      istream=None,
                      post_output=None,
                      with_raw_output=False,
                      with_exception=False,
                      with_extended_output=False):
        # Start the process
        proc = subprocess.Popen(command,
                                stdin=istream,
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                **extra
                                )
        if istream:
            return proc

        # Wait for the process to return
        try:
            stdout_value = proc.stdout.read()
            stderr_value = proc.stderr.read()
            status = proc.wait()
        finally:
            proc.stdout.close()
            proc.stderr.close()

        # Strip off trailing whitespace by default
        if not with_raw_output:
            stdout_value = stdout_value.strip()
            stderr_value = stderr_value.strip()

        if with_exception and status != 0:
            raise CommandExecutedFalur(stderr_value)

        if post_output:
            stdout_value = post_output(stdout_value)
        # Allow access to the command's status code
        if with_extended_output:
            return (status, stdout_value, stderr_value)
        else:
            return stdout_value

    def transform_kwargs(self, **kwargs):
        """
        Transforms Python style kwargs into git command line options.
        """
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
                    args.append("--%s=%s" % (dashify(k), v))
        return args

    def _call_process(self, *args, **kwargs):
        subcmd = kwargs.get('subcmd')
        if subcmd:
            del(kwargs['subcmd'])

        # Handle optional arguments prior to calling transform_kwargs
        # otherwise these'll end up in args, which is bad.
        _kwargs = {}
        for kwarg in execute_kwargs:
            try:
                _kwargs[kwarg] = kwargs.pop(kwarg)
            except KeyError:
                pass

        # Prepare the argument list
        opt_args = self.transform_kwargs(**kwargs)
        ext_args = map(str, args)
        args = opt_args + ext_args

        call = [self.cmd]
        if subcmd:
            if self.subcmd_prefix:
                subcmd = self.subcmd_prefix + subcmd
            elif self.pre_subcmd:
                subcmd = self.pre_subcmd(subcmd)
            call.append(subcmd)
        call.extend(args)
        return self.execute(call, **_kwargs)

    def __call__(self, *args, **kwargs):
        return self._call_process(*args, **kwargs)

class CmdDispatcher(SingleCmd):

    def __init__(self, cmd=None, subcmd_prefix=None):
        if cmd:
            self.cmd = cmd
        if subcmd_prefix:
            self.subcmd_prefix = subcmd_prefix
        super(CmdDispatcher, self).__init__(self.cmd)

    def __getattr__(self, name):
        if name[:1] == '_':
            raise AttributeError(name)
        return lambda *args, **kwargs: self._call_process(*args, subcmd=dashify(name), **kwargs)

def cmd(name, subcmd_prefix=None):
    if not subcmd_prefix:
        return SingleCmd(name)
    else:
        return CmdDispatcher(name, subcmd_prefix)
