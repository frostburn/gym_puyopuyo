import sys

import gym
import gym.envs.registration
from gym import spaces
from six import StringIO

from gym_puyopuyo.state import BottomState


class PuyoPuyoEndlessEnv(gym.Env):
    """
    Puyo Puyo environment. Single player endless mode.
    """

    metadata = {"render.modes": ["human", "ansi"]}

    def __init__(self, height, width, num_colors, num_deals):
        self.state = BottomState(height, width, num_colors, num_deals)
        self.reward_range = (-1, self.state.max_chain ** 2)

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
        chain = self.state.step(*action)
        reward = chain * chain if chain >= 0 else -1
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
