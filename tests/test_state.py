from __future__ import print_function

import numpy as np
import pytest

from gym_puyopuyo.field import BottomField, TallField
from gym_puyopuyo.state import State

_ = None
R = 0
G = 1
Y = 2
B = 3
P = 4
C = 5
W = 6


def test_action_mask():
    state = State(8, 7, 2, 1)
    stack = [
        R, _, R, _, _, _, G, _,
    ]
    state.field = BottomField.from_list(stack, num_layers=state.num_layers)
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


def test_action_mask_tsu():
    state = State(13, 6, 2, 1, tsu_rules=True)
    stack = [_, _, _, _, _, _, _, _] * state.field.offset
    stack += [
        R, _, R, G, _, G, _, _,
    ]
    state.field = TallField.from_list(stack, num_layers=state.num_layers, tsu_rules=state.tsu_rules)
    state.render()
    mask = state.get_action_mask()
    print(mask)
    assert (len(mask) == 5 + 5 + 6 + 6)
    for i, (x, orientation) in enumerate(state.actions):
        if x in (1, 4):
            assert (mask[i])
        elif orientation in (0, 2) and x in (0, 3):
            assert (mask[i])
        else:
            assert (not mask[i])


@pytest.mark.parametrize("height", [8, 16])
def test_make_move(height):
    state = State(height, 5, 2, 1)
    state.deals[0] = (0, 1)
    state.render()
    state.play_deal(2, 3)
    state.render()
    _, stack = state.encode()
    print(stack)
    assert (stack[0][1][2])
    assert (stack[1][0][2])


def test_resolve():
    state = State(8, 7, 2, 1)
    state.deals[0] = (0, 0)
    stack = [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, G, G, G, _, _, _, _,
        _, R, R, R, G, G, G, _,
    ]
    state.field = BottomField.from_list(stack, num_layers=state.num_layers)
    state.render()
    reward = state.step(0, 1)
    state.render()
    assert (reward == 4)


def test_resolve_large():
    state = State(16, 7, 2, 1)
    state.deals[0] = (0, 0)
    stack = [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, G, G, G, _, _, _, _,
        _, R, R, R, G, G, G, _,
    ]
    state.field = TallField.from_list(stack, num_layers=state.num_layers)
    state.render()
    reward = state.step(0, 1)
    assert (reward == 8500 + 760)


def test_no_moves():
    state = State(8, 2, 4, 1)
    stack = [
        _, R, _, _, _, _, _, _,
        B, R, _, _, _, _, _, _,
        Y, B, _, _, _, _, _, _,
        G, B, _, _, _, _, _, _,
        G, R, _, _, _, _, _, _,
        Y, R, _, _, _, _, _, _,
        B, G, _, _, _, _, _, _,
        B, R, _, _, _, _, _, _,
    ]
    state.field = BottomField.from_list(stack, num_layers=state.num_layers)
    state.render()
    assert (not state.get_children())


def test_has_moves_tsu():
    state = State(13, 2, 4, 1, tsu_rules=True)
    stack = [_, _, _, _, _, _, _, _] * state.field.offset
    stack += [
        _, R, _, _, _, _, _, _,
        B, R, _, _, _, _, _, _,
        Y, B, _, _, _, _, _, _,
        G, B, _, _, _, _, _, _,
        G, R, _, _, _, _, _, _,
        Y, R, _, _, _, _, _, _,
        B, G, _, _, _, _, _, _,
        B, R, _, _, _, _, _, _,
        B, R, _, _, _, _, _, _,
        Y, B, _, _, _, _, _, _,
        G, B, _, _, _, _, _, _,
        G, R, _, _, _, _, _, _,
        Y, R, _, _, _, _, _, _,
    ]
    state.field = TallField.from_list(stack, num_layers=state.num_layers, tsu_rules=state.tsu_rules)
    state.render()
    assert (state.get_children())


def test_garbage():
    state = State(8, 5, 3, 1, has_garbage=True)
    state.step(0, 0)
    state.add_garbage(9)
    state.render()
    O = state.field.num_colors  # noqa
    stack = state.field.to_list()
    expected = [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        O, O, _, _, _, _, _, _,
        O, O, O, O, _, _, _, _,
        0, 0, O, O, O, _, _, _,
    ]
    for p1, p2 in zip(stack, expected):
        if p1 == O:
            assert (p2 == O)
        else:
            assert (p2 != O)


def test_garbage_tsu():
    state = State(13, 6, 5, 1, tsu_rules=True, has_garbage=True)
    stack = [_, _, _, _, _, _, _, _] * state.field.offset
    stack += [
        _, R, _, _, _, _, _, _,
        B, R, _, _, _, _, _, _,
        Y, B, _, _, _, _, _, _,
        G, B, _, _, _, _, _, _,
        G, R, _, _, _, _, _, _,
        Y, R, _, _, _, _, _, _,
        B, G, _, _, _, _, _, _,
        B, R, _, _, _, _, _, _,
        B, R, _, _, _, _, _, _,
        Y, B, _, _, _, _, _, _,
        G, B, _, _, _, _, _, _,
        G, R, _, _, _, _, _, _,
        Y, R, _, _, _, _, _, _,
    ]
    state.field = TallField.from_list(
        stack,
        num_layers=state.num_layers,
        tsu_rules=state.tsu_rules,
        has_garbage=state.has_garbage
    )
    state.render()
    state.add_garbage(39)
    state.render()
    state.field.resolve()
    assert (state.field.popcount == 51)


@pytest.mark.parametrize("height", [8, 16])
def test_mirrorr(height):
    state = State(height, 5, 3, 5)
    twin = state.clone()
    for i in range(state.num_deals):
        x = np.random.randint(0, state.width - 1)
        orientation = np.random.randint(0, 4)
        state.step(x, orientation)
        x = state.width - x - 1
        if orientation % 2 == 0:
            x -= 1
            orientation = (orientation + 2) % 4
        twin.step(x, orientation)
    state.render()
    twin.render()
    state.mirror()
    state.render()
    assert (state.field.to_list() == twin.field.to_list())
