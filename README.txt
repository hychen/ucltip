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

::

	>>>ucltip.regcmds('apt-get', 'apt-cache', cls=ucltip.CmdDispatcher)
	>>> apt_get
	<ucltip.CmdDispatcher object at 0xb7305dcc>
	>>> apt_cache
	<ucltip.CmdDispatcher object at 0xb7308bec>
