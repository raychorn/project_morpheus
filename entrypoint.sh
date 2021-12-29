#!/bin/bash

DIR0="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

VENV_DIR=$(ls $DIR0/venv*/bin/activate | head -n 1)

sleeping () {
    echo "Sleeping due to an issue..."
    sleep infinity
}

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

$PY $DIR0/morpheus.py $HOSTNAME
