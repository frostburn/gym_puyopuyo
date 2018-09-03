import numpy as np
import pytest
from gym.envs.registration import make
from six import StringIO

from gym_puyopuyo.env import ENV_NAMES, ENV_PARAMS
from gym_puyopuyo.env.versus import PuyoPuyoVersusEnv
from gym_puyopuyo.util import print_up


@pytest.mark.parametrize("name", ENV_NAMES.values())
def test_env(name):
    env = make(name)
    ob_space = env.observation_space
    act_space = env.action_space
    ob = env.reset()
    msg = 'Reset observation: {!r} not in space'.format(ob)
    assert ob_space.contains(ob), msg
    a = act_space.sample()
    observation, reward, done, _info = env.step(a)
    msg = 'Step observation: {!r} not in space'.format(observation)
    assert ob_space.contains(observation), msg
    if hasattr(env.unwrapped, "permute_observation"):
        permuted = env.unwrapped.permute_observation(observation)
        print(permuted[0] == observation[0])
        assert ob_space.contains(permuted), msg
    assert np.isscalar(reward), "{} is not a scalar for {}".format(reward, env)
    assert isinstance(done, bool), "Expected {} to be a boolean".format(done)

    for mode in env.metadata.get('render.modes', []):
        env.render(mode=mode)
    env.close()

    # Make sure we can render the environment after close.
    for mode in env.metadata.get('render.modes', []):
        env.render(mode=mode)
    env.close()


@pytest.mark.parametrize("name", ENV_NAMES.values())
def test_random_rollout(name):
    env = make(name)
    agent = lambda ob: env.action_space.sample()  # noqa: E731
    ob = env.reset()
    for _ in range(100):
        assert env.observation_space.contains(ob)
        a = agent(ob)
        assert env.action_space.contains(a)
        action_mask = env.unwrapped.get_action_mask()
        (ob, _reward, done, _info) = env.step(a)
        env.render(mode="human")
        if done:
            break
        else:
            assert action_mask[a]


def test_custom_vs():
    agent = lambda game: np.random.randint(0, 22)  # noqa: E731
    env = PuyoPuyoVersusEnv(agent, ENV_PARAMS[ENV_NAMES["vs-tsu"]], garbage_clue_weight=1)
    ob = env.reset()
    assert env.observation_space.contains(ob)
    env.step(11)
    env.render()


@pytest.mark.parametrize("name", [ENV_NAMES["small"], ENV_NAMES["tsu"]])
def test_tree_search(name):
    env = make(name)

    def deep_agent():
        root = env.unwrapped.get_root()
        best_score = 0
        best_action = np.random.randint(0, env.action_space.n)
        for action, (child, score) in enumerate(root.get_children(True)):
            if child is None:
                continue
            for grand_child, child_score in child.get_children():
                for _, grand_child_score in grand_child.get_children():
                    total = score + child_score + grand_child_score
                    if total > best_score:
                        best_action = action
                        best_score = total
        return best_action

    def agent():
        root = env.unwrapped.get_root()
        best_score = 0
        best_action = np.random.randint(0, env.action_space.n)
        for action, (child, score) in enumerate(root.get_children(True)):
            if child is None:
                continue
            for _, child_score in child.get_children():
                total = score + child_score
                if total > best_score:
                    best_action = action
                    best_score = total
        return best_action

    env.reset()
    total_reward = 0
    for _ in range(10):
        _, reward, done, _ = env.step(agent())
        if done:
            break
        total_reward += reward
        env.render(mode="human")
        print_up(1)
        print("Reward =", total_reward)


def test_read_record():
    record = """[[
    1, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0
    ],[
    0, 0, 1, 0, 0, 0,
    0, 0, 2, 0, 0, 0
    ],[
    0, 3, 2, 0, 0, 0,
    0, 0, 0, 0, 0, 0
    ],[
    3, 0, 0, 0, 0, 0,
    3, 0, 0, 0, 0, 0
    ],[
    0, 1, 2, 0, 0, 0,
    0, 0, 0, 0, 0, 0
    ],[
    0, 0, 0, 2, 0, 0,
    0, 0, 0, 4, 0, 0
    ],[
    0, 0, 0, 4, 0, 0,
    0, 0, 0, 4, 0, 0
    ],[
    0, 0, 0, 0, 1, 0,
    0, 0, 0, 0, 1, 0
    ],[
    0, 0, 0, 0, 1, 0,
    0, 0, 0, 0, 4, 0
    ],[
    0, 0, 0, 0, 0, 2,
    0, 0, 0, 0, 0, 2
    ],[
    0, 0, 0, 0, 0, 2,
    0, 0, 0, 0, 0, 1
    ],[
    3, 4, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0
    ]]"""
    stream = StringIO()
    stream.write(record)
    stream.seek(0)
    env = make(ENV_NAMES["tsu"])
    for observation, reward, done, info in env.read_record(stream):
        info["state"].render()


@pytest.mark.parametrize(
    "name",
    [
        ENV_NAMES["boxed-small"], ENV_NAMES["boxed-wide"], ENV_NAMES["boxed-tsu"], ENV_NAMES["boxed-large"],
        ENV_NAMES["vs-boxed-small"], ENV_NAMES["vs-boxed-small-easy"],
        ENV_NAMES["vs-boxed-wide"], ENV_NAMES["vs-boxed-tsu"], ENV_NAMES["vs-boxed-large"],
    ]
)
def test_boxed(name):
    env = make(name)
    initial = env.reset()
    env.render()
    height, width, num_layers = env.observation_space.shape
    if name == ENV_NAMES["boxed-large"]:
        assert height == (16 + 1 + 3)
        assert width == 8
        assert num_layers == 5
    if "Versus" in name:
        width = (width - 1) // 2
    final, _, _, _ = env.step(width * 2)  # Drop straight down.
    env.render()
    print(initial)
    print(final)

    for i in range(num_layers):
        # Check that the deal fell to the bottom.
        assert (initial[2, 0, i] == final[height - 1, 0, i])
        assert (initial[2, 1, i] == final[height - 1, 1, i])

        # Check that the deals advanced.
        assert (initial[0, 0, i] == final[1, 0, i])
        assert (initial[0, 1, i] == final[1, 1, i])
        assert (initial[1, 0, i] == final[2, 0, i])
        assert (initial[1, 1, i] == final[2, 1, i])
