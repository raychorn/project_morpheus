#!/usr/bin/env bash

PY=$(which python3.9)

APT=$(which apt)
YUM=$(which yum)

if [ ! -z "$APT" ]; then
    sudo apt install zsh -y
    sudo apt install wget curl -y
    #sudo apt-get install cockpit -y
    sudo add-apt-repository ppa:git-core/ppa -y
    sudo apt update -y
    sudo apt upgrade -y
    sudo apt install git -y
    if [ ! -f "$PY" ]; then
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt install python3.9 python3.9-dev python3.9-venv -y
    fi
    PY=$(which python3.9)
else
    if [ ! -z "$YUM" ]; then
        sudo yum install zsh -y
        sudo yum install wget curl -y
        sudo yum install git -y
        # yum install latest python 3.9
        GCC=$(which gcc)
        if [ -z "$GCC" ]; then
            sudo yum groupinstall "Development Tools" -y
            sudo yum install openssl-devel libffi-devel bzip2-devel -y
        fi
        if [ ! -f "$PY" ]; then
            wget https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tgz
            tar xvf Python-3.9.9.tgz
            cd Python-3.9*/
            ./configure --enable-optimizations
            sudo make altinstall
        fi
        PY=$(which python3.9)
    else
        echo "No apt or yum found. Exiting..."
        exit 1
    fi
fi


PIP_TEST=$(pip --version | grep python3.9)
if [ -z "$PIP_TEST" ]; then
	$PY -m ensurepip --default-pip --user
	PIP=$(which pip3.9)
fi

ZSH=$(which zsh)

sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k

echo "powerlevel10k/powerlevel10k"

echo "DONE."
