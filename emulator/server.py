# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-05-05 20:17:33
# @modify: 2021-05-16 15:17:33
# @desc. : [description]

"""
Server for pica in network
all functions are similiar to vnf.py 
"""
import numpy as np
import time
from picautils.icanetwork import icanetwork
from picautils.icabuffer import ICABuffer
from picautils.packetutils import *
from picautils.pybss_testbed import pybss_tb
from simpleemu.simplecoin import SimpleCOIN
from simpleemu.simpleudp import simpleudp



IFCE_NAME, NODE_IP = simpleudp.get_local_ifce_ip('10.0.')
DEF_INIT_SETTINGS = {'is_finish': False, 'm': np.inf, 'W': None, 'proc_len': np.inf,
                     'proc_len_multiplier': 2, 'node_max_ext_nums': [np.inf], 'node_max_lens': [np.inf]}
init_settings = {}
init_settings.update(DEF_INIT_SETTINGS)
dst_ip_addr = None
ica_processed = False

ica_buf = ICABuffer(max_size=16e4)

app = SimpleCOIN(ifce_name=IFCE_NAME, n_func_process=1)


@app.main()
def main(simplecoin, af_packet: bytes):
    packet = simpleudp.parse_af_packet(af_packet)
    if packet['Protocol'] == 17 and packet['IP_src'] != NODE_IP:
        chunk = packet['Chunk']
        header = int(chunk[0])
        if header == HEADER_CLEAR_CACHE:
            print('*** server clearing cache!')
            simplecoin.submit_func(pid = 0, id='clear_cache')
        elif header == HEADER_INIT:
            print('*** server initializing!')
            simplecoin.submit_func(pid = 0, id='set_init_settings',
                                  args=(pickle.loads(chunk[1:]),))
        elif header == HEADER_DATA or header == HEADER_FINISH:
            simplecoin.submit_func(pid = 0,
                id='put_ica_buf', args=(pickle.loads(chunk[1:]),))
            if header == HEADER_FINISH:
                t = time.localtime()
                print('*** last_pkt:', time.strftime("%H:%M:%S", t))
                simplecoin.sendto(b'*** time server recv all  : ', ('10.0.0.12', 1000))
        else:
            pass


@app.func('clear_cache')
def clear_cache(simplecoin):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    ica_processed = False
    ica_buf.init()
    init_settings.update(DEF_INIT_SETTINGS)


@app.func('set_init_settings')
def set_init_settings(simplecoin, _init_settings):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    init_settings.update(_init_settings)
    if init_settings['is_finish'] == True:
        print('*** no further ica process on server!')
        simplecoin.sendto(b'*** time server ica finish: ', ('10.0.0.12', 1000))
        simplecoin.submit_func(pid=-1,id='evaluation')


@app.func('put_ica_buf')
def ica_buf_put(simplecoin, data):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    if ica_processed == False:
        ica_buf.put(data)
        if ica_buf.size() >= init_settings['m']:
            simplecoin.submit_func(pid=-1,id='fastica_service')


@app.func('fastica_service')
def fastica_service(simplecoin):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    if (not ica_processed) and ica_buf.size() >= init_settings['m']:
        print('*** server fastica processing!')
        icanetwork.fastica_nw(init_settings, ica_buf)
        init_settings['is_finish'] = True
        print('*** server fastica processing finished!')
        ica_processed = True
        simplecoin.sendto(b'finished', ('10.0.0.12', 1000))
        simplecoin.submit_func(pid=-1,id='evaluation')


@app.func('evaluation')
def evaluation(simplecoin):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    print('*** server separating the matrix X!')
    # print(ica_buf.size())
    if init_settings['W'] is not None and ica_buf.size() == init_settings['m']:
        W = init_settings['W']
        X = ica_buf.buffer
        hat_S = np.dot(W, X)
        S = np.load("S.npy")
        eval_db = pybss_tb.bss_evaluation(S, hat_S, 'psnr')
        print('*** server separation eval:', eval_db)
        ica_buf.init()
        init_settings.update(DEF_INIT_SETTINGS)


if __name__ == "__main__":
    app.run()
