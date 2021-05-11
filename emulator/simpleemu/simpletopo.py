# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-02
# @modify: 2021-04-02
# @desc. : [description]

import os
from shlex import split
from subprocess import check_output
from comnetsemu.cli import CLI
from comnetsemu.net import Containernet
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller

class SimpleTopo():
    def __init__(self):
        setLogLevel("info")
        self.nodes = {}
        self.net = Containernet(controller=Controller, link=TCLink,
                                autoSetMacs=True, autoStaticArp=True, xterms=True,)

    def addController(self, name):
        info("*** Adding controller "+name+"\n")
        self.net.addController(name)

    def addHostNode(self, name, dimage, ip, volume=None, docker_args={}):
        info("*** Adding host "+name+"\n")
        docker_args.update({"hostname": name,"volumes": {volume: {"bind": '/volume', "mode": "rw"}},"working_dir": '/volume'})
        if volume is None:
            volume = os.path.abspath(os.path.join(os.path.curdir, os.pardir))
        self.nodes[name] = self.net.addDockerHost(name, dimage=dimage, ip=ip, docker_args=docker_args)

    def addSwitchNode(self, name):
        info("*** Adding switch "+name+"\n")
        self.nodes[name] = self.net.addSwitch(name)

    def addLink(self, src, dst, *args, **kwargs):
        info("*** Adding link "+src+"-"+dst+"\n")
        self.net.addLinkNamedIfce(src, dst, *args, **kwargs)
        info("\n")

    def startNetwork(self):
        info("*** Starting network\n")
        self.net.start()
        self.net.pingAll()
        return SimpleNet(self.net)

class SimpleNet():
    def __init__(self,net) -> None:
        self.net = net

    def getOpenFlowPort(self, node):
        return check_output(split("ovs-vsctl get Interface "+node+" ofport")).decode("utf-8")

    def addFlowOnNode(self, node, proto, in_port, out_port):
        in_port = self.getOpenFlowPort(node+'-'+in_port)
        out_port = self.getOpenFlowPort(node+'-'+out_port)
        check_output(split('ovs-ofctl add-flow '+node+' "'+proto +
                        ',in_port='+in_port+',actions=output='+out_port+'"'))

    def delFlowsOnNode(self, node):
        check_output(split("ovs-ofctl del-flows "+node))

    def disableNodeCksum(self, node, port):
        check_output(
            split("sudo ethtool --offload " + node + '-' + port + " rx off tx off" ))

    def enterCLI(self):
        info("*** Enter CLI\n")
        CLI(self.net)
        info("*** Stopping network")
        self.net.stop()