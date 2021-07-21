# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-02
# @modify: 2021-05-16
# @desc. : [description]

import numpy as np
import threading

class ICABuffer():
    def __init__(self, max_size):
        self.length = 0
        self.buffer = np.zeros(max_size, dtype=np.float32)
        self.lock = threading.Lock()

    def init(self):
        self.lock.acquire()
        self.length = 0
        self.lock.release()

    def clear_buffer(self):
        self.lock.acquire()
        self.length = 0
        self.buffer = np.zeros_like(self.buffer)
        self.lock.release()

    def put(self, x):
        self.lock.acquire()
        _size = self.length + x.shape[1]
        self.buffer[:,self.length:_size] = x
        self.length = _size
        self.lock.release()

    def extract_n(self, n):
        self.lock.acquire()
        out = self.buffer[:, :int(n)]
        self.lock.release()
        return out

    def size(self):
        return self.length