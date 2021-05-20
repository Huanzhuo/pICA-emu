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
    n_vnf = 10
    # it should at first create the network infrastructure then set the flows
    ## network infrastructure ##
    mytopo = SimpleTopo()
    # create network devices
    mytopo.addController(node_name='c0')
    mytopo.addHostNodes(node_names=['client', 'server']+list(map(lambda x: 'vnf'+str(x), range(n_vnf))),
                        ip_prefix='10.0.0.', ip_suffixes=['12', '15']+list(map(lambda x: str(100+x), range(n_vnf))),
                        dimage='pica_dev:4', volume='/vagrant/emulator',
                        docker_args={"cpuset_cpus": '1', 'cpu_quota': 8000})
    mytopo.addSwitchNodes(node_names=list(
        map(lambda x: 's'+str(x), range(n_vnf))))
    # create links, `bw` is bandwith, unit of bandwith is 'Mbit/s'
    mytopo.addLinks(links=['client - '+''.join(list(map(lambda x: 's'+str(x)+'-', range(n_vnf))))+'server'] +
                    list(map(lambda x: 's'+str(x)+'-'+'vnf'+str(x), range(n_vnf))), bw=1000, delay='10ms', use_htb=True)
    mynet = mytopo.startNetwork()
    ## network settings ##
    # delete default flows
    mynet.delFlowsOnSwitches(node_names=list(
        map(lambda x: 's'+str(x), range(n_vnf))))
    # add flows
    mynet.addFlowsOnSwitch(proto='udp', flows=[
                           'client - '+''.join(list(map(lambda x: 's'+str(x)+'-vnf'+str(x)+'-s'+str(x)+'-', range(n_vnf))))+'server',
                            'server - '+''.join(list(map(lambda x: 's'+str(x)+'-', reversed(range(n_vnf)))))+'client'])
    # disable checksum, `node_nameports = ['switch_name:port_name',...]``
    mynet.disableSwitchCksums(node_nameports=list(
        map(lambda x: 's'+str(x)+':'+'vnf'+str(x), range(n_vnf))))
    mynet.enterCLI()
