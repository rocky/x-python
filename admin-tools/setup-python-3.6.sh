#!/bin/bash
# Check out python-3.6-to-3.10 and dependent development branches.
PYTHON_VERSION=3.6

bs=${BASH_SOURCE[0]}
# if [[ $0 == $bs ]] ; then
#     echo "This script should be *sourced* rather than run directly through bash"
#     exit 1
# fi

xpython_owd=$(pwd)
mydir=$(dirname $bs)
x_python_fulldir=$(readlink -f $mydir)

if ! source $x_python_fulldir/../admin-tools/pyenv-3.6-3.10-versions ; then
    exit $?
fi

. $x_python_fulldir/checkout_common.sh

(cd $x_python_fulldir/../ && setup_version python-xdis python-3.6)
checkout_finish python-3.6-to-3.10
