#!/usr/bin/env python

import sys
from setuptools import setup

major = sys.version_info[0]
minor = sys.version_info[1]

if major != 3 or not minor >= 11:
    sys.stderr.write("This installation medium is only for Python 3.11 and later. You are running Python %s.%s.\n" % (major, minor))

if major == 3 and 6 <= minor <= 10:
    sys.stderr.write("Please install using xpython-x.y.z.tar.gz from https://github.com/rocky/x-python/releases\n")
    sys.exit(1)
elif major == 3 and 3 <= minor <= 5:
    sys.stderr.write("Please install using xpython_33-x.y.z.tar.gz from https://github.com/rocky/x-python/releases\n")
    sys.exit(1)
if major == 3 and 1 <= minor <= 2:
    sys.stderr.write("Please install using xpython_31-x.y.z.tar.gz from https://github.com/rocky/x-python/releases\n")
    sys.exit(1)
elif major == 2:
    sys.stderr.write("Please install using xpython_2.4-x.y.z.tar.gz from https://github.com/rocky/x-python/releases\n")
    sys.exit(1)

setup()
