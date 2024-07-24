#!/bin/bash
# Build distibution for Python 3.1 .. 3.2
# FIXME put some of the below in a common routine
PACKAGE=x-python
PACKAGE_=x_python

xpython_owd=$(pwd)
trap finish EXIT

cd $(dirname ${BASH_SOURCE[0]})

if ! source ./pyenv-3.1-3.2-versions ; then
    exit $?
fi

if ! source ./setup-python-3.1.sh ; then
    exit $?
fi

cd ..
source xpython/version.py
if [[ ! -n $__version__ ]]; then
    echo "You need to set __version__ first"
fi
echo $__version__

for pyversion in $PYVERSIONS; do
    echo --- $pyversion ---
    if ! pyenv local $pyversion ; then
	exit $?
    fi
    # pip bdist_egg create too-general wheels. So
    # we narrow that by moving the generated wheel.

    # Pick out first two number of version, e.g. 3.5.1 -> 35
    first_two=$(echo $pyversion | cut -d'.' -f 1-2 | sed -e 's/\.//')
    rm -fr build
    python setup.py bdist_egg
    echo === $pyversion ===
done

python ./setup.py sdist

tarball=dist/${PACKAGE}-${__version__}.tar.gz
if [[ -f $tarball ]]; then
    mv -v $tarball dist/${PACKAGE}_31-${__version__}.tar.gz
fi
finish
