import gym.envs

from gym_puyopuyo.agent import (
    LargeTreeSearchAgent, SmallTreeSearchAgent, TsuTreeSearchAgent,
    WideTreeSearchAgent)

ENV_NAMES = {
    "small": "PuyoPuyoEndlessSmall-v2",
    "wide": "PuyoPuyoEndlessWide-v2",
    "tsu": "PuyoPuyoEndlessTsu-v2",
    "large": "PuyoPuyoEndlessLarge-v2",
    "normal": "PuyoPuyoEndlessNormal-v2",

    "boxed-small": "PuyoPuyoEndlessBoxedSmall-v1",
    "boxed-wide": "PuyoPuyoEndlessBoxedWide-v1",
    "boxed-tsu": "PuyoPuyoEndlessBoxedTsu-v1",
    "boxed-large": "PuyoPuyoEndlessBoxedLarge-v1",
    "boxed-normal": "PuyoPuyoEndlessBoxedNormal-v1",

    "vs-small": "PuyoPuyoVersusSmall-v0",
    "vs-small-easy": "PuyoPuyoVersusSmallEasy-v0",
    "vs-wide": "PuyoPuyoVersusWide-v0",
    "vs-tsu": "PuyoPuyoVersusTsu-v0",
    "vs-large": "PuyoPuyoVersusLarge-v0",

    "vs-boxed-small": "PuyoPuyoVersusBoxedSmall-v1",
    "vs-boxed-small-easy": "PuyoPuyoVersusBoxedSmallEasy-v1",
    "vs-boxed-wide": "PuyoPuyoVersusBoxedWide-v1",
    "vs-boxed-tsu": "PuyoPuyoVersusBoxedTsu-v1",
    "vs-boxed-large": "PuyoPuyoVersusBoxedLarge-v1",
}


ENV_PARAMS = {
    ENV_NAMES["vs-small"]: {
        "height": 8,
        "width": 3,
        "num_colors": 3,
        "num_deals": 3,
        "target_score": 1,
        "step_bonus": 0,
        "all_clear_bonus": 0,
    },
    ENV_NAMES["vs-wide"]: {
        "height": 8,
        "width": 8,
        "num_colors": 4,
        "num_deals": 3,
        "target_score": 1,
        "step_bonus": 0,
        "all_clear_bonus": 16,
    },
    ENV_NAMES["vs-tsu"]: {
        "height": 13,
        "width": 6,
        "tsu_rules": True,
        "num_colors": 4,
        "num_deals": 3,
        "target_score": 70,
        "step_bonus": 10,
        "all_clear_bonus": 70 * 5 * 6,
        "max_received_garbage": 5 * 6,
    },
    ENV_NAMES["vs-large"]: {
        "height": 16,
        "width": 8,
        "num_colors": 5,
        "num_deals": 3,
        "target_score": 70,
        "step_bonus": 10,
        "all_clear_bonus": 70 * 5 * 8,
        "max_received_garbage": 5 * 8,
    },
}


class TreeWrapper(object):
    def __init__(self, agent):
        self.agent = agent

    def __call__(self, game):
        if game.players[0].chain_number:
            return 0
        return self.agent.get_action(game.players[0])


