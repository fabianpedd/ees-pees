import abc
from pynput import keyboard
import numpy as np
import time

import webotsgym.communicate as communicate
import webotsgym.environment as environment
from webotsgym.action import ContinuousAction
from webotsgym.webot import WebotAction


class Agent(abc.ABC):
    def __init__(self):
        self.history = []

    @abc.abstractmethod
    def action(self):
        pass


class RndWebotAgent(Agent):
    def __init__(self):
        self.com = communicate.Com((1, 2))

    def action(self):
        action = WebotAction()
        action.heading = np.random.random() * 2 - 1
        action.speed = np.random.random() * 2 - 1
        time.sleep(0.2)
        self.com.send_command(action)


class WebotCtrAgent(Agent):
    def __init__(self, direction_type="heading"):
        self.dheading = 0.05
        self.dspeed = 0.05
        action_class = ContinuousAction(direction_type=direction_type)
        self.env = environment.WebotsEnv(action_class=action_class)
        self._init_action()

    def _init_action(self):
        self.act = WebotAction()
        self.act.speed = 0
        self.act.heading = 0

    def action(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        if key == keyboard.Key.up:
            self.act.speed += self.dspeed
        elif key == keyboard.Key.down:
            self.act.speed -= self.dspeed
        elif key == keyboard.Key.left:
            self.act.heading -= self.dheading
        elif key == keyboard.Key.right:
            self.act.heading += self.dheading
        else:
            return
        self.act.print()
        self.env.send_command_and_data_request(self.act)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False


if __name__ == "__main__":
    james = WebotCtrAgent(direction_type="heading")
    james.action()
