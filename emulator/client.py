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
from picautils.packetutils import *
from picautils.pybss_testbed import pybss_tb
from simpleemu.simpleudp import simpleudp
import sys

# read wavs
n = 4
folder_address = '/volume/MIMII/mix_type'
S, A, X = pybss_tb.generate_matrix_S_A_X(
        folder_address, wav_range=10, source_number=n, mixing_type="normal", max_min=(1, 0.01), mu_sigma=(0, 1))
np.save("S.npy",S)
W = np.random.random_sample((n, n))

# settings
serverAddressPort   = ("10.0.0.15", 9999)
INIT_SETTINGS_ComputeForward = {'is_finish':False,'m':160000,'W':W,'proc_len':80,'proc_len_multiplier':2,'node_max_ext_nums':[4,4],'node_max_lens':[160000,160000]}
INIT_SETTINGS_StoreForward = {'is_finish':False,'m':160000,'W':W,'proc_len':80,'proc_len_multiplier':2,'node_max_ext_nums':[0,0],'node_max_lens':[160000,160000]}

if __name__ == "__main__":

    if len(sys.argv) == 1:
        INIT_SETTINGS = INIT_SETTINGS_ComputeForward
        print("*** Mode: Compute Forward")
    elif sys.argv[1] =='computefwd':
        INIT_SETTINGS = INIT_SETTINGS_ComputeForward
        print("*** Mode: Compute Forward")
    elif sys.argv[1] =='storefwd':
        INIT_SETTINGS = INIT_SETTINGS_StoreForward
        print("*** Mode: Store Forward")
    else:
        print("Invalid argument. The argument must be 'computefwd' or 'storefwd'.")

    chunk_arr = pktutils.get_chunks(init_settings=INIT_SETTINGS,X=X,m_substream=80,dtype=np.float32)

    # send clear cache command
    print(pktutils.serialize_data(HEADER_CLEAR_CACHE))
    simpleudp.sendto(pktutils.serialize_data(HEADER_CLEAR_CACHE),serverAddressPort)
    time.sleep(1)
    t = time.time()
    i = 0
    for chunk in chunk_arr:
        simpleudp.sendto(chunk, serverAddressPort)
        if i%200==0:
            print('packet:',i,', len:',len(chunk))
        i += 1
        time.sleep(0.001) #0.0005 maybe the smallest gap for this framework with no packet lost
    for i in range(2):
        print(simpleudp.recvfrom(1000))
        print('usd time:',time.time()-t)