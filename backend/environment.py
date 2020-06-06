import numpy as np
import gym
import utils
import communicate
import automate

from Config import WebotConfig
from Action import DiscreteAction
from Reward import Reward
from Observation import observation_std


class WebotsEnv(gym.Env):
    def __init__(self, seed=None, train=False, start_controller=False,
                 action_class=DiscreteAction, reward_class=Reward,
                 observation_func=observation_std,
                 config: WebotConfig = WebotConfig()):
        super(WebotsEnv, self).__init__()
        self.set_seed(seed)

        # some general inits
        self.i = 0
        self.history = {}
        self.config = config

        # init action, reward, observation
        self.action_class = action_class
        self.reward_class = reward_class
        self.observation_func = observation_func
        self._init_act_rew_obs(self)

        # communication and supervisor
        self.train = train
        self._setup_train()
        self.com = communicate.Com(config)
        if start_controller is True:
            self.external_controller = automate.ExtCtrl()
            self.external_controller.init()
            self.com.recv()

    # =========================================================================
    # ==========================       SEEDING       ==========================
    # =========================================================================
    def set_seed(self, seed):
        """Set main seed of env + 1000 other seeds for placements."""
        if seed is None:
            seed = utils.set_random_seed()
        self.seeds = [seed]
        np.random.seed(seed)
        self.seeds.extend(utils.seed_list(seed, n=1000))

    def get_next_seed(self):
        """Get next random seed, increment next_seed_idx."""
        seed = self.seeds[self.next_seed_idx]
        self.next_seed_idx += 1
        return seed

    @property
    def main_seed(self):
        """Get the main seed of the env, first in seeds (list)."""
        return int(self.seeds[0])

    # =========================================================================
    # ==========================        SETUPS       ==========================
    # =========================================================================
    def _setup_train(self):
        if self.train is True:
            # start webots program, establish tcp connection
            self.supervisor = automate.WebotCtrl(self.config)
            self.supervisor.init()

            # start environment and update config
            self.supervisor.start_env()

    def _init_act_rew_obs(self, env):
        # type to instance
        if type(self.action_class) == type:
            self.action_class = (self.action_class)()
        if type(self.reward_class) == type:
            self.reward_class = (self.reward_class)(env)

        self.action_space = self.action_class.action_space
        self.reward_range = self.reward_class.reward_range

    # =========================================================================
    # ==========================         CORE        ==========================
    # =========================================================================
    def step(self, action):
        """Perform action on environment.

        Handled inside com class.
        """
        action = self.action_class.map(action, self.state_object)
        self.send(action)
        self.recv()
        reward = self.calc_reward()
        done = self.check_done()

        # return self.state, reward, done, {}
        return self.observation, reward, done, {}

    def calc_reward(self):
        """Calc reward with reward class."""
        return self.reward_class.calc()

    def check_done(self):
        """Check done."""
        # TODO: Part of reward_class?
        if self.gps_actual == self.gps_target:
            return True
        return False

    def reset(self):
        """Reset environment to random."""
        if self.supervisor_connected is True:
            seed = utils.np_random_seed(set=False)
            self.seed(seed)
            self.supervisor.start_env(self.main_seed)
            return self.observation

    def close(self):
        """Close connection to supervisor and external controller."""
        if self.supervisor_connected is True:
            self.supervisor.close()
            # TODO: sure to close external controller? Does it do harm if left open?
            self.external_controller.close()

    def render(self):
        """Render, does nothing just dummy."""
        pass

    # =========================================================================
    # ==========================        HELPER       ==========================
    # =========================================================================
    def send(self, action):
        """Send action via Com class."""
        self.com.send(action)

    def recv(self):
        """Receive state via Com class."""
        self.com.recv()
        self._update_history()

    def _update_history(self):
        """Add current state of Com to history."""
        self.history[self.i] = self.state
        self.i += 1

    def get_target_distance(self):
        """Calculate euklidian distance to target."""
        return utils.euklidian_distance(self.gps_actual, self.gps_target)

    @property
    def observation(self):
        return self.observation_func(self)

    @property
    def state(self):
        return self.com.state.get()

    @property
    def state_object(self):
        return self.com.state

    @property
    def gps_actual(self):
        return self.com.state.gps_actual

    @property
    def gps_target(self):
        return self.com.state.gps_target

    @property
    def supervisor_connected(self) -> bool:
        if self.supervisor is not None and self.supervisor.return_code.value == 0:
            return True
        return False
