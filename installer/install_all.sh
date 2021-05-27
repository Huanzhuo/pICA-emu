#!bin/bash

echo "Installing python and dependencies!"
echo "#################################################################"
sudo apt -y update
sudo apt -y upgrade
sudo apt install -y git make pkg-config sudo python3 libpython3-dev python3-dev python3-pip software-properties-common
pip install setuptools
pip install build

echo "Installing comnetsemu!"
echo "#################################################################"

git clone https://git.comnets.net/public-repo/comnetsemu.git

cd comnetsemu/util
bash ./install.sh -a

echo "Installing simpleemu!"
echo "#################################################################"

cd ../../simpleemu
sudo python3 ./setup.py install

