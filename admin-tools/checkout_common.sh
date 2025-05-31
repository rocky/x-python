# Common checkout routine
export PATH=$HOME/.pyenv/bin/pyenv:$PATH
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
fulldir=$(readlink -f $mydir)

function checkout_version {
    local repo=$1
    version=${2:-python-3.12}
    echo Checking out $version on $repo ...
    (cd ../$repo && git checkout $version && pyenv local $PYTHON_VERSION) && \
	git pull
    return $?
}

function setup_version {
    local repo=$1
    version=$2
    echo Running setup $version on $repo ...
    (cd ../$repo && . ./admin-tools/setup-${version}.sh)
    return $?
}

function checkout_finish {
    branch=$1
    cd $xpython_owd
    git checkout $branch && pyenv local $PYTHON_VERSION && git pull
    rc=$?
    return $rc
}
