# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-25
# @modify: 2021-04-25
# @desc. : [description]

import numpy as np
import pickle

# HEADER DEF
HEADER_INIT = 4
HEADER_DATA = 5
HEADER_FINISH = 6
HEADER_CLEAR_CACHE = 7
HEADER_EVAL = 10
HEADER_MID_RES = 12

MTU = 1500 - 1 - 14

class PacketUtils():
    def serialize_data(self, header, data=None):
        byte_arr = pickle.dumps(data,protocol=-1)
        if len(byte_arr) >= MTU:
            raise ValueError('package size is bigger than MTU !')
        return bytes([header])+pickle.dumps(data,protocol=-1)

    def _get_substream_chunks(self, substream_arr):
        chunks_arr = []
        for substream in substream_arr:
            chunks_arr += [self.serialize_data(HEADER_DATA, substream)]
        chunks_arr[-1] = bytes([HEADER_FINISH]) + chunks_arr[-1][1:]
        return chunks_arr

    def _get_substream_arr(self, X, m_substream, dtype=np.float16):
        n, m = np.shape(X)
        X = X.astype(dtype)
        substream_num = int(np.ceil(m/m_substream))
        return [X[:, i*m_substream:(i+1)*m_substream] for i in range(substream_num)]

    def get_chunks(self, init_settings, X, m_substream, dtype=np.float16):
        chunks_arr = [self.serialize_data(HEADER_INIT, init_settings)]
        substream_arr = self._get_substream_arr(X, m_substream, dtype)
        chunks_arr += self._get_substream_chunks(substream_arr)
        return chunks_arr

pktutils = PacketUtils()