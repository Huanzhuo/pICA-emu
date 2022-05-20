[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# 1. pICA Emulator
![](image/logo.png)

## 1.1. Table of Contents
- [1. pICA Emulator](#1-pica-emulator)
  - [1.1. Table of Contents](#11-table-of-contents)
  - [1.2. Description](#12-description)
  - [1.3. Requirements](#13-requirements)
  - [1.4. Getting Started](#14-getting-started)
    - [1.4.1. Option1: Install in a Vagrant managed VM (Highly Recommended)](#141-option1-install-in-a-vagrant-managed-vm-highly-recommended)
    - [1.4.2. Option2: Install on user's custom VM or directly on host OS (Ubuntu20.04)](#142-option2-install-on-users-custom-vm-or-directly-on-host-os-ubuntu2004)
  - [1.5. Install docker image of pICA](#15-install-docker-image-of-pica)
  - [1.6. Run pICA in the Emulator](#16-run-pica-in-the-emulator)
  - [1.7. Citation](#17-citation)
  - [1.8. About Us](#18-about-us)
  - [1.9. License](#19-license)


## 1.2. Description

This application emulate the Progressive Independent Component Analysis (pICA) in the network, it is **based on the [comnetsemu](https://git.comnets.net/public-repo/comnetsemu)**.
A pICA demonstrator can be accessed on [pICA-Demo](https://huanzhuo.github.io/pICA-demo/).

## 1.3. Requirements

Please install `vagrant` and `Virtualbox` on the host OS to build the testbed VM.

## 1.4. Getting Started

Please run follow steps to setup the emulator. Assume the source directory of `pICA-emu` project is `~/pICA-emu`.

### 1.4.1. Option1: Install in a Vagrant managed VM (Highly Recommended)

1. Create the testbed VM using Vagrant on your host OS.
    ```bash
    cd ~/pICA-emu || exit
    vagrant up testbed
    ```
    Then run `vagrant ssh testbed` to login into the VM. Following steps should be run **inside the VM**.

2. Install `docker-ce` and add docker into user group
    ```bash
    cd ~/comnetsemu/util
    bash ./install.sh -d

    sudo groupadd docker
    sudo gpasswd -a vagrant docker
    newgrp docker
    sudo systemctl start docker
    
    cd /home/vagrant/comnetsemu/test_containers || exit
    sudo bash ./build.sh
    ```

<!-- 2. 
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
    ``` -->

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

### 1.4.2. Option2: Install on user's custom VM or directly on host OS (Ubuntu20.04)

1. Install the comnetsemu and simpleemu on your host OS.
    ```bash
    cd ~/pICA-emu/emu-installer || exit
    bash ./install.sh
    ```
2. Run test to make sure the `ComNetsEmu` is installed correctly (optional).
    ```bash
    cd ~/comnetsemu
    sudo make test
    ```
    Only run following steps when all tests passed without any errors. Otherwise, please create issues on [Github](https://github.com/stevelorenz/comnetsemu/issues) from Zuo Xiang.

<!-- 2. Install the docker image for pICA.
    ```bash
    cd ~/pICA-emu || exit
    sudo bash ./build_docker_images.sh
    ```

3. Run the topology in the folder ```~/pICA-emu/emulator```:
    ```bash
    cd ~/pICA-emu/emulator
    sudo python3 ./topo.py
    ```
    Then, the next steps are the same as below -->

## 1.5. Install docker image of pICA
1. Build the docker image of pICA.
    ```bash
    cd /vagrant
    sudo bash ./build_docker_images.sh
    ```
    After this step, you should see the image with name ```pica_dev``` when running ```docker image ls```. You should change your work path inside the VM for following steps.

## 1.6. Run pICA in the Emulator
1. Run the topology in the folder ```/vagrant/emulator```:
    ```bash 
    cd /vagrant/emulator
    sudo python3 ./topo.py
    ```
    You should see the prompt `mininet>` when the network configuration is finished.
    And five terminals are popped up, you can identify client, server, VNF, swich, and a controller by looking at the host name (e.g., `@client`) in the shell.

    The number of VNFs is defined as 2 in ```topo.py```. For an arbitary number of VNFs, please define the value of ```n_vnf``` in ```topo_n_vnf.py``` and run ```topo_n_vnf.py``` instead of ```topo.py```.

3. Please firstly run `server.py` inside the server's shell, then the rest. The default work mode is ```compute-and-forward``` (```cf```). With the flag ``` sf``` on the client, the work mode will be changed to ```store-and-forward```. With the flag ```data_id``` on the client, an integer value is expected to set the id of test data set. With the flag ```n_test``` on the client, an integer value is expected to set the evaluation rounds.
    ```bash
    # in the server terminal
    sudo python3 ./server.py

    # in the vnf terminal
    sudo python3 ./vnf.py

    # in the client terminal
    sudo python3 ./client.py cf data_id n_test
    ```


## 1.7. Citation

If you like our repository, please cite our papers.

    ``` 
    @Article{wu2022picaextension,
        author  = {Wu, Huanzhuo and Shen, Yunbin and Xiao, Xun and Nguyen, Giang T. and Hecker, Artur and Fitzek, Frank H.-P.},
        title   = {Accelerating Industrial IoT Acoustic Data Separation with In-Network Computing},
        doi     = {10.1109/JIOT.2022.3176974},
        pages   = {1--15},
        groups  = {my_paper},
        journal = {IEEE Internet of Things Journal},
        year    = {2022},
        }
    ```
    
## 1.8. About Us

We are researchers at the Deutsche Telekom Chair of Communication Networks (ComNets) at TU Dresden, Germany. Our focus is on in-network computing.

* **Huanzhuo Wu** - huanzhuo.wu@tu-dresden.de or wuhuanzhuo@gmail.com
* **Yunbin Shen** - yunbin.shen@mailbox.tu-dresden.de or shenyunbin@outlook.com

## 1.9. License

This project is licensed under the [MIT license](./LICENSE).