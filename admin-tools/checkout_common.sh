# Common checkout routine
export PATH=$HOME/.pyenv/bin/pyenv:$PATH
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
x_python_fulldir=$(readlink -f $mydir)

function setup_version {
    local repo=$1
    version=$2
    echo Running setup $version on $repo ...
    (cd $x_python_fulldir/../../$repo && . ./admin-tools/setup-${version}.sh)
    return $?
}

function checkout_finish {
    branch=$1
    cd $x_python_fulldir/..
    git checkout $branch && pyenv local $PYTHON_VERSION && git pull
    cd $xpython_owd
    rc=$?
    return $rc
}
