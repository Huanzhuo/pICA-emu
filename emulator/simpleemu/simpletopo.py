# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-02
# @modify: 2021-04-02
# @desc. : [description]

import os
import copy
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

    def addController(self, node_name):
        info("*** Adding controller "+node_name+"\n")
        self.net.addController(node_name)

    def addHostNode(self, node_name, ip, dimage, volume=None, docker_args={}, **params):
        info("*** Adding host "+node_name+"\n")
        docker_args = copy.copy(docker_args)
        docker_args.update({"hostname": node_name,"volumes": {volume: {"bind": '/volume', "mode": "rw"}},"working_dir": '/volume'})
        if volume is None:
            volume = os.path.abspath(os.path.join(os.path.curdir, os.pardir))
        node = self.net.addDockerHost(name=node_name, dimage=dimage, ip=ip, docker_args=docker_args, **params)
        self.nodes[node_name] = {'node':node,'type':'host','ports':[]}

    def addHostNodes(self, node_names, ip_prefix, ip_suffixes, dimage, volume=None, docker_args={}, **params):
        for node_name, ip_suffix in zip(node_names, ip_suffixes):
            ip = ip_prefix + str(ip_suffix)
            self.addHostNode(node_name, ip, dimage, volume, docker_args, **params)

    def addSwitchNode(self, node_name):
        info("*** Adding switch "+node_name+"\n")
        node = self.net.addSwitch(node_name)
        self.nodes[node_name] = {'node':node,'type':'switch','ports':[]}
    
    def addSwitchNodes(self, node_names):
        for node_name in node_names:
            self.addSwitchNode(node_name)

    def addLink(self, src, dst, *args, **kwargs):
        info("*** Adding link "+src+"-"+dst+"\n")
        if self.nodes[src]['type'] == 'switch' and self.nodes[dst]['type'] == 'switch':
            self.net.addLink(self.nodes[src]['node'], self.nodes[dst]['node'], *args, **kwargs)
        else:
            self.net.addLinkNamedIfce(self.nodes[src]['node'], self.nodes[dst]['node'], *args, **kwargs)            
        self.nodes[src]['ports'].append(dst)
        self.nodes[dst]['ports'].append(src)
        info("\n")

    def addLinks(self, links, *args, **kwargs):
        for link in links:
            link = link.replace(' ','')
            node_names = link.split('-')
            for i in range(len(node_names)-1):
                self.addLink(node_names[i], node_names[i+1], *args, **kwargs)

    def startNetwork(self):
        info("*** Starting network\n")
        self.net.start()
        self.net.pingAll()
        return SimpleNet(self.net, self.nodes)

class SimpleNet():
    def __init__(self,net, nodes) -> None:
        self.net = net
        self.nodes = nodes

    def getOpenFlowPort(self, node_name, port):
        return str(self.nodes[node_name]['ports'].index(port) + 1)

    def addFlowOnSwitch(self, node_name, proto, in_port, out_port):
        info("*** Adding flow " + in_port + "-" + node_name + "-" + out_port + " on switch\n")
        in_port = self.getOpenFlowPort(node_name, in_port)
        out_port = self.getOpenFlowPort(node_name, out_port)
        check_output(split('ovs-ofctl add-flow '+node_name+' "'+proto +
                        ',in_port='+in_port+',actions=output='+out_port+'"'))
    
    def addFlowsOnSwitch(self, proto, flows):
        for flow in flows:
            flow = flow.replace(' ','')
            node_names = flow.split('-')
            for i in range(len(node_names)-2):
                in_port, node_name, out_port = node_names[i],node_names[i+1],node_names[i+2]
                if self.nodes[node_name]['type'] == 'switch':
                    self.addFlowOnSwitch(node_name, proto, in_port, out_port)

    def delFlowsOnSwitch(self, node_name):
        info("*** Deleting flow on switch " + node_name + "\n")
        check_output(split("ovs-ofctl del-flows "+node_name))

    def delFlowsOnSwitches(self, node_names):
        for node_name in node_names:
            self.delFlowsOnSwitch(node_name)

    def disableSwitchCksum(self, node_name, port):
        info("*** Disabling flow on switch " + node_name + "\n")
        check_output(
            split("sudo ethtool --offload " + node_name + '-' + port + " rx off tx off" ))
    
    def disableSwitchCksums(self, node_nameports):
        for node_nameport in node_nameports:
            node_name, port = node_nameport.split(':')
            self.disableSwitchCksum(node_name, port)

    def enterCLI(self):
        info("*** Enter CLI\n")
        CLI(self.net)
        info("*** Stopping network")
        self.net.stop()