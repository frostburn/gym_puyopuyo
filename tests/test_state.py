from __future__ import print_function

import pytest

from gym_puyopuyo.state import BottomField

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
    state = BottomField.from_list(stack)
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


def test_resolve():
    stack = [
        R, Y, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        R, G, B, _, _, _, _, _,
        R, R, G, B, _, _, _, _,
        G, G, B, B, _, _, _, _,
    ]
    state = BottomField.from_list(stack)
    state.render()
    print()
    chain = state.resolve()
    state.render()
    stack = state.to_list()
    assert (stack == [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, Y, _, _, _, _, _, _,
    ])
    assert (chain == 3)


def test_overlay():
    state = BottomField(3)
    state.overlay([R, G, _, _, _, _, _, _])
    state.handle_gravity()
    state.render()
    print()
    valid = state.overlay([
        _, Y, _, _, _, _, _, _,
        _, Y, _, _, _, _, _, _,
    ])
    state.handle_gravity()
    state.render()
    print()
    assert (valid)
    stack = state.to_list()
    assert (stack == [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, Y, _, _, _, _, _, _,
        _, Y, _, _, _, _, _, _,
        R, G, _, _, _, _, _, _,
    ])


def test_invalid_overlay():
    state = BottomField(4)
    state.overlay([R, B, _, _, _, _, _, _])
    valid = state.overlay([G, Y, _, _, _, _, _, _])
    assert (not valid)


def test_encode():
    stack = [
        _, R, _, _, _, _, _, _,
        G, _, G, _, _, _, _, _,
        _, _, _, G, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, R,
    ]
    state = BottomField.from_list(stack)
    state.render()
    encoded = state.encode()
    expected = [
        [
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
        ],
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ],
    ]
    assert (encoded == expected).all()


def test_uneven_from_list():
    bad_stack = [R, G, B]
    with pytest.raises(ValueError):
        BottomField.from_list(bad_stack)


def test_too_big_from_list():
    bad_stack = [R, G, B] * 80
    with pytest.raises(ValueError):
        BottomField.from_list(bad_stack)
