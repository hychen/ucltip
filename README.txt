UCLTIP - Use command line tool in Python

This library make you easy to use command line tool in Python.
The idea and most of basic codes are from GitPython project `http://pypi.python.org/pypi/GitPython/`

Here is examples

::
    from ucltip import SingleCmd
    ls = SingleCmd('ls')
    # use it as a function
    print ls(a=True,l=True)

if the command has sub commd , you can use CmdDispatcher

::
    from ucltip import CmdDispatcher

    class Zenity(CmdDispatcher):

        cmd = 'zenity'
        subcmd_prefix = '--'

    zenity = Zenity()
    zenity.info(text="hello", width="200")
