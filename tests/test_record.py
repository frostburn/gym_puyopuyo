from __future__ import unicode_literals

import json
try:  # noqa: I003
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from gym_puyopuyo.record import read_record, write_record  # noqa: I001
from gym_puyopuyo.state import State  # noqa: I001


def test_write_record():
    state = State(13, 6, 4, 3, True)
    actions = state.actions[:]
    stream = StringIO()
    write_record(stream, state, actions)
    stream.seek(0)
    stacks = json.load(stream)
    assert (len(stacks) == len(actions))
    assert (stacks[0][0])
    assert (any(stacks[-1]))


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
    actions = [
        (0, 0),
        (2, 1),
        (1, 0),
        (0, 1),
        (1, 0),
        (3, 1),
        (3, 1),
        (4, 1),
        (4, 1),
        (5, 1),
        (5, 1),
        (0, 0),
    ]
    stream = StringIO()
    stream.write(record)
    stream.seek(0)
    base_state = State(13, 6, 4, 3, True)
    result = list(read_record(stream, base_state))
    total_reward = 0
    for (state, action, reward), expected_action in zip(result, actions):
        state.render()
        total_reward += reward
        assert (action[0] == expected_action[0])
        assert (action[1] % 2 == expected_action[1])
    assert (total_reward == 4840)
