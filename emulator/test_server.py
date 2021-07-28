# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-05-05 20:41:14
# @modify: 2021-05-16 15:41:14
# @desc. : [description]


"""
Forwarding VNF via packet socket.
"""

import numpy as np
import pickle
import time
from picautils.test_icanetwork import icanetwork
from picautils.icabuffer import ICABuffer
from picautils.packetutils import *
from simpleemu.simplecoin import SimpleCOIN
from simpleemu.simpleudp import simpleudp
# from measurement.measure import measure_write, measure_arr_to_jsonstr, measure_jsonstr_to_arr
from test_settings import *

EVALS = []
EVAL_W = None
process_time = 0

IFCE_NAME, NODE_IP = simpleudp.get_local_ifce_ip('10.0.')
DEF_INIT_SETTINGS = {'is_finish': False, 'm': np.inf, 'W': None, 'proc_len': np.inf,
                     'proc_len_multiplier': 2, 'node_max_ext_nums': [np.inf]}
init_settings = {}
init_settings.update(DEF_INIT_SETTINGS)
dst_ip_addr = None
ica_processed = False

ica_buf = ICABuffer(max_size=(4, 160000))

app = SimpleCOIN(ifce_name=IFCE_NAME, n_func_process=1, lightweight_mode=test_server_settings['lite_mode'])

EVAL_MODE = None

# main function for processing the data
# af_packet is the raw af_packet from the socket
@app.main()
def main(simplecoin: SimpleCOIN.IPC, af_packet: bytes):
    global EVAL_MODE
    # parse the raw packet to get the ip/udp infomations like ip, port, protocol, data
    packet = simpleudp.parse_af_packet(af_packet)
    # if prorocol is 17, that means is udp
    if packet['Protocol'] == 17 and packet['IP_src'] != NODE_IP:
        # the 1st byte is header other bytes are datas (here is "chunk")
        chunk = packet['Chunk']
        header = int(chunk[0])
        if header == HEADER_CLEAR_CACHE:
            print('*** vnf clearing cache!')
            simplecoin.submit_func(pid=0, id='clear_cache')
            print('*** vnf transmiting clearing message to next node!')
            simplecoin.forward(af_packet)
        elif header == HEADER_INIT:
            init_settings.update(pickle.loads(chunk[1:]))
            if init_settings['is_finish'] == False:
                print('*** vnf initializing!')
                simplecoin.submit_func(pid=0, id='set_init_settings', args=(
                    init_settings, (packet['IP_dst'], packet['Port_dst']),))
            else:
                print('*** vnf transmit init_settings!')
                simplecoin.forward(af_packet)
                simplecoin.submit_func(pid=0, id='measure@time_start')
            EVAL_MODE = init_settings['mode']
        elif header == HEADER_DATA or header == HEADER_FINISH:
            # ####################################
            # simplecoin.sendto(chunk,(packet['IP_dst'], packet['Port_dst']))
            simplecoin.forward(af_packet)
            # ####################################
            simplecoin.submit_func(
                pid=0, id='put_ica_buf', args=(pickle.loads(chunk[1:]),))
            if header == HEADER_FINISH:
                t = time.localtime()
                print('*** last_pkt:', time.strftime("%H:%M:%S", t))
                simplecoin.sendto(b'### time server recv all  : ', ('10.0.0.12', 1000))
            
        elif header == HEADER_EVAL:
            simplecoin.submit_func(pid=0, id='measure@write_results', args=(
                EVAL_MODE, init_settings['W'],af_packet))
            
        else:
            # simplecoin.forward(af_packet)
            pass


@app.func('measure@time_start')
def rec_time_start(simplecoin: SimpleCOIN.IPC):
    global EVALS
    EVALS += ['time_no_compute', time.time()]


@app.func('measure@write_results')
def write_results(simplecoin: SimpleCOIN.IPC, EVAL_MODE, W, af_packet):
    global EVALS
    # Measurements write.
    if EVALS[0] != 'time_no_compute':
        V = EVALS[-1].copy()
        del EVALS[-1]
        rec_num = len(EVALS)//4
        for i in range(rec_num):
            W = measure_jsonstr_to_arr(EVALS[int(4*i+3)])
            EVALS[int(4*i+3)] = measure_arr_to_jsonstr(np.dot(W,V))
        process_time = float(EVALS[-3]) - float(EVALS[1])
        EVALS = ['process_time', process_time] + EVALS

    print('*** write reults')
    if len(EVALS) <= 2:
        EVALS += ['matrix_w', measure_arr_to_jsonstr(W)]
        EVALS = ['process_time', 0] + EVALS
    EVALS = ['rec_'+IFCE_NAME,] + EVALS
    measure_write('rec_intermediate_ws_all', EVALS)
    simplecoin.forward(af_packet)


@app.func('clear_cache')
def clear_cache(simplecoin: SimpleCOIN.IPC):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed, EVALS
    EVALS = []
    ica_processed = False
    ica_buf.init()
    init_settings.update(DEF_INIT_SETTINGS)


@app.func('set_init_settings')
def set_init_settings(simplecoin: SimpleCOIN.IPC, _init_settings, _dst_ip_addr):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed, EVALS
    init_settings.update(_init_settings)
    dst_ip_addr = _dst_ip_addr
    if init_settings['is_finish'] == True:
        print('*** no further ica process on server!')
        simplecoin.sendto(b'### time server ica finish: ', ('10.0.0.12', 1000))
    elif ica_buf.size() >= init_settings['m']:
        simplecoin.submit_func(pid=-1, id='pica_service')


@app.func('put_ica_buf')
def ica_buf_put(simplecoin: SimpleCOIN.IPC, data):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed
    if ica_processed == False:
        ica_buf.put(data)
        if ica_buf.size() >= init_settings['proc_len'] or ica_buf.size() >= init_settings['m']:
            simplecoin.submit_func(pid=-1, id='pica_service')


@app.func('pica_service')
def pica_service(simplecoin: SimpleCOIN.IPC):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, ica_processed, EVALS
    if not ica_processed:
        while True:
            if init_settings['is_finish'] == True or init_settings['node_max_ext_nums'][0] == 0:
                del init_settings['node_max_ext_nums'][0]
                ica_processed = True
                ica_buf.init()
                init_settings.update(DEF_INIT_SETTINGS)
                print('*** server pica processing finished!')
                simplecoin.sendto(b'### time fastica finish: ', ('10.0.0.12', 1000))
                break
            elif ica_buf.size() >= init_settings['m']:
                print('*** server pica processing!')
                EVALS += icanetwork.fastica_nw(init_settings, ica_buf)
                init_settings['node_max_ext_nums'][0] -= 1
                init_settings['is_finish'] = True
            else:
                break


if __name__ == "__main__":
    app.run()
