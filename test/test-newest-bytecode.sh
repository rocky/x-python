#!/bin/bash
# Simple script to run xpython 3.11+ bytecode
if (( $# > 0 )); then
    # FIXME
    print "Arg not handled yet"
    exit 1
fi
mydir=$(dirname ${BASH_SOURCE[0]})
set -e

source ../admin-tools/pyenv-newest-versions

for version in $PYVERSIONS; do
    pyenv local $version
    echo "Using Python $version"
    first_two=$(echo $version | cut -d'.' -f 1-2)
    for file in bytecode-${first_two}/*.pyc; do
	echo ======= $file ========
	xpython "$file"
	echo ------- $file --------
    done
done
rm .python-version
