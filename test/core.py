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

import ucltip

class ConsoleTestCase(unittest.TestCase):

    #{{{def setUp(self):
    def setUp(self):
        pass
    #}}}

    #{{{def tearDown(self):
    def tearDown(self):
        pass
    #}}}

    #{{{def test_opttransform(self):
    def test_opttransform(self):
        self.assertEquals(['--all','h','--all','i'],ucltip.make_optargs('all', ('h','i')))
        self.assertEquals(['--all=h','--all=i'],ucltip.make_optargs('all', ('h','i'), 1))
    #}}}

    #{{{def test_command_not_found(self):
    def test_command_not_found(self):
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, None)
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, '')
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, 1234.5)
        self.assertRaises(ucltip.CommandNotFound, ucltip.SingleCmd, '000')
    #}}}

    #{{{def test_singlecmd(self):
    def test_singlecmd(self):
        expr = ucltip.SingleCmd('expr')
        self.assertEquals(expr('3', '+', '4'), '7\n')
        # test pipe
        ls = ucltip.SingleCmd('ls')
        grep = ucltip.SingleCmd('grep')
        self.assertEquals('setup.py\n', 
                grep('setup.py', stdin=ls(a=True, interact=True).stdout))
    #}}}
pass

def suite():
    return unittest.makeSuite(ConsoleTestCase, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
