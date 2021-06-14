# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-02
# @modify: 2021-05-18
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
    """
    ### Description:

        Just make it easy to create a emulator. It is based on comnetsemu.

    ### Getting Started:

        Just use like follows, you can cope with most situations

        ```
        from simpleemu.simpletopo import SimpleTopo

        if __name__ == "__main__":
             
            ## network infrastructure ##
            # it should at first create the network infrastructure then set the flows
            
            mytopo = SimpleTopo()
            
            ## create network devices
            
            mytopo.addController(node_name='c0')

            # create host one by one, the ip of dockers are `ip_prefix + ip_suffixes`, 
            # `dimage` is the selected docker image name, `volume` is the path of the
            # shared folder.
            mytopo.addHostNodes(node_names=['client', 'vnf1', 'vnf2', 'server'],
                                ip_prefix='10.0.0.', ip_suffixes=['12', '13', '14', '15'],
                                dimage='pica_dev:4', volume='/vagrant/emulator',
                                docker_args={"cpuset_cpus": '1', 'cpu_quota': 25000})

            mytopo.addSwitchNodes(node_names=['s1', 's2'])
            
            # create links, `bw` is bandwith, unit of bandwith is 'Mbit/s'
            mytopo.addLinks(links=['client - s1 - s2 - server', 's1 - vnf1',
                                's2 - vnf2'], bw=1000, delay='10ms', use_htb=True)
            
            # start network and set the flow
            mynet = mytopo.startNetwork()
            
            
            ## network settings ##
            
            # delete default flows
            mynet.delFlowsOnSwitches(node_names=['s1', 's2'])
            
            # add flows
            mynet.addFlowsOnSwitch(proto='udp', flows=[
                                'client - s1 - vnf1 - s1 - s2 - vnf2 - s2 - server', 'server - s2 - s1 - client'])
            
            # disable checksum, node_nameports = ['switch_name:port_name',...]
            mynet.disableSwitchCksums(node_nameports=['s1:vnf1', 's2:vnf2'])

            # start the dockers and terminals
            mynet.enterCLI()
        ```

    """
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
        if volume is None:
            volume = os.getcwd()
        docker_args = copy.copy(docker_args)
        docker_args.update({"hostname": node_name,"volumes": {volume: {"bind": '/volume', "mode": "rw"}},"working_dir": '/volume'})
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