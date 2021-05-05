# PICA IN NETWORK

## Description

This application emulate the progressive ica in the network, it is **based on the [comnetsemu](https://git.comnets.net/public-repo/comnetsemu)**.

## How to run this example

1. Install [comnetsemu](https://git.comnets.net/public-repo/comnetsemu) and copy this folder to ```$COMNETSEMU_DIR/app/pICA-emu```

2. Run the comnetsemu, the following steps should be made in the comnetsemu

3. Move to the directory ```/pICA-emu``` and install docker pica_dev:4 for this application:

    ```bash
    $ cd $TOP_DIR/comnetsemu/app/pICA-emu
    $ sudo ./docker/build_docker_images.sh
    ```
4. Run the topology at first:

    ```bash
    $ sudo python3 ./topo.py
    ```

5. There will be 5 terminals on the desktop, i.e. 'c1', 's1', 'server', 'client', 'vnf'. In the following terminals run the following command:

    ```bash
    # in the server terminal
    $ sudo python3 ./server.py

    # in the vnf terminal
    $ sudo python3 ./vnf.py

    # in the client terminal
    $ sudo python3 ./client.py
    ```
