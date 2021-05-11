import argparse
import math
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from shlex import split
from subprocess import check_output

from comnetsemu.cli import CLI
from comnetsemu.net import Containernet
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller, RemoteController
from mininet.term import makeTerm


PARENT_DIR = os.path.abspath(os.path.join(os.path.curdir, os.pardir))


def add_ovs_flows():
    """Add Openflow rules to redirect traffic between client and server to vnf."""
    check_output(split("ovs-ofctl del-flows s1"))
    check_output(split("ovs-ofctl del-flows s2"))
    check_output(split('ovs-ofctl add-flow s1 "priority=1,in_port=1,actions=output=2"'))
    check_output(split('ovs-ofctl add-flow s1 "priority=1,in_port=2,actions=output=3"'))
    check_output(split('ovs-ofctl add-flow s1 "priority=1,in_port=3,actions=output=1"'))

    check_output(split('ovs-ofctl add-flow s2 "priority=1,in_port=1,actions=output=2"'))
    check_output(split('ovs-ofctl add-flow s2 "priority=1,in_port=2,actions=output=3"'))
    check_output(split('ovs-ofctl add-flow s1 "priority=1,in_port=3,actions=output=1"'))


def disable_cksum_offload(ifces):
    """Disable RX/TX checksum offloading"""
    for ifce in ifces:
        check_output(split("sudo ethtool --offload %s rx off tx off" % ifce))


def test_tope():
    net = Containernet(controller=Controller, link=TCLink, autoSetMacs=True, autoStaticArp=True, xterms=False)
    info("*** Adding controller\n")
    net.addController("c0")
    # MARK: Host addresses below 11 could be used for network services.
    info("*** Adding hosts\n")
    client = net.addDockerHost(
        "client",
        dimage="ia-net-lite-emu",
        ip="10.0.1.11/16",
        docker_args={"cpuset_cpus": "0",
                     "hostname": "client",
                     "volumes": {
                         PARENT_DIR: {"bind": "/ia-net-lite-emu", "mode": "rw"},
                     },
                     "working_dir": "/ia-net-lite-emu/emulator"},
    )
    server = net.addDockerHost(
        "server",
        dimage="ia-net-lite-emu",
        ip="10.0.3.11/16",
        docker_args={"cpuset_cpus": "0", "hostname": "server",
                     "volumes": {
                         PARENT_DIR: {"bind": "/ia-net-lite-emu", "mode": "rw"},
                     },
                     "working_dir": "/ia-net-lite-emu/emulator"},
    )
    vnf1 = net.addDockerHost(
        "vnf1",
        dimage="ia-net-lite-emu",
        ip= "10.0.2.11/16",
        docker_args={"cpuset_cpus": "0", "hostname": "vnf1",
                     "volumes": {
                         PARENT_DIR: {"bind": "/ia-net-lite-emu", "mode": "rw"},
                     },
                     "working_dir": "/ia-net-lite-emu/emulator"},
    )
    vnf2 = net.addDockerHost(
        "vnf2",
        dimage="ia-net-lite-emu",
        ip="10.0.2.12/16",
        docker_args={"cpuset_cpus": "0", "hostname": "vnf2",
                     "volumes": {
                         PARENT_DIR: {"bind": "/ia-net-lite-emu", "mode": "rw"},
                     },
                     "working_dir": "/ia-net-lite-emu/emulator"},
    )


    info("*** Adding switch\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    info("*** Creating links\n")
    net.addLinkNamedIfce(s1, client, bw=10, delay="150ms", use_htb=True)
    net.addLinkNamedIfce(s1, vnf1, bw=1000, delay="10ms", use_htb=True)
    net.addLink(s1, s2, bw=10, delay="150ms", use_htb=True)
    net.addLinkNamedIfce(s2, vnf2, bw=1000, delay="10ms", use_htb=True)
    net.addLinkNamedIfce(s2, server, bw=10, delay="150ms", use_htb=True)
    info("*** Starting network\n")
    net.start()
    net.pingAll()
    add_ovs_flows()
    ifces = ["s1-vnf1", "s2-vnf2"]
    disable_cksum_offload(ifces)

    info("*** Enter CLI\n")
    CLI(net)

    info("*** Stopping network")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    test_tope()





