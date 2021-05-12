# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-05-05 20:17:33
# @modify: 2021-05-05 20:17:33
# @desc. : [description]

"""
Server for pica in network
all functions are similiar to vnf.py 
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
        if len(paragraph) > 6 and len(paragraph[0]) > 1:
            ifce_name = paragraph[0][:-1].decode("utf-8")
            ip = paragraph[5].decode("utf-8")
            if ip_telegram in ip:
                return ifce_name, ip
    raise ValueError('ip not detected!')


IFCE_NAME, NODE_IP = get_addr('10.0.')
DEF_INIT_SETTINGS = {'is_finish': False, 'm': np.inf, 'W': None, 'proc_len': np.inf,
                     'proc_len_multiplier': 2, 'node_max_ext_nums': [np.inf], 'node_max_lens': [np.inf]}
init_settings = {}
init_settings.update(DEF_INIT_SETTINGS)
dst_ip_addr = None
ica_processed = False

ica_buf = ICABuffer(max_size=16e4)

app = SimpleCOIN(ifce_name=IFCE_NAME)


@app.main()
def main(af_packet):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    packet = app.parse_af_packet(af_packet)
    if packet['Protocol'] == 17 and packet['IP_src'] != NODE_IP:
        chunk = packet['Chunk']
        header = int(chunk[0])
        if header == HEADER_CLEAR_CACHE:
            print('*** server clearing cache!')
            ica_processed = False
            ica_buf.init()
            init_settings.update(DEF_INIT_SETTINGS)
        elif header == HEADER_INIT:
            print('*** server initializing!')
            init_settings.update(pickle.loads(chunk[1:]))
            if init_settings['is_finish'] == True:
                print('*** no further ica process on server!')
                app.call_func('evaluation')
        elif header == HEADER_DATA or header == HEADER_FINISH:
            if ica_processed == False:
                ica_buf.put(pickle.loads(chunk[1:]))
                app.call_func('fastica_service')
        else:
            pass


@app.func('fastica_service')
def pica_service():
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    if not ica_processed:
        if ica_buf.size() >= init_settings['m']:
            print('*** server fastica processing!')
            icanetwork.fastica_nw(init_settings, ica_buf)
            init_settings['is_finish'] = True
            print('*** server fastica processing finished!')
            ica_processed = True
            app.call_func('evaluation')


@app.func('evaluation')
def evaluation():
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    print('*** server separating the matrix X!')
    W = init_settings['W']
    X = ica_buf.buffer
    hat_S = np.dot(W, X)
    S = np.load("S.npy")
    eval_db = pybss_tb.bss_evaluation(S, hat_S, 'psnr')
    print('*** server separation eval:', eval_db)
    ica_buf.init()
    init_settings.update(DEF_INIT_SETTINGS)
    app.sendto(b'finished',('10.0.0.12',1000))


if __name__ == "__main__":
    app.run()
