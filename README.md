[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# pICA-emulator

## Table of Contents
- [pICA-emulator](#pica-emulator)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Requirements](#requirements)
  - [Getting Started](#getting-started)
  - [Run pICA in the Emulator](#run-pica-in-the-emulator)
  - [About Us](#about-us)
  - [License](#license)


## Description

This application emulate the progressive ICA in the network, it is **based on the [comnetsemu](https://git.comnets.net/public-repo/comnetsemu)**.

## Requirements

Please install `vagrant` and `Virtualbox` on the host OS to build the testbed VM.

## Getting Started

Please run follow steps to setup the emulator. Assume the source directory of `pICA-emu` project is `~/pICA-emu`.

1. Create the testbed VM using Vagrant on your host OS.
    ```bash
    cd ~/pICA-emu || exit
    vagrant up testbed
    ```
    Then run `vagrant ssh testbed` to login into the VM. Following steps should be run **inside the VM**.

2. Install `docker-ce` and add docker into user group
    ```bash
    sudo apt-get update
    sudo apt-get install  apt-transport-https  ca-certificates curl  software-properties-common
    curl -fsSL  https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add
    sudo add-apt-repository "deb [arch=amd64]  https://download.docker.com/linux/ubuntu bionic stable" 
    sudo apt-get update
    sudo apt-get install docker-ce

    sudo groupadd docker
    sudo gpasswd -a vagrant docker
    newgrp docker

    cd /home/vagrant/comnetsemu/test_containers || exit
    sudo bash ./build.sh
    ```

3. Upgrade ComNetsEmu Python module and all dependencies automatically inside VM
    ```bash
    cd ~/comnetsemu/util
    bash ./install.sh -u
    ```

4. Run test to make sure the `ComNetsEmu` is installed correctly (optional).
    ```bash
    cd ~/comnetsemu
    sudo make test
    ```
    Only run following steps when all tests passed without any errors. Otherwise, please create issues on [Github](https://github.com/stevelorenz/comnetsemu/issues) from Zuo Xiang.


## Run pICA in the Emulator

1. Install docker image of pICA:
   ```bash
   cd /vagrant
   sudo bash ./build_docker_images.sh
   ```
    After this step, you should see the image with name ```pica_dev``` when running ```docker image ls```.
    You should change your work path inside the VM for following steps.

2. Run the topology in the folder ```/vagrant/emulator```:
    ```bash
    cd /vagrant/emulator
    sudo python3 ./topo.py
    ```
    You should see the prompt `mininet>` when the network configuration is finished.
    And five terminals are popped up, you can identify client, server, VNF, swich, and a controller by looking at the host name (e.g., `@client`) in the shell.

3. Please firstly run `server.py` inside the server's shell, then the rest. The default work mode is ```compute-and-forward```, with the flag ``` storefwd``` on the client, the work mode will be changed to ```store-and-forward```.
    ```bash
    # in the server terminal
    sudo python3 ./server.py

    # in the vnf terminal
    sudo python3 ./vnf.py

    # in the client terminal
    sudo python3 ./client.py
    ```
## About Us

We are researchers at the Deutsche Telekom Chair of Communication Networks (ComNets) at TU Dresden, Germany. Our focus is on in-network computing.

* **Huanzhuo Wu** - huanzhuo.wu@tu-dresden.de or wuhuanzhuo@gmail.com
* **Yunbin Shen** - yunbin.shen@mailbox.tu-dresden.de or shenyunbin@outlook.com

## License

This project is licensed under the [MIT license](./LICENSE).