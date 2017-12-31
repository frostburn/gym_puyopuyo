from __future__ import print_function

import pytest

from gym_puyopuyo.state import BottomField, BottomState

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
    field = BottomField.from_list(stack)
    field.render()
    print()
    field.handle_gravity()
    field.render()
    stack = field.to_list()
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
    field = BottomField.from_list(stack)
    field.render()
    print()
    chain = field.resolve()
    field.render()
    stack = field.to_list()
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
    field = BottomField(3)
    field.overlay([R, G, _, _, _, _, _, _])
    field.handle_gravity()
    field.render()
    print()
    valid = field.overlay([
        _, Y, _, _, _, _, _, _,
        _, Y, _, _, _, _, _, _,
    ])
    field.handle_gravity()
    field.render()
    print()
    assert (valid)
    stack = field.to_list()
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
    field = BottomField(4)
    field.overlay([R, B, _, _, _, _, _, _])
    valid = field.overlay([G, Y, _, _, _, _, _, _])
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
    field = BottomField.from_list(stack)
    field.render()
    encoded = field.encode()
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


def test_action_mask():
    state = BottomState(8, 7, 2, 1)
    stack = [
        R, _, R, _, _, _, G, _,
    ]
    state.field = BottomField.from_list(stack, num_colors=state.num_colors)
    state.render()
    mask = state.get_action_mask()
    print(mask)
    assert (len(mask) == 6 + 6 + 7 + 7)
    for i, (x, orientation) in enumerate(state.actions):
        if x in (3, 4):
            assert (mask[i])
        elif orientation in (1, 3) and x in (1, 5):
            assert (mask[i])
        else:
            assert (not mask[i])


def test_uneven_from_list():
    bad_stack = [R, G, B]
    with pytest.raises(ValueError):
        BottomField.from_list(bad_stack)


def test_too_big_from_list():
    bad_stack = [R, G, B] * 80
    with pytest.raises(ValueError):
        BottomField.from_list(bad_stack)
