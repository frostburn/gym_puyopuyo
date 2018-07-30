from gym_puyopuyo.field import BottomField
from gym_puyopuyo.rendering.state import AnimationState
from gym_puyopuyo.state import State


def test_gravity():
    _ = None
    stack = [_] * 8 * 6
    stack += [
        1, 2, _, 1, _, _, _, _,
        3, _, _, _, _, _, _, _,
    ]

    state = State(8, 4, 4, deals=[])
    state.field = BottomField.from_list(stack)

    state = AnimationState(state)

    assert state.step_gravity()

    stack = [_] * 4 * 6
    stack += [
        1, _, _, _,
        3, 2, _, 1,
    ]

    assert state.to_list() == stack

    assert not state.step_gravity()
