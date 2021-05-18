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
        self.max_size = max_size
        self.buffer = None
        self.lock = threading.Lock()

    def init(self):
        self.lock.acquire()
        self.buffer = None
        self.lock.release()

    def clear_buffer(self):
        self.lock.acquire()
        self.buffer = None
        self.lock.release()

    def put(self, x):
        self.lock.acquire()
        if self.buffer is None:
            self.buffer = x
        else:
            self.buffer = np.concatenate([self.buffer, x], axis=1)
        self.lock.release()

    def extract_n(self, n):
        self.lock.acquire()
        out = self.buffer[:, :int(n)]
        self.lock.release()
        return out

    def size(self):
        self.lock.acquire()
        if self.buffer is None:
            out = 0
        else:
            out = np.shape(self.buffer)[1]
        self.lock.release()
        return out