def register():
    # Single player

    gym.envs.register(
        id=ENV_NAMES["small"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessEnv",
        kwargs={"width": 3, "height": 8, "num_colors": 3, "num_deals": 3},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.register(
        id=ENV_NAMES["wide"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessEnv",
        kwargs={"width": 8, "height": 8, "num_colors": 4, "num_deals": 3},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.register(
        id=ENV_NAMES["tsu"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessEnv",
        kwargs={"width": 6, "height": 13, "num_colors": 4, "num_deals": 3, "tsu_rules": True},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.register(
        id=ENV_NAMES["large"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessEnv",
        kwargs={"width": 8, "height": 16, "num_colors": 5, "num_deals": 3},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.register(
        id=ENV_NAMES["normal"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessEnv",
        kwargs={"width": 6, "height": 12, "num_colors": 4, "num_deals": 2, "tsu_rules": False},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    # Single player with a contiguous observation space

    gym.envs.register(
        id=ENV_NAMES["boxed-small"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessBoxedEnv",
        kwargs={"width": 3, "height": 8, "num_colors": 3, "num_deals": 3},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.register(
        id=ENV_NAMES["boxed-wide"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessBoxedEnv",
        kwargs={"width": 8, "height": 8, "num_colors": 4, "num_deals": 3},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.register(
        id=ENV_NAMES["boxed-tsu"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessBoxedEnv",
        kwargs={"width": 6, "height": 13, "num_colors": 4, "num_deals": 3, "tsu_rules": True},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.register(
        id=ENV_NAMES["boxed-large"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessBoxedEnv",
        kwargs={"width": 8, "height": 16, "num_colors": 5, "num_deals": 3},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    gym.envs.register(
        id=ENV_NAMES["boxed-normal"],
        entry_point="gym_puyopuyo.env.endless:PuyoPuyoEndlessEnv",
        kwargs={"width": 6, "height": 12, "num_colors": 4, "num_deals": 2, "tsu_rules": False},
        max_episode_steps=None,
        reward_threshold=25.0,
    )

    # Multiplayer with a fixed opponent

    agent = SmallTreeSearchAgent()
    agent.depth = 3
    agent = TreeWrapper(agent)
    gym.envs.register(
        id=ENV_NAMES["vs-small"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-small"]],
        },
        max_episode_steps=None,
        reward_threshold=1,
    )
    gym.envs.register(
        id=ENV_NAMES["vs-boxed-small"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusBoxedEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-small"]],
        },
        max_episode_steps=None,
        reward_threshold=1,
    )

    agent = lambda game: game.players[0].np_random.randint(0, len(game.players[0].actions))  # noqa
    gym.envs.register(
        id=ENV_NAMES["vs-small-easy"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-small"]],
            "garbage_clue_weight": 0.01
        },
        max_episode_steps=None,
        reward_threshold=1,
    )
    gym.envs.register(
        id=ENV_NAMES["vs-boxed-small-easy"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusBoxedEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-small"]],
            "garbage_clue_weight": 0.01
        },
        max_episode_steps=None,
        reward_threshold=1,
    )

    agent = WideTreeSearchAgent()
    agent.depth = 2
    agent = TreeWrapper(agent)
    gym.envs.register(
        id=ENV_NAMES["vs-wide"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-wide"]],
        },
        max_episode_steps=None,
        reward_threshold=1,
    )
    gym.envs.register(
        id=ENV_NAMES["vs-boxed-wide"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusBoxedEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-wide"]],
        },
        max_episode_steps=None,
        reward_threshold=1,
    )

    agent = TsuTreeSearchAgent()
    agent.depth = 2
    agent = TreeWrapper(agent)
    gym.envs.register(
        id=ENV_NAMES["vs-tsu"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-tsu"]],
        },
        max_episode_steps=None,
        reward_threshold=1,
    )
    gym.envs.register(
        id=ENV_NAMES["vs-boxed-tsu"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusBoxedEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-tsu"]],
        },
        max_episode_steps=None,
        reward_threshold=1,
    )

    agent = LargeTreeSearchAgent()
    agent.depth = 2
    agent = TreeWrapper(agent)
    gym.envs.register(
        id=ENV_NAMES["vs-large"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-large"]],
        },
        max_episode_steps=None,
        reward_threshold=1,
    )
    gym.envs.register(
        id=ENV_NAMES["vs-boxed-large"],
        entry_point="gym_puyopuyo.env.versus:PuyoPuyoVersusBoxedEnv",
        kwargs={
            "opponent": agent,
            "state_params": ENV_PARAMS[ENV_NAMES["vs-large"]],
        },
        max_episode_steps=None,
        reward_threshold=1,
    )
