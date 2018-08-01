import sys

import gym
from gym import spaces
from six import StringIO

from gym_puyopuyo.versus import Game


class PuyoPuyoVersusEnv(gym.Env):
    """
    Puyo Puyo environment. Versus mode.
    """

    metadata = {"render.modes": ["human", "ansi"]}

    def __init__(self, opponent, state_params, garbage_clue_weight=0):
        self.opponent = opponent
        self.state = Game(state_params=state_params)
        self.garbage_clue_weight = garbage_clue_weight

        self.reward_range = (-1, 1)

        player = self.state.players[0]
        max_steps = player.height * player.width
        if not player.tsu_rules:
            max_steps //= 2
        max_score = player.max_score + max_steps * player.step_bonus
        player_space = spaces.Dict({
            "deals": spaces.Box(0, 1, (player.num_colors, player.num_deals, 2)),
            "field": spaces.Box(0, 1, (player.num_layers, player.height, player.width)),
            "chain_number": spaces.Discrete(player.max_chain),
            "pending_score": spaces.Discrete(max_score),
            "pending_garbage": spaces.Discrete(max_score // player.target_score),
            "all_clear": spaces.Discrete(2),
        })
        self.observation_space = spaces.Tuple((player_space, player_space))
        self.action_space = spaces.Discrete(len(player.actions))
        self.player = player
        self.seed()

    def seed(self, seed=None):
        return [self.state.seed(seed)]

    def reset(self):
        self.state.reset()
        return self.state.encode()

    def render(self, mode="console"):
        outfile = StringIO() if mode == "ansi" else sys.stdout
        self.state.render(outfile)
        return outfile

    def step(self, action):
        root = self.get_root()
        root.players = root.players[::-1]
        opponent_action = self.opponent(root)
        acts = self.player.actions
        reward, garbage, done = self.state.step([acts[action], acts[opponent_action]])
        reward += self.garbage_clue_weight * garbage
        observation = self.state.encode()
        return observation, reward, done, {"state": self.state}

    def get_action_mask(self):
        return self.player.get_action_mask()

    def get_root(self):
        return self.state.clone()

    # TODO: Records
    # TODO: Observation permutations
