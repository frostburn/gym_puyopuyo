from __future__ import print_function

import pytest

from gym_puyopuyo.field import BottomField

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


def test_clear_groups():
    O = Y + 1  # noqa
    stack = [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, G, _, _, _,
        _, _, _, _, G, G, _, _,
        _, _, O, _, G, Y, _, _,
        R, R, O, _, G, Y, _, _,
        R, R, O, _, G, Y, _, _,
    ]
    field = BottomField.from_list(stack, has_garbage=True)
    field.render()
    print()
    score = field.clear_groups(3)
    field.render()
    stack = field.to_list()
    assert (score == 9)
    assert (stack == [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, O, _, _, Y, _, _,
        _, _, _, _, _, Y, _, _,
        _, _, _, _, _, Y, _, _,
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
    chain = field.resolve()[1]
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


def test_resolve_garbage():
    O = Y + 1  # noqa
    stack = [
        R, Y, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, Y, _, _, _, _, _,
        _, O, O, O, _, _, _, _,
        R, G, B, O, O, _, _, _,
        R, R, G, B, O, O, _, _,
        G, G, B, B, O, O, O, _,
    ]
    field = BottomField.from_list(stack, has_garbage=True)
    field.render()
    print()
    chain = field.resolve()[1]
    field.render()
    stack = field.to_list()
    assert (stack == [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, O, O, _, _, _,
        _, _, Y, O, O, O, _, _,
        _, Y, O, O, O, O, O, _,
    ])
    assert (chain == 2)


def test_overlay():
    field = BottomField(3)
    field.overlay([R, G, _, _, _, _, _, _])
    field.handle_gravity()
    field.render()
    print()
    field.overlay([
        _, Y, _, _, _, _, _, _,
        _, Y, _, _, _, _, _, _,
    ])
    field.handle_gravity()
    field.render()
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


def test_overlapping_overlay():
    field = BottomField(4)
    field.overlay([R, B, _, _, _, _, _, _])
    field.render()
    print()
    field.overlay([G, Y, G, _, _, _, _, _])
    field.render()
    stack = field.to_list()
    assert (stack[:8] == [R, B, G, _, _, _, _, _])


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


def test_uneven_from_list():
    bad_stack = [R, G, B]
    with pytest.raises(ValueError):
        BottomField.from_list(bad_stack)


def test_too_big_from_list():
    bad_stack = [R, G, B] * 80
    with pytest.raises(ValueError):
        BottomField.from_list(bad_stack)


def _reference_valid_moves(lines):
    valid = []
    for x in range(7):
        if (lines[0] & (1 << x)) | (lines[0] & (2 << x)):
            valid.append(False)
        else:
            valid.append(True)
    for x in range(8):
        if (lines[0] & (1 << x)) | (lines[1] & (1 << x)):
            valid.append(False)
        else:
            valid.append(True)
    return sum(v * (1 << i) for i, v in enumerate(valid))


def test_valid_moves():
    field = BottomField(1)
    for top in range(1 << 16):
        field.data[0] = top & 255
        field.data[1] = top >> 8

        assert (_reference_valid_moves(field.data) == field._valid_moves())


def test_mirror():
    stack = [
        R, R, _, _, _, _, _, _,
        G, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, G, _, _, _, _, _,
        _, _, _, _, _, _, _, R,
    ]
    field = BottomField.from_list(stack)
    field.render()
    print()
    field.mirror()
    field.render()
    stack = field.to_list()
    assert (stack == [
        _, _, _, _, _, _, R, R,
        _, _, _, _, _, _, _, G,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, G, _, _,
        R, _, _, _, _, _, _, _,
    ])


def test_positive_shift():
    stack = [
        R, R, _, _, _, _, _, _,
        G, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, G, _, _, _, _, _,
        _, _, _, R, _, _, _, _,
    ]
    field = BottomField.from_list(stack)
    field.render()
    print()
    field.shift(1)
    field.render()
    stack = field.to_list()
    assert (stack == [
        _, R, R, _, _, _, _, _,
        _, G, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, G, _, _, _, _,
        _, _, _, _, R, _, _, _,
    ])


def test_negative_shift():
    stack = [
        _, _, G, _, _, _, _, _,
        _, _, _, G, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, G, _, _, _, _, _,
        _, _, _, R, _, _, _, R,
    ]
    field = BottomField.from_list(stack)
    field.render()
    print()
    field.shift(-2)
    field.render()
    stack = field.to_list()
    assert (stack == [
        G, _, _, _, _, _, _, _,
        _, G, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        G, _, _, _, _, _, _, _,
        _, R, _, _, _, R, _, _,
    ])
