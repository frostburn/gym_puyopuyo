from __future__ import print_function

import pytest

from gym_puyopuyo.state import BottomState

_ = None
R = 0
G = 1
Y = 2
B = 3
P = 4
C = 5
W = 6


def test_gravity():
    stack = [
        R, R, _, _, _, _, _, _,
        G, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
    ]
    state = BottomState.from_list(stack)
    state.render()
    print()
    state.handle_gravity()
    state.render()
    stack = state.to_list()
    assert (stack == [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        R, _, _, _, _, _, _, _,
        G, R, _, _, _, _, _, _,
    ])


def test_uneven_from_list():
    bad_stack = [R, G, B]
    with pytest.raises(ValueError):
        BottomState.from_list(bad_stack)


def test_too_big_from_list():
    bad_stack = [R, G, B] * 80
    with pytest.raises(ValueError):
        BottomState.from_list(bad_stack)
