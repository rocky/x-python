#!/bin/bash
# Check out python-3.3-to-3.5 and dependent development branches.

PYTHON_VERSION=3.3.7

bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

function checkout_version {
    local repo=$1
    version=${2:-python-3.3-to-3.5}
    echo Checking out $version on $repo ...
    (cd ../$repo && git checkout $version && pyenv local $PYTHON_VERSION) && \
	git pull
    return $?
}

owd=$(pwd)

export PATH=$HOME/.pyenv/bin/pyenv:$PATH

mydir=$(dirname $bs)
fulldir=$(readlink -f $mydir)
cd $fulldir/..
(cd $fulldir/.. && checkout_version python-xdis python-3.3-to-3.5 && checkout_version x-python)

rm -v */.python-version || true
cd $owd
