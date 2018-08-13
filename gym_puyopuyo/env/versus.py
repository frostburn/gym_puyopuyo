import sys

import gym
import numpy as np
from gym import spaces
from six import StringIO

from gym_puyopuyo.versus import Game


class PuyoPuyoVersusEnv(gym.Env):
    """
    Puyo Puyo environment. Versus mode.
    """

    TESTING = False

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
            "deals": spaces.Box(0, 1, (player.num_colors, player.num_deals, 2), dtype=np.int8),
            "field": spaces.Box(0, 1, (player.num_layers, player.height, player.width), dtype=np.int8),
            "chain_number": spaces.Discrete(player.max_chain),
            "pending_score": spaces.Discrete(max_score),
            "pending_garbage": spaces.Discrete(max_score // player.target_score),
            "all_clear": spaces.Discrete(2),
        })
        self.observation_space = spaces.Tuple((player_space, player_space))
        self.action_space = spaces.Discrete(len(player.actions))
        self.player = player
        self.seed()

        self.viewer = None
        self.anim_states = [None, None]
        self.last_actions = [None, None]

    def seed(self, seed=None):
        return [self.state.seed(seed)]

    def reset(self):
        self.state.reset()
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

            for i in range(len(self.state.players)):
                player = self.state.players[i]
                if self.anim_states[i]:
                    # TODO: Intra step frames
                    # self.anim_states[i].state.deals[1:] = player.deals[:-1]
                    self.anim_states[i].state.deals[:] = player.deals[:-1]
                    self.anim_states[i].state.field.data[:] = player.field.data
                else:
                    self.anim_states[i] = AnimationState(player.clone())
                if self.last_actions[i] is not None:
                    # TODO: Intra step frames
                    # self.anim_states[i].state.play_deal(*player.actions[self.last_actions[i]])
                    self.anim_states[i].infer_entities()

            if not self.viewer:
                self.viewer = ImageViewer(
                    width=(self.anim_states[0].width + 5) * len(self.state.players) - 1,
                    height=self.anim_states[0].height
                )

            # TODO: Synchronous gravity resolution
            # persistent_frames = [None, None]
            # for frames in zip_longest(*(state.resolve() for state in self.anim_states)):
            #     self.viewer.begin_flip()
            #     for i, frame in enumerate(frames):
            #         if frame:
            #             persistent_frames[i] = frame
            #         self.viewer.render_state(
            #             persistent_frames[i],
            #             x_offset=i * (frame.width + 5),
            #             flip=False
            #         )
            #     self.viewer.end_flip()
            #     sleep(0.05)

            self.viewer.begin_flip()
            for i, frame in enumerate(self.anim_states):
                self.viewer.render_state(
                    frame,
                    x_offset=i * (frame.width + 5),
                    flip=False
                )
            self.viewer.end_flip()
            sleep(0.5)

            return

        outfile = StringIO() if mode == "ansi" else sys.stdout
        self.state.render(outfile)
        if mode == "ansi":
            return outfile

    def step(self, action):
        self.last_actions[0] = action
        root = self.get_root()
        root.players = root.players[::-1]
        opponent_action = self.opponent(root)
        self.last_actions[1] = opponent_action
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


class PuyoPuyoVersusBoxedEnv(PuyoPuyoVersusEnv):
    """
    Environment with observations in the form of a single box to make it compatible with plain CNN policies.
    """

    def __init__(self, *args, **kwargs):
        super(PuyoPuyoVersusBoxedEnv, self).__init__(*args, **kwargs)
        player = self.state.players[0]
        self.observation_space = spaces.Box(0, 1, (
            player.num_layers,
            player.height + 1 + player.num_deals,
            (player.width + 1) * len(self.state.players) - 1),
            dtype=np.float32,
        )

    def encode(self):
        assert len(self.state.players) == 2
        player = self.state.players[0]
        opponent = self.state.players[1]
        bottom_box = np.concatenate((
            player.encode_field(),
            np.zeros((player.num_layers, player.height, 1), dtype=np.int8),
            opponent.encode_field()
        ), axis=2)
        top_box = np.concatenate((
            player.encode_deals_box(),
            np.zeros((player.num_layers, player.num_deals, 1), dtype=np.int8),
            opponent.encode_deals_box(),
        ), axis=2)
        padding = np.zeros((player.num_layers, 1, (player.width + 1) * len(self.state.players) - 1), dtype=np.int8)
        box = np.concatenate((top_box, padding, bottom_box), axis=1).astype(np.float32)

        assert player.num_deals >= 3
        # Add "gauges" for garbage
        mask = 0.25 ** np.arange(player.width)
        pending_score = player.chain_score + player.step_score
        player_gauge = np.tanh(np.vstack((
            mask * pending_score,
            mask * player.pending_garbage
        )))
        pending_score = opponent.chain_score + opponent.step_score
        opponent_gauge = np.tanh(np.vstack((
            mask * pending_score,
            mask * opponent.pending_garbage
        )))
        box[player.num_layers - 1, 0:2, 0:player.width] = player_gauge
        box[opponent.num_layers - 1, 0:2, player.width + 1:] = opponent_gauge

        # All clear flags
        box[player.num_layers - 1, 2, 0] = player.all_clear_pending
        box[opponent.num_layers - 1, 2, player.width + 1] = opponent.all_clear_pending

        return box

    def reset(self):
        super(PuyoPuyoVersusBoxedEnv, self).reset()
        return self.encode()

    def step(self, action):
        _, reward, done, info = super(PuyoPuyoVersusBoxedEnv, self).step(action)
        return self.encode(), reward, done, info
