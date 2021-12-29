#!/bin/bash

DIR0="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

VENV_DIR=$(ls $DIR0/venv*/bin/activate | head -n 1)

sleeping () {
    echo "Cannot continue..."
    exit 1
}

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

COMPILER=$DIR0/compile_to_pyc.py

if [ ! -f "$COMPILER" ]; then
    echo "No compiler found. Exiting..."
    sleeping
fi

VENV_DIR=$(dirname $VENV_DIR)
VENV_DIR=$(dirname $VENV_DIR)
$PY $COMPILER $DIR0 $VENV_DIR

#echo "VENV_DIR:$VENV_DIR"

tar --exclude="./venv*" --exclude="./.git" --exclude='.env' --exclude='.gitignore' --exclude='*.py' --exclude='get-pip.cpython-39.pyc' --exclude='compiler.sh' --exclude='./scripts/__pycache__' -zcvf ../project_morpheus.tgz .
