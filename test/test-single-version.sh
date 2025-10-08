#!/bin/bash
# Test a single Python version, e.g. 3.7.16
# using only that bytecode for that version
# e.g. byteocde-3.7.
set -e

PYTHON=${PYTHON:-python}
PYTHON_VERSION=${1:-$(python -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2)}
PLATFORM=$(${PYTHON} -c 'import platform; print(platform.python_implementation())')
VERBOSE=${VERBOSE:-0}
XPYTHON_OPTS=${XPYTHON_OPTS:-""}


bytecode_dir="bytecode-${PYTHON_VERSION}"
if [[ $PLATFORM == "PyPy" ]]; then
    bytecode_dir="bytecode-pypy${PYTHON_VERSION}"
else
    bytecode_dir="bytecode-${PYTHON_VERSION}"
fi

echo Testing Python $PYTHON_VERSION $PLATFORM

for file in ${bytecode_dir}/*.pyc ; do
    (( $VERBOSE != 0)) && echo $file
    if ! xpython ${XPYTHON_OPTS} $file ; then
	echo "$file broken"
	break
    fi
done
