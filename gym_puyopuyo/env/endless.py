from __future__ import division

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

    TESTING = False

    metadata = {"render.modes": ["human", "console", "ansi"]}

    def __init__(self, height, width, num_colors, num_deals, tsu_rules=False):
        self.state = State(height, width, num_colors, num_deals, tsu_rules=tsu_rules)
        self.reward_range = (-1, self.state.max_score)

        self.action_space = spaces.Discrete(len(self.state.actions))
        self.observation_space = spaces.Tuple((
            spaces.Box(0, 1, (self.state.num_colors, self.state.num_deals, 2), dtype=np.int8),
            spaces.Box(0, 1, (self.state.num_colors, self.state.height, self.state.width), dtype=np.int8),
        ))
        self.seed()

        self.viewer = None
        self.anim_state = None
        self.last_action = None

    def seed(self, seed=None):
        return [self.state.seed(seed)]

    def reset(self):
        self.state.reset()
        if self.viewer:
            self.anim_state = None
            self.last_action = None
        return self.state.encode()

    def close(self):
        if self.viewer:
            self.viewer.close()

    def render(self, mode="console"):
        if self.TESTING and mode == "human":
            mode = "console"

        if mode == "human":
            from time import sleep
            from gym_puyopuyo.rendering import ImageViewer, AnimationState

            if self.anim_state:
                self.anim_state.state.deals[1:] = self.state.deals[:-1]
            else:
                self.anim_state = AnimationState(self.state.clone())

            if not self.viewer:
                self.viewer = ImageViewer(width=self.anim_state.width + 4, height=self.anim_state.height)

            if self.last_action is not None:
                self.anim_state.state.play_deal(*self.state.actions[self.last_action])
                self.anim_state.state.deals.pop()
                self.anim_state.infer_entities()

            for frame in self.anim_state.resolve():
                self.viewer.render_state(frame)
                sleep(0.05)
            return

        outfile = StringIO() if mode == "ansi" else sys.stdout
        self.state.render(outfile)
        if mode == "ansi":
            return outfile

    def _step_state(self, state, action, include_observations=True):
        action = self.state.actions[action]
        reward = self.state.step(*action)
        if include_observations:
            return self.state.encode(), reward
        return reward

    def step(self, action):
        self.last_action = action
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


class PuyoPuyoEndlessBoxedEnv(PuyoPuyoEndlessEnv):
    """
    Environment with observations in the form of a single box to make it compatible with plain CNN policies.
    """
    def __init__(self, *args, **kwargs):
        super(PuyoPuyoEndlessBoxedEnv, self).__init__(*args, **kwargs)
        self.observation_space = spaces.Box(0, 1, (
            self.state.num_colors,
            self.state.height + 1 + self.state.num_deals,
            self.state.width),
            dtype=np.float32,
        )

    def encode(self):
        field = self.state.encode_field()
        deals = self.state.encode_deals_box()
        padding = np.zeros((self.state.num_colors, 1, self.state.width), dtype=np.int8)
        return np.hstack((deals, padding, field)).astype(np.float32)

    def reset(self):
        super(PuyoPuyoEndlessBoxedEnv, self).reset()
        return self.encode()

    def step(self, action):
        _, reward, done, info = super(PuyoPuyoEndlessBoxedEnv, self).step(action)
        return self.encode(), reward, done, info

    @classmethod
    def permute_observation(cls, observation):
        colors = np.copy(observation)
        perm = list(range(len(colors)))
        random.shuffle(perm)
        permute(colors, perm)
        return colors
