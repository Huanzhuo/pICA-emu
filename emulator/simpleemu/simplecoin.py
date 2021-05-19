# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-25
# @modify: 2021-05-19
# @desc. : SimpleCOIN 0.3.3


import socket
import multiprocessing as mp
from typing import Any, Callable, Tuple
import time
from functools import wraps


# Simple Computing In Network Framework


class SimpleCOIN():
    """
    ### Description:

    1. Structure of the SimpleCOIN:

                                                      |--(func_queues[0])--> func_process[0]|
        recv_process --(recv_queue)--> main_process --|--(func_queues[1])--> func_process[1]|----
                                           |          |--(...           )--> ...            |    |
                                           |                                                     |
                                           ∨                                                     ∨
        send_process <--(send_queue)------------------------------------------------------------- 

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

        `id` is the id of user defined functions, which is defined by 
        `@app.func(id:Any)`

        `pid = 0,1,2,...,n_func_process-1`, is the id of `func_process`. The 
        structure of `func_process` with id `pid` is shown as follows.

                                 ----------------------------------------------
                                |    simplecoin.submit_func(pid,id,args,kwargs)
                                |            |                  
        #in other processes  :  |            |user_function, pid, args, kwargs
                                |            ∨
                                |    func_params_queue[pid].put()
                                 ----------  |  -------------------------------
                                             |  
                                 ----------  v  -------------------------------
                                |    func_params_queue[pid].get() <--------
        #in func_process[pid]:  |            |                             ∧
                                |            |user_function, args, kwargs  |
                                |            ∨                             |
                                |    user_function(args, kwargs) ----------
                                 ----------------------------------------------

        The `user_function` is the function defined by `@app.func(id)` with the 
        same value of `id` as in `simplecoin.submit_func(pid,id,args,kwargs)`.
        User can use `simplecoin.submit_func(pid,id,args,kwargs)` to put 
        the data into the `func_params_queue[process_id]`. Once the 
        `func_params_queue[id]` has values, the func_process will run the 
        `user_function(args, kwargs)` immediately.

    ### Getting Started:

    1. Initialization the SimpleCOIN Framework:

        Firstly, SimpleCOIN needs to be initialized at the beginning 
        of the program, just like some web application framework. 

        ```
        app = SimpleCOIN(ifce_name: str, mtu: int = 1500, 
                chunk_gap: int = 0.0012, n_func_process: int = 1)
        ````

            ifce_name: is the network interface name, which is used to 
                receive raw packet from the network device. 

            mtu: is the value of the MTU.

            chunk_gap: is the time interval for sending data.

            n_func_process: is the number of processes to run 'user 
                defined functions', which are the functions defined by 
                `@app.func(id)`. These 'user defined functions' runs 
                one by one in one particular process when they submitted
                by `simpcoin.submit(pid,id,args,keargs)`. And the value 
                of `pid` is the process id, the value should be an integer 
                in the interval [0,n_func_process).

    2. Define the main processing function:

        ```
        @app.main
        def user_defined_function(simplecoin:SimpleCOIN.IPC, af_packet:bytes):

            # Call user defined function, where `pid` is the id of `func_prcess`.
            # When pid is `-1`, that means the function will run at the local
            # process. When the `pid` is in the interval [0,n_func_process), 
            # that means the submitted function will run in the `pid`-th 
            # `func_prcess`. The global value between different processes is
            # not shared.
            simplecoin.submit(pid:int,id:Any,args,kwargs)

            # Forward the raw packet
            simplecoin.forward(af_packet:bytes)

            # Send data by udp
            simplecoin.sendto(data:bytes,dst_addr:Tuple[str,int])

            pass
        ````

        The first argument of the `user_defined_function` must be reserved for 
        `simplecoin:SimpleCOIN.IPC`, which is a Interprocess Communication 
        Framework and has several important function for calling function and
        networking. The `af_apcket` is the raw packet received from the nework
        device.

    3. Define the user defined function:

        ```
        @app.func(id:Any)
        def user_defined_function(simplecoin:SimpleCOIN.IPC, *args,**kwargs)

            # Call user defined function, where `pid` is the id of `func_prcess`.
            # When pid is `-1`, that means the function will run at the local
            # process. When the `pid` is in the interval [0,n_func_process), 
            # that means the submitted function will run in the `pid`-th 
            # `func_prcess`. The global value between different processes is
            # not shared.
            simplecoin.submit(pid:int,id:Any,args,kwargs)

            # Forward the raw packet
            simplecoin.forward(af_packet:bytes)

            # Send data by udp
            simplecoin.sendto(data:bytes,dst_addr:Tuple[str,int])

            pass
        ```

        The first argument of the `user_defined_function` must be reserved for 
        `simplecoin:SimpleCOIN.IPC`, which is a Interprocess Communication 
        Framework and has several important function for calling function and
        networking.

    4. Run the SimpleCOIN Framework:

        ```
        if __name__ == "__main__":
        app.run()
        ```

    ### Example:

    program:

        ```
        import time
        from simpleemu.simplecoin import SimpleCOIN
        from simpleemu.simpleudp import simpleudp

        # network interface: 'vnf1-s1'
        # device ip: '10.0.0.13'

        n_submit = 0

        app = SimpleCOIN(ifce_name='vnf1-s1',n_func_process=2)

        @app.main()
        def main(simplecoin, af_packet):
            # parse the raw packet to get the ip/udp infomations like ip, port, protocol, data
            packet = simpleudp.parse_af_packet(af_packet)
            if packet['Protocol'] == 17 and packet['IP_src'] != '10.0.0.13':
                simplecoin.submit_func(pid=0,id='submit_count',args=('pid=0 @ main',))
                time.sleep(1)
                print('*** sleep 1s')
                simplecoin.submit_func(pid=1,id='submit_count',args=('pid=1 @ main',))
                time.sleep(1)
                print('*** sleep 1s')
                simplecoin.submit_func(pid=0,id='submit_count',args=('pid=0 @ main',))


        @app.func('submit_count')
        def submit_count(simplecoin, myvalue):
            global n_submit
            n_submit += 1
            print(myvalue, n_submit)
            if n_submit == 1:
                print('before submit in func')
                simplecoin.submit_func(pid=-1,id='submit_count',args=('pid=-1 @ func',))
                print('after submit in func')


        if __name__ == "__main__":
            app.run()

        ```

    output:

        ```
        pid=0 @ main 1
        before submit in func
        pid=-1 @ func 2
        after submit in func

        *** sleep 1s

        pid=1 @ main 1
        before submit in func
        pid=-1 @ func 2
        after submit in func

        *** sleep 1s

        pid=0 @ main 3

        ```

        When `pid=-1` the submitted function will run immediately in the
        local process, without put the parameters to the `func_params_queue`.
        The global valves between different processes are independent.

    """

    # Interprocess communication
    class IPC():

        def __init__(self, send_queue: mp.Queue, func_map: dict, func_params_queues: list):
            self.send_queue = send_queue
            self.func_params_queues = func_params_queues
            self.func_map = func_map

            class NameSpace():
                pass
            self.namespace = NameSpace()

        def shared_namespace(self):
            return self.namespace

        def submit_func(self, pid: int, id: Any, args=(), kwargs={}):
            if pid < 0:
                func = self.func_map[id]
                func(self, *args, **kwargs)
            elif id in self.func_map:
                self.func_params_queues[pid].put(
                    (id, args, kwargs), block=False)

        def forward(self, af_packet: bytes):
            self.send_queue.put(('raw', af_packet, None), block=False)

        def sendto(self, data: bytes, dst_addr: Tuple[str, int]):
            self.send_queue.put(('udp', data, dst_addr), block=False)

    # The body
    def __init__(self, ifce_name: str, mtu: int = 1500, chunk_gap: int = 0.0012, n_func_process: int = 1):
        # Network Device Settings
        self.CHUNK_GAP = chunk_gap
        self.buffer_size = mtu
        self.buf = bytearray(self.buffer_size)
        self.af_socket = socket.socket(
            socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
        self.af_socket.bind((ifce_name, 0))
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Network Service and User Defined Packet Processing Program
        self.main_processing = None
        self.func_init_processing = lambda ipc: None
        self.func_map = {}
        self.recv_queue = mp.Queue()
        self.send_queue = mp.Queue()
        if n_func_process > 0:
            self.func_params_queues = [
                mp.Queue() for _ in range(n_func_process)]
        else:
            raise ValueError('The value of n_func_process must bigger than 0.')
        # Recv and Send Service
        self.process_send_loop = mp.Process(
            target=self.__send_loop, args=(self.send_queue,))
        self.process_recv_loop = mp.Process(
            target=self.__recv_loop, args=(self.recv_queue,))
        # User Defined Main Processing PRogram
        self.process_main_loop = mp.Process(target=self.__main_loop, args=(
            self.recv_queue, self.send_queue, self.func_map, self.func_params_queues,))
        # User Defined Muti-processing Program
        self.process_func_loops = [mp.Process(target=self.__func_loop, args=(
            self.send_queue, self.func_map, self.func_params_queues, pid,)) for pid in range(n_func_process)]

    def main(self):
        def decorator(func: Callable):
            self.main_processing = func
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def func_init(self):
        def decorator(func: Callable):
            self.func_init_processing = func
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def func(self, id: Any):
        def decorator(func: Callable):
            if id in self.func_map:
                raise ValueError(
                    'The function id with the same name already exists!')
            self.func_map[id] = func
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def __send_loop(self, send_queue: mp.Queue):
        time_packet_sent = time.time()
        while True:
            time.sleep(max(0, time_packet_sent - time.time()))
            time_packet_sent += self.CHUNK_GAP
            if not send_queue.empty():
                typ, data, dst_addr = send_queue.get()
                if typ == 'raw':
                    self.af_socket.send(data)
                elif typ == 'udp':
                    self.client.sendto(data, dst_addr)

    def __recv_loop(self, recv_queue: mp.Queue):
        while True:
            frame_len = self.af_socket.recv_into(self.buf, self.buffer_size)
            recv_queue.put(self.buf[:frame_len], block=False)

    def __main_loop(self, recv_queue: mp.Queue, send_queue: mp.Queue, func_map: dict, func_params_queues: list):
        ipc = SimpleCOIN.IPC(send_queue, func_map, func_params_queues)
        while True:
            self.main_processing(ipc, recv_queue.get())

    def __func_loop(self, send_queue: mp.Queue, func_map: dict, func_params_queues: list, pid: int):
        ipc = SimpleCOIN.IPC(send_queue, func_map, func_params_queues)
        self.func_init_processing(ipc)
        while True:
            id, args, kwargs = func_params_queues[pid].get()
            func = self.func_map[id]
            func(ipc, *args, **kwargs)

    def run(self):
        if self.main_processing is not None:
            self.process_send_loop.start()
            self.process_main_loop.start()
            for process_func_loop in self.process_func_loops:
                process_func_loop.start()
            self.process_recv_loop.start()
            print('\n///////////////////////////////////////////////\n')

            print('*** SimpleCOIN v0.3.3 Framework is running !')
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
