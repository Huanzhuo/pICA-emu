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

1. Create the testbed VM using Vagrant on your host OS, the docker image `pica_dev:4` will automatically intalled in this step:.

    ```bash
    cd ~/pICA-emu || exit
    vagrant up testbed
    ```

Then run `vagrant ssh testbed` to login into the VM. Following steps should be run **inside the VM**.


2. Upgrade ComNetsEmu Python module and all dependencies automatically inside VM (optional).
   
    ```bash
    cd ~/comnetsemu/util
    bash ./install.sh -u
    ```

3. Run test to make sure the `ComNetsEmu` is installed correctly (optional).

    ```bash
    cd ~/comnetsemu
    sudo make test
    ```

Only run following steps when all tests passed without any errors. Otherwise, please create issues on [Github](https://github.com/stevelorenz/comnetsemu/issues) from Zuo Xiang.


## Run pICA in the Emulator

1. Run the topology in the folder ```$TOP_DIR/vagrant/emulator```:

    ```bash
    cd /vagrant/emulator
    sudo python3 ./topo.py
    ```
You should see the prompt `mininet>` when the network configuration is finished.
And five terminals are popped up, you can identify client, server, VNF, swich, and a controller by looking at the host name (e.g. `@client`) in the shell.

2. Please firstly run `server.py` inside the server's shell, then the rest:

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