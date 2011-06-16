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

Command Option
--------------

so far, we already leanr how to execute command with arguments, but how about command options?
it is pretty easy also, just think command option like python keyword arguments.

Boolean option
-------------

when the type of keyword arguments's value is boolean, then this kind of keyword arguments
will be converted to command boolean option, for example, `-a` is equal '''func(a=True)'''

::
	>>>ls('/tmp', a=True)
	['ls', '/tmp', '-a']

Key-Value option
----------------

::
	>>>ls('tmp', quoting_style='c')
	['ls', '--quoting-style', 'c']

::
	>>>ls.conf.opt_style = 1
	>>>ls('tmp', quoting_style='c')
	['ls', '--quoting-style=c']

CmdDispatcher
-------------
