#!/bin/bash
# Check out python-2.7 and dependent development branches.
PYTHON_VERSION=2.7

bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

xpython_owd=$(pwd)
mydir=$(dirname $bs)
x_python_fulldir=$(readlink -f $mydir)

if ! source $x_python_fulldir/../admin-tools/pyenv-2.7-versions ; then
    exit $?
fi

cd $mydir
. ./checkout_common.sh
(cd $fulldir/.. && setup_version python-xdis python-2.4)
checkout_finish python-2.4-to-2.7
