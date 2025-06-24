#!/bin/bash
# Simple script to create bytecode files from Python source
if [[ $# == 0 ]]; then
    print 2>&1 "Need to pass a python file to compile"
    exit 1
fi
mydir=$(dirname ${BASH_SOURCE[0]})

(cd ../../python-xdis && . ./admin-tools/setup-master.sh)

if [[ -z "$PYVERSIONS" ]]; then
    print 2>&1 "Need to have PYVERSIONS set first"
    exit 2
fi

for version in $PYVERSIONS; do
    # Note: below we use
    if [[ $version == 2.6.9 ]]; then
        (cd ../../python-xdis && . ./admin-tools/setup-python-2.4.sh)
    fi
    for file in $*; do
        pyenv local $version
	    python ${mydir}/compile-file.py "$file"
    done
    short=$(basename $file .py)
    git add -f ${mydir}/bytecode-*/${short}*
    rm -v .pyenv_version *~ 2>/dev/null || /bin/true
done
rm -v .python-version 2>/dev/null || /bin/true
# (cd ../../python-xdis && . ./admin-tools/setup-master.sh)
