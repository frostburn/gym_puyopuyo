import random

import pytest

from gym_puyopuyo.versus import Game


@pytest.mark.parametrize("height", [8, 16])
def test_single_garbage(height):
    params = {
        "height": height,
        "width": 8,
        "num_colors": 4,
        "deals": [(0, 0), (0, 0), (1, 1), (1, 2), (2, 3), (3, 3)],
        "target_score": 1 if height == 8 else 70,
        "step_bonus": 0 if height == 8 else 20,
    }

    game = Game(state_params=params)
    game.step([(0, 0), (1, 1)])
    game.render()
    game.step([(0, 0), (7, 1)])
    game.render()
    game.step([(2, 0), (7, 1)])
    game.render()
    assert (4 not in game.players[1].field.to_list())
    game.step([(2, 0), (0, 1)])
    game.render()
    assert (4 in game.players[1].field.to_list())
    game.step([(2, 0), (2, 1)])
    game.render()
    result, garbage, done = game.step([(2, 0), (0, 1)])
    game.render()
    assert (result == 0)
    assert (done is False)


@pytest.mark.parametrize("height", [8, 16])
def test_gravity_delay(height):
    params = {
        "height": height,
        "width": 8,
        "num_colors": 4,
        "deals": [(0, 0), (1, 1), (0, 0), (1, 2), (2, 3), (3, 3)],
        "target_score": 1 if height == 8 else 70,
        "step_bonus": 0 if height == 8 else 10,
    }

    game = Game(state_params=params)
    game.step([(0, 0), (1, 1)])
    game.render()
    game.step([(0, 0), (7, 1)])
    game.render()
    game.step([(2, 0), (7, 1)])
    game.render()
    game.step([(2, 0), (0, 1)])
    game.render()
    result, garbage, done = game.step([(2, 0), (2, 1)])
    game.render()
    assert (garbage)
    assert (4 not in game.players[1].field.to_list())
    result, garbage, done = game.step([(2, 0), (0, 1)])
    game.render()
    assert (4 in game.players[1].field.to_list())
    assert (result == 0)
    assert (done is False)


def test_mirror():
    params = {
        "height": 8,
        "width": 4,
        "num_colors": 3,
        "num_deals": 2,
        "target_score": 1,
    }
    game = Game(state_params=params)
    for i in range(100):
        action = random.choice(game.players[0].actions)
        result, garbage, done = game.step([action, action])
        game.render()
        stack = game.players[0].field.to_list()
        assert (not garbage)
        assert (3 not in stack)
        assert (stack == game.players[1].field.to_list())
        if done:
            break
    assert (result == 0)


@pytest.mark.parametrize("height", [8, 13, 16])
def test_random(height):
    params = {
        "tsu_rules": (height == 13),
        "height": height,
        "width": 5,
        "num_colors": 4,
        "num_deals": 2,
        "target_score": 70,
        "step_bonus": 10,
        "all_clear_bonus": 70 * 5 * 5,
    }
    game = Game(state_params=params)
    for i in range(100):
        actions = [random.choice(p.actions) for p in game.players]
        print(actions)
        result, garbage, done = game.step(actions)
        game.render()
        if done:
            break
    assert (result in (-1, 0, 1))
