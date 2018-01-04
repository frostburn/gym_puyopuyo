from __future__ import print_function

import pytest

from gym_puyopuyo.field import TallField

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
        _, _, _, _, _, _, R, _,
        _, _, _, _, _, _, R, _,
        _, _, _, _, _, _, _, G,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
    ]
    field = TallField.from_list(stack)
    field.render()
    field.handle_gravity()
    print()
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
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        R, _, _, _, _, _, R, _,
        G, R, _, _, _, _, R, G,
    ])


@pytest.mark.parametrize("tsu_rules", [True, False])
def test_resolve_plain(tsu_rules):
    stack = [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, G, _, _, _, _, _, _,
        _, G, _, _, _, _, _, _,
        _, G, _, _, _, _, _, _,
        _, B, G, _, _, _, _, _,
        _, G, B, _, _, _, _, _,
        _, G, B, _, _, _, _, _,
        R, R, G, _, _, _, _, _,
        R, R, G, G, _, _, _, _,
    ]
    field = TallField.from_list(stack)
    field.render()
    print()
    score, chain = field.resolve(tsu_rules=tsu_rules)
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
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, B, _, _, _, _, _,
        _, B, B, _, _, _, _, _,
    ])
    assert (chain == 2)
    assert (score == 940)


def test_resolve_all_clear():
    stack = [
        R, G, _, _, _, _, _, _,
        _, _, R, _, _, _, _, _,
        _, _, R, _, _, _, _, _,
        _, _, R, _, _, _, _, _,
        _, _, Y, R, _, _, _, _,
        _, _, Y, R, _, _, _, _,
        _, _, Y, R, _, _, _, _,
        _, _, R, Y, _, _, _, _,
        _, _, R, Y, _, _, _, _,
        _, _, R, Y, _, _, _, _,
        _, _, Y, R, _, _, _, _,
        _, _, Y, R, _, _, _, _,
        _, _, Y, R, _, _, _, _,
        R, G, B, Y, _, _, _, _,
        R, R, G, B, _, _, _, _,
        G, G, B, B, _, _, _, _,
    ]
    field = TallField.from_list(stack)
    field.render()
    print()
    score, chain = field.resolve()
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
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
    ])
    assert (chain == 3)
    expected = 8500  # all clear
    expected += 4 * 10 * (1)  # Reds
    expected += 5 * 10 * (8 + 2)  # Greens
    # Blues, yellows and reds
    num_cleared = 26
    chain_power = 16
    group_bonuses = 0 + 0 + 3 + 3 + 3
    color_bonus = 6
    expected += num_cleared * 10 * (chain_power + group_bonuses + color_bonus)
    assert (score == expected)


def test_resolve_ghost():
    stack = [
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, P, _, _,
        _, _, _, _, _, P, _, _,
        _, _, _, _, _, P, _, _,
        _, _, _, _, _, P, _, _,
        _, _, _, _, _, B, _, _,
        _, _, _, _, _, B, _, _,
        _, _, _, _, _, B, _, _,
        _, _, _, _, _, B, _, _,
        _, _, _, _, _, R, _, _,
        _, _, _, _, _, R, _, _,
        _, _, _, _, _, Y, _, _,
        _, _, _, _, _, G, _, _,
        _, _, _, _, _, G, _, _,
    ]
    field = TallField.from_list(stack)
    field.render()
    print()
    score, chain = field.resolve(tsu_rules=True)
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
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, R, _, _,
        _, _, _, _, _, R, _, _,
        _, _, _, _, _, Y, _, _,
        _, _, _, _, _, G, _, _,
        _, _, _, _, _, G, _, _,
    ])
    assert (chain == 2)
    assert (score == 360)
