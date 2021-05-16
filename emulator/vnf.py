# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-05-05 20:41:14
# @modify: 2021-05-16 15:41:14
# @desc. : [description]


"""
Forwarding VNF via packet socket.
"""

from picautils.icanetwork import icanetwork
from picautils.icabuffer import ICABuffer
import numpy as np
import time
from picautils.packetutils import *
from picautils.pybss_testbed import pybss_tb
from simpleemu.simplecoin import SimpleCOIN
import socket

# get ifce name and node ip automatically
def get_addr(ip_telegram):
    from subprocess import Popen, PIPE
    ifconfig_output = Popen('ifconfig', stdout=PIPE).stdout.read()
    for paragraph in ifconfig_output.split(b'\n\n'):
        paragraph = paragraph.split()
        if len(paragraph)>6 and len(paragraph[0])>1:
            ifce_name = paragraph[0][:-1].decode("utf-8")
            ip = paragraph[5].decode("utf-8")
            if ip_telegram in ip:
                return ifce_name,ip
    raise ValueError('ip not detected!')

IFCE_NAME, NODE_IP = get_addr('10.0.')
DEF_INIT_SETTINGS = {'is_finish':False,'m': np.inf, 'W': None, 'proc_len': np.inf,'proc_len_multiplier': 2, 'node_max_ext_nums': [np.inf], 'node_max_lens': [np.inf]}
init_settings = {}
init_settings.update(DEF_INIT_SETTINGS)
dst_ip_addr = None
ica_processed = False

ica_buf = ICABuffer(max_size=16e4) 

app = SimpleCOIN(ifce_name=IFCE_NAME,n_func_process=1)

# main function for processing the data
# af_packet is the raw af_packet from the socket
@app.main()
def main(simlecoin, af_packet):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    # parse the raw packet to get the ip/udp infomations like ip, port, protocol, data
    packet = app.parse_af_packet(af_packet)
    # if prorocol is 17, that means is udp
    if packet['Protocol'] == 17 and packet['IP_src'] != NODE_IP:
        # the 1st byte is header other bytes are datas (here is "chunk")
        chunk = packet['Chunk']
        header = int(chunk[0])
        if header == HEADER_CLEAR_CACHE:
            print('*** vnf clearing cache!')
            simlecoin.submit_func(id='clear_cache', pid=0)
            print('*** vnf transmiting clearing message to next node!')
            simlecoin.forward(af_packet)
        elif header == HEADER_INIT:
            init_settings.update(pickle.loads(chunk[1:]))
            if init_settings['is_finish'] == False:
                print('*** vnf initializing!')
                simlecoin.submit_func(id='set_init_settings', pid=0, args=(init_settings,(packet['IP_dst'],packet['Port_dst']),))
            else:
                print('*** vnf transmit init_settings!')
                simlecoin.forward(af_packet)
        elif header == HEADER_DATA or header == HEADER_FINISH:
            simlecoin.submit_func(id='put_ica_buf', pid=0, args=(pickle.loads(chunk[1:]),))
            simlecoin.forward(af_packet)
            if header == HEADER_FINISH:
                t = time.localtime()
                print('*** last_pkt:',time.strftime("%H:%M:%S", t))
        else:
            simlecoin.forward(af_packet)

@app.func('clear_cache')
def clear_cache(simlecoin):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    ica_processed = False
    ica_buf.init()
    init_settings.update(DEF_INIT_SETTINGS)


@app.func('set_init_settings')
def initialization(simlecoin, _init_settings, _dst_ip_addr):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    init_settings.update(_init_settings)
    dst_ip_addr = _dst_ip_addr
    if ica_buf.size() >= init_settings['proc_len']:
        simlecoin.submit_func(id='pica_service', pid=0)

@app.func('put_ica_buf')
def ica_buf_put(simlecoin, data):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    if ica_processed == False:
        ica_buf.put(data)
        if ica_buf.size() >= init_settings['proc_len']:
            # to call the function 'pica_service' and the function will run at once in another thread, 
            # when the previous call of 'pica_service' is still not finished, 
            # it will not start until the previous call of 'pica_service' finished.
            simlecoin.submit_func(id='pica_service', pid=0)

# the function app.func('xxx') will create a new thread to run the function
@app.func('pica_service')
def pica_service(simlecoin):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    if not ica_processed:
        while True:
            if init_settings['is_finish'] == True or init_settings['node_max_ext_nums'][0] == 0 or init_settings['proc_len'] > init_settings['node_max_lens'][0]:
                del init_settings['node_max_lens'][0]
                del init_settings['node_max_ext_nums'][0]
                print('*** vnf pica processing finished!')
                simlecoin.sendto(pktutils.serialize_data(HEADER_INIT, init_settings),dst_ip_addr)
                ica_processed = True
                ica_buf.init()
                init_settings.update(DEF_INIT_SETTINGS)
                print('*** vnf pica processing finished!')
                break
            elif ica_buf.size() >= init_settings['proc_len']:
                if init_settings['proc_len'] == init_settings['m']:
                    print('*** vnf pica processing!')
                    icanetwork.fastica_nw(init_settings, ica_buf)
                    init_settings['is_finish'] = True
                else:
                    print('*** vnf pica processing!')
                    icanetwork.pica_nw(init_settings, ica_buf)
                    init_settings['node_max_ext_nums'][0] -= 1
                    if init_settings['proc_len'] > init_settings['m']:
                        init_settings['proc_len'] = init_settings['m']
            else:
                break



if __name__ == "__main__":
    app.run()
