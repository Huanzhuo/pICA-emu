# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-01
# @modify: 2021-04-01
# @desc. : [description]

import socket
from typing import Tuple

class SimpleUDP():
    def __init__(self,BUFFER_SIZE:int=4096) -> None:
        self.BUFFER_SIZE = BUFFER_SIZE
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sockets = {}
        pass

    def sendto(self,data:bytes,dst_addr:Tuple[str,int]):  
        self.client.sendto(data, dst_addr)
        

    def recvfrom(self,port:int):
        if port not in self.recv_sockets:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            _socket.bind(('',port))
            self.recv_sockets[port] = _socket
        return self.recv_sockets[port].recvfrom(self.BUFFER_SIZE)

    def close(self):
        self.client.close()
        for _socket in self.recv_sockets.keys():
            _socket.close()

    def parse_af_packet(self,af_packet:bytes,frame_len:int=0):
        if frame_len>14:
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


simpleudp = SimpleUDP()