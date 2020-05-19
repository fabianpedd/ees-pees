import numpy as np
import matplotlib.pyplot as plt
import communicate
import utils
import abc
import gym


class MyGym(gym.Env):
    def __init__(self, seed=0):
        super(MyGym, self).__init__()
        self.seed(seed)
        self.reward_range = (-100, 100)

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def step(self):
        pass

    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    def seed(self, seed):
        """Set main seed of env + 1000 other seeds for placements."""
        self.seeds = [self.main_seed]
        np.random.seed(self.main_seed)
        self.seeds.extend(list(set(np.random.randint(0, 10**6, 1000))))
        self.next_seed_idx = 1
        return self.seeds

    def get_next_seed(self):
        """Get next random seed, increment next_seed_idx."""
        seed = self.seeds[self.next_seed_idx]
        self.next_seed_idx += 1
        return seed

    @property
    def main_seed(self):
        """Get the main seed of the env, first in seeds (list)."""
        return self.seeds[0]


class WebotsBlue(MyGym):
    def __init__(self):
        super(WebotsBlue, self).__init__()

    def reset(self):
        self.com.reset()

    def step(self, action):
        self.com.send(action)
        self.com.recv()
        reward = self.calc_reward()
        done = self.check_done()
        return self.state, reward, done, {}

    def get_target_distance(self):
        """Calculate euklidian distance to target."""
        # return utils.euklidian_distance(self.gps_actual[0:2],
        #                                 self.gps_target[0:2])
        return utils.euklidian_distance(self.gps_actual, self.gps_target)

    @abc.abstractmethod
    def calc_reward(self):
        pass

    @abc.abstractmethod
    def check_done(self):
        pass

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


class WebotsEnv(WebotsBlue):
    def __init__(self):
        super(WebotsEnv, self).__init__(fake=False)
        self.com = communicate.Com(self.seeds)


class WebotsFake(WebotsBlue):
    def __init__(self, N=100, num_of_sensors=4, obstacles_each=4):
        super(WebotsEnv, self).__init__(fake=True)
        self.com = FakeCom(self.seeds, N, num_of_sensors, obstacles_each)

    def step(self, action):
        self.com.send(action)
        self.com.recv()
        reward = self.calc_reward()
        done = self.check_done()
        return self.state, reward, done, {}

    def render(self):
        plt.figure(figsize=(10, 10))
        f = self.com.field.copy()
        rx, ry = self.gps_actual
        tx, ty = self.gps_target
        s = self.com.plotpadding
        r_minx = max(0, (rx - s))
        r_maxx = min(rx + s + 1, self.com.N)
        r_miny = max(0, (ry - s))
        r_maxy = min(ry + s + 1, self.com.N)

        t_minx = max(0, (tx - s))
        t_maxx = min(tx + s + 1, self.com.N)
        t_miny = max(0, (ty - s))
        t_maxy = min(ty + s + 1, self.com.N)

        f[r_minx:r_maxx, r_miny:r_maxy] = VAL_ROBBIE
        f[t_minx:t_maxx, t_miny:t_maxy] = VAL_TARGET
        plt.matshow(f)


WALLSIZE = 1
VAL_WALL = 1
VAL_OBSTACLE = 2
VAL_ROBBIE = 4
VAL_TARGET = 6


