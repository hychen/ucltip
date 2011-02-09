#!/usr/bin/env python
# -*- encoding=utf8 -*-
#
# Copyright © 2011 Hsin Yi Chen
from distutils.core import setup

setup(
    name = 'ucltip',
    version = open('VERSION.txt').read().strip(),
    description = 'A library to help making command line tool Python binding faster',
    long_description=open('README.txt').read(),
    author = 'Hsin-Yi Chen 陳信屹 (hychen)',
    author_email = 'ossug.hychen@gmail.com',
    url='http://github.com/hychen/ucltip',
    license = 'BSD-2-clause License',
    packages=['ucltip'],
    classifiers = [
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: BSD License",
      "Operating System :: OS Independent",
      "Programming Language :: Python",
      "Programming Language :: Python :: 2.5",
      "Programming Language :: Python :: 2.6",
      "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
