from gym.spaces import Discrete, Tuple
import numpy as np

from webotsgym.env.action.action import WbtAct


class WbtActDiscrete(WbtAct):
    """Discrete action class.

    Generate matrix of possible actions. Rows are possible speeds, columns
    possible directions. The following symetric grid is generated by settings:
        direcstions = 5
        range_direction = 0.3
        speeds = 3
        range_speed = 0.1
        NOTE: range_ should be a float in (0, 1] as it specifies the endpoints
              of the action grid.

                            DIRECTIONS
            +------+ +------+-------+---+------+-----+
            |      | | -0.3 | -0.15 | 0 | 0.15 | 0.3 |
        S   +------+ +------+-------+---+------+-----+
        P   +------+ +------+-------+---+------+-----+
        E   | -0.1 | | 0    | 1     | 2 | 3    | 4   |
        E   +------+ +------+-------+---+------+-----+
        D   | 0    | | 5    | ...   |   |      |     |
        S   +------+ +------+-------+---+------+-----+
            | 0.1  | |      |       |   |      |     |
            +------+ +------+-------+---+------+-----+
            Example: RL-agent action = 4 is mapped to (0.3, -0.1).


    Parameters
    ----------
    config : WbtConfig
    directions : int
    range_direction : float in (0, 1]
    speeds : int
    range_speed : float in (0, 1]
    mode : str
        "flatten": expects 1 integer in action range
        "tuple": expects 2 integers, indexing speed or direction respectively
    relative : bool
        True: action_out = prev_state + new_action
        False: action_out = new_action
    """

    def __init__(self, config, directions=3, range_direction=1, speeds=3,
                 range_speed=1, mode="flatten", relative=True):
        """Initialize WbtActDiscrete action class."""
        super(WbtActDiscrete, self).__init__()
        self.config = config
        self.type = "normal"
        self.mode = mode
        self.relative = relative

        # setup rows and columns values of action grid
        self.dirspace = np.linspace(-range_direction, range_direction,
                                    directions)
        self.speedspace = np.linspace(-range_speed, range_speed, speeds)

        # setup action space
        self.action_tuple = (directions, speeds)
        self._set_action_space()

    @property
    def number_of_actions(self):
        """Set number of actions for flatten or tuple mode."""
        if self.mode == "flatten":
            return self.action_tuple[0] * self.action_tuple[1] + 1
        if self.mode == "tuple":
            return self.action_tuple[0] * (self.action_tuple[1] + 1)
        return None

    def _set_action_space(self):
        """Set action space for flatten or tuple mode."""
        if self.mode == "flatten":
            self.action_space = Discrete(self.action_tuple[0]
                                         * self.action_tuple[1])  # noqa W503
        elif self.mode == "tuple":
            self.action_space = Tuple((Discrete(self.action_tuple[0]),
                                       Discrete(self.action_tuple[1])))

    def map(self, action, pre_action=None):
        """Map RL-agent action to webots action.

        If 'relative' is True, the mapped values of 'action' will be added
        to the 'pre-action', e.g. pre_action = (0.2, 0.3), action = (-0.1, 0.1)
        will result in (0.1, 0.4).

        Parameters
        ----------
        action : int, tuple
            Action from RL-agent.
        pre_action : ActionOut
            Last action send to external controller.

        Returns
        -------
        ActionOut
            New action to be send to external controller.

        """
        if self.mode == "flatten":
            dir_idx = action % len(self.dirspace)
            speed_idx = int((action - dir_idx) / len(self.dirspace))
        elif self.mode == "tuple":
            dir_idx = action[0]
            speed_idx = action[1]

        action = (self.dirspace[dir_idx], self.speedspace[speed_idx])
        return super().map(action, pre_action)