class FakeCom():
    def __init__(self, seeds, N=100, num_of_sensors=4, obstacles_each=4):
        self.seeds = seeds
        self.next_seed_idx = 1
        self.inits = (N, num_of_sensors, obstacles_each)
        self.N = N
        self.offset = int(2 * N)
        self.num_of_sensors = num_of_sensors
        self.plotpadding = 1
        self.setup_fields()

        # place obstacles randomly (horizontal and vertical walls)
        self.place_random_obstacle(dx=1, dy=int(N / 3), N=obstacles_each)
        self.place_random_obstacle(int(N / 3), 1, N=obstacles_each)

        # random start and finish positions
        gps_actual = self.random_position()
        gps_target = self.random_position()

    # #########################################################################
    # ###############################   SETUP   ###############################
    # #########################################################################
    def setup_fields(self):
        self.field = np.zeros((self.N, self.N))
        self.inner = (self.offset, self.offset + self.N)
        # set up walls
        self.field[0:WALLSIZE] = VAL_WALL
        self.field[-WALLSIZE:] = VAL_WALL
        self.field[:, 0:WALLSIZE] = VAL_WALL
        self.field[:, -WALLSIZE:] = VAL_WALL

    # #########################################################################
    # ######################   RANDOM OBJECT PLACEMENT   ######################
    # #########################################################################
    def get_next_seed(self):
        """Get next random seed, increment next_seed_idx."""
        seed = self.seeds[self.next_seed_idx]
        self.next_seed_idx += 1
        return seed

    def random_grid_int(self):
        seed = self.get_next_seed()
        np.random.seed(seed)
        random_grid_int = np.random.randint(self.N)
        return random_grid_int

    def random_position(self):
        """Get a random x,y pair."""
        x = self.random_grid_int()
        y = self.random_grid_int()
        if self.field[x, y] > 0:
            x, y = self.random_position()
        return (x, y)

    def place_random_obstacle(self, dx, dy, N=1):
        if N == 1:
            x, y = self.random_position()
            xmax = min(x + dx, self.N - 1)
            ymax = min(y + dy, self.N - 1)
            self.add_obstacle((x, xmax, y, ymax))
        else:
            for _ in range(N):
                self.place_random_obstacle(dx, dy)

    def pts_to_anchor(self, anchor, filterout=True):
        pts = []
        line = utils.get_line(self.pos_outer, anchor)
        for i, p in enumerate(line):
            if (self.inner[0] <= p[0] <= self.inner[1]) and \
               (self.inner[0] <= p[1] <= self.inner[1]):
                p = self.pt2inner(p)
                x, y = p
                if filterout is True and i > 0 and self.field[x, y] > 0:
                    return pts, utils.euklidian_distance(self.pos, p)
                pts.append(p)
        return pts, utils.euklidian_distance(self.pos, p)

    def distance_sensor(self):
        N = self.N
        pos = self.pos
        endpoints = [(0, 0), (N - 1, 0), (0, N - 1), (N - 1, N - 1)]
        radius = round(max([utils.euklidian_distance(pos, ep) for
                            ep in endpoints]))
        phi = np.linspace(0, 2 * np.pi, self.num_of_sensors + 1)[:-1]
        pos = self.pos_outer
        y = (radius * np.cos(phi)).astype(int) + pos[1]
        x = (radius * np.sin(phi)).astype(int) + pos[0]
        anchors = list(zip(x, y))
        distances = []
        self.anchors = anchors
        for anch in anchors:
            distances.append(self.pts_to_anchor(anch)[1] - 1)
        self.distances = distances
        return anchors, distances

    def apply_action(self, action):
        if self.distances is None:
            self.distance_sensor()
        if action is None:
            action = self.random_action()
        orientation_idx, len_ = action
        pts_on_line = self.pts_to_anchor(self.anchors[orientation_idx],
                                         filterout=False)[0]
        self.pt = pts_on_line
        crash = False
        safept = self.pos
        for i, pt in enumerate(pts_on_line):
            if self.field[pt[0], pt[1]] > 0:
                crash = True
                break
            if utils.euklidian_distance(self.pos, pt) > len_:
                break
            else:
                safept = pt
        self.pos = safept
        self.distance_sensor()
        reward = self.reward(crash)
        if self.target_distance() < target_gap:
            done = True
        else:
            done = False
        return self.state, reward, done, {}

