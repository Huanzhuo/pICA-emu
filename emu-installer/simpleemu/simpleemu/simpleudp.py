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

    # send udp packet
    def sendto(self,data:bytes,dst_addr:Tuple[str,int]):  
        self.client.sendto(data, dst_addr)
        
    # recv udp packet
    def recvfrom(self,port:int):
        if port not in self.recv_sockets:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            _socket.bind(('',port))
            self.recv_sockets[port] = _socket
        dst_addr, data =  self.recv_sockets[port].recvfrom(self.BUFFER_SIZE)
        return dst_addr, data

    # close the socket
    def close(self):
        self.client.close()
        for _socket in self.recv_sockets.keys():
            _socket.close()

    # parse the udp raw packet
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

    # get ifce name and node ip automatically
    def get_local_ifce_ip(self, ip_prefix: str):
        from subprocess import Popen, PIPE
        ifconfig_output = Popen('ifconfig', stdout=PIPE).stdout.read()
        for paragraph in ifconfig_output.split(b'\n\n'):
            paragraph = paragraph.split()
            if len(paragraph)>6 and len(paragraph[0])>1:
                ifce_name = paragraph[0][:-1].decode("utf-8")
                ip = paragraph[5].decode("utf-8")
                if ip_prefix in ip:
                    return ifce_name,ip
        raise ValueError('ip not detected!')

simpleudp = SimpleUDP()