import sys

import gym
import gym.envs.registration
from gym import spaces
from gym.utils import seeding
import numpy as np  # noqa: I001
from six import StringIO

from gym_puyopuyo.state import BottomState


class PuyoPuyoEndlessEnv(gym.Env):
    """
    Puyo Puyo environment. Single player endless mode.
    """

    metadata = {"render.modes": ["human", "ansi"]}

    def __init__(self, height, width, num_colors, num_deals):
        if height > BottomState.HEIGHT:
            raise ValueError("Maximum height is {}".format(BottomState.HEIGHT))
        if width > BottomState.WIDTH:
            raise ValueError("Maximum width is {}".format(BottomState.WIDTH))
        self.state = BottomState(num_colors)
        self.width = width
        self.height = height
        self.num_colors = num_colors
        self.reward_range = (-1, self.max_chain ** 2)
        self.num_deals = num_deals
        self.make_actions()
        self.action_space = spaces.Discrete(len(self.actions))
        self.observation_space = spaces.Tuple((
            spaces.Box(0, 1, (self.num_colors, self.num_deals, 2)),
            spaces.Box(0, 1, (self.num_colors, self.height, self.width)),
        ))
        self._seed()
        self.make_deals()

    @property
    def max_chain(self):
        return self.width * self.height // self.state.CLEAR_THRESHOLD

    def make_actions(self):
        self.actions = []
        for x in range(self.width):
            self.actions.append((x, 1))
            self.actions.append((x, 3))
        for x in range(self.width - 1):
            self.actions.append((x, 0))
            self.actions.append((x, 2))

    def make_deals(self):
        self.deals = []
        for _ in range(self.num_deals):
            self.make_deal()

    def make_deal(self):
        self.deals.append((
            self.np_random.randint(0, self.num_colors),
            self.np_random.randint(0, self.num_colors),
        ))

    def encode_deals(self):
        np_deals = np.zeros((self.num_colors, self.num_deals, 2))
        for i, deal in enumerate(self.deals):
            np_deals[deal[0]][i][0] = 1
            np_deals[deal[1]][i][1] = 1
        return np_deals

    def encode_state(self):
        np_state = self.state.encode()
        return np_state[:self.num_colors, (self.state.HEIGHT - self.height):, :self.width]

    def play_deal(self, x, orientation):
        self.make_deal()
        puyo_a, puyo_b = self.deals.pop(0)
        stack = [None] * (2 * self.state.WIDTH)
        if orientation == 0:
            stack[x] = puyo_a
            stack[x+1] = puyo_b
        elif orientation == 1:
            stack[x] = puyo_a
            stack[x + self.state.WIDTH] = puyo_b
        elif orientation == 2:
            stack[x] = puyo_b
            stack[x+1] = puyo_a
        elif orientation == 3:
            stack[x] = puyo_b
            stack[x + self.state.WIDTH] = puyo_a
        else:
            raise ValueError("Unknown orientation")
        return stack

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _reset(self):
        self.state.reset()
        return (self.encode_deals(), self.encode_state())

    def _render(self, mode="human", close=False):
        if close:
            return
        outfile = StringIO() if mode == "ansi" else sys.stdout
        self.state.render(outfile)
        return outfile

    def _step_state(self, state, action, include_observations=True):
        action = self.actions[action]
        stack = self.play_deal(*action)
        valid = self.state.overlay(stack)
        chain = self.state.resolve()
        reward = chain * chain if valid else -1
        if include_observations:
            observation = (self.encode_deals(), self.encode_state())
            return observation, reward
        return reward

    def _step(self, action):
        observation, reward = self._step_state(self.state, action)
        return observation, reward, (reward < 0), {"state": self.state}

    def get_root(self):
        return self.state.clone()


def register():
    gym.envs.registration.register(
        id="PuyoPuyoEndlessSmall-v0",
        entry_point="gym_puyopuyo.env:PuyoPuyoEndlessEnv",
        kwargs={"width": 3, "height": 8, "num_colors": 3, "num_deals": 3},
        max_episode_steps=200,
        reward_threshold=25.0,
    )

    gym.envs.registration.register(
        id="PuyoPuyoEndlessWide-v0",
        entry_point="gym_puyopuyo.env:PuyoPuyoEndlessEnv",
        kwargs={"width": 8, "height": 8, "num_colors": 4, "num_deals": 3},
        max_episode_steps=200,
        reward_threshold=25.0,
    )
