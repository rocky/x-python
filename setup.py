#!/usr/bin/env python

import sys
from setuptools import setup

from setuptools import find_packages
from __pkginfo__ import (
    __version__,
    author,
    author_email,
    classifiers,
    entry_points,
    install_requires,
    long_description,
    py_modules,
    short_desc,
    url,
)

major = sys.version_info[0]
minor = sys.version_info[1]

if major != 3 or not 3 <= minor < 6:
    sys.stderr.write("This installation medium is only for Python 3.6 .. 5. You are running Python %s.%s.\n" % (major, minor))

if major == 3 and minor > 10:
    sys.stderr.write("Please install using xpython-x.y.z.tar.gz from https://github.com/rocky/x-python/releases\n")
    sys.exit(1)
elif major == 3 and 6 <= minor <= 10:
    sys.stderr.write("Please install using xpython_36-x.y.z.tar.gz from https://github.com/rocky/x-python/releases\n")
    sys.exit(1)
if major == 3 and 1 <= minor <= 2:
    sys.stderr.write("Please install using xpython_31-x.y.z.tar.gz from https://github.com/rocky/x-python/releases\n")
    sys.exit(1)
elif major == 2:
    sys.stderr.write("Please install using xpython_24-x.y.z.tar.gz from https://github.com/rocky/x-python/releases\n")
    sys.exit(1)


setup(
    name="x-python",
    version=__version__,
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    description=short_desc,
    entry_points=entry_points,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=find_packages(),
    py_modules=py_modules,
    install_requires=install_requires,
    url=url,
)