class FakeEnvironmentAbstract(Env):
    def __init__(self, N=100, startpos=None, targetpos=None, num_of_sensors=4, obstacles_each=4):
        self.inits = (N, num_of_sensors, obstacles_each)
        self.N = N
        self.offset = int(2 * N)
        self.setup_fields()
        self.num_of_sensors = num_of_sensors
        if startpos is None:
        if targetpos is None:
            targetpos = self.random_position()
        self.startpos = startpos
        self.pos = startpos
        self.target = targetpos
        self.plotpadding = 1
        self.place_random_obstacle(dx=1, dy=int(N/3), N=obstacles_each)
        self.place_random_obstacle(int(N/3), 1, N=obstacles_each)
        self.distance_sensor()

    def reset(self):
        N, num_of_sensors, obstacles_each = self.inits
        self.__init__(N=N, num_of_sensors=num_of_sensors, obstacles_each=obstacles_each)
        reward = self.reward(crash=False)
        return self.state, reward, False, {}

    def random_position(self):
        x = np.random.randint(self.N)
        y = np.random.randint(self.N)
        if self.field[x, y] > 0:
            x, y = self.random_position()
        return (x, y)

    def step(self, action=None, target_gap=0, step_len=1):
        if self.distances is None:
            self.distance_sensor()
        if action is None:
            action = self.random_action()
        orientation_idx, len_ = action
        pts_on_line = self.pts_to_anchor(self.anchors[orientation_idx],
                                         filterout=False)[0]
        self.pt = pts_on_line
        crash = False
        safept = self.pos
        for i, pt in enumerate(pts_on_line):
            if self.field[pt[0], pt[1]] > 0:
                crash = True
                break
            if utils.euklidian_distance(self.pos, pt) > len_:
                break
            else:
                safept = pt
        self.pos = safept
        self.distance_sensor()
        reward = self.reward(crash)
        if self.target_distance() < target_gap:
            done = True
        else:
            done = False
        return self.state, reward, done, {}

    def random_action(self, length=None):
        orientation = np.random.randint(len(self.distance_arr))
        if length is None:
            length = int(self.N / 10)
        return orientation, length

    def reward(self, crash):
        reward = np.sqrt(2) * self.N**2 * (1 - crash) - self.target_distance()
        return reward

    def setup_fields(self):
        self.field = np.zeros((self.N, self.N))
        self.inner = (self.offset, self.offset + self.N)

        # set up walls
        self.field[0:WALLSIZE] = VAL_WALL
        self.field[-WALLSIZE:] = VAL_WALL
        self.field[:, 0:WALLSIZE] = VAL_WALL
        self.field[:, -WALLSIZE:] = VAL_WALL

    def add_obstacle(self, x1x2y1y2):
        x1, x2, y1, y2 = x1x2y1y2
        field_tmp = self.field.copy()
        field_tmp[x1:x2, y1:y2] = VAL_OBSTACLE
        if field_tmp[self.pos[0], self.pos[1]] != 0:
            return None
        if field_tmp[self.target[0], self.target[1]] != 0:
            return None
        self.field = field_tmp
        self.distance_sensor()

    def place_random_obstacle(self, dx, dy, N=1):
        if N == 1:
            x, y = self.random_position()
            xmax = min(x + dx, self.N - 1)
            ymax = min(y + dy, self.N - 1)
            self.add_obstacle((x, xmax, y, ymax))
        else:
            for _ in range(N):
                self.place_random_obstacle(dx, dy)

    def pts_to_anchor(self, anchor, filterout=True):
        pts = []
        line = utils.get_line(self.pos_outer, anchor)
        for i, p in enumerate(line):
            if (self.inner[0] <= p[0] <= self.inner[1]) and \
               (self.inner[0] <= p[1] <= self.inner[1]):
                p = self.pt2inner(p)
                x, y = p
                if filterout is True and i > 0 and self.field[x, y] > 0:
                    return pts, utils.euklidian_distance(self.pos, p)
                pts.append(p)
        return pts, utils.euklidian_distance(self.pos, p)

    def distance_sensor(self):
        N = self.N
        pos = self.pos
        endpoints = [(0, 0), (N - 1, 0), (0, N - 1), (N - 1, N - 1)]
        radius = round(max([utils.euklidian_distance(pos, ep) for
                            ep in endpoints]))
        phi = np.linspace(0, 2 * np.pi, self.num_of_sensors + 1)[:-1]
        pos = self.pos_outer
        y = (radius * np.cos(phi)).astype(int) + pos[1]
        x = (radius * np.sin(phi)).astype(int) + pos[0]
        anchors = list(zip(x, y))
        distances = []
        self.anchors = anchors
        for anch in anchors:
            distances.append(self.pts_to_anchor(anch)[1] - 1)
        self.distances = distances
        return anchors, distances

    def render(self):
        plt.figure(figsize=(10, 10))
        f = self.field.copy()
        rx, ry = self.pos
        tx, ty = self.target
        s = self.plotpadding
        r_minx = max(0, (rx - s))
        r_maxx = min(rx + s + 1, self.N)
        r_miny = max(0, (ry - s))
        r_maxy = min(ry + s + 1, self.N)

        t_minx = max(0, (tx - s))
        t_maxx = min(tx + s + 1, self.N)
        t_miny = max(0, (ty - s))
        t_maxy = min(ty + s + 1, self.N)

        f[r_minx:r_maxx, r_miny:r_maxy] = VAL_ROBBIE
        f[t_minx:t_maxx, t_miny:t_maxy] = VAL_TARGET
        plt.matshow(f)

    def target_distance(self):
        return utils.euklidian_distance(self.pos, self.target)

    def pt2outer(self, pt):
        return (pt[0] + self.offset, pt[1] + self.offset)

    def pt2inner(self, pt):
        return (pt[0] - self.offset, pt[1] - self.offset)

    @property
    def distance_arr(self):
        return np.array(self.distances).ravel()

    @property
    def total_len(self):
        return self.N + 2 * self.offset

    @property
    def pos_outer(self):
        return self.pt2outer(self.pos)

    @property
    def state(self):
        positions = np.array([self.pos, self.target]).ravel()
        self.distance_sensor()
        data = np.hstack((positions, self.distance_arr))
        return data


