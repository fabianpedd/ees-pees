class WebotConfig(object):

    def __init__(self):
        # -------------------------- General Settings  ------------------------
        self.direction_type = "heading"  # vs. "steering"
        self.reset_env_after = 1 * 10**4  # in sec
        self.DIST_VECS = 360
        self.wait_env_creation = 5  # in sec
        self.wait_env_reset = 2  # in sec
        self.send_recv_wait_time = 32  # in ms
        self.step_wait_time = 0  # in sec

        # ------------------------ External Controller ------------------------
        self.IP = "127.0.0.1"
        self.CONTROL_PORT = 6969
        self.BACKEND_PORT = 6970
        self.PACKET_SIZE = 1484
        self.TIME_OFFSET_ALLOWED = 1.0

        # ------------------------ Supervisor ------------------------
        # network settings
        self.IP_S = "127.0.0.1"
        self.PORT_S = 10201
        self.PACKET_SIZE_S = 16

        # setting for world generation via supervisor
        self.seed = None
        self.fast_simulation = False
        self.num_obstacles = 10
        self.world_size = 20
        self._world_scaling = 0.25  # meters: 20*0.25 -> 5m x 5m

        # (received) world metadata
        self.gps_target = None
        self.sim_time_step = 32  # ms

    def print(self):
        for (k, v) in self.__dict__.items():
            print(str(k) + "\t" + str(v))

    @property
    def world_scaling(self):
        return self._world_scaling

    @world_scaling.setter
    def world_scaling(self, value):
        if value < 0.25:
            raise ValueError("world_scaling must be larger or equal 0.25")
        self._world_scaling = value