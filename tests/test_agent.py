import pytest
from gym import make

from gym_puyopuyo.agent import AGENTS
from gym_puyopuyo.env import ENV_NAMES


@pytest.mark.parametrize("name", AGENTS.keys())
def test_agent(name):
    env = make(ENV_NAMES[name])
    agent = AGENTS[name]()

    env.reset()
    state = env.unwrapped.state
    for i in range(3):
        action = agent.get_action(state)
        _, _, done, info = env.step(action)
        state = info["state"]
        env.render()
        if done:
            break
