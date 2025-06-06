#!/bin/bash
# Check out python-2.7 and dependent development branches.
pyenv local $PYTHON_VERSION

bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

PYTHON_VERSION=2.7

xpython_owd=$(pwd)
mydir=$(dirname $bs)
fulldir=$(readlink -f $mydir)
cd $mydir
. ./checkout_common.sh
(cd $fulldir/.. && setup_version python-xdis python-2.4)
checkout_finish python-2.4-to-2.7
