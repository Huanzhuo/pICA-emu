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
    mytopo.addController(name='c0')
    mytopo.addHostNode(name='client', dimage='pica_dev:4', ip='10.0.0.12/24',
                       volume='/home/vagrant/comnetsemu/app/pICA-emu', docker_args={"cpuset_cpus": '0'})
    mytopo.addHostNode(name='vnf', dimage='pica_dev:4', ip='10.0.0.13/24',
                       volume='/home/vagrant/comnetsemu/app/pICA-emu',docker_args={"cpuset_cpus": '0'})
    mytopo.addHostNode(name='server', dimage='pica_dev:4', ip='10.0.0.14/24',
                       volume='/home/vagrant/comnetsemu/app/pICA-emu', docker_args={"cpuset_cpus": '0'})
    mytopo.addSwitchNode(name='s1')
    mytopo.addLink(src='s1', dst='client', bw=10, delay='10ms', use_htb=True)
    mytopo.addLink(src='s1', dst='vnf', bw=10, delay='10ms', use_htb=True)
    mytopo.addLink(src='s1', dst='server', bw=10, delay='10ms', use_htb=True)
    mynet = mytopo.startNetwork()
    ## network settings ##
    mynet.delFlowsOnNode(node='s1')
    mynet.addFlowOnNode(node='s1',proto='udp',in_port='client',out_port='vnf')
    mynet.addFlowOnNode(node='s1',proto='udp',in_port='vnf',out_port='server')
    mynet.addFlowOnNode(node='s1',proto='udp',in_port='server',out_port='client')
    mynet.disableNodeCksum(node='s1',port='vnf')
    mynet.enterCLI()
