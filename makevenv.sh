#!/bin/bash

TARGET_PY="3.9"
LOCAL_BIN=~/.local/bin

DIR0="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

export DEBIAN_FRONTEND=noninteractive
export TZ=US/Mountain
ln -s /usr/share/zoneinfo/$TZ /etc/localtime
echo $TZ > /etc/timezone

VENV=$DIR0/venv
REQS=$DIR0/requirements.txt

python39=$(which python3.9)

if [[ -f $python39 ]]
then
    echo "7. Found $python39"
else
    echo "8. Installing python3.9"
    apt update -y
    apt install software-properties-common -y
    echo -ne '\n' | add-apt-repository ppa:deadsnakes/ppa
    apt install python3.9 -y
	apt install python3.9-distutils -y
fi

python39=$(which python3.9)
pip3=$(which pip3)
setuptools="0"

if [[ -f $python39 ]]
then
    pip_local=$LOCAL_BIN/pip3
    if [[ -f $pip_local ]]
    then
        echo "8. Found $pip_local"
        export PATH=$LOCAL_BIN:$PATH
    else
        echo "Must install PIP?"
        if [[ -f $pip3 ]]
        then
            echo "9. $pip3 exists so not installing pip3, at this time."
        else
            echo "10. Installing pip3"
            GETPIP=$DIR0/scripts/get-pip.py

            if [[ -f $GETPIP ]]
            then
                $python39 $GETPIP
                export PATH=$LOCAL_BIN:$PATH
                pip3=$(which pip3)
                if [[ -f $pip3 ]]
                then
                    echo "11. Upgrading setuptools"
                    setuptools="1"
                    $pip3 install --upgrade setuptools > /dev/null 2>&1
                fi
            else
                echo "12. $GETPIP not found. Exiting..."
                exit 1
            fi
        fi
    fi
fi

pip3=$(which pip3)
echo "12. pip3 is $pip3"

if [[ -f $pip3 ]]
then
    echo "13. Upgrading pip"
    $pip3 install --upgrade pip > /dev/null 2>&1
    if [[ "$setuptools." == "0." ]]
    then
        echo "14. Upgrading setuptools"
        $pip3 install --upgrade setuptools > /dev/null 2>&1
    fi
fi

if [[ ! -f $pip3 ]]
then
    echo "14. pip3 not found. Exiting..."
    exit 1
fi

virtualenv=$(which virtualenv)
echo "15. virtualenv is $virtualenv"

if [[ ! -f $virtualenv ]]
then
    echo "15.1 installing virtualenv"
    $pip3 install virtualenv > /dev/null 2>&1
    $pip3 install --upgrade virtualenv > /dev/null 2>&1
fi

virtualenv=$(which virtualenv)

if [[ ! -f $virtualenv ]]
then
    echo "15.2 virtualenv not found. Exiting..."
    exit 1
fi

choice=$(which python3.9)

version=$($choice --version)
echo "Use this -> $choice --> $version"

v=$($choice -c 'import sys; i=sys.version_info; print("{}{}{}".format(i.major,i.minor,i.micro))')
vv=$($choice -c 'import sys; i=sys.version_info; print("{}.{}.{}".format(i.major,i.minor,i.micro))')
echo "Use this -> $choice --> $v -> $vv"

VENV=$VENV$v
echo "VENV -> $VENV"

if [[ -d $VENV ]]
then
    rm -R -f $VENV
fi

if [[ ! -d $VENV ]]
then
    echo "Making virtualenv for Python $choice -> $VENV"
    virtualenv --python $choice -v $VENV
fi

if [[ -d $VENV ]]
then
    . $VENV/bin/activate
    pip install --upgrade setuptools > /dev/null 2>&1
    pip install --upgrade pip > /dev/null 2>&1

    if [[ -f $REQS ]]
    then
        echo "Installing $REQS"
        pip install -r $REQS
    fi

fi