class FakeEnvironmentMini(FakeEnvironmentAbstract):
    def __init__(self, N=10, num_of_sensors=4, obstacles_each=2):
        super(FakeEnvironmentMini, self).__init__(N=10, num_of_sensors=num_of_sensors, obstacles_each=obstacles_each)
        self.plotpadding = 0


class FakeEnvironmentMedium(FakeEnvironmentAbstract):
    def __init__(self, N=50, num_of_sensors=8, obstacles_each=3):
        super(FakeEnvironmentMedium, self).__init__(N=50, num_of_sensors=num_of_sensors, obstacles_each=obstacles_each)
        self.plotpadding = 1


class FakeEnvironmentLarge(FakeEnvironmentAbstract):
    def __init__(self, N=100, num_of_sensors=32, obstacles_each=4):
        super(FakeEnvironmentLarge, self).__init__(N=100, num_of_sensors=num_of_sensors, obstacles_each=obstacles_each)
        self.plotpadding = 2


class DQNEnv(FakeEnvironmentMini):
    def __init__(self):
        super(DQNEnv, self).__init__()

    def fields_around(self, radius):
        n_f = radius * 2 + 1
        fields = np.zeros(shape=(n_f, n_f))
        pos = self.pos
        x = 0
        y = 0
        d = (0, 0)
        for i in range(-radius, radius + 1):
            y = 0
            for j in range(-radius, radius + 1):
                d = (i, j)
                pt = tuple(map(lambda i, j: i + j, pos, d))
                if pt == pos:
                    fields[x][y] = -1
                elif self.field[pt[0]][pt[1]] > 0:
                    fields[x][y] = 1
                y += 1
            x += 1

        return fields

    def step_f(self, action, radius):
        done = False
        crash = False
        o_pos = self.pos
        direction, len_ = action
        adj = (0, 0)
        if direction == 1:
            adj = (-1, 0)
        elif direction == 2:
            adj = (0, 1)
        elif direction == 3:
            adj = (1, 0)
        elif direction == 4:
            adj = (0, -1)
        n_p = tuple(map(lambda i, j: i + j, o_pos, adj))
        if self.field[n_p[0], n_p[1]] > 0:
            crash = True
        else:
            self.pos = n_p
        if self.pos == self.target:
            done = True
        n_pos = self.pos
        state = (self.pos, self.fields_around(radius))
        reward = self.calc_reward(crash, done, o_pos, n_pos)
        return state, reward, done, {}

    def dist_reward(self, o_pos, n_pos):
        d_reward = 0
        t_pos = self.target
        dx_old = abs(o_pos[0] - t_pos[0])
        dx_new = abs(n_pos[0] - t_pos[0])
        dy_old = abs(o_pos[1] - t_pos[1])
        dy_new = abs(n_pos[1] - t_pos[1])

        if dx_old > dx_new:
            d_reward = 20
        if dx_old < dx_new:
            d_reward = -20
        if dy_old > dy_new:
            d_reward = 20
        if dy_old < dy_new:
            d_reward = -20

        return d_reward

    def calc_reward(self, crash, done, o_pos, n_pos):
        reward = 0
        if done is True:
            reward = reward + 1000
        if crash is True:
            reward = reward - 100
        reward = reward + self.dist_reward(o_pos, n_pos)
        reward = reward - 10
        return reward

    def plot(self):
        self.render()
