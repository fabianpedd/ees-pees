from gym.spaces import Discrete


class WbtActGrid():
    """Map proposed fake environment moves to webots.

    0: Right -> Up    (1)
    1: Down  -> Left  (2)
    2: Left  -> Down  (3)
    3: Up    -> Right (4)
    """
    def __init__(self, config=None):
        """Initialize WbtActGrid class."""
        self.config = config
        self.action_space = Discrete(4)
        self.direction_type = "steering"  # just a dummy
        self.type = "grid"

    def map(self, action):
        """Map fake environment action to webots.

        Description:
        ------------
        We use a different mapping in the fake environment as
        in webots so that we use the function here to map them accordingly

        Parameter:
        ----------
        action : integer
            action of the fake environment

        Return:
        -------
        integer
            action mapped on webots environment

        """
        return int(action + 1)
