import subprocess
import socket
import struct
import time
import numpy as np
from enum import IntEnum
import psutil

from Config import WebotConfig
import utils


class FunctionCode(IntEnum):
    UNDEFINED = -1
    NO_FUNCTION = 0
    START = 1
    RESET = 2
    CLOSE = 3


class ReturnCode(IntEnum):
    UNDEFINED = -1
    SUCCESS = 0
    ERROR = 1


class WebotCtrl():
    def __init__(self, config: WebotConfig = WebotConfig()):
        self.config = config
        self.sock = None
        self.client_sock = None
        self.address = None
        self.return_code = ReturnCode.SUCCESS

    def init(self):
        self.compile_program()
        self.start_program()
        self.establish_connection()

    def close(self):
        self.close_connection()
        self.close_program()

    def is_program_started(self):
        # check if there is a process with the name "webots-bin" running
        return "webots-bin" in (p.name() for p in psutil.process_iter())

    def compile_program(self):
        self.close_program()
        # clean both controllers in webots
        subprocess.call(["make", "clean"], cwd="../webots/controllers/supervisor")
        subprocess.call(["make", "clean"], cwd="../webots/controllers/internal")
        # compile both controllers in webots
        subprocess.call(["make", "all"], cwd="../webots/controllers/supervisor")
        subprocess.call(["make", "all"], cwd="../webots/controllers/internal")

    def start_program(self):
        if self.is_program_started() is False:
            # start webots with the path of the world as argument
            subprocess.Popen(["webots", "../webots/worlds/training_env.wbt"])

    def close_program(self):
        if self.is_program_started() is True:
            # kill webots process
            subprocess.call(["pkill", "webots-bin"])

    def establish_connection(self):
        # start tcp connection to Webot Supervisor
        if self.sock is not None:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # reuse socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set buffer size to packet size to store only latest package
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,
                             self.config.PACKET_SIZE_S)
        # return self.sock.connect((self.config.IP, self.config.PORT))
        self.sock.bind((self.config.IP_S, self.config.PORT_S))
        self.sock.listen(5)
        print("Accepting on Port: ", self.config.PORT_S)
        (self.client_sock, self.address) = self.sock.accept()
        # print("Accepting done")
        # data = struct.pack('iiiii', 0, 1, 2, 3, 4)
        # self.client_sock.send(data)

    def close_connection(self):
        # close tcp connection to webot supervisor
        self.sock.close()

    def start_env(self, seed=None, waiting_time=1):
        if seed is None:
            seed = utils.set_random_seed()
        print("HI PETER")
        print(seed)
        print(self.config.world_scaling)
        data = struct.pack('iiiiif',
                           FunctionCode.START,
                           seed,
                           int(self.config.fast_simulation),
                           self.config.num_obstacles,
                           self.config.world_size,
                           self.config.world_scaling)
        self.client_sock.send(data)
        time.sleep(waiting_time)
        self.get_metadata()

    def get_metadata(self):
        buffer = self.client_sock.recv(self.config.PACKET_SIZE_S)
        self.return_code = struct.unpack('i', buffer[0:4])[0]
        self.config.sim_time_step = struct.unpack('i', buffer[4:8])[0]
        self.config.gps_target = struct.unpack('2f', buffer[8:16])[0]

    def reset_environment(self):
        # environment sollte sein wie beim start der simulation
        data = struct.pack('iiiii', FunctionCode.RESET, 0, 0, 0, 0)
        self.client_sock.send(data)

    def close_environment(self):
        # environment sollte sein wie beim start der simulation
        data = struct.pack('iiiii', FunctionCode.CLOSE, 0, 0, 0, 0)
        self.client_sock.send(data)

    def print(self):
        print("===== WebotCtrl =====")
        print("return_code", self.return_code)
        print("target", self.config.gps_target)
        print("sim_time_step", self.sim_time_step)
        print("=====================")


class ExtCtrl():
    def init(self):
        self.compile()
        self.start()

    def compile(self):
        self.close()
        subprocess.call(["make", "clean"], cwd="../controller")
        subprocess.call(["make", "all"], cwd="../controller")

    def start(self):
        subprocess.Popen(["../controller/build/controller"])

    def close(self):
        subprocess.call(["pkill", "controller"])
