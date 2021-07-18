# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-05-05 20:43:27
# @modify: 2021-05-05 20:43:27
# @desc. : [description]


"""
PICA in Network Topo
"""
import sys
from simpleemu.simpletopo import SimpleTopo

if __name__ == "__main__":
    if len(sys.argv) == 1:
        n_vnf = 1 # the value of n_vnf is [0,1,2,...,6,7]
    else:
        n_vnf = int(sys.argv[1])
    print("*** VNF Number:",n_vnf)
    # it should at first create the network infrastructure then set the flows
    ## network infrastructure ##
    mytopo = SimpleTopo()
    # create network devices
    mytopo.addController(node_name='c0')
    # distribute vnf into multiple cpus
    mytopo.addHostNodes(node_names=['client', 'server'],
                        ip_prefix='10.0.0.', ip_suffixes=['12', '15'],
                        dimage='pica_dev:4', volume=None,
                        docker_args={"cpuset_cpus": '0', 'cpu_quota': 30000})
    # mytopo.addHostNodes(node_names=['vnf'+ str(i) for i in range(n_vnf)],
    #                     ip_prefix='10.0.0.', ip_suffixes=[str(i+1) for i in range(n_vnf)],
    #                     dimage='pica_dev:4', volume=None,
    #                     docker_args={"cpuset_cpus": '1', 'cpu_quota': 13500})
    for i in range(n_vnf):
        mytopo.addHostNodes(node_names=['vnf'+ str(i)],
                            ip_prefix='10.0.0.', ip_suffixes=[str(i+1)],
                            dimage='pica_dev:4', volume=None,
                            docker_args={"cpuset_cpus": str(i//3+1), 'cpu_quota': 30000})

    mytopo.addSwitchNodes(node_names=['s'+ str(i) for i in range(n_vnf)])
    # create links, `bw` is bandwith, unit of bandwith is 'Mbit/s'
    mytopo.addLinks(links=['client' + ''.join(['-s'+ str(i) for i in range(n_vnf)]) + '-server'] + 
                    ['s'+str(i)+'-vnf'+str(i) for i in range(n_vnf)],
                    bw=1000, delay='10ms', use_htb=True)
    mynet = mytopo.startNetwork()
    ## network settings ##
    # add flows
    if n_vnf > 0:
        mynet.addFlowsOnSwitch(proto='udp', flows=['client-s0-vnf0'] + 
                                ['s' + str(i-1) + '-s' + str(i) + '-vnf'+str(i) for i in range(1,n_vnf)] + 
                                ['server' + ''.join(['-s'+ str(i) for i in range(n_vnf-1,-1,-1)]) + '-client'])
    mynet.enterCLI()
