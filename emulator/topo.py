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
    mytopo.addHostNodes(node_names=['client', 'vnf1', 'vnf2', 'server'],
                        ip_prefix='10.0.0.', ip_suffixes=['12', '13', '14', '15'],
                        dimage='pica_dev:4', volume=None,
                        docker_args={"cpuset_cpus": '1', 'cpu_quota': 25000})
    mytopo.addSwitchNodes(node_names=['s1', 's2'])
    # create links, `bw` is bandwith, unit of bandwith is 'Mbit/s'
    mytopo.addLinks(links=['client - s1 - s2 - server', 's1 - vnf1',
                           's2 - vnf2'], bw=1, delay='10ms', use_htb=True)
    mynet = mytopo.startNetwork()
    ## network settings ##
    # delete default flows
    mynet.delFlowsOnSwitches(node_names=['s1', 's2'])
    # add flows
    mynet.addFlowsOnSwitch(proto='udp', flows=[
                           'client - s1 - vnf1 - s1 - s2 - vnf2 - s2 - server', 'server - s2 - s1 - client'])
    # disable checksum, `node_nameports = ['switch_name:port_name',...]``
    mynet.disableSwitchCksums(node_nameports=['s1:vnf1', 's2:vnf2'])
    mynet.enterCLI()
