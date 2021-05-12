# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-25
# @modify: 2021-04-25
# @desc. : [description]

import queue
import socket
import threading
from typing import Any, Callable, Tuple
import time



# Simple Computing In Network Framework



class SimpleCOIN():
    '''
    Usage:
        app = SimpleCOIN(IFCE_NAME:str, BUFFER_SIZE:int)

        @app.main
        def func(af_packet):
            pass

        @app.func(rule:Any)
        def func(*args,**kwargs)
            pass

        app.call_func(rule:Any,*args,**kwargs):
            pass

        app.forward(af_packet:bytes):
            pass

        app.sendto(data:bytes,dst_addr:Tuple[str,int]):
            pass

        app.run():
            pass

        app.exit():
            pass
    '''

    def __init__(self, ifce_name: str, buffer_size: int = 4096, chunk_gap: int = 0.0004):
        self.IS_RUNNIG = True
        self.CHUNK_GAP = chunk_gap
        self.time_packet_sent = 0
        # Network Device Settings
        self.ifce_name = ifce_name
        self.buffer_size = buffer_size
        self.buf = bytearray(self.buffer_size)
        self.af_socket = socket.socket(
            socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
        self.af_socket.bind((self.ifce_name, 0))
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_lock = threading.Lock()
        # Network Service and User Defined Packet Processing Program
        self.main_processing = None
        self.packet_queue = queue.Queue()
        self.thread_recv_loop = threading.Thread(
            target=self.__recv_loop, args=(self.packet_queue,))
        self.thread_main_loop = threading.Thread(
            target=self.__main_loop, args=(self.packet_queue,))
        # User Defined Muti-threading Program
        self.func_params_queue_map = {}
        self.thread_func_loops = []

    def parse_af_packet(self, af_packet: bytes, frame_len: int = 0):
        if frame_len > 14:
            af_packet = af_packet[:frame_len]
        packet = {}
        packet['Raw'] = af_packet
        data = af_packet[14:]
        packet['Protocol'] = data[9]
        packet['IP_src'] = '.'.join(
            map(str, [data[x] for x in range(12, 16)]))
        packet['IP_dst'] = '.'.join(
            map(str, [data[x] for x in range(16, 20)]))
        packet['Port_src'] = (data[20] << 8) + data[21]
        packet['Port_dst'] = (data[22] << 8) + data[23]
        packet['Chunk'] = data[28:]
        return packet

    def __send(self, send_func: Callable, *args, **kwargs):
        self.socket_lock.acquire()
        _chunk_gap = time.time() - self.time_packet_sent
        if _chunk_gap < self.CHUNK_GAP:
            time.sleep(self.CHUNK_GAP - _chunk_gap)
        send_func(*args, **kwargs)
        self.time_packet_sent = time.time()
        self.socket_lock.release()

    def forward(self, af_packet: bytes):
        self.__send(self.af_socket.send, af_packet)

    def sendto(self, data: bytes, dst_addr: Tuple[str, int]):
        self.__send(self.client.sendto, data, dst_addr)

    def main(self):
        def decorator(func):
            self.main_processing = func
            return func
        return decorator

    def func(self, id: Any):
        def decorator(func):
            if id in self.func_params_queue_map:
                raise ValueError(
                    'The function id with the same name already exists!')
            params_queue = queue.Queue()
            self.func_params_queue_map[id] = (func, params_queue)
            self.thread_func_loops.append(threading.Thread(
                target=self.__create_func_loop, args=(func, params_queue)))
            return func
        return decorator

    def call_func(self, id: Any, *args, **kwargs):
        if id in self.func_params_queue_map:
            _, params_queue = self.func_params_queue_map[id]
            params_queue.put((args, kwargs), block=False)

    def __recv_loop(self, packet_queue: queue.Queue):
        while(self.IS_RUNNIG):
            frame_len = self.af_socket.recv_into(self.buf, self.buffer_size)
            packet_queue.put(self.buf[:frame_len], block=False)

    def __main_loop(self, packet_queue: queue.Queue):
        while(self.IS_RUNNIG):
            self.main_processing(packet_queue.get())

    def __create_func_loop(self, func: Callable, params_queue: queue.Queue):
        while(self.IS_RUNNIG):
            args, kwargs = params_queue.get()
            func(*args, **kwargs)

    def run(self):
        if self.main_processing is not None:
            for thread_func_loop in self.thread_func_loops:
                thread_func_loop.start()
            self.thread_recv_loop.start()
            print('*** SimpleCOIN Framework is running !')
            self.thread_main_loop.run()
        else:
            raise ValueError('The @main function is not defined!')

    def __thread_join(self, thread: threading.Thread):
        if thread.is_alive():
            thread.join()

    def exit(self):
        self.IS_RUNNIG = False
        self.af_socket.close()
        for thread_func_loop in self.thread_func_loops:
            self.__thread_join(thread_func_loop)
        self.__thread_join(self.thread_recv_loop)
        self.__thread_join(self.thread_main_loop)
