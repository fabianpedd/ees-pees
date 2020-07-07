import numpy as np
import gym
import time

import webotsgym.utils as utils
from webotsgym.config import WbtConfig

from webotsgym.env.action import WbtActContinuous
from webotsgym.env.webot.observation import WbtObs
from webotsgym.env.reward import WbtReward
from webotsgym.com import WbtCtrl, Communication


class WbtGym(gym.Env):
    def __init__(self,
                 seed=None,
                 gps_target=(1, 1),
                 train=False,
                 action_class=WbtActContinuous,
                 request_start_data=False,
                 evaluate_class=WbtReward,
                 observation_class=WbtObs,
                 config: WbtConfig = WbtConfig()):
        super(WbtGym, self).__init__()
        self.seed(seed)

        self._gps_target = gps_target

        # some general inits
        self.history = []
        self.config = config
        self.distances = []
        self.rewards = []

        # init action, reward, observation
        self.action_class = action_class
        self.evaluate_class = evaluate_class
        self.observation_class = observation_class
        self._init_act_rew_obs(self)

        # comunication and supervisor
        self.train = train
        self._setup_train()
        self._init_com()

        if request_start_data is True:
            self.get_data()

    # =========================================================================
    # ====================       IMPORTANT PROPERTIES       ===================
    # =========================================================================
    @property
    def supervisor_connected(self) -> bool:
        if self.supervisor is not None and self.supervisor.return_code == 0:
            return True
        return False

    @property
    def gps_target(self):
        if self.supervisor_connected:
            return self.config.gps_target
        elif self._gps_target is not None:
            return self._gps_target
        raise ValueError("Target GPS not defined.")

    @property
    def state(self):
        return self.com.state

    # =========================================================================
    # ==========================       SEEDING       ==========================
    # =========================================================================
    def seed(self, seed):
        """Set main seed of env + 1000 other seeds for placements."""
        if seed is None:
            seed = utils.set_random_seed()
        self.seeds = [seed]
        np.random.seed(seed)
        self.seeds.extend(utils.seed_list(seed, n=1000))

    @property
    def main_seed(self):
        """Get the main seed of the env, first in seeds (list)."""
        return int(self.seeds[0])

    # =========================================================================
    # ==========================        SETUPS       ==========================
    # =========================================================================
    def _init_com(self):
        self.com = Communication(self.config)

    def _setup_train(self):
        self.supervisor = None
        if self.train is True:
            # start webots program, establish tcp connection
            self.supervisor = WbtCtrl(self.config)
            self.supervisor.init()

            # start environment and update config
            self.supervisor.start_env()

    def _init_act_rew_obs(self, env):
        # type to instance
        if type(self.action_class) == type:
            self.action_class = (self.action_class)()
        if type(self.observation_class) == type:
            self.observation_class = (self.observation_class)(env)
        if type(self.evaluate_class) == type:
            self.evaluate_class = (self.evaluate_class)(env, self.config)

        self.action_space = self.action_class.action_space
        self.config.direction_type = self.action_class.direction_type
        self.observation_space = self.observation_class.observation_space

    @property
    def observation(self):
        return self.observation_class.get()

    # =========================================================================
    # ==========================         CORE        ==========================
    # =========================================================================
    def step(self, action):
        """Perform action on environment.

        Handled inside com class.
        """
        if self.action_class.type == "grid":
            raise TypeError("Grid action class must be used in WebotsGrid.")

        pre_action = self.state.get_pre_action()
        action = self.action_class.map(action, pre_action)
        self.send_command_and_data_request(action)

        reward = self.calc_reward()
        done = self.check_done()

        # logging, printing
        self.rewards.append(reward)
        self.distances.append(self.get_target_distance())
        # if len(self.history) % 500 == 0:
        #     print("Reward (", len(self.history), ")\t", reward)

        return self.observation, reward, done, {}

    def calc_reward(self):
        """Calc reward with evaluate class."""
        return self.evaluate_class.calc_reward()

    def check_done(self):
        """Check done."""
        return self.evaluate_class.check_done()

    def reset(self, seed=None):
        """Reset environment to random."""
        if self.supervisor_connected is True:
            if seed is None:
                seed = utils.set_random_seed(apply=False)
            self.seed(seed)

            self.supervisor.reset_environment(self.main_seed)
            # self.supervisor.start_env(self.main_seed)
            self.rewards = []
            self.distances = []
            self._init_com()
            self.get_data()

            if self.get_target_distance(False) < 0.05:
                self.reset()

            return self.observation

    def close(self):
        """Close connection to supervisor and external controller."""
        if self.supervisor_connected is True:
            self.supervisor.close()

    def render(self):
        """Render dummy, does nothing."""
        pass

    # =========================================================================
    # ==============================   PLOTTING   =============================
    # =========================================================================
    def plot_lidar(self, relative=False):
        if relative is True:
            data = self.state.lidar_relative
        else:
            data = self.state.lidar_absolute
        utils.plot_lidar(data)

    # =========================================================================
    # ========================   HELPER / PROPERTIES   ========================
    # =========================================================================
    def get_data(self):
        self.com.get_data()
        self._update_history()

    def send_command_and_data_request(self, action):
        self.com.send_command_and_data_request(action)
        self._update_history()

    def _time_for_requests(self, requests=1000):
        t0 = time.time()
        for _ in range(requests):
            self.get_data()
        return time.time() - t0

    def _time_for_actions(self, actions=1000):
        t0 = time.time()
        for _ in range(actions):
            h = np.random.random() * 2 - 1
            s = np.random.random() * 2 - 1
            self.step((h, s))
        return time.time() - t0

    def _update_history(self):
        """Add current state of Com to history."""
        self.history.append(self.state)

    def get_target_distance(self, normalized=False):
        """Calculate euklidian distance to target."""
        distance = utils.euklidian_distance(self.gps_actual, self.gps_target)
        if normalized is True:
            distance = distance / self.max_distance
        return distance

    @property
    def iterations(self):
        return len(self.history)

    @property
    def total_reward(self):
        return sum(self.rewards)

    @property
    def gps_actual(self):
        return self.com.state.gps_actual

    @property
    def max_distance(self):
        return np.sqrt(2) * self.config.world_size