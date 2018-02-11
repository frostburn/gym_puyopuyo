import random
import sys

import gym
import numpy as np
from gym import spaces
from six import StringIO

from gym_puyopuyo.record import read_record
from gym_puyopuyo.state import State
from gym_puyopuyo.util import permute


class PuyoPuyoEndlessEnv(gym.Env):
    """
    Puyo Puyo environment. Single player endless mode.
    """

    metadata = {"render.modes": ["human", "ansi"]}

    def __init__(self, height, width, num_colors, num_deals, tsu_rules=False):
        self.state = State(height, width, num_colors, num_deals, tsu_rules=tsu_rules)
        self.reward_range = (-1, self.state.max_score)

        self.action_space = spaces.Discrete(len(self.state.actions))
        self.observation_space = spaces.Tuple((
            spaces.Box(0, 1, (self.state.num_colors, self.state.num_deals, 2)),
            spaces.Box(0, 1, (self.state.num_colors, self.state.height, self.state.width)),
        ))
        self._seed()

    def _seed(self, seed=None):
        return [self.state.seed(seed)]

    def _reset(self):
        self.state.reset()
        return self.state.encode()

    def _render(self, mode="human", close=False):
        if close:
            return
        outfile = StringIO() if mode == "ansi" else sys.stdout
        self.state.render(outfile)
        return outfile

    def _step_state(self, state, action, include_observations=True):
        action = self.state.actions[action]
        reward = self.state.step(*action)
        if include_observations:
            return self.state.encode(), reward
        return reward

    def _step(self, action):
        observation, reward = self._step_state(self.state, action)
        return observation, reward, (reward < 0), {"state": self.state}

    def get_action_mask(self):
        return self.state.get_action_mask()

    def get_root(self):
        return self.state.clone()

    def read_record(self, file, include_last=False):
        """
        Reads a record and yields observations like step does.

        The actions played are available under the info element.
        """
        initial_state = self.state.clone()
        initial_state.reset()
        for state, action, reward in read_record(file, initial_state, include_last=include_last):
            info = {
                "state": state,
                "action": state.actions.index(action) if action else None,
            }
            done = True if reward is None else (reward < 0)
            yield state.encode(), reward, done, info
            if done:
                return

    @classmethod
    def permute_observation(cls, observation):
        """
        Permute the observation in-place without affecting which action is optimal
        """
        deals, colors = observation
        deals = np.copy(deals)
        colors = np.copy(colors)

        # Flip deals other than the first one as it affects next action
        for i in range(1, len(deals[0])):
            if random.random() < 0.5:
                for color in range(len(deals)):
                    deals[color][i][0], deals[color][i][1] = deals[color][i][1], deals[color][i][0]

        perm = list(range(len(colors)))
        random.shuffle(perm)
        permute(deals, perm)
        permute(colors, perm)
        return (deals, colors)

    # TODO: Action affecting permutations (mirroring)
