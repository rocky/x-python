#/bin/bash
# Setup for running Python 3.6 .. 3.10, merging Python 3.6-to-3.10 into this branch
xpython_36_owd=$(pwd)
cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.6.sh; then
    git merge master
fi
cd $xpython_36_owd
