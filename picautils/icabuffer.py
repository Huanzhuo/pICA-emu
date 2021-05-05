# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-02
# @modify: 2021-04-02
# @desc. : [description]

import numpy as np
import threading

class ICABuffer():
    def __init__(self, max_size):
        self.max_size = max_size
        self.ack_n = 0
        self.buffer = None
        self.lock = threading.Lock()

    def init(self):
        self.lock.acquire()
        self.ack_n = 0
        self.buffer = None
        self.lock.release()

    def clear_buffer(self):
        self.lock.acquire()
        self.buffer = None
        self.lock.release()

    def put(self, x):
        self.lock.acquire()
        self.ack_n += np.shape(x)[1]
        if self.buffer is None:
            self.buffer = x
        else:
            if np.shape(self.buffer)[1] < self.max_size:
                self.buffer = np.concatenate([self.buffer, x], axis=1)
        if np.shape(self.buffer)[1] > self.max_size:
            self.buffer = self.buffer[:, :self.max_size]
        self.lock.release()

    def extract_n(self, n):
        self.lock.acquire()
        m = np.shape(self.buffer)[1]
        mid_ack_n = self.ack_n - m // 2
        proc_indexs = np.linspace(0, m, n, endpoint=False, dtype=np.int)
        out = self.buffer[:, proc_indexs]
        self.lock.release()
        return mid_ack_n, out.astype(np.float64)

    def size(self):
        self.lock.acquire()
        if self.buffer is None:
            out = 0
        else:
            out = np.shape(self.buffer)[1]
        self.lock.release()
        return out