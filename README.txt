# vim:syn=rst:
========================================
UCLTIP - Use command line tool in Python
========================================

This library makes you use command line tool in Python more easier.
The original idea are from GitPython project `http://pypi.python.org/pypi/GitPython/`

The basic concept is to transform:

1) command as a instance,
2) command options as arguments or function/method keyword arguments.

Feature:

- Transform CLI Tool arguments to Python function/method arguments
- Transform CLI Tool Boolean option style to Python function/method keyword arguments
- Transform CLI Tool Key-Value option style to Python function/method keyword arguments
- Transform CLI Tool Key-Value option style to Python function/method keyword arguments
- Transform CLI Command as Python Class and use it in your script
- Set default options of Command for multiple use

-------
Example
-------

::

	>>>expr = ucltip.Cmd('expr')
	>>>ret = expr(3, '+', 4)
	>>>ret
	"7\n"

create a Cmd callable object

::
	>>>expr = ucltip.Cmd('expr')

run Cmd object as a function to get result like executing `expr 3 + 4` in shell,
the result will be storeged in '''ret''' variable, as the following shows, you can think
command line tool arguments as Python function arguments.

::
	>>>ret = expr(3, '+', 4)

if you want to only check what command string will be combined, you can doing dry run,
but ramind the command string will be split as a list.

::
	>>>expr = ucltip.Cmd('expr')
	>>>expr.conf.dry_run = True
	>>>expr(3, "+", 4)
	['expr', '3', '+', '4']


please note that jhe command be executed by subprocess.call, it bypass the shell.

::

	# the result is $HOME, and it will not show output directly
	print Cmd('echo')("$HOME")

if you want execute command via shell and use shell enviroment variable, please
do as follow, if args of function includes '''via_shell=True''', the command be executed by os.system

::

	# the result is "/home/somebody", and show output directly
	Cmd('echo')("$HOME", via_shell=True)

-----------------------------------
Handling Error of command execution
-----------------------------------
if the command you want to use is not exists, the exception ucltip.CommandNotFound raises

::

	>> a=ucltip.Cmd('oo')
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  File "ucltip/__init__.py", line 103, in __init__
	    raise CommandNotFound()
	ucltip.CommandNotFound

if the command be executed falied, the exception ucltip.CommandExecutedError raises

