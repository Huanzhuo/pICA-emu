# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-25
# @modify: 2021-05-16
# @desc. : SimpleCOIN 3.0


import socket
import multiprocessing
from typing import Any, Callable, Tuple
import time


class SimpleCIONUtils():
    # Parse the UDP packet
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



# Simple Computing In Network Framework



class SimpleCOIN(SimpleCIONUtils):
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

    # Interprocess communication
    class IPC(SimpleCIONUtils):
        def __init__(self, send_queue: multiprocessing.Queue, func_map: dict, func_params_queues: list):
            self.send_queue = send_queue
            self.func_params_queues = func_params_queues
            self.func_map = func_map

        def submit_func(self, id: Any, pid: int = 0, args = (), kwargs = {}):
            if id in self.func_map:
                self.func_params_queues[pid].put((id, args, kwargs), block=False)

        def forward(self, af_packet: bytes):
            self.send_queue.put(('raw', af_packet, None), block=False)

        def sendto(self, data: bytes, dst_addr: Tuple[str, int]):
            self.send_queue.put(('udp', data, dst_addr), block=False)

    # The body
    def __init__(self, ifce_name: str, buffer_size: int = 1500, chunk_gap: int = 0.0005, n_func_process: int = 1):
        # Network Device Settings
        self.CHUNK_GAP = chunk_gap
        self.buffer_size = buffer_size
        self.buf = bytearray(self.buffer_size)
        self.af_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
        self.af_socket.bind((ifce_name, 0))
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Network Service and User Defined Packet Processing Program
        self.main_processing = None
        self.func_map = {}
        self.recv_queue = multiprocessing.Queue()
        self.send_queue = multiprocessing.Queue()
        if n_func_process > 0:
            self.func_params_queues = [multiprocessing.Queue()] * n_func_process
        else:
            raise ValueError('The value of n_func_process must bigger than 0.')
        # Recv and Send Service
        self.process_send_loop = multiprocessing.Process(target=self.__send_loop, args=(self.send_queue,))
        self.process_recv_loop = multiprocessing.Process(target=self.__recv_loop, args=(self.recv_queue,))
        # User Defined Main Processing PRogram
        self.process_main_loop = multiprocessing.Process(target=self.__main_loop, args=(self.recv_queue, self.send_queue, self.func_map, self.func_params_queues,))
        # User Defined Muti-processing Program
        self.process_func_loops = []
        for func_params_queue in self.func_params_queues:
            self.process_func_loops.append(multiprocessing.Process(target=self.__func_loop, args=(self.send_queue, self.func_map, func_params_queue, self.func_params_queues,)))

    def main(self):
        def decorator(func: Callable):
            self.main_processing = func
            return func
        return decorator

    def func(self, id: Any):
        def decorator(func: Callable):
            if id in self.func_map:
                raise ValueError(
                    'The function id with the same name already exists!')
            self.func_map[id] = func
            return func
        return decorator

    def __send_loop(self, send_queue: multiprocessing.Queue):
        time_packet_sent = 0
        while True:
            typ, data, dst_addr = send_queue.get()
            time.sleep(max(0, time_packet_sent+self.CHUNK_GAP-time.time()))
            if typ == 'raw':
                self.af_socket.send(data)
            elif typ == 'udp':
                self.client.sendto(data, dst_addr)
            time_packet_sent = time.time()

    def __recv_loop(self, recv_queue: multiprocessing.Queue):
        while True:
            frame_len = self.af_socket.recv_into(self.buf, self.buffer_size)
            recv_queue.put(self.buf[:frame_len], block=False)

    def __main_loop(self, recv_queue: multiprocessing.Queue, send_queue: multiprocessing.Queue, func_map: dict, func_params_queues: list):
        ipc = SimpleCOIN.IPC(send_queue, func_map, func_params_queues)
        while True:
            self.main_processing(ipc, recv_queue.get())

    def __func_loop(self, send_queue: multiprocessing.Queue, func_map: dict, func_params_queue: multiprocessing.Queue, func_params_queues: list):
        ipc = SimpleCOIN.IPC(send_queue, func_map, func_params_queues)
        while True:
            id, args, kwargs = func_params_queue.get()
            func = self.func_map[id]
            func(ipc, *args, **kwargs)

    def run(self):
        if self.main_processing is not None:
            self.process_send_loop.start()
            self.process_main_loop.start()
            for process_func_loop in self.process_func_loops:
                process_func_loop.start()
            self.process_recv_loop.start()
            print('///////////////////////////////////////////////\n')

            print('*** SimpleCOIN v3.0 Framework is running !')
            print('*** press enter to exit')
            print('-----------------------------------------------')
            input()
            print('*** SimpleCOIN try to shut down ...')
            self.terminate()
        else:
            raise ValueError('The @main function is not defined!')

    def terminate(self):
        self.process_recv_loop.terminate()
        for process_func_loop in self.process_func_loops:
            process_func_loop.terminate()
        self.process_main_loop.terminate()
        self.process_send_loop.terminate()
        self.af_socket.close()
        self.client.close()