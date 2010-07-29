#!/usr/bin/env python
# -*- encoding=utf8 -*-
#
# Copyright © 2010 Hsin Yi Chen
from distutils.core import setup

setup(
    name = 'ucltip',
    version = open('VERSION.txt').read().strip(),
    description = 'Use command line tool in Python',
    long_description=open('README.txt').read(),
    author = 'Hsin-Yi Chen 陳信屹 (hychen)',
    author_email = 'ossug.hychen@gmail.com',
    license = 'BSD License',
    packages=['ucltip'],
)
