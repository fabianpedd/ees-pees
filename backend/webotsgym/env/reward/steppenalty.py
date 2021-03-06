import numpy as np
from webotsgym.utils import exponential_decay


def step_pen_tanh(env, step_base=-1):
    """Calculate step penalty with tanh."""
    distance = env.get_target_distance()
    dist_fac = np.tanh(distance / (0.5 * env.max_distance))
    return step_base * dist_fac


def step_pen_exp(x, step_penalty=-1, lambda_=5):
    """Calculate step penalty with exponential_decay."""
    return step_penalty * (1 - exponential_decay(x, lambda_=lambda_))
