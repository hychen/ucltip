# vim:syn=rst:
========================================
UCLTIP - Use command line tool in Python
========================================

This library makes you use command line tool in Python more easier.
The original idea and most of basic codes are from GitPython project
`http://pypi.python.org/pypi/GitPython/`

Basic Usage
-----------

::

	# without options
	uname = SingleCmd('uname')
	# result is Linux
	print uname()

	# with args
	expr  = SingleCmd('expr')
	# result is 10
	print expr(7, '+', 3)

	# with options, the style is '-a - l'
	# example: ls -a -l
	ls = SingleCmd('ls')
	# enable debug mode to see what command string will be executed.
	# show the debug message like this: DBG: execute cmd 'ls -a -l'
	ls.__DEBUG__ = True
	print ls(l=True, a=True)

	# with boolean options, the style is 'ls --all --almost-all'
	# variable has '-' should replaced by '_', otherwise syntax error happens
	print ls(all=True, almost_all=True)

	# with key-value optons, has 2 different style,
	# `--key value` or `--key=value`, you can use opt_style variable to control them
	wget = SingleCmd('wget')

	# replacement of wget -o log http://url
	wget('http://url', o='log')

	# replacement of wget -o log=http://url
	wget = SingleCmd('wget', opt_style=1)
	wget('http://url', o='log')

	# you can also overwrite the bound command
	ls.cmdname = 'echo'
	# the result is
	# DBG: execute cmd 'echo hi'
	#'hi\n'
	print ls("hi")

	# some options is mutiple, which means the name is name, but you can give
	# many different values, for example
	# `foo -a -b -o Dir=/var -o Dir::Cache=/tmp`
	# so you need to use make_optargs to create args if the opt name is duplicate
	optargs = ucltip.make_optargs('o', ('Dir=/var','Dir::Cache=/tmp'))
	SingleCmd('foo')(optargs, a=True, b=True)

The command be executed by subprocess.call, it bypass the shell.

::

	# the result is $HOME, and it will not show output directly
	print SingleCmd('echo')("$HOME")

if you want execute command via shell and use shell enviroment variable, please
do as follow, if args of function includes `via_shell=True`, the command be executed by os.system

::

	# the result is "/home/somebody", and show output directly
	SingleCmd('echo')("$HOME", via_shell=True)

And here is the replacement if you want to do pipe for mutiple commands

::

        ls = SingleCmd('ls')
        grep = SingleCmd('grep')
	# the result is setup.py
	print grep('setup.py', stdin=ls(a=True, interact=True).stdout))

	#p.s ls(a=True, interact=True) return a Popen instance, so you can have more control
	#    of that process

Handling Error of command execution
-----------------------------------
if the command you want to use is not exists, the exception ucltip.CommandNotFound raises

::

	>> a=ucltip.SingleCmd('oo')
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  File "ucltip/__init__.py", line 103, in __init__
	    raise CommandNotFound()
	ucltip.CommandNotFound

if the command be executed falied, the exception ucltip.CommandExecutedFalur raises

::

	>>> a=ucltip.SingleCmd('ls')
	>>> a
	SingleCmd object bound 'ls'
	>>> a(ccc=True)
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  File "ucltip/__init__.py", line 109, in __call__
	    return self._callProcess(*args, **kwargs)
	  File "ucltip/__init__.py", line 126, in _callProcess
	    return self.execute(call, **_kwargs)
	  File "ucltip/__init__.py", line 169, in execute
	    raise CommandExecutedFalur(status, stderr_value)
	ucltip.CommandExecutedFalur: ls: unrecognized option '--ccc'
	Try `ls --help' for more information.

here is a example to hanlde error:

::

	try:
		print ucltip.SingleCmd('ls')
	except ucltip.CommandExecutedFalur as e:
		print e

Command Dispatcher
------------------

Some command tools has sub command, like `git`, `zenity`, `pbuilder`, `apt-get`, etc.
and some commands like `zenity`, they have prefix string in their sub command.

::

	# the sub command name is the method name
	git = CmdDispatcher('git')
	git.log()
	# and you can also give args and options like what SingleCmd can use
	git.log(raw=True, since='2010')

	# you can get Popen instance also
	proc = git.log(interact=True)

	# zenity has '--' prefix in its sub command, so you need to specify prefix string
	# and option style
	zenity = CmdDispatcher('zneity', opt_style=1, subcmd_prefix='--')

	# zneity --info --text=hi
	zneity.info(text="hi")
