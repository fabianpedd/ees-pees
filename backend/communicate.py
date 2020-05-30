import socket
import struct
import time
import numpy as np
from enum import Enum

import config
from webots import WebotState, WebotAction


class PacketError(Enum):
    UNITILIZED = -1
    NO_ERROR = 0
    SIZE = 1
    IP = 2
    COUNT = 3
    TIME = 4


class Packet(object):
    def __init__(self):
        self.buffer = None
        self.time_in = None
        self.error = PacketError.UNITILIZED

    @property
    def count(self):
        return struct.unpack('Q', self.buffer[0:8])[0]

    @property
    def time(self):
        return struct.unpack('d', self.buffer[8:16])[0]

    @property
    def success(self):
        if self.error == PacketError.UNITILIZED:
            return None
        elif self.error == PacketError.NO_ERROR:
            return True
        return False


class Com(object):
    def __init__(self):
        self.conf = config.WebotConfig()
        self.msg_cnt_in = 0
        self.msg_cnt_out = 1
        self.latency = None
        self.state = WebotState()
        self.packet = Packet()
        self.history = []
        self.sock = None

    def _set_sock(self):
        if self.sock is not None:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.conf.PACKET_SIZE)
        self.sock.bind((self.conf.IP, self.conf.BACKEND_PORT))

    def _update_history(self):
        self.history.append([self.packet.time, self.packet])

    def recv(self):
        self._set_sock()
        self.packet.buffer, addr = self.sock.recvfrom(self.conf.PACKET_SIZE)
        self.state.fill_from_buffer(self.packet.buffer, self.conf.DIST_VECS)

        ### TESTING START
        print("gps[0] ", end = '')
        print(self.state.gps_actual[0], end = '')
        print("  gps[1] ", end = '')
        print(self.state.gps_actual[1])

        # print(self.state.gps_actual[0])
        # print(self.state.gps_actual[1])
        ### TESTING END

        # if PACKET_SIZE < len(self.packet.buffer):
        #     print("ERROR: recv did not get full packet", len(self.packet.buffer))
        #     return
        #
        # if IP != addr[0]:
        #     print("ERROR: recv did from wrong address", addr)
        #     return
        #
        # if self.packet.count != self.packet.msg_cnt_in:
        #     print("ERROR: recv wrong msg count, is ", self.packet.count, " should ", self.packet.msg_cnt_in)
        #     self.packet.msg_cnt_in = self.packet.count
        #     return
        #
        # if abs(time.time() - self.packet.time) > TIME_OFFSET_ALLOWED:
        #     print("ERROR: recv time diff to big local ", time.time()," remote ",
        #           self.packet.time, " diff ", abs(time.time() - self.packet.time))
        #     return

    def send(self, action: WebotAction):
        self._set_sock()
        data = struct.pack('Qdff', self.msg_cnt_out, time.time(),
                           action.heading, action.speed)
        ret = self.sock.sendto(data, (self.conf.IP, self.conf.CONTROL_PORT))
        if ret == len(data):
            self.msg_cnt_out += 2
        else:
            print("ERROR: could not send message, is ", ret, " should ", len(data))
