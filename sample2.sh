#!/usr/bin/env bash

APT=$(which apt)
YUM=$(which yum)

if [ ! -z "$APT" ]; then
    sudo apt install docker.io -y
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    sudo systemctl status docker
    sudo groupadd docker
    sudo gpasswd -a $USER docker
else
    if [ ! -z "$YUM" ]; then
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum-config-manager --disable docker-ce-stable
        sudo yum install docker-ce containerd.aarch64 -y
    else
        echo "No apt or yum found. Exiting..."
        exit 1
    fi
fi

cpu_arch=$(uname -m)
echo "cpu_arch:$cpu_arch"

if [ "$cpu_arch" == "x86_64" ]; then
	echo "Installing docker-compose via apt."
	sudo apt-get install docker-compose -y
else
	echo "Installing docker-compose via curl."
	sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose
fi
docker-compose --version

echo "DONE."
