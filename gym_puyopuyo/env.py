import sys

import gym
import gym.envs.registration
from gym import spaces
from six import StringIO

from gym_puyopuyo.record import read_record
from gym_puyopuyo.state import State

ENV_NAMES = {
    "small": "PuyoPuyoEndlessSmall-v0",
    "wide": "PuyoPuyoEndlessWide-v0",
    "tsu": "PuyoPuyoEndlessTsu-v0",
    "large": "PuyoPuyoEndlessLarge-v0",
}


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

    def read_record(self, file):
        """
        Reads a record and yields observations like step does.

        The actions played are available under the info element.
        """
        initial_state = self.state.clone()
        initial_state.reset()
        for state, action, reward in read_record(file, initial_state):
            info = {
                "state": state,
                "action": state.actions.index(action),
            }
            done = (reward < 0)
            yield state.encode(), reward, done, info
            if done:
                return


def register():
    gym.envs.registration.register(
        id=ENV_NAMES["small"],
        entry_point="gym_puyopuyo.env:PuyoPuyoEndlessEnv",
        kwargs={"width": 3, "height": 8, "num_colors": 3, "num_deals": 3},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.registration.register(
        id=ENV_NAMES["wide"],
        entry_point="gym_puyopuyo.env:PuyoPuyoEndlessEnv",
        kwargs={"width": 8, "height": 8, "num_colors": 4, "num_deals": 3},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.registration.register(
        id=ENV_NAMES["tsu"],
        entry_point="gym_puyopuyo.env:PuyoPuyoEndlessEnv",
        kwargs={"width": 6, "height": 13, "num_colors": 4, "num_deals": 3, "tsu_rules": True},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.registration.register(
        id=ENV_NAMES["large"],
        entry_point="gym_puyopuyo.env:PuyoPuyoEndlessEnv",
        kwargs={"width": 8, "height": 16, "num_colors": 5, "num_deals": 3},
        max_episode_steps=None,
        reward_threshold=25.0,
    )
