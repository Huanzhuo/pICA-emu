# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-05-05 20:43:27
# @modify: 2021-05-05 20:43:27
# @desc. : [description]


"""
PICA in Network Topo
"""

from simpleemu.simpletopo import SimpleTopo

if __name__ == "__main__":
    # it should at first create the network infrastructure then set the flows
    ## network infrastructure ##
    mytopo = SimpleTopo()
    # create network devices
    mytopo.addController(node_name='c0')
    mytopo.addHostNode(node_name='client', dimage='pica_dev:4', ip='10.0.0.12/24',
                       volume='/vagrant/emulator', docker_args={"cpuset_cpus": '0'})
    mytopo.addHostNode(node_name='vnf1', dimage='pica_dev:4', ip='10.0.0.13/24',
                       volume='/vagrant/emulator',docker_args={"cpuset_cpus": '1'})
    mytopo.addHostNode(node_name='vnf2', dimage='pica_dev:4', ip='10.0.0.14/24',
                       volume='/vagrant/emulator',docker_args={"cpuset_cpus": '1'})
    mytopo.addHostNode(node_name='server', dimage='pica_dev:4', ip='10.0.0.15/24',
                       volume='/vagrant/emulator', docker_args={"cpuset_cpus": '0'})
    mytopo.addSwitchNode(node_name='s1')
    mytopo.addSwitchNode(node_name='s2')
    # create links
    mytopo.addLinks(['client - s1 - s2 - server','s1 - vnf1','s2 - vnf2'], bw=10, delay='10ms', use_htb=True)
    mynet = mytopo.startNetwork()
    ## network settings ##
    # delete default flows
    mynet.delFlowsOnSwitch(node_name='s1')
    mynet.delFlowsOnSwitch(node_name='s2')
    # add flows
    mynet.addFlowsOnSwitch(proto='udp', flows=['client - s1 - vnf1 - s1 - s2 - vnf2 - s2 - server','server - s2 - s1 - client'])
    # disable checksum
    mynet.disableNodeCksum(node_name='s1',port='vnf1')
    mynet.disableNodeCksum(node_name='s2',port='vnf2')
    mynet.enterCLI()
