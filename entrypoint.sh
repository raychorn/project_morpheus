#!/bin/bash

DIR0="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

VENV_DIR=$(ls $DIR0/venv*/bin/activate | head -n 1)

MAKEVENV=$DIR0/makevenv.sh
if [ ! -f "$VENV_DIR" ]; then
    echo "No virtualenv found. Creating one..."
    if [ ! -f "$MAKEVENV" ]; then
        echo "No makevenv.sh found. Exiting..."
        exit 1
    fi
    $MAKEVENV
    VENV_DIR=$(ls $DIR0/venv*/bin/activate | head -n 1)
fi

if [ ! -f "$VENV_DIR" ]; then
    echo "No Virtual Env ($VENV_DIR) found. Exiting..."
    exit 1
fi
. $VENV_DIR

PY=$(which python3.9)

if [ ! -f "$PY" ]; then
    echo "No python3.9 found. Exiting..."
    exit 1
fi

$PY $DIR0/morpheus.py
