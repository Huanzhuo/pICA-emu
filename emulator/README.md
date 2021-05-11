# Emulation of Distributed IA-Net-Lite

## Requirements

Please install `vagrant` and `Virtualbox` on the host OS to build the testbed VM.

## Getting Started

Please run follow steps to setup the emulator and  run a simple store and forward example.

Assume the source directory of `ia-net-lite-emu` project is `~/ia-net-lite-emu`.

1. Create the testbed VM using Vagrant on your host OS.

```bash
cd ~/ia-net-lite-emu || exit
vagrant up testbed
```

Then run `vagrant ssh testbed` to login into the VM.

Following steps should be run **inside the VM**.

Install `docker-ce` and add docker into user group
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
```

Upgrade ComNetsEmu Python module and all dependencies automatically inside VM
```bash
cd ~/comnetsemu/util
bash ./install.sh -u
```

2. Run test to make sure the `ComNetsEmu` is installed correctly.

```bash
cd ~/comnetsemu
sudo make test
```

Only run following steps when all tests passed without any errors.
Otherwise, please create issues on [Github](https://github.com/stevelorenz/comnetsemu/issues) or send Emails to Zuo Xiang.

3. Build the Docker image for `ia-net-lite-emu`

```bash
cd /vagrant
chmod u+x build.sh
./build.sh
```

After this step, you should see the image with name `ia-net-lite-emu` when running `docker image ls`.

You should change your current path to `/vagrant/emulator` (inside the VM, of course) for following steps.


4. Run the multi-hop network emulation script.

```bash
sudo python3 ./topology.py
```

Now you should see the pop-up window for logs of the Ryu SDN controller running the application `./multi_hop_controller.py`.
And you should also see the prompt `mininet>` when the network configuration is finished.
If you check the CPU usage inside the VM using `htop`, two VNF processes are heavily using the second CPU core.

5. Login server, client, vnf1, and vnf2 inside the corresponded container.

```bash
mininet> xterm client server vnf1 vnf2
```

Then four windows are popped up, you can identify client, server and two VNFs by looking at the host name (e.g. `@client`) in the shell.

Then please firstly run `server.py` inside the server's shell and then `client.py` in the clients shell (use `-h` to check the CLI options).

Run server, vnf1, vnf2, and client with compute-and-forward mode (the default option). Currently, this order must be kept manually. Please use the following sequence:

```bash
root@server# python3 ./server.py

root@vnf1# python3 ./vnf.py --id 1

root@vnf2# python3 ./vnf.py --id 2
# change epochs to modify running rounds (e.g. 60)
root@client# python3 ./client.py --epochs 60
```


Run server, vnf1, vnf2, and client with store-and-forward mode, please use the following sequence:

```bash
root@server# python3 ./server.py -m 0

root@vnf1# python3 ./vnf.py --id 1 -m 0

root@vnf2# python3 ./vnf.py --id 2 -m 0
# change epochs to modify running rounds (e.g. 60)
root@client# python3 ./client.py -m 0 --epochs 60
```

Run ia-net with store-and-forward:
simply change IA_NET = True in file: emulator_utils.py
change LENGTH can modify the input length

Results will store in latency_results

## Todo
1. Configure the links in the network and the computing power of nodes.
