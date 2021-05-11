# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-05-05 20:41:14
# @modify: 2021-05-05 20:41:14
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

app = SimpleCOIN(ifce_name=IFCE_NAME)

# main function for processing the data
# af_packet is the raw af_packet from the socket
@app.main()
def main(af_packet):
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
            ica_processed = False
            ica_buf.init()
            init_settings.update(DEF_INIT_SETTINGS)
            print('*** vnf transmiting clearing message to next node!')
            app.forward(af_packet)
        elif header == HEADER_INIT:
            init_settings.update(pickle.loads(chunk[1:]))
            if init_settings['is_finish'] == False:
                print('*** vnf initializing!')
                dst_ip_addr = (packet['IP_dst'],packet['Port_dst'])
            else:
                print('*** vnf transmit init_settings!')
                app.forward(af_packet)
        elif header == HEADER_DATA or header == HEADER_FINISH:
            if ica_processed == False:
                ica_buf.put(pickle.loads(chunk[1:]))
                # to call the function 'pica_service' and the function will run at once in another thread, 
                # when the previous call of 'pica_service' is still not finished, 
                # it will not start until the previous call of 'pica_service' finished.
                app.call_func('pica_service')
            app.forward(af_packet)
        else:
            app.forward(af_packet)

# the function app.func('xxx') will create a new thread to run the function
@app.func('pica_service')
def pica_service():
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    if not ica_processed:
        if init_settings['is_finish'] == True or init_settings['node_max_ext_nums'][0] == 0 or init_settings['proc_len'] > init_settings['node_max_lens'][0]:
            del init_settings['node_max_lens'][0]
            del init_settings['node_max_ext_nums'][0]
            print('*** vnf pica processing finished!')
            app.sendto(pktutils.serialize_data(HEADER_INIT, init_settings),dst_ip_addr)
            ica_processed = True
            ica_buf.init()
            init_settings.update(DEF_INIT_SETTINGS)
            print('*** vnf pica processing finished!')
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
            app.call_func('pica_service')


if __name__ == "__main__":
    app.run()
