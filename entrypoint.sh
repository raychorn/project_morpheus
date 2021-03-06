#!/bin/bash

DIR0="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

BUILD_OPTS="--build"

if [ -z "$1" ]; then
    BUILD_OPTS=""
fi

VENV_DIR=$(ls $DIR0/venv*/bin/activate | head -n 1)

sleeping () {
    echo "Sleeping due to an issue..."
    sleep infinity
}

cat $DIR0/scripts/get-pip.txt > $DIR0/scripts/get-pip.py

MAKEVENV=$DIR0/makevenv.sh
if [ ! -f "$VENV_DIR" ]; then
    echo "No virtualenv found. Creating one..."
    if [ ! -f "$MAKEVENV" ]; then
        echo "No makevenv.sh found. Exiting..."
        sleeping
    fi
    $MAKEVENV
    VENV_DIR=$(ls $DIR0/venv*/bin/activate | head -n 1)
fi

if [ ! -f "$VENV_DIR" ]; then
    echo "No Virtual Env ($VENV_DIR) found. Exiting..."
    sleeping
fi
. $VENV_DIR

PY=$(which python3.9)

if [ ! -f "$PY" ]; then
    echo "No python3.9 found. Exiting..."
    sleeping
fi

HOST_ETC=$(ls /host_etc)

if [ -z "$HOST_ETC" ]; then
    echo "No /host_etc found. Exiting..."
    sleeping
fi

HOSTNAME=$(cat /host_etc/hostname)

if [ -z "$HOSTNAME" ]; then
    echo "No hostname found. Exiting..."
    sleeping
fi

PYCACHE=$DIR0/__pycache__

if [ -d "$PYCACHE" ]; then
    echo "Moving pycache contents..."
    mv $PYCACHE/* $DIR0/
    mv $DIR0/relocate_pyc.cpython-39.pyc $DIR0/relocate_pyc.pyc
    rm -rf $PYCACHE
fi

##################################################
MOVER=$DIR0/relocate_pyc.pyc

if [ ! -f "$MOVER" ]; then
    echo "No mover found. Exiting..."
    sleeping
fi

VENV_DIR=$(dirname $VENV_DIR)
VENV_DIR=$(dirname $VENV_DIR)
$PY $MOVER $DIR0 $VENV_DIR
##################################################

APP=$DIR0/morpheus.py

if [ ! -f "$APP" ]; then
    APP=$DIR0/morpheus.pyc
fi

if [ ! -f "$APP" ]; then
    echo "No morpheus.py found. Exiting..."
    sleeping
fi

if [ -z "$BUILD_OPTS" ]; then
    echo "Running $PY $APP $HOSTNAME"
    $PY $APP $HOSTNAME
fi
