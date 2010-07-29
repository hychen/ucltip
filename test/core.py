#!/usr/bin/env python
# -*- encoding=utf8 -*-
#
# Author 2010 Hsin-Yi Chen
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

import os
import unittest
import shutil
import tempfile

from ucltip import SingleCmd, CommandNotFound, CmdDispatcher, CommandExecutedFalur, dashify

class ConsoleTestCase(unittest.TestCase):

    #{{{def setUp(self):
    def setUp(self):
        pass
    #}}}

    #{{{def tearDown(self):
    def tearDown(self):
        pass
    #}}}

    #{{{def test_command_not_found(self):
    def test_command_not_found(self):
        self.assertRaises(CommandNotFound, SingleCmd, None)
        self.assertRaises(CommandNotFound, SingleCmd, '')
        self.assertRaises(CommandNotFound, SingleCmd, 1234.5)
        self.assertRaises(CommandNotFound, SingleCmd, '000')
    #}}}

    #{{{def test_singlecmd(self):
    def test_singlecmd(self):
        expr = SingleCmd('expr')
        self.assertEquals(expr('3', '+', '4'), '7')
        self.assertEquals(expr('3', '+', '4', with_raw_output=True), '7\n')
        self.assertEquals(expr('3', '+', '4', post_output=int), 7)
        try:
            git = SingleCmd('git')
            self.assertEquals(git('log',subcmd='help', with_extended_output=True)[0],0)
        except CommandNotFound, e:
            print "Skip: git does not be installed."
    #}}}

    #{{{def test_cmddispather(self):
    def test_cmddispather(self):
        git = CmdDispatcher('git')
        git.pre_subcmd = dashify
        self.assertRaises(CommandExecutedFalur,git.log)
    #}}}
pass

def suite():
    return unittest.makeSuite(ConsoleTestCase, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
