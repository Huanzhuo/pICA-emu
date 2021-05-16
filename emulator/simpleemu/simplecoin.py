# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-25
# @modify: 2021-05-16
# @desc. : SimpleCOIN 3.1


import socket
import multiprocessing
from typing import Any, Callable, Tuple
import time



# Simple Computing In Network Framework



class SimpleCOIN():
    """
    ### Description:

    1. Structure of the SimpleCOIN:

        recv_process --> main_process --> func_process, func_process, ...
                            |                         |
                            ∨                         ∨
        send_process <-- -- -- <-- -- -- <-- -- -- <-- 

        The SimpleCOIN is a mutliproccessing framework, it includes a
        process for receving data, a process for sending data, a process
        for main contol function (user defined) and N processes for 
        running user defined functions.

    2. Details of recv_process:

        recv_process:

            network -----------> recv_queue.put()
               ∧     af_packet       |      
               |                     ∨
                <--------------------      

        Once received af_packet from network it will immediately put it
        to the `recv_queue`, which is also used by main_process

    3. Details of main_process:

        main_process:

            recv_queue.get() -----------> main(simplecoin, afpacket)
               ∧              af_packet            |      
               |                                   ∨
                <----------------------------------  

        Once the recv_queue has values, the main function will immediately
        run with the paramters form the `recv_queue`, i.e. the af_apcket. The
        main function can be defined by `@app.main()`.

    4. Details of func_process:

        func_process:

            simplecoin.submit_func(id,pid,args,kwargs)
                    |                  
                    |function, process_id, args, kwargs
                    ∨
            func_params_queue[process_id].put()

            func_params_queue[process_id=0,1,2,...,n_func_process].get()
                    |                                          ∧
                    |function, process_id, args, kwargs        |
                    ∨                                          |
            function(args, kwargs) ----------------------------
        
        User can use `simplecoin.submit_func(id,pid,args,kwargs)` to put 
        the data into the `func_params_queue[process_id]`. Once the 
        `func_params_queue[process_id]` has values, the func_process 
        will fun the `function(args, kwargs)` immediately.

    ### Getting Started:

    1. Initialization the SimpleCOIN Framework:

        Firstly, SimpleCOIN needs to be initialized at the beginning 
        of the program, just like some web application framework. 

        ```
        app = SimpleCOIN(ifce_name: str, mtu: int = 1500, 
                chunk_gap: int = 0.0004, n_func_process: int = 1)
        ````

            ifce_name: is the network interface name, which is used to 
                receive raw packet from the network device. 

            mtu: is the value of the MTU.

            chunk_gap: is the time interval for sending data.

            n_func_process: is the number of processes to run 'user 
                defined functions', which are the functions defined by 
                `@app.func(id)`. These 'user defined functions' runs 
                one by one in one particular process when they submitted
                by `simpcoin.submit(id,pid,args,keargs)`. And the value 
                of `pid` is the process id, the value should be an integer 
                in the interval [0,n_func_process).

    2. Define the main processing function:

        ```
        @app.main
        def user_defined_function(simplecoin:SimpleCOIN.IPC, af_packet:bytes):
        ````

            # call user defined function, where pid is the id of `func_prcess`
            simplecoin.submit(id:Any,pid:int,args,kwargs)

            # forward the raw packet
            simplecoin.forward(af_packet:bytes)

            # send data by udp
            simplecoin.sendto(data:bytes,dst_addr:Tuple[str,int])

        The first argument of the `user_defined_function` must be reserved for 
        `simplecoin:SimpleCOIN.IPC`, which is a Interprocess Communication 
        Framework and has several important function for calling function and
        networking. The `af_apcket` is the raw packet received from the nework
        device.

    3. Define the user defined function:

        ```
        @app.func(id:Any)
        def user_defined_function(simplecoin:SimpleCOIN.IPC, *args,**kwargs)
            pass
        ```
        The first argument of the `user_defined_function` must be reserved for 
        `simplecoin:SimpleCOIN.IPC`, which is a Interprocess Communication 
        Framework and has several important function for calling function and
        networking.

    """

    # Interprocess communication
    class IPC():
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
    def __init__(self, ifce_name: str, mtu: int = 1500, chunk_gap: int = 0.0004, n_func_process: int = 1):
        # Network Device Settings
        self.CHUNK_GAP = chunk_gap
        self.buffer_size = mtu
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
        while True:
            typ, data, dst_addr = send_queue.get()
            if typ == 'raw':
                self.af_socket.send(data)
            elif typ == 'udp':
                self.client.sendto(data, dst_addr)
            time.sleep(self.CHUNK_GAP)

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

            print('*** SimpleCOIN v3.1 Framework is running !')
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