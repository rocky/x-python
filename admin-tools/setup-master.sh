#!/bin/bash
# Check out master branch and dependent development master branches
PYTHON_VERSION=3.11

xpython_owd=$(pwd)
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

mydir=$(dirname $bs)
x_python_fulldir=$(readlink -f $mydir)

if ! source $x_python_fulldir/../admin-tools/pyenv-newest-versions ; then
    exit $?
fi

. ${x_python_fulldir}/checkout_common.sh

(cd ${x_python_fulldir}/../.. && setup_version python-xdis master)
checkout_finish master
