# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-05-05 20:41:14
# @modify: 2021-07-23 08:41:14
# @desc. : [description]


"""
Forwarding VNF via packet socket.
"""

import numpy as np
import pickle
import time
from picautils.icanetwork import icanetwork
from picautils.icabuffer import ICABuffer
from picautils.packetutils import *
from simpleemu.simplecoin import SimpleCOIN
from simpleemu.simpleudp import simpleudp
from measurement.measure import measure_write, measure_arr_to_jsonstr

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

app = SimpleCOIN(ifce_name=IFCE_NAME, n_func_process=1, lightweight_mode=True)

EVAL_MODE = None
PKTS = []

# main function for processing the data
# af_packet is the raw af_packet from the socket
@app.main()
def main(simplecoin, af_packet):
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
            print('*** vnf initializing!')
            simplecoin.submit_func(pid=0, id='set_init_settings', args=(
                init_settings, (packet['IP_dst'], packet['Port_dst']),))
            EVAL_MODE = init_settings['mode']
        elif header == HEADER_DATA or header == HEADER_FINISH:
            simplecoin.submit_func(
                pid=0, id='put_ica_buf', args=(pickle.loads(chunk[1:]),af_packet))
            if header == HEADER_FINISH:
                t = time.localtime()
                print('*** last_pkt:', time.strftime("%H:%M:%S", t))
        elif header == HEADER_EVAL:
            simplecoin.submit_func(pid=0, id='measure@write_results', args=(
                EVAL_MODE, init_settings['W']))
            simplecoin.forward(af_packet)
        else:
            # simplecoin.forward(af_packet)
            pass


@app.func('measure@time_start')
def rec_time_start(simplecoin: SimpleCOIN.IPC):
    global EVALS
    EVALS += ['time_start', time.time()]


@app.func('measure@write_results')
def write_results(simplecoin: SimpleCOIN.IPC, EVAL_MODE, W):
    global EVALS
    # Measurements write.
    EVALS = ['mode', EVAL_MODE] + EVALS
    print('*** write reults')
    if EVALS[1] == 'cf':
        if len(EVALS) <= 4:
            EVALS += ['matrix_w_pre', measure_arr_to_jsonstr(W), 'process_time', 0, 'matrix_w', measure_arr_to_jsonstr(W)]
        measure_write(IFCE_NAME+'_'+init_settings['mode'], EVALS)


@app.func('clear_cache')
def clear_cache(simplecoin):
    global DEF_INIT_SETTINGS, init_settings, EVALS, PKTS
    PKTS = []
    EVALS = []
    ica_buf.init()
    init_settings.update(DEF_INIT_SETTINGS)


@app.func('set_init_settings')
def set_init_settings(simplecoin, _init_settings, _dst_ip_addr):
    global init_settings, dst_ip_addr
    init_settings.update(_init_settings)
    dst_ip_addr = _dst_ip_addr
    if(ica_buf.size()>=init_settings['m']):
        simplecoin.submit_func(pid=-1, id='pica_service')

@app.func('put_ica_buf')
def ica_buf_put(simplecoin, data, af_packet):
    global PKTS
    ica_buf.put(data)
    PKTS.append(af_packet)
    if(ica_buf.size()>=init_settings['m'] and init_settings['W'] is not None):
        simplecoin.submit_func(pid=-1, id='pica_service')
# the function app.func('xxx') will create a new thread to run the function

@app.func('pica_service')
def pica_service(simplecoin):
    global DEF_INIT_SETTINGS, init_settings, dst_ip_addr, EVALS, PKTS
    while True:
        time_finish, time_start = 0, 0
        if init_settings['is_finish'] == True or init_settings['node_max_ext_nums'][0] == 0:
            del init_settings['node_max_ext_nums'][0]
            simplecoin.submit_func(pid=0, id='measure@time_start')
            break
        elif ica_buf.size() >= init_settings['proc_len']:
            W_pre = init_settings['W']
            print('*** vnf pica processing!')
            # Measurements begin.
            time_start = time.time()
            icanetwork.pica_nw(init_settings, ica_buf)
            time_finish = time.time()
            # Measurements end.
            # Measurements begin.
            EVALS += ['time_start', time_start, 'matrix_w_pre', measure_arr_to_jsonstr(W_pre),
                        'process_time', time_finish - time_start]
            EVALS += ['matrix_w',
                        measure_arr_to_jsonstr(init_settings['W'])]
            # Measurements end.
            init_settings['node_max_ext_nums'][0] -= 1
        elif ica_buf.size() >= init_settings['m']:
            W_pre = init_settings['W']
            print('*** vnf pica processing!')
            # Measurements begin.
            time_start = time.time()
            icanetwork.fastica_nw(init_settings, ica_buf)
            time_finish = time.time()
            # Measurements end.
            # Measurements begin.
            EVALS += ['time_start', time_start, 'matrix_w_pre', measure_arr_to_jsonstr(W_pre),
                        'process_time', time_finish - time_start]
            EVALS += ['matrix_w',
                        measure_arr_to_jsonstr(init_settings['W'])]
            # Measurements end.
            init_settings['node_max_ext_nums'][0] -= 1
            init_settings['is_finish'] = True
        else:
            break

    print('*** vnf pica processing finished!')
    print('*** vnf forwarding packets!')
    t = time.time()
    time_packet_sent = t
    for af_packet in PKTS:
        time.sleep(max(0, time_packet_sent - time.time()))
        time_packet_sent += 0.0015
        simplecoin.forward(af_packet)
    time.sleep(max(0, time_packet_sent - time.time()))
    simplecoin.sendto(pktutils.serialize_data(
        HEADER_INIT, init_settings), dst_ip_addr)
    print('*** vnf forwarding finished!')
    ica_buf.init()
    init_settings.update(DEF_INIT_SETTINGS)
if __name__ == "__main__":
    app.run()
