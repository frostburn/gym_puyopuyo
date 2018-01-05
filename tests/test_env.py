import numpy as np
import pytest
from gym.envs.registration import make

from gym_puyopuyo.env import ENV_NAMES, register
from gym_puyopuyo.util import print_up

register()


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
    assert np.isscalar(reward), "{} is not a scalar for {}".format(reward, env)
    assert isinstance(done, bool), "Expected {} to be a boolean".format(done)

    for mode in env.metadata.get('render.modes', []):
        env.render(mode=mode)
    env.render(close=True)

    # Make sure we can render the environment after close.
    for mode in env.metadata.get('render.modes', []):
        env.render(mode=mode)
    env.render(close=True)

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