::

	>>> a=ucltip.Cmd('ls')
	>>> a
	Cmd object bound 'ls'
	>>> a(ccc=True)
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  File "ucltip/__init__.py", line 109, in __call__
	    return self._callProcess(*args, **kwargs)
	  File "ucltip/__init__.py", line 126, in _callProcess
	    return self.execute(call, **_kwargs)
	  File "ucltip/__init__.py", line 169, in execute
	    raise CommandExecutedError(status, stderr_value)
	ucltip.CommandExecutedError: ls: unrecognized option '--ccc'
	Try `ls --help' for more information.

here is a example to hanlde error:

::

	try:
		print ucltip.Cmd('ls')
	except ucltip.CommandExecutedError as e:
		print e

--------------
Command Option
--------------

so far, we already leanr how to execute command with arguments, but how about command options?
it is pretty easy also, just think command option like python keyword arguments.

''Boolean option''

when the type of keyword arguments's value is boolean, then this kind of keyword arguments
will be converted to command boolean option, for example, `-a` is equal '''func(a=True)'''

::
	>>>ls('/tmp', a=True)
	['ls', '/tmp', '-a']

Key-Value option
================

when the type of keyword arguments's value is interge number or string, then these of keyword
arguments will be coverted to command key-value option, for example, '--quoting_style 1' is equal
'''func(quoting_style=1)'''

::
	>>>ls('tmp', quoting_style='c')
	['ls', '--quoting-style', 'c']

also, you can change option style by set '''opt_style''' attribute, support option style are `gnu`,
`posix`,`java`, the default value is `posix`.

note: java option style is not fully supported.

::
	>>>ls.conf.opt_style = 'gnu'
	>>>ls('tmp', quoting_style='c')
	['ls', '--quoting-style=c']

some options is mutiple, which means the name is name, but you can give
many different values, for example

::
	# `foo -a -b -o Dir=/var -o Dir::Cache=/tmp`
	# so you need to use make_optargs to create args if the opt name is duplicate
	optargs = ucltip.make_optargs('o', ('Dir=/var','Dir::Cache=/tmp'))
	Cmd('foo')(optargs, a=True, b=True)

-------------
CmdDispatcher
-------------

The CmdDispatcher is an object for mapping some command tools has sub command,
like `git`, `zenity`, `pbuilder`, `apt-get`, etc.

method name indicates as sub command name, method arguements indicates sub command arguments,
and method keyword arguments indicates sub command options.

::
	>>apt_get = ucltip.CmdDispatcher('apt-get')
	>>apt_get.conf.dry_run = True
	>>apt_get.install('vim')
	['apt-get', 'install', 'vim']

if sub command has prefix string, you can use '''subcmd_prefix''' attribute to set it.

::

	>>zenity = ucltip.CmdDispatcher('zenity')
	>>zenity.subcmd_prefix = '--'
	>>zenity.conf.dry_run = True
	>>zenity.info(text='hello')
	['zenity', '--info', '--text hello']

--------------
Default Option
--------------

the options does not be stored after you execute command, if you want to keep options
for multiple using, you can use ''''opts''' function to set default options as the following

::

	>>>ls = ucltip.Cmd('ls)
	>>>ls.conf.dry_run=True
	>>>ls.opts(l=True)
	>>>ls('/tmp')
	['ls', '/tmp', '-l']

CmdDispatcher sub command will load default options from its parent, in this case,
'''apt_get.install.opts()''' is the same as '''apt_get.opts()'''

::

	>>>apt_get = ucltip.CmdDispatcher('apt-get')
	>>>apt_get.conf.dry_run = True
	>>>apt_get.opts(t='maverick')
	>>>apt_get.install.opts()
	{t':'maverick'}
	>>>apt_get.install('vim')
	apt-get', 'install', 'vim', '-t maverick']
	>>>apt_get.opts(t=False)
	>>>apt_get.install('vim')
	['apt-get', 'install', 'vim']

Pipe
====
In subprocess, the way for doing pipeline is

::

	>>>p1 = Popen(["dmesg"], stdout=PIPE)
	>>>p2 = Popen(["grep", "hda"], stdin=p1.stdout, stdout=PIPE)
	>>>output = p2.communicate()[0]

which is not convenience when you want to pipe many commands.

Pipe class provide similar interface as C library `libpipeline` (http://libpipeline.nongnu.org/)
that manipulating pipelines of subprocesses in a flexible and convenient way in C.

firstly, you need to create a Pipe instance

::
	>>>pipe = ucltip.Pipe()

and then add some command arguments as you want

::

	>>>pipe.add('expr', 1, '+' 3)
	>>>pipe.add('sed', 's/4/5/', '--posix')

finally run the process, wait it terminate and get its output

::

	>>>pipe.wait()
	>>>pipe.stdout.read()
	5
	# get error message in case command executed error
	>>>pipe.stderr.read()

the first argument of Pipe.add function can be Cmd or SubCmd,
please remaind the usage of add function is changed in this case

::
	>>>pipe = ucltip.Pipe()
	>>>pipe.add(Cmd('expr'), 1, '+', 3)
	>>>pipe.add(Cmd('sed'), 's/4/5', posix=True)
	>>>pipe.wait()
	>>>pipe.stdout.read()
	5

::

	>>>apt_cache = ucltip.CmdDispatcher('apt-cache')
	>>>pipe = ucltip.Pipe()
	>>>pipe.add(apt_cache.search, 'vim-common')
	>>>pipe.add(Cmd('grep'), 'vim')
	>>>pipe.wait()
	>>>pipe.stdout.read()

Helper
======

regcmds is used to register multiple command in built-in environment one time

::

	>>>ucltip.regcmds('ls', 'wget', 'sed')
	>>> ls
	Cmd object bound 'ls'
	>>> wget
	Cmd object bound 'wget'
	>>> sed
	Cmd object bound 'sed'

avaliabl for specify class

::

	>>>ucltip.regcmds('apt-get', 'apt-cache', cls=ucltip.CmdDispatcher)
	>>> apt_get
	<ucltip.CmdDispatcher object at 0xb7305dcc>
	>>> apt_cache
	<ucltip.CmdDispatcher object at 0xb7308bec>

`global_config` is used to set up global configure of All class

To change executing behavior of Cmd or CmdDispatcher

::
	# executing command, default setting
	>>>ucltip.global_config(execmod='process')

	# produce command arguments only, same as dry_run
	>>>ucltip.global_config(execmod='list')
	>>>ucltip.Cmd('ls')(a=True)
	['ls', '-a']

	# produce command string only
	>>>ucltip.global_config(execmod='string')
	>>>ucltip.Cmd('ls')(a=True)
	'ls -a'

Debugging
=========

ucltip provid debug output in /var/log/syslog after you enable debug mode

::
	>>> ucltip.global_config(debug=True)

Get invlolved
=============

if you are interesting to help, please contact author,
Hychen, his email is  <ossug.hychen at gmail.com>.

The VCS of code is avaliabl on  http://github.com/hychen/ucltip
