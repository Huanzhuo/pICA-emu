# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-05-05 20:19:59
# @modify: 2021-05-05 20:19:59
# @desc. : [description]


"""
Client
generate and send udp packages
"""

import numpy as np
import time
import pickle
import sys
from picautils.packetutils import *
from picautils.pybss_testbed import pybss_tb
from simpleemu.simpleudp import simpleudp
from measurement.measure import measure_write

# read wavs
# n = 4
# l = 4
# m = l * 16000
# number of iteration rounds on every node
# delta = 2
# folder_address = '/volume/MIMII/mix_type'
# S, A, X = pybss_tb.generate_matrix_S_A_X(
#         folder_address, wav_range=10, source_number=n, mixing_type="normal", max_min=(1, 0.01), mu_sigma=(0, 1))
# #np.save("S.npy",S)
# W = np.random.random_sample((n, n))
# np.save("S.npy",S)
# np.save("X.npy",X)
# np.save("W.npy",W)
# S = np.load("S.npy")
# X = np.load("X.npy")
# W = np.load("W.npy")

# settings
W = np.load("W.npy")
serverAddressPort = ("10.0.0.15", 9999)
INIT_SETTINGS_pICA_enabled = {'is_finish': False, 'm': 160000, 'W': W, 'proc_len': 1280,
                              'proc_len_multiplier': 2, 'node_max_ext_nums': [1]*10, 'mode': 'cf'}
INIT_SETTINGS_pICA_disabled = {'is_finish': False, 'm': 160000, 'W': W, 'proc_len': 1280,
                               'proc_len_multiplier': 2, 'node_max_ext_nums': [0]*10, 'mode': 'sf'}

if __name__ == "__main__":
    n_test = 1
    if len(sys.argv) != 3:
        print("Invalid argument. The argument must be 'cf n_test' or 'sf n_test'.")
        sys.exit(1)

    if sys.argv[1] == 'cf':
        INIT_SETTINGS = INIT_SETTINGS_pICA_enabled
        print("*** Compute and Forward Mode: pICA enabled")
    elif sys.argv[1] == 'sf':
        INIT_SETTINGS = INIT_SETTINGS_pICA_disabled
        print("*** Store and Forward Mode: normal, pICA disabled")
    else:
        print("Invalid argument. The argument must be 'cf n_test' or 'sf n_test'.")
        sys.exit(1)

    n_test = int(sys.argv[2])

    print("*** N_test:", n_test)

    for i in range(n_test):
        print("*** no.:", i+1)
        fr = open('saxs.pkl', 'rb')
        saxs = pickle.load(fr)
        ss, aa, xx = saxs
        fr.close()
        S, A, X = ss[0], aa[0], xx[0]

        time.sleep(0.5)

        chunk_arr = pktutils.get_chunks(
            init_settings=INIT_SETTINGS, X=X, m_substream=80, dtype=np.float32)

        # send clear cache command
        print('*** send clear cache command')
        simpleudp.sendto(pktutils.serialize_data(
            HEADER_CLEAR_CACHE), serverAddressPort)
        time.sleep(1)
        print('*** send data')

        i = 0
        t = time.time()
        time_packet_sent = t
        for chunk in chunk_arr:
            time.sleep(max(0, time_packet_sent - time.time()))
            time_packet_sent += 0.003
            simpleudp.sendto(chunk, serverAddressPort)
            if i % 500 == 0:
                print('packet:', i, ', len:', len(chunk))
            i += 1
            # time.sleep(0.0016) #0.0005 maybe the smallest gap for this framework with no packet lost

        print('*** last_pkt:', time.strftime("%H:%M:%S", time.localtime()))
        print('*** time sent all pkg     : ', time.time()-t)
        print(simpleudp.recvfrom(1000)[0], time.time()-t)
        transmission_latency = time.time() - t
        print(simpleudp.recvfrom(1000)[0], time.time()-t)
        service_latency = time.time() - t
        measure_write('client_'+INIT_SETTINGS['mode'],
                      ['transmission_latency', transmission_latency, 'service_latency', service_latency])

        print('*** send write evaluation results command')
        simpleudp.sendto(pktutils.serialize_data(
            HEADER_EVAL), serverAddressPort)
        time.sleep(5